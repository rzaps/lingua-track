from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Feedback(models.Model):
    """Модель для хранения отзывов пользователей"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Пользователь",
        null=True,
        blank=True,
        help_text="Пользователь, оставивший отзыв (может быть анонимным)"
    )
    
    text = models.TextField(
        verbose_name="Текст отзыва",
        help_text="Содержание отзыва, предложения или сообщения об ошибке"
    )
    
    telegram_id = models.BigIntegerField(
        verbose_name="Telegram ID",
        null=True,
        blank=True,
        help_text="ID пользователя в Telegram (если отзыв из бота)"
    )
    
    created_at = models.DateTimeField(
        verbose_name="Дата создания",
        default=timezone.now,
        help_text="Время создания отзыва"
    )
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']
    
    def __str__(self):
        if self.user:
            return f"Отзыв от {self.user.username} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"
        elif self.telegram_id:
            return f"Отзыв из Telegram {self.telegram_id} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"
        else:
            return f"Анонимный отзыв ({self.created_at.strftime('%d.%m.%Y %H:%M')})"
