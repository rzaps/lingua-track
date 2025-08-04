import pytest
from django.contrib.auth.models import User
from words.models import Card, Repetition
from words.forms import CardForm

@pytest.mark.django_db
def test_repetition_created_on_card_add():
    user = User.objects.create_user(username='repuser', password='123')
    form = CardForm(data={
        'word': 'banana',
        'translation': 'банан',
        'level': 'beginner',
    })
    assert form.is_valid()
    card = form.save(commit=False)
    card.user = user
    card.save()
    # Проверяем, что Repetition создан
    assert Repetition.objects.filter(card=card, user=user).exists() 