from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Админка для профилей пользователей"""
    list_display = ['user', 'telegram_id', 'telegram_username', 'is_telegram_user', 'created_at']
    list_filter = ['is_telegram_user', 'created_at']
    search_fields = ['user__username', 'user__email', 'telegram_username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'is_telegram_user')
        }),
        ('Telegram данные', {
            'fields': ('telegram_id', 'telegram_username')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
