import pytest
from django.contrib.auth.models import User
from users.models import UserProfile

@pytest.mark.django_db
def test_register_user():
    user = User.objects.create_user(username='testuser', email='test@example.com', password='123')
    assert user.email == 'test@example.com'
    assert user.check_password('123')

@pytest.mark.django_db
def test_unique_email():
    User.objects.create_user(username='user1', email='unique@example.com', password='123')
    with pytest.raises(Exception):
        User.objects.create_user(username='user2', email='unique@example.com', password='456')

@pytest.mark.django_db
def test_unique_telegram_id():
    user1 = User.objects.create_user(username='tguser1', email='tg1@example.com', password='123')
    profile1 = UserProfile.objects.create(user=user1, telegram_id=12345)
    user2 = User.objects.create_user(username='tguser2', email='tg2@example.com', password='123')
    with pytest.raises(Exception):
        UserProfile.objects.create(user=user2, telegram_id=12345) 