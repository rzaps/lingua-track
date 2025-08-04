import pytest
from django.contrib.auth.models import User
from users.models import UserProfile

@pytest.mark.django_db
def test_userprofile_creation():
    user = User.objects.create_user(username='tguser', email='tg@example.com', password='123')
    profile = UserProfile.objects.create(user=user, telegram_id=1111)
    assert profile.telegram_id == 1111
    assert profile.user == user

@pytest.mark.django_db
def test_userprofile_unique_telegram_id():
    user1 = User.objects.create_user(username='tguser1', email='tg1@example.com', password='123')
    UserProfile.objects.create(user=user1, telegram_id=2222)
    user2 = User.objects.create_user(username='tguser2', email='tg2@example.com', password='123')
    with pytest.raises(Exception):
        UserProfile.objects.create(user=user2, telegram_id=2222) 