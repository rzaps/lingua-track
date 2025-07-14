"""
Telegram Bot для LinguaTrack
Основной файл бота с настройкой и запуском
"""

import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv

# Импортируем роутеры
from routers import commands, test_handlers, progress_handlers, cards_handlers, tts_handlers
from config import Config

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("Не найден токен бота в переменных окружения!")
    exit(1)

# Создаём экземпляры бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Список команд бота
async def set_commands(bot: Bot):
    """Устанавливает команды бота"""
    commands_list = [
        BotCommand(command=cmd, description=desc) 
        for cmd, desc in Config.BOT_COMMANDS
    ]
    await bot.set_my_commands(commands_list)

# Регистрируем роутеры
def register_routers():
    """Регистрирует все роутеры"""
    dp.include_router(commands.router)
    dp.include_router(test_handlers.router)
    dp.include_router(progress_handlers.router)
    dp.include_router(cards_handlers.router)
    dp.include_router(tts_handlers.router)

async def main():
    """Основная функция запуска бота"""
    logger.info("Запуск Telegram бота LinguaTrack...")
    
    # Регистрируем роутеры
    register_routers()
    
    # Устанавливаем команды бота
    await set_commands(bot)
    
    # Запускаем систему напоминаний
    try:
        from services.reminder_service import ReminderService
        reminder_service = ReminderService(bot)
        await reminder_service.start_reminder_scheduler()
        logger.info("Система напоминаний запущена")
    except Exception as e:
        logger.error(f"Ошибка при запуске системы напоминаний: {e}")
    
    # Запускаем бота
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        # Останавливаем систему напоминаний
        try:
            if 'reminder_service' in locals():
                await reminder_service.stop_reminder_scheduler()
                logger.info("Система напоминаний остановлена")
        except Exception as e:
            logger.error(f"Ошибка при остановке системы напоминаний: {e}")
        
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main()) 