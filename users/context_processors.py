from django.conf import settings

def telegram_settings(request):
    """Добавляет настройки Telegram в контекст шаблонов"""
    return {
        'settings': {
            'TELEGRAM_BOT_USERNAME': settings.TELEGRAM_BOT_USERNAME,
        }
    } 