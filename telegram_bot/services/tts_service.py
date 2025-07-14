"""
Сервис для работы с озвучкой слов (TTS)
"""

import os
import re
from typing import Optional

class TTSService:
    """Сервис для работы с озвучкой слов"""
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Определяет язык текста
        Пока простая логика - если есть кириллица, то русский, иначе английский
        """
        # Проверяем наличие кириллических символов
        cyrillic_pattern = re.compile(r'[а-яё]', re.IGNORECASE)
        
        if cyrillic_pattern.search(text):
            return 'ru'
        else:
            return 'en'
    
    @staticmethod
    def clean_word(word: str) -> str:
        """Очищает слово от лишних символов"""
        return re.sub(r'[^\w\s-]', '', word).strip()
    
    @staticmethod
    def validate_word(word: str) -> bool:
        """Проверяет, является ли слово валидным"""
        cleaned_word = TTSService.clean_word(word)
        return len(cleaned_word) > 0 and len(cleaned_word) <= 100
    
    @staticmethod
    async def generate_audio(word: str, lang: str) -> Optional[str]:
        """
        Генерирует аудиофайл для слова
        """
        try:
            # Импортируем функцию генерации TTS из Django
            import sys
            import os
            
            # Добавляем путь к Django проекту
            django_path = os.path.join(os.getcwd(), '..')
            sys.path.append(django_path)
            
            # Настраиваем Django
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingua_track.settings')
            import django
            django.setup()
            
            # Импортируем функцию генерации TTS
            from words.utils import generate_tts
            
            # Генерируем аудио
            relative_path = generate_tts(word, lang)
            
            # Получаем абсолютный путь
            from django.conf import settings
            absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            
            return absolute_path
            
        except Exception as e:
            print(f"Ошибка при генерации TTS: {e}")
            return None
    
    @staticmethod
    def format_audio_caption(word: str, lang: str) -> str:
        """Форматирует подпись для аудиофайла"""
        return f"🔊 {word} ({lang.upper()})"
    
    @staticmethod
    def get_processing_message(word: str) -> str:
        """Возвращает сообщение о начале обработки"""
        return f"🔊 Озвучиваю слово '{word}'..."
    
    @staticmethod
    def get_error_message(word: str) -> str:
        """Возвращает сообщение об ошибке"""
        return f"❌ Не удалось озвучить слово '{word}'"
    
    @staticmethod
    def get_usage_message() -> str:
        """Возвращает сообщение с инструкцией по использованию"""
        return """🔊 Озвучка слова

Использование: /say слово

Примеры:
/say hello
/say привет
/say beautiful

Бот озвучит слово на соответствующем языке.""" 