"""
Сервис для автоматических напоминаний
"""

import asyncio
from datetime import datetime, time
from typing import List
from utils.django_utils import get_today_cards
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class ReminderService:
    """Сервис для отправки напоминаний"""
    
    def __init__(self, bot):
        self.bot = bot
        self.reminder_task = None
    
    async def start_reminder_scheduler(self):
        """Запускает планировщик напоминаний"""
        self.reminder_task = asyncio.create_task(self._reminder_loop())
    
    async def stop_reminder_scheduler(self):
        """Останавливает планировщик напоминаний"""
        if self.reminder_task:
            self.reminder_task.cancel()
    
    async def _reminder_loop(self):
        """Основной цикл отправки напоминаний"""
        while True:
            try:
                # Ждём до следующего часа
                now = datetime.now()
                next_hour = now.replace(minute=0, second=0, microsecond=0)
                if next_hour <= now:
                    next_hour = next_hour.replace(hour=next_hour.hour + 1)
                
                wait_seconds = (next_hour - now).total_seconds()
                await asyncio.sleep(wait_seconds)
                
                # Проверяем, пора ли отправлять напоминания
                if now.hour == 10:  # Напоминания в 10:00
                    await self._send_daily_reminders()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка в планировщике напоминаний: {e}")
                await asyncio.sleep(60)  # Ждём минуту перед повтором
    
    async def _send_daily_reminders(self):
        """Отправляет ежедневные напоминания всем пользователям"""
        try:
            from asgiref.sync import sync_to_async
            
            # Получаем всех пользователей с Telegram ID
            users = await sync_to_async(list)(User.objects.filter(username__startswith='telegram_'))
            
            for user in users:
                try:
                    # Извлекаем Telegram ID из username
                    telegram_id = int(user.username.replace('telegram_', ''))
                    
                    # Проверяем, есть ли слова на повторение
                    today_cards = await sync_to_async(get_today_cards)(user)
                    
                    if today_cards:
                        # Отправляем напоминание
                        await self._send_reminder(telegram_id, today_cards)
                    
                except (ValueError, Exception) as e:
                    logger.error(f"Ошибка при отправке напоминания пользователю {user.username}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Ошибка при отправке ежедневных напоминаний: {e}")
    
    async def _send_reminder(self, telegram_id: int, cards: List):
        """Отправляет напоминание конкретному пользователю"""
        try:
            message = "🔔 Пора повторить слова!\n\n"
            message += f"У вас {len(cards)} слов на повторение сегодня:\n\n"
            
            for i, card in enumerate(cards[:5], 1):  # Показываем первые 5
                level_emoji = {
                    'beginner': '🟢',
                    'intermediate': '🟡', 
                    'advanced': '🔴'
                }.get(card.level, '⚪')
                
                message += f"{i}. {level_emoji} {card.word} — {card.translation}\n"
            
            if len(cards) > 5:
                message += f"\n... и ещё {len(cards) - 5} слов"
            
            message += "\n\nИспользуйте команду /today для просмотра всех слов"
            message += "\nИли /test для проверки знаний!"
            
            await self.bot.send_message(telegram_id, message)
            
        except Exception as e:
            logger.error(f"Ошибка при отправке напоминания {telegram_id}: {e}")
    
    async def send_manual_reminder(self, telegram_id: int):
        """Отправляет ручное напоминание (для тестирования)"""
        try:
            # Получаем пользователя
            from utils.django_utils import get_user_by_telegram_id
            from asgiref.sync import sync_to_async
            
            user = await sync_to_async(get_user_by_telegram_id)(telegram_id)
            
            # Проверяем слова на повторение
            today_cards = await sync_to_async(get_today_cards)(user)
            
            if today_cards:
                await self._send_reminder(telegram_id, today_cards)
            else:
                await self.bot.send_message(
                    telegram_id, 
                    "✅ Отлично! Сегодня нет слов для повторения."
                )
                
        except Exception as e:
            logger.error(f"Ошибка при отправке ручного напоминания: {e}") 