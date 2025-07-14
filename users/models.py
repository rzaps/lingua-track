from django.db import models
from django.contrib.auth.models import User

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
