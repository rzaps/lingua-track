"""
Главный файл Telegram бота
"""

import asyncio
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Инициализация Django
from utils.django_init import *

from aiogram import Bot, Dispatcher
from config import Config

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Создаём экземпляр бота
bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()

# Импортируем роутеры после создания диспетчера
from routers import commands, test_handlers, progress_handlers, cards_handlers, tts_handlers

# Регистрируем все роутеры
dp.include_router(commands.router)
dp.include_router(test_handlers.router)
dp.include_router(progress_handlers.router)
dp.include_router(cards_handlers.router)
dp.include_router(tts_handlers.router)

async def main():
    """Запуск бота"""
    # Удаляем все обновления, накопившиеся за время остановки бота
    await bot.delete_webhook(drop_pending_updates=True)
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main()) 