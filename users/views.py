from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .forms import UserRegistrationForm
from .models import UserProfile, TelegramLinkToken
from telegram_bot.config import Config
import json
import urllib.parse

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

@login_required
@require_http_methods(["POST"])
def generate_link_token(request):
    """API для генерации токена привязки Telegram"""
    try:
        # Генерируем токен для привязки
        token_obj = TelegramLinkToken.generate_token(
            user=request.user, 
            token_type='link'
        )
        
        # Формируем ссылку для бота
        bot_username = getattr(Config, 'BOT_USERNAME', 'Lingua_Track_Bot')
        bot_start_url = f"https://t.me/{bot_username}?start={token_obj.token}"
        
        # Правильно кодируем URL для QR-кода
        encoded_url = urllib.parse.quote(bot_start_url, safe='')
        
        # Используем альтернативный сервис QR-кода
        qr_url = f"https://chart.googleapis.com/chart?cht=qr&chs=200x200&chl={encoded_url}"
        
        return JsonResponse({
            'success': True,
            'token': token_obj.token,
            'bot_url': bot_start_url,
            'expires_at': token_obj.expires_at.isoformat(),
            'qr_url': qr_url
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_auth_token(request):
    """API для генерации токена автовхода"""
    try:
        data = json.loads(request.body)
        telegram_id = data.get('telegram_id')
        
        if not telegram_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing telegram_id'
            }, status=400)
        
        # Находим пользователя по Telegram ID
        try:
            profile = UserProfile.objects.get(telegram_id=telegram_id)
            user = profile.user
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'User not found'
            }, status=404)
        
        # Генерируем токен автовхода
        token_obj = TelegramLinkToken.generate_token(
            user=user,
            token_type='auth'
        )
        
        # Формируем ссылку для автовхода
        auth_url = f"{request.build_absolute_uri('/').rstrip('/')}/users/telegram-auth/?token={token_obj.token}"
        
        return JsonResponse({
            'success': True,
            'token': token_obj.token,
            'auth_url': auth_url,
            'expires_at': token_obj.expires_at.strftime('%H:%M:%S'),
            'user_id': user.id,
            'username': user.username
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def telegram_link_callback(request):
    """API для обработки привязки от бота"""
    try:
        data = json.loads(request.body)
        token = data.get('token')
        telegram_id = data.get('telegram_id')
        telegram_username = data.get('telegram_username')
        
        if not token or not telegram_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing token or telegram_id'
            }, status=400)
        
        # Находим токен
        try:
            token_obj = TelegramLinkToken.objects.get(
                token=token,
                token_type='link',
                is_used=False
            )
        except TelegramLinkToken.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Invalid or expired token'
            }, status=400)
        
        # Проверяем срок действия
        if not token_obj.is_valid():
            return JsonResponse({
                'success': False,
                'error': 'Token expired'
            }, status=400)
        
        # Привязываем Telegram к пользователю
        profile, created = UserProfile.objects.get_or_create(user=token_obj.user)
        profile.telegram_id = telegram_id
        profile.telegram_username = telegram_username
        profile.is_telegram_user = True
        profile.save()
        
        # Помечаем токен как использованный
        token_obj.mark_as_used()
        
        return JsonResponse({
            'success': True,
            'user_id': token_obj.user.id,
            'username': token_obj.user.username
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def telegram_auth_login(request):
    """Страница автовхода через Telegram токен"""
    token = request.GET.get('token')
    
    if not token:
        messages.error(request, 'Отсутствует токен авторизации')
        return redirect('users:login')
    
    try:
        # Находим токен автовхода
        token_obj = TelegramLinkToken.objects.get(
            token=token,
            token_type='auth',
            is_used=False
        )
        
        # Проверяем срок действия
        if not token_obj.is_valid():
            messages.error(request, 'Токен истек или уже использован')
            return redirect('users:login')
        
        # Автоматически входим в систему
        login(request, token_obj.user)
        
        # Помечаем токен как использованный
        token_obj.mark_as_used()
        
        messages.success(request, f'Добро пожаловать, {token_obj.user.username}!')
        return redirect('words:index')
        
    except TelegramLinkToken.DoesNotExist:
        messages.error(request, 'Недействительный токен авторизации')
        return redirect('users:login')
