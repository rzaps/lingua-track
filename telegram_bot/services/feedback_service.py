"""
Сервис для работы с отзывами в Telegram боте
"""

from config import Config
from .http_client import HttpClient

class FeedbackService:
	"""Сервис для отправки отзывов"""
	_client = HttpClient()
	
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
		url = f"{Config.SITE_URL}/feedback/api/v1/telegram/"
		payload = {"text": text, "telegram_id": telegram_id}
		return cls._client.post_json(url, payload) 