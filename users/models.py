from django.db import models
from django.contrib.auth.models import User
import secrets
from datetime import timedelta
from django.utils import timezone

# Create your models here.

class UserProfile(models.Model):
    """Расширенный профиль пользователя для интеграции с Telegram"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True, 
                                       help_text="Telegram ID пользователя")
    telegram_username = models.CharField(max_length=100, blank=True, 
                                       help_text="Username в Telegram")
    is_telegram_user = models.BooleanField(default=False, 
                                          help_text="Зарегистрирован ли через Telegram")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Профиль {self.user.username}"
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"


class TelegramLinkToken(models.Model):
    """Токены для привязки Telegram и автовхода на сайт"""
    TOKEN_TYPE_CHOICES = [
        ('link', 'Привязка Telegram'),
        ('auth', 'Автовход на сайт'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='telegram_tokens')
    token = models.CharField(max_length=64, unique=True, help_text="Уникальный токен")
    token_type = models.CharField(max_length=10, choices=TOKEN_TYPE_CHOICES, help_text="Тип токена")
    telegram_id = models.BigIntegerField(null=True, blank=True, help_text="Telegram ID (для привязки)")
    expires_at = models.DateTimeField(help_text="Время истечения токена")
    is_used = models.BooleanField(default=False, help_text="Использован ли токен")
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_token_type_display()} токен для {self.user.username}"
    
    class Meta:
        verbose_name = "Telegram токен"
        verbose_name_plural = "Telegram токены"
    
    @classmethod
    def generate_token(cls, user, token_type, telegram_id=None):
        """Генерирует новый токен для пользователя"""
        # Удаляем старые неиспользованные токены того же типа
        cls.objects.filter(
            user=user, 
            token_type=token_type, 
            is_used=False,
            expires_at__lt=timezone.now()
        ).delete()
        
        # Определяем время жизни токена
        if token_type == 'link':
            expires_in = timedelta(minutes=5)  # 5 минут для привязки
        else:  # auth
            expires_in = timedelta(minutes=10)  # 10 минут для автовхода
        
        # Генерируем уникальный токен
        while True:
            token = secrets.token_urlsafe(32)
            if not cls.objects.filter(token=token).exists():
                break
        
        # Создаем токен
        return cls.objects.create(
            user=user,
            token=token,
            token_type=token_type,
            telegram_id=telegram_id,
            expires_at=timezone.now() + expires_in
        )
    
    def is_valid(self):
        """Проверяет, действителен ли токен"""
        return not self.is_used and self.expires_at > timezone.now()
    
    def mark_as_used(self):
        """Помечает токен как использованный"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
