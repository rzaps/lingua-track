from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta
from words.models import Card, Repetition
from .models import TestResult, UserStats

# Главная страница статистики (dashboard)
# Показывает общую статистику пользователя: карточки, повторения, тесты
@login_required
def dashboard(request):
    # Получаем или создаём статистику пользователя
    user_stats, created = UserStats.objects.get_or_create(user=request.user)
    
    # Обновляем статистику карточек
    cards = Card.objects.filter(user=request.user)
    user_stats.total_cards = cards.count()
    user_stats.beginner_cards = cards.filter(level='beginner').count()
    user_stats.intermediate_cards = cards.filter(level='intermediate').count()
    user_stats.advanced_cards = cards.filter(level='advanced').count()
    
    # Обновляем статистику повторений
    repetitions = Repetition.objects.filter(user=request.user)
    user_stats.total_reviews = repetitions.aggregate(total=Sum('total_reviews'))['total'] or 0
    user_stats.successful_reviews = repetitions.aggregate(success=Sum('successful_reviews'))['success'] or 0
    user_stats.failed_reviews = repetitions.aggregate(failed=Sum('failed_reviews'))['failed'] or 0
    
    # Обновляем статистику тестов
    test_results = TestResult.objects.filter(user=request.user)
    user_stats.total_tests = test_results.count()
    if user_stats.total_tests > 0:
        # Вычисляем среднюю точность в Python, так как accuracy - это property
        total_accuracy = sum(test.accuracy for test in test_results)
        user_stats.tests_accuracy = total_accuracy / user_stats.total_tests
    else:
        user_stats.tests_accuracy = 0
    
    user_stats.save()
    
    # Получаем последние тесты
    recent_tests = test_results.order_by('-completed_at')[:5]
    
    # Получаем слова, требующие повторения
    today = timezone.now().date()
    due_cards = Card.objects.filter(
        user=request.user,
        repetition__next_review__lte=today
    ).count()
    
    context = {
        'user_stats': user_stats,
        'recent_tests': recent_tests,
        'due_cards': due_cards,
        'recommendations': user_stats.get_recommendations()[:3],  # Топ-3 рекомендации
    }
    return render(request, 'stats/dashboard.html', context)

# Страница с графиками и диаграммами
# Показывает визуализацию прогресса пользователя
@login_required
def charts(request):
    # Статистика по уровням карточек
    level_stats = Card.objects.filter(user=request.user).values('level').annotate(
        count=Count('id')
    ).order_by('level')
    
    # Статистика тестов по типам
    test_results = TestResult.objects.filter(user=request.user)
    test_type_stats = []
    
    # Группируем результаты по типам тестов
    for test_type in ['multiple_choice', 'typing', 'matching']:
        type_results = test_results.filter(test_type=test_type)
        if type_results.exists():
            count = type_results.count()
            avg_accuracy = sum(test.accuracy for test in type_results) / count
            test_type_stats.append({
                'test_type': test_type,
                'count': count,
                'avg_accuracy': avg_accuracy
            })
    
    # Статистика тестов по дням (последние 30 дней)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    daily_test_results = TestResult.objects.filter(
        user=request.user,
        completed_at__date__gte=thirty_days_ago
    ).order_by('completed_at__date')
    
    # Группируем результаты по дням
    daily_test_stats = []
    current_date = None
    current_tests = []
    
    for test in daily_test_results:
        test_date = test.completed_at.date()
        if test_date != current_date:
            if current_tests:
                count = len(current_tests)
                avg_accuracy = sum(t.accuracy for t in current_tests) / count
                daily_test_stats.append({
                    'completed_at__date': current_date,
                    'count': count,
                    'avg_accuracy': avg_accuracy
                })
            current_date = test_date
            current_tests = [test]
        else:
            current_tests.append(test)
    
    # Добавляем последнюю группу
    if current_tests:
        count = len(current_tests)
        avg_accuracy = sum(t.accuracy for t in current_tests) / count
        daily_test_stats.append({
            'completed_at__date': current_date,
            'count': count,
            'avg_accuracy': avg_accuracy
        })
    
    # Статистика повторений по дням
    daily_review_stats = Repetition.objects.filter(
        user=request.user,
        last_reviewed__gte=thirty_days_ago
    ).values('last_reviewed').annotate(
        total_reviews=Sum('total_reviews'),
        successful_reviews=Sum('successful_reviews')
    ).order_by('last_reviewed')
    
    context = {
        'level_stats': list(level_stats),
        'test_type_stats': list(test_type_stats),
        'daily_test_stats': list(daily_test_stats),
        'daily_review_stats': list(daily_review_stats),
    }
    return render(request, 'stats/charts.html', context)

# Страница с рекомендациями
# Показывает персонализированные советы для улучшения обучения
@login_required
def recommendations(request):
    user_stats = get_object_or_404(UserStats, user=request.user)
    
    # Получаем все рекомендации
    all_recommendations = user_stats.get_recommendations()
    
    # Группируем рекомендации по категориям
    card_recommendations = [r for r in all_recommendations if 'слов' in r.lower()]
    review_recommendations = [r for r in all_recommendations if 'повтор' in r.lower()]
    test_recommendations = [r for r in all_recommendations if 'тест' in r.lower()]
    
    # Получаем слова с низкой успешностью повторений
    all_repetitions = Repetition.objects.filter(
        user=request.user,
        total_reviews__gte=3  # Минимум 3 повторения для анализа
    ).select_related('card')
    
    # Фильтруем в Python, так как success_rate - это property
    weak_cards = []
    for repetition in all_repetitions:
        if repetition.success_rate < 70 or repetition.consecutive_failures >= 2:
            weak_cards.append(repetition)
        if len(weak_cards) >= 10:  # Ограничиваем до 10 результатов
            break
    
    context = {
        'user_stats': user_stats,
        'all_recommendations': all_recommendations,
        'card_recommendations': card_recommendations,
        'review_recommendations': review_recommendations,
        'test_recommendations': test_recommendations,
        'weak_cards': weak_cards,
    }
    return render(request, 'stats/recommendations.html', context)

# История тестов
# Показывает все пройденные тесты с детальной статистикой
@login_required
def test_history(request):
    # Получаем все тесты пользователя с пагинацией
    test_results = TestResult.objects.filter(user=request.user).order_by('-completed_at')
    
    # Фильтрация по типу теста
    test_type = request.GET.get('test_type')
    if test_type:
        test_results = test_results.filter(test_type=test_type)
    
    # Фильтрация по направлению
    direction = request.GET.get('direction')
    if direction:
        test_results = test_results.filter(direction=direction)
    
    # Статистика по фильтрам
    total_tests = test_results.count()
    if total_tests > 0:
        avg_accuracy = sum(test.accuracy for test in test_results) / total_tests
    else:
        avg_accuracy = 0
    
    # Группировка по типам тестов
    test_summary = []
    for test_type in ['multiple_choice', 'typing', 'matching']:
        type_results = test_results.filter(test_type=test_type)
        if type_results.exists():
            count = type_results.count()
            avg_accuracy_type = sum(test.accuracy for test in type_results) / count
            best_score = max(test.score for test in type_results)
            test_summary.append({
                'test_type': test_type,
                'count': count,
                'avg_accuracy': avg_accuracy_type,
                'best_score': best_score
            })
    
    context = {
        'test_results': test_results,
        'total_tests': total_tests,
        'avg_accuracy': round(avg_accuracy, 1),
        'test_summary': test_summary,
        'current_filters': {
            'test_type': test_type,
            'direction': direction,
        }
    }
    return render(request, 'stats/test_history.html', context)
