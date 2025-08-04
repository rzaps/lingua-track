import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../telegram_bot')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../telegram_bot/utils')))

import pytest
from django.contrib.auth.models import User
from words.models import Card, Repetition
from telegram_bot.services.test_service import TestService

@pytest.mark.django_db
def test_create_test():
    user = User.objects.create_user(username='testuser', password='123')
    from users.models import UserProfile
    profile = UserProfile.objects.create(user=user, telegram_id=7777)
    
    # Создаём карточки для теста
    for i in range(5):
        card = Card.objects.create(user=user, word=f'word{i}', translation=f'trans{i}', level='beginner')
        Repetition.objects.create(card=card, user=user)
    
    test_data = TestService.create_test(7777)
    assert test_data is not None
    assert 'cards' in test_data
    assert len(test_data['cards']) > 0

@pytest.mark.django_db
def test_process_answer():
    user = User.objects.create_user(username='testuser2', password='123')
    from users.models import UserProfile
    profile = UserProfile.objects.create(user=user, telegram_id=8888)
    
    card = Card.objects.create(user=user, word='test', translation='тест', level='beginner')
    Repetition.objects.create(card=card, user=user)
    
    # Создаём тест
    test_data = TestService.create_test(8888)
    assert test_data is not None
    
    # Обрабатываем правильный ответ
    result = TestService.process_answer(8888, 'тест')
    assert result is not None
    assert result['is_correct'] == True

@pytest.mark.django_db
def test_finish_test():
    user = User.objects.create_user(username='testuser3', password='123')
    from users.models import UserProfile
    profile = UserProfile.objects.create(user=user, telegram_id=9999)
    
    # Создаём карточки и тест
    for i in range(3):
        card = Card.objects.create(user=user, word=f'word{i}', translation=f'trans{i}', level='beginner')
        Repetition.objects.create(card=card, user=user)
    
    test_data = TestService.create_test(9999)
    assert test_data is not None
    
    # Отвечаем на все вопросы
    for _ in range(len(test_data['cards'])):
        TestService.process_answer(9999, 'trans0')  # Простой ответ
    
    # Завершаем тест
    results = TestService.finish_test(9999)
    assert results is not None
    assert 'total_questions' in results
    assert 'correct_answers' in results 