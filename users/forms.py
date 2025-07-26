from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

class EmailAuthenticationForm(AuthenticationForm):
    """Форма входа по email вместо username"""
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            # Получаем пользователя по email
            try:
                user = User.objects.get(email=email)
                # Пытаемся аутентифицировать с username и паролем
                self.user_cache = authenticate(username=user.username, password=password)
                if self.user_cache is None:
                    raise forms.ValidationError('Неверный email или пароль.')
            except User.DoesNotExist:
                raise forms.ValidationError('Неверный email или пароль.')

        return self.cleaned_data

class UserRegistrationForm(UserCreationForm):
    """Минимальная регистрация: только длина пароля >= 6, без других ограничений"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Этот email уже используется.')
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1 and len(password1) < 6:
            raise ValidationError('Пароль должен содержать минимум 6 символов.')
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Пароли не совпадают.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Генерируем username из email
        email = self.cleaned_data.get('email')
        username = email.split('@')[0]
        # Если такой username существует, добавляем цифры
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user.username = username
        
        if commit:
            user.save()
            # Создаём пустой профиль пользователя
            UserProfile.objects.create(user=user)
        return user 