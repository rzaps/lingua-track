"""
Утилиты для интеграции Telegram бота с Django
"""

import os
import django
from datetime import date

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingua_track.settings')
django.setup()

# Импортируем модели после настройки Django
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from words.models import Card, Repetition
from users.models import UserProfile
from stats.models import TestResult, UserStats
from django.core.cache import cache

CACHE_TTL_SHORT = 60  # 1 минута
CACHE_TTL_PROGRESS = 300  # 5 минут


def get_user_by_telegram_id(telegram_id: int) -> User:
    """
    Получает пользователя Django по Telegram ID
    Создаёт пользователя, если его нет
    """
    try:
        # Ищем пользователя по Telegram ID в профиле
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        return profile.user
    except UserProfile.DoesNotExist:
        # Проверяем, не существует ли уже пользователь с таким telegram_id (дополнительная защита)
        if UserProfile.objects.filter(telegram_id=telegram_id).exists():
            return UserProfile.objects.get(telegram_id=telegram_id).user
        # Создаём нового пользователя с профилем
        username = f"telegram_{telegram_id}"
        user = User.objects.create_user(
            username=username,
            email=f"{username}@linguatrack.local",
            password=f"{username}_password"
        )
        UserProfile.objects.create(
            user=user,
            telegram_id=telegram_id,
            is_telegram_user=True
        )
        return user

def link_telegram_to_existing_user(telegram_id: int, telegram_username: str, django_username: str) -> User:
    """
    Связывает существующего пользователя Django с Telegram
    """
    try:
        # Проверяем, не связан ли уже этот Telegram ID с каким-либо пользователем
        try:
            existing_profile = UserProfile.objects.get(telegram_id=telegram_id)
            if existing_profile.user.username != django_username:
                raise ValueError(f"Этот Telegram ID уже привязан к другому аккаунту: {existing_profile.user.username}")
        except UserProfile.DoesNotExist:
            pass
        # Ищем пользователя Django
        user = User.objects.get(username=django_username)
        # Создаём или обновляем профиль
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'telegram_id': telegram_id,
                'telegram_username': telegram_username,
                'is_telegram_user': True
            }
        )
        if not created:
            # Обновляем существующий профиль
            profile.telegram_id = telegram_id
            profile.telegram_username = telegram_username
            profile.is_telegram_user = True
            profile.save()
        return user
    except User.DoesNotExist:
        raise ValueError(f"Пользователь Django с username '{django_username}' не найден")

def get_user_telegram_info(user: User) -> dict:
    """
    Получает информацию о Telegram пользователе
    """
    try:
        profile = user.profile
        return {
            'telegram_id': profile.telegram_id,
            'telegram_username': profile.telegram_username,
            'is_telegram_user': profile.is_telegram_user
        }
    except UserProfile.DoesNotExist:
        return {
            'telegram_id': None,
            'telegram_username': None,
            'is_telegram_user': False
        }

def get_today_cards(user: User) -> list:
    """
    Получает карточки на повторение сегодня
    """
    cache_key = f"today_cards:{user.id}:{timezone.now().date()}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    today = timezone.now().date()
    # Получаем уникальные card_id для избежания дублирования
    card_ids = Repetition.objects.filter(
        user=user, 
        next_review__lte=today
    ).values_list('card_id', flat=True).distinct()
    
    # Получаем карточки по уникальным ID
    cards = list(Card.objects.filter(id__in=card_ids))
    cache.set(cache_key, cards, CACHE_TTL_SHORT)
    return cards

def get_user_cards_paginated(user: User, page: int = 1, per_page: int = 10) -> dict:
    """
    Получает карточки пользователя с пагинацией
    """
    cards = Card.objects.filter(user=user).order_by('-created_at')
    total = cards.count()
    
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'cards': list(cards[start:end]),
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    }

def get_user_progress(user: User) -> dict:
    """
    Получает статистику пользователя
    """
    cache_key = f"user_progress:{user.id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # Получаем или создаём статистику
    user_stats, created = UserStats.objects.get_or_create(user=user)
    
    # Обновляем статистику
    cards = Card.objects.filter(user=user)
    user_stats.total_cards = cards.count()
    user_stats.beginner_cards = cards.filter(level='beginner').count()
    user_stats.intermediate_cards = cards.filter(level='intermediate').count()
    user_stats.advanced_cards = cards.filter(level='advanced').count()
    
    # Статистика повторений
    repetitions = Repetition.objects.filter(user=user)
    agg = repetitions.aggregate(
        total=Sum('total_reviews'),
        success=Sum('successful_reviews'),
        failed=Sum('failed_reviews'),
    )
    user_stats.total_reviews = agg['total'] or 0
    user_stats.successful_reviews = agg['success'] or 0
    user_stats.failed_reviews = agg['failed'] or 0
    
    # Статистика тестов
    test_results = TestResult.objects.filter(user=user)
    user_stats.total_tests = test_results.count()
    if user_stats.total_tests > 0:
        total_accuracy = sum(test.accuracy for test in test_results)
        user_stats.tests_accuracy = total_accuracy / user_stats.total_tests
    
    user_stats.save()
    
    result = {
        'total_cards': user_stats.total_cards,
        'total_reviews': user_stats.total_reviews,
        'total_tests': user_stats.total_tests,
        'review_success_rate': user_stats.review_success_rate,
        'tests_accuracy': round(user_stats.tests_accuracy, 1),
        'beginner_cards': user_stats.beginner_cards,
        'intermediate_cards': user_stats.intermediate_cards,
        'advanced_cards': user_stats.advanced_cards,
    }
    cache.set(cache_key, result, CACHE_TTL_PROGRESS)
    return result

def get_random_cards_for_test(user: User, count: int = 5) -> list:
    """
    Получает случайные карточки для теста
    """
    from django.db.models import Q
    
    # Получаем карточки с повторениями (более изученные)
    cards_with_repetitions = Card.objects.filter(
        user=user,
        repetition__total_reviews__gte=1
    ).distinct()
    
    # Если карточек с повторениями мало, добавляем все карточки
    if cards_with_repetitions.count() < count:
        all_cards = Card.objects.filter(user=user)
        cards_for_test = list(all_cards)
    else:
        cards_for_test = list(cards_with_repetitions)
    
    # Перемешиваем и возвращаем нужное количество
    import random
    random.shuffle(cards_for_test)
    return cards_for_test[:count]

def save_test_result(user: User, test_type: str, direction: str, 
                    score: int, total: int, correct_answers: int, 
                    wrong_answers: int, time_taken: int = None) -> TestResult:
    """
    Сохраняет результат теста
    """
    return TestResult.objects.create(
        user=user,
        test_type=test_type,
        direction=direction,
        score=score,
        total=total,
        correct_answers=correct_answers,
        wrong_answers=wrong_answers,
        time_taken=time_taken
    )

def update_repetition_stats(user: User, card: Card, quality: int):
    """
    Обновляет статистику повторения
    """
    repetition, created = Repetition.objects.get_or_create(
        user=user, 
        card=card
    )
    
    # Обновляем статистику
    repetition.update_stats(quality)
    
    # Обновляем интервал по алгоритму SM-2
    from words.utils import update_sm2
    update_sm2(repetition, quality)
    
    repetition.save() 