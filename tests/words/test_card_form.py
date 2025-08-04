import pytest
from django.contrib.auth.models import User
from words.forms import CardForm
from words.models import Card, Repetition

@pytest.mark.django_db
def test_card_form_valid():
    user = User.objects.create_user(username='carduser', password='123')
    form = CardForm(data={
        'word': 'computer',
        'translation': 'компьютер',
        'level': 'intermediate',
    })
    assert form.is_valid()
    card = form.save(commit=False)
    card.user = user
    card.save()
    assert card.word == 'computer'
    assert card.translation == 'компьютер'
    assert card.level == 'intermediate'

@pytest.mark.django_db
def test_card_form_invalid_empty_word():
    form = CardForm(data={
        'word': '',
        'translation': 'перевод',
        'level': 'beginner',
    })
    assert not form.is_valid()
    assert 'word' in form.errors

@pytest.mark.django_db
def test_card_form_invalid_empty_translation():
    form = CardForm(data={
        'word': 'word',
        'translation': '',
        'level': 'beginner',
    })
    assert not form.is_valid()
    assert 'translation' in form.errors

@pytest.mark.django_db
def test_card_form_creates_repetition():
    user = User.objects.create_user(username='repuser', password='123')
    form = CardForm(data={
        'word': 'test',
        'translation': 'тест',
        'level': 'beginner',
    })
    assert form.is_valid()
    card = form.save(commit=False)
    card.user = user
    card.save()
    # Проверяем, что Repetition создан автоматически
    assert Repetition.objects.filter(card=card, user=user).exists() 