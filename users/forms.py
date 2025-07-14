from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(UserCreationForm):
    """Расширенная форма регистрации с полем для Telegram ID"""
    telegram_id = forms.IntegerField(
        required=False, 
        help_text="Необязательно. Ваш Telegram ID для синхронизации с ботом",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    telegram_username = forms.CharField(
        max_length=100,
        required=False,
        help_text="Необязательно. Ваш username в Telegram (без @)",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'telegram_id', 'telegram_username')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Создаём профиль пользователя
            UserProfile.objects.create(
                user=user,
                telegram_id=self.cleaned_data.get('telegram_id'),
                telegram_username=self.cleaned_data.get('telegram_username'),
                is_telegram_user=bool(self.cleaned_data.get('telegram_id'))
            )
        return user 