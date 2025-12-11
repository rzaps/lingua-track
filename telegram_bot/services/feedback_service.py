"""
Сервис для работы с отзывами в Telegram боте
"""

import requests
from config import Config

class FeedbackService:
    """Сервис для отправки отзывов"""
    
    @classmethod
    async def send_feedback(cls, text: str, telegram_id: int) -> dict:
        """
        Отправляет отзыв на сайт
        
        Args:
            text: Текст отзыва
            telegram_id: ID пользователя в Telegram
            
        Returns:
            dict: Результат отправки
        """
        try:
            response = requests.post(
                f"{Config.SITE_URL}/feedback/api/telegram/",
                json={
                    'text': text,
                    'telegram_id': telegram_id
                },
                timeout=10
            )
            
            return response.json()
            
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f'Ошибка соединения: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Неизвестная ошибка: {str(e)}'
            } 