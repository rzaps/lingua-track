"""
Сервис для работы с пользователями
"""

from utils.django_utils import get_user_by_telegram_id, get_today_cards, get_user_progress, get_user_cards_paginated

class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    def get_or_create_user(telegram_id: int):
        """Получает или создаёт пользователя по Telegram ID"""
        return get_user_by_telegram_id(telegram_id)
    
    @staticmethod
    def get_today_reviews(telegram_id: int):
        """Получает карточки на повторение сегодня"""
        user = get_user_by_telegram_id(telegram_id)
        return get_today_cards(user)
    
    @staticmethod
    def get_user_statistics(telegram_id: int):
        """Получает статистику пользователя"""
        user = get_user_by_telegram_id(telegram_id)
        return get_user_progress(user)
    
    @staticmethod
    def get_user_cards(telegram_id: int):
        """Получает карточки пользователя"""
        user = get_user_by_telegram_id(telegram_id)
        cards_data = get_user_cards_paginated(user, 1, 50)  # Получаем первые 50 карточек
        return cards_data['cards']  # Возвращаем только список карточек
    
    @staticmethod
    def format_cards_for_display(cards: list) -> str:
        """Форматирует карточки для отображения"""
        if not cards:
            return "📝 Карточки не найдены"
        
        cards_text = ""
        for i, card in enumerate(cards, 1):
            level_emoji = {
                'beginner': '🟢',
                'intermediate': '🟡', 
                'advanced': '🔴'
            }.get(card.level, '⚪')
            
            cards_text += f"{i}. {level_emoji} <b>{card.word}</b> — {card.translation}\n"
        
        return cards_text
    
    @staticmethod
    def format_statistics_for_display(stats: dict) -> str:
        """Форматирует статистику для отображения"""
        stats_text = "📊 Ваша статистика:\n\n"
        stats_text += f"📚 Всего слов: {stats['total_cards']}\n"
        stats_text += f"🔄 Повторений: {stats['total_reviews']}\n"
        stats_text += f"📝 Тестов пройдено: {stats['total_tests']}\n\n"
        
        stats_text += "📈 Успешность:\n"
        stats_text += f"• Повторения: {stats['review_success_rate']}%\n"
        stats_text += f"• Тесты: {stats['tests_accuracy']}%\n\n"
        
        stats_text += "📊 Слова по уровням:\n"
        stats_text += f"• 🟢 Начальный: {stats['beginner_cards']}\n"
        stats_text += f"• 🟡 Средний: {stats['intermediate_cards']}\n"
        stats_text += f"• 🔴 Продвинутый: {stats['advanced_cards']}\n\n"
        
        if stats['total_cards'] == 0:
            stats_text += "💡 Создайте карточки на сайте для начала обучения!"
        
        return stats_text 