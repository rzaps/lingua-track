from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from words.models import Card
from stats.models import TestResult
import random

# Главная страница выбора типа теста и направления
# Пользователь выбирает: тип теста (множественный выбор, ввод, сопоставление) + направление (en-ru, ru-en)
@login_required
def choose_test(request):
    # Получаем все карточки пользователя для проверки
    user_cards = list(Card.objects.filter(user=request.user))
    # Если карточек меньше 2 — тест невозможен
    if len(user_cards) < 2:
        return render(request, 'quiz/need_more_cards.html')

    # Если пользователь отправил форму выбора
    if request.method == 'POST':
        test_type = request.POST.get('test_type')  # Тип теста: multiple_choice, typing, matching
        direction = request.POST.get('direction')   # Направление: en-ru, ru-en
        
        # Сохраняем выбор в сессии
        request.session['quiz_test_type'] = test_type
        request.session['quiz_direction'] = direction
        # Сбросить прогресс предыдущего теста
        request.session['quiz_question_idx'] = 0
        request.session['quiz_score'] = 0
        
        # Перенаправляем на соответствующий тест
        if test_type == 'multiple_choice':
            return redirect('quiz:multiple_choice')
        elif test_type == 'typing':
            return redirect('quiz:typing')
        elif test_type == 'matching':
            return redirect('quiz:matching')
    
    # Показываем форму выбора (GET запрос)
    return render(request, 'quiz/choose_test.html')

# Вьюха для теста с множественным выбором (обновлённая версия)
# Теперь направление берётся из сессии, выбранного на главной странице
@login_required
def multiple_choice_test(request):
    # Получаем все карточки пользователя
    user_cards = list(Card.objects.filter(user=request.user))
    # Если карточек меньше 2 — тест невозможен
    if len(user_cards) < 2:
        return render(request, 'quiz/need_more_cards.html')

    # Получаем направление из сессии (должно быть выбрано на главной странице)
    direction = request.session.get('quiz_direction')
    if not direction:
        # Если направление не выбрано, возвращаемся к выбору
        return redirect('quiz:choose_test')

    # Индекс текущего вопроса (номер карточки в тесте), хранится в сессии
    question_idx = request.session.get('quiz_question_idx', 0)
    # Текущее количество правильных ответов
    score = request.session.get('quiz_score', 0)

    # Если все вопросы пройдены — показать результат и сбросить прогресс
    if question_idx >= len(user_cards):
        result = {'score': score, 'total': len(user_cards)}
        
        # Сохраняем результат теста в статистику
        test_type = request.session.get('quiz_test_type', 'multiple_choice')
        direction = request.session.get('quiz_direction', 'en-ru')
        
        TestResult.objects.create(
            user=request.user,
            test_type=test_type,
            direction=direction,
            score=score,
            total=len(user_cards),
            correct_answers=score,
            wrong_answers=len(user_cards) - score
        )
        
        # Сбросить прогресс для нового теста
        request.session['quiz_question_idx'] = 0
        request.session['quiz_score'] = 0
        return render(request, 'quiz/quiz_result.html', result)

    # Текущая карточка для вопроса
    current_card = user_cards[question_idx]

    # --- Формируем вопрос и варианты в зависимости от направления ---
    if direction == 'en-ru':
        # Показываем слово на английском, варианты — переводы
        question = current_card.word
        correct = current_card.translation
        # Список других карточек (для неправильных вариантов)
        other_cards = [c for c in user_cards if c.pk != current_card.pk]
        # Случайно выбираем до 3 неправильных вариантов
        wrong = random.sample(other_cards, min(3, len(other_cards)))
        options = [correct] + [c.translation for c in wrong]
    else:  # ru-en
        # Показываем перевод, варианты — слова на английском
        question = current_card.translation
        correct = current_card.word
        other_cards = [c for c in user_cards if c.pk != current_card.pk]
        wrong = random.sample(other_cards, min(3, len(other_cards)))
        options = [correct] + [c.word for c in wrong]
    random.shuffle(options)  # Перемешиваем варианты

    # Если пользователь отправил ответ (POST)
    if request.method == 'POST' and 'answer' in request.POST:
        answer = request.POST.get('answer')
        # Если ответ правильный — увеличиваем счёт
        if answer == correct:
            request.session['quiz_score'] = score + 1
        # Переходим к следующему вопросу
        request.session['quiz_question_idx'] = question_idx + 1
        return redirect('quiz:multiple_choice')

    # Контекст для шаблона: вопрос, варианты, прогресс, направление
    context = {
        'question': question,           # Слово или перевод для вопроса
        'options': options,             # Варианты ответа
        'question_number': question_idx + 1,  # Номер текущего вопроса
        'total': len(user_cards),       # Всего вопросов
        'score': score,                 # Количество правильных ответов
        'direction': direction,         # Направление теста
    }
    return render(request, 'quiz/multiple_choice.html', context)

# Вьюха для теста с вводом с клавиатуры
# Пользователь видит слово/перевод и должен ввести правильный ответ
@login_required
def typing_test(request):
    # Получаем все карточки пользователя
    user_cards = list(Card.objects.filter(user=request.user))
    # Если карточек меньше 1 — тест невозможен
    if len(user_cards) < 1:
        return render(request, 'quiz/need_more_cards.html')

    # Получаем направление из сессии (должно быть выбрано на главной странице)
    direction = request.session.get('quiz_direction')
    if not direction:
        # Если направление не выбрано, возвращаемся к выбору
        return redirect('quiz:choose_test')

    # Индекс текущего вопроса (номер карточки в тесте), хранится в сессии
    question_idx = request.session.get('quiz_question_idx', 0)
    # Текущее количество правильных ответов
    score = request.session.get('quiz_score', 0)

    # Если все вопросы пройдены — показать результат и сбросить прогресс
    if question_idx >= len(user_cards):
        result = {'score': score, 'total': len(user_cards)}
        
        # Сохраняем результат теста в статистику
        test_type = request.session.get('quiz_test_type', 'typing')
        direction = request.session.get('quiz_direction', 'en-ru')
        
        TestResult.objects.create(
            user=request.user,
            test_type=test_type,
            direction=direction,
            score=score,
            total=len(user_cards),
            correct_answers=score,
            wrong_answers=len(user_cards) - score
        )
        
        # Сбросить прогресс для нового теста
        request.session['quiz_question_idx'] = 0
        request.session['quiz_score'] = 0
        return render(request, 'quiz/quiz_result.html', result)

    # Текущая карточка для вопроса
    current_card = user_cards[question_idx]

    # --- Формируем вопрос и правильный ответ в зависимости от направления ---
    if direction == 'en-ru':
        # Показываем слово на английском, пользователь вводит перевод
        question = current_card.word
        correct_answer = current_card.translation
    else:  # ru-en
        # Показываем перевод, пользователь вводит слово на английском
        question = current_card.translation
        correct_answer = current_card.word

    # Если пользователь отправил ответ (POST)
    if request.method == 'POST' and 'answer' in request.POST:
        user_answer = request.POST.get('answer').strip().lower()  # Убираем пробелы и приводим к нижнему регистру
        correct_answer_lower = correct_answer.lower()  # Приводим правильный ответ к нижнему регистру
        
        # Если ответ правильный (с учётом регистра) — увеличиваем счёт
        if user_answer == correct_answer_lower:
            request.session['quiz_score'] = score + 1
        
        # Переходим к следующему вопросу
        request.session['quiz_question_idx'] = question_idx + 1
        return redirect('quiz:typing')

    # Контекст для шаблона: вопрос, правильный ответ, прогресс, направление
    context = {
        'question': question,           # Слово или перевод для вопроса
        'question_number': question_idx + 1,  # Номер текущего вопроса
        'total': len(user_cards),       # Всего вопросов
        'score': score,                 # Количество правильных ответов
        'direction': direction,         # Направление теста
    }
    return render(request, 'quiz/typing.html', context)

# Вьюха для теста с сопоставлением
# Пользователь видит список слов и список переводов, должен правильно их соединить
@login_required
def matching_test(request):
    # Получаем все карточки пользователя
    user_cards = list(Card.objects.filter(user=request.user))
    # Если карточек меньше 2 — тест невозможен
    if len(user_cards) < 2:
        return render(request, 'quiz/need_more_cards.html')

    # Получаем направление из сессии (должно быть выбрано на главной странице)
    direction = request.session.get('quiz_direction')
    if not direction:
        # Если направление не выбрано, возвращаемся к выбору
        return redirect('quiz:choose_test')

    # Индекс текущего вопроса (номер карточки в тесте), хранится в сессии
    question_idx = request.session.get('quiz_question_idx', 0)
    # Текущее количество правильных ответов
    score = request.session.get('quiz_score', 0)

    # Если все вопросы пройдены — показать результат и сбросить прогресс
    if question_idx >= len(user_cards):
        result = {'score': score, 'total': len(user_cards)}
        
        # Сохраняем результат теста в статистику
        test_type = request.session.get('quiz_test_type', 'matching')
        direction = request.session.get('quiz_direction', 'en-ru')
        
        TestResult.objects.create(
            user=request.user,
            test_type=test_type,
            direction=direction,
            score=score,
            total=len(user_cards),
            correct_answers=score,
            wrong_answers=len(user_cards) - score
        )
        
        # Сбросить прогресс для нового теста
        request.session['quiz_question_idx'] = 0
        request.session['quiz_score'] = 0
        return render(request, 'quiz/quiz_result.html', result)

    # Текущая карточка для вопроса
    current_card = user_cards[question_idx]

    # --- Формируем вопрос и варианты в зависимости от направления ---
    if direction == 'en-ru':
        # Показываем слово на английском, варианты — переводы
        question = current_card.word
        correct = current_card.translation
        # Список других карточек (для неправильных вариантов)
        other_cards = [c for c in user_cards if c.pk != current_card.pk]
        # Случайно выбираем до 3 неправильных вариантов
        wrong = random.sample(other_cards, min(3, len(other_cards)))
        options = [correct] + [c.translation for c in wrong]
    else:  # ru-en
        # Показываем перевод, варианты — слова на английском
        question = current_card.translation
        correct = current_card.word
        other_cards = [c for c in user_cards if c.pk != current_card.pk]
        wrong = random.sample(other_cards, min(3, len(other_cards)))
        options = [correct] + [c.word for c in wrong]
    random.shuffle(options)  # Перемешиваем варианты

    # Если пользователь отправил ответ (POST)
    if request.method == 'POST' and 'answer' in request.POST:
        answer = request.POST.get('answer')
        # Если ответ правильный — увеличиваем счёт
        if answer == correct:
            request.session['quiz_score'] = score + 1
        # Переходим к следующему вопросу
        request.session['quiz_question_idx'] = question_idx + 1
        return redirect('quiz:matching')

    # Контекст для шаблона: вопрос, варианты, прогресс, направление
    context = {
        'question': question,           # Слово или перевод для вопроса
        'options': options,             # Варианты ответа
        'question_number': question_idx + 1,  # Номер текущего вопроса
        'total': len(user_cards),       # Всего вопросов
        'score': score,                 # Количество правильных ответов
        'direction': direction,         # Направление теста
    }
    return render(request, 'quiz/matching.html', context)
