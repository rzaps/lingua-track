import pytest
from words.models import Card, Repetition
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_create_card():
    user = User.objects.create_user(username='testuser', password='123')
    card = Card.objects.create(user=user, word='apple', translation='яблоко', level='beginner')
    assert card.word == 'apple'
    assert card.translation == 'яблоко'
    assert card.level == 'beginner'
    assert card.user == user

@pytest.mark.django_db
def test_card_appears_in_repetition():
    user = User.objects.create_user(username='testuser2', password='123')
    card = Card.objects.create(user=user, word='orange', translation='апельсин', level='beginner')
    rep = Repetition.objects.create(card=card, user=user)
    assert rep.card == card
    assert rep.user == user
    assert rep.next_review is not None 