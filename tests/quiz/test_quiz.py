import pytest
from django.contrib.auth.models import User
from words.models import Card

@pytest.mark.django_db
def test_quiz_generation():
    user = User.objects.create_user(username='quizuser', password='123')
    for i in range(5):
        Card.objects.create(user=user, word=f'word{i}', translation=f'перевод{i}', level='beginner')
    cards = Card.objects.filter(user=user)
    assert cards.count() == 5

# Здесь можно добавить тесты для бизнес-логики quiz/test_service, если она вынесена отдельно 