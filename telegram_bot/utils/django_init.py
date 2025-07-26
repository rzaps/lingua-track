"""
Инициализация Django для использования в Telegram боте
"""

import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingua_track.settings')
django.setup() 