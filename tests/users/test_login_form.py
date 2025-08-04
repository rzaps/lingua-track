import pytest
from django.contrib.auth.models import User
from users.forms import EmailAuthenticationForm

@pytest.mark.django_db
def test_login_form_valid():
    user = User.objects.create_user(username='loginuser', email='login@example.com', password='123')
    form = EmailAuthenticationForm(data={
        'email': 'login@example.com',
        'password': '123',
    })
    assert form.is_valid()

@pytest.mark.django_db
def test_login_form_invalid_password():
    user = User.objects.create_user(username='loginuser2', email='login2@example.com', password='123')
    form = EmailAuthenticationForm(data={
        'email': 'login2@example.com',
        'password': 'wrong',
    })
    assert not form.is_valid()

@pytest.mark.django_db
def test_login_form_nonexistent_user():
    form = EmailAuthenticationForm(data={
        'email': 'nonexistent@example.com',
        'password': '123',
    })
    assert not form.is_valid() 