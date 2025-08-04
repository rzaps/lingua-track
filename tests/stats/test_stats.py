import pytest
from django.contrib.auth.models import User
from words.models import Card

@pytest.mark.django_db
def test_stats_card_count():
    user = User.objects.create_user(username='statsuser', password='123')
    Card.objects.create(user=user, word='one', translation='один', level='beginner')
    Card.objects.create(user=user, word='two', translation='два', level='beginner')
    assert Card.objects.filter(user=user).count() == 2 