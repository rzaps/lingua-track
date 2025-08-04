import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../telegram_bot')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../telegram_bot/utils')))

import pytest
from django.contrib.auth.models import User
from words.models import Card, Repetition
from telegram_bot.services.user_service import UserService

@pytest.mark.django_db
def test_get_user_cards_paginated():
    user = User.objects.create_user(username='botuser', password='123')
    from users.models import UserProfile
    profile = UserProfile.objects.create(user=user, telegram_id=5555)
    for i in range(7):
        Card.objects.create(user=user, word=f'w{i}', translation=f't{i}', level='beginner')
    data = UserService.get_user_cards_paginated(5555, page=1, per_page=5)
    assert len(data['cards']) == 5
    assert data['total_pages'] == 2

@pytest.mark.django_db
def test_get_today_reviews():
    user = User.objects.create_user(username='botuser2', password='123')
    from users.models import UserProfile
    profile = UserProfile.objects.create(user=user, telegram_id=6666)
    card = Card.objects.create(user=user, word='today', translation='сегодня', level='beginner')
    rep = Repetition.objects.create(card=card, user=user)
    reviews = UserService.get_today_reviews(6666)
    assert any(c.word == 'today' for c in reviews) 