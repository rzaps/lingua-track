from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Админка для отзывов"""
    
    list_display = ['user', 'telegram_id', 'created_at', 'text_preview']
    list_filter = ['created_at', 'user']
    search_fields = ['text', 'user__username', 'telegram_id']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('text', 'created_at')
        }),
        ('Пользователь', {
            'fields': ('user', 'telegram_id'),
            'classes': ('collapse',)
        }),
    )
    
    def text_preview(self, obj):
        """Краткий предварительный просмотр текста отзыва"""
        return obj.text[:100] + "..." if len(obj.text) > 100 else obj.text
    
    text_preview.short_description = "Текст отзыва"
    
    def has_add_permission(self, request):
        """Запрещаем добавление отзывов через админку"""
        return False
