import pytest
from django.contrib.auth.models import User
from words.models import Card, Repetition
from users.models import UserProfile
from words.forms import CardForm

@pytest.mark.django_db
def test_full_user_cycle():
    # 1. Регистрация пользователя
    user = User.objects.create_user(username='cycleuser', email='cycle@example.com', password='123')
    profile = UserProfile.objects.create(user=user, telegram_id=11111)
    
    # 2. Добавление карточки
    form = CardForm(data={
        'word': 'integration',
        'translation': 'интеграция',
        'level': 'advanced',
    })
    assert form.is_valid()
    card = form.save(commit=False)
    card.user = user
    card.save()
    
    # 3. Проверяем, что карточка создана и появилась в повторении
    assert Card.objects.filter(user=user, word='integration').exists()
    assert Repetition.objects.filter(card=card, user=user).exists()
    
    # 4. Добавляем ещё карточки для теста
    for i in range(3):
        card = Card.objects.create(user=user, word=f'word{i}', translation=f'trans{i}', level='beginner')
        Repetition.objects.create(card=card, user=user)
    
    # 5. Проверяем статистику
    total_cards = Card.objects.filter(user=user).count()
    assert total_cards == 4  # 1 + 3 дополнительных
    
    # 6. Проверяем, что карточки доступны через сервис бота
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../telegram_bot')))
    from telegram_bot.services.user_service import UserService
    
    cards_data = UserService.get_user_cards_paginated(11111, page=1, per_page=10)
    assert len(cards_data['cards']) == 4

@pytest.mark.django_db
def test_telegram_integration():
    # Тест интеграции с Telegram (имитация)
    user = User.objects.create_user(username='tguser', email='tg@example.com', password='123')
    profile = UserProfile.objects.create(user=user, telegram_id=22222)
    
    # Добавляем карточки
    for i in range(5):
        card = Card.objects.create(user=user, word=f'tgword{i}', translation=f'tgtrans{i}', level='beginner')
        Repetition.objects.create(card=card, user=user)
    
    # Проверяем через сервисы бота
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../telegram_bot')))
    from telegram_bot.services.user_service import UserService
    from telegram_bot.services.test_service import TestService
    
    # Получаем карточки
    cards_data = UserService.get_user_cards_paginated(22222, page=1, per_page=10)
    assert len(cards_data['cards']) == 5
    
    # Создаём тест
    test_data = TestService.create_test(22222)
    assert test_data is not None
    assert len(test_data['cards']) > 0 