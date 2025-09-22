from django.contrib import admin
from .models import UserProfile, TelegramLinkToken

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

@admin.register(TelegramLinkToken)
class TelegramLinkTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_type', 'is_used', 'created_at', 'expires_at']
    list_filter = ['token_type', 'is_used', 'created_at']
    search_fields = ['user__username', 'token']
    readonly_fields = ['token', 'created_at', 'used_at']
    
    def has_add_permission(self, request):
        return False  # Токены создаются только программно
