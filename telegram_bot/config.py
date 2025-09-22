"""
Конфигурация Telegram бота
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

class Config:
    """Конфигурация бота"""
    
    # Основные настройки
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    BOT_USERNAME = os.getenv('BOT_USERNAME', 'Lingua_Track_Bot')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # URL сайта для API запросов
    SITE_URL = os.getenv('SITE_URL', 'http://127.0.0.1:8000')
    
    # Настройки тестов
    TEST_QUESTIONS_COUNT = 5  # Количество вопросов в тесте по умолчанию
    
    # Настройки напоминаний
    REMINDER_HOUR = 9  # Час для отправки напоминаний (UTC)
    REMINDER_MINUTE = 0  # Минута для отправки напоминаний

    # Сообщения бота
    MESSAGES = {
        "welcome": "👋 Добро пожаловать в LinguaTrack Bot!\n\nИспользуйте меню или команды для изучения слов.",
        "help": "ℹ️ Доступные команды:\n/today — слова на сегодня\n/progress — статистика\n/cards — все карточки\n/test — пройти тест\n/remind — тест напоминаний\n/feedback — оставить отзыв\n\nДля связи аккаунта используйте /link",
        "no_reviews_today": "Сегодня нет слов для повторения. Добавьте новые карточки!",
        "not_registered": "❗️ Вы не зарегистрированы. Сначала свяжите аккаунт через /link.",
        "no_cards": "У вас пока нет карточек. Добавьте их на сайте или через бота.",
        # --- Сообщения для тестов ---
        "test_start": "📝 Начинаем тест! Вопросов: {count}.\nНажмите '✅ Начать тест', чтобы приступить.",
        "test_complete": "✅ Тест завершён!\nПравильных ответов: {correct}/{total}\nТочность: {accuracy}%\n{message}",
    }

    # Сообщения об оценке результата теста
    TEST_MESSAGES = {
        "excellent": "🎉 Отличный результат! Так держать!",
        "good": "👍 Хорошо! Ещё немного практики и будет отлично.",
        "satisfactory": "🙂 Неплохо. Продолжайте тренировки.",
        "poor": "🧠 Есть над чем поработать. Повторите слова и попробуйте снова.",
    }

    # URL для QR-кода
    @classmethod
    def get_bot_url(cls):
        """Возвращает URL для перехода к боту"""
        return f"https://t.me/{cls.BOT_USERNAME}"
    
    @classmethod
    def get_qr_url(cls):
        """Возвращает URL для генерации QR-кода"""
        bot_url = cls.get_bot_url()
        return f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={bot_url}" 