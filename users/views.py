from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import UserProfile

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
        telegram_info = {
            'telegram_id': None,
            'telegram_username': None,
            'is_telegram_user': False
        }
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'link':
            # Логика связывания (в будущем можно добавить верификацию)
            telegram_id = request.POST.get('telegram_id')
            telegram_username = request.POST.get('telegram_username')
            
            if telegram_id:
                try:
                    # Создаём или обновляем профиль
                    profile, created = UserProfile.objects.get_or_create(
                        user=request.user,
                        defaults={
                            'telegram_id': int(telegram_id),
                            'telegram_username': telegram_username,
                            'is_telegram_user': True
                        }
                    )
                    
                    if not created:
                        # Обновляем существующий профиль
                        profile.telegram_id = int(telegram_id)
                        profile.telegram_username = telegram_username
                        profile.is_telegram_user = True
                        profile.save()
                    
                    messages.success(request, 'Аккаунт успешно связан с Telegram!')
                except ValueError as e:
                    messages.error(request, f'Ошибка: {str(e)}')
                except Exception as e:
                    messages.error(request, 'Произошла ошибка при связывании аккаунта')
    
    context = {
        'telegram_info': telegram_info,
        'user': request.user
    }
    
    return render(request, 'users/telegram_link.html', context)
