from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import UserProfile
from telegram_bot.config import Config

def register(request):
    """View для регистрации новых пользователей"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Создаём нового пользователя с профилем
            user = form.save()
            # Автоматически входим в систему
            login(request, user)
            # Перенаправляем на главную страницу
            return redirect('words:index')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def telegram_link(request):
    """Страница для управления связью с Telegram"""
    try:
        telegram_info = {
            'telegram_id': request.user.profile.telegram_id,
            'telegram_username': request.user.profile.telegram_username,
            'is_telegram_user': request.user.profile.is_telegram_user
        }
    except UserProfile.DoesNotExist:
        # Создаем пустой профиль, если его нет
        profile = UserProfile.objects.create(user=request.user)
        telegram_info = {
            'telegram_id': None,
            'telegram_username': None,
            'is_telegram_user': False
        }
    
    context = {
        'telegram_info': telegram_info,
        'user': request.user,
        'bot_url': Config.get_bot_url(),
        'qr_url': Config.get_qr_url(),
    }
    
    return render(request, 'users/telegram_link.html', context)
