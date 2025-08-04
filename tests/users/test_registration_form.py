import pytest
from users.forms import UserRegistrationForm
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_registration_form_valid():
    form = UserRegistrationForm(data={
        'email': 'test1@example.com',
        'password1': 'testpass123',
        'password2': 'testpass123',
    })
    assert form.is_valid()
    user = form.save()
    assert user.email == 'test1@example.com'

@pytest.mark.django_db
def test_registration_form_invalid_email():
    form = UserRegistrationForm(data={
        'email': 'not-an-email',
        'password1': 'testpass123',
        'password2': 'testpass123',
    })
    assert not form.is_valid()
    assert 'email' in form.errors

@pytest.mark.django_db
def test_registration_form_duplicate_email():
    User.objects.create_user(username='user1', email='dup@example.com', password='123')
    form = UserRegistrationForm(data={
        'email': 'dup@example.com',
        'password1': 'testpass123',
        'password2': 'testpass123',
    })
    assert not form.is_valid()
    assert 'email' in form.errors 