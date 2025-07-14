from django.contrib import admin
from .models import Card, Repetition

# Register your models here.

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['word', 'translation', 'level', 'user', 'created_at']
    list_filter = ['level', 'created_at', 'user']
    search_fields = ['word', 'translation', 'user__username']
    readonly_fields = ['created_at']

@admin.register(Repetition)
class RepetitionAdmin(admin.ModelAdmin):
    list_display = ['card', 'user', 'next_review', 'interval', 'repetition_count', 'success_rate']
    list_filter = ['next_review', 'interval', 'user']
    search_fields = ['card__word', 'user__username']
    readonly_fields = ['last_reviewed', 'total_reviews', 'successful_reviews', 'failed_reviews']
