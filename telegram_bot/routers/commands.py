"""
Роутер для основных команд бота
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import Config
from keyboards.main_keyboard import get_main_keyboard, get_cards_navigation_keyboard
from services.user_service import UserService
from utils.django_utils import get_user_by_telegram_id, link_telegram_to_existing_user, get_user_telegram_info

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        Config.MESSAGES['welcome'],
        reply_markup=get_main_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(Config.MESSAGES['help'])

@router.message(Command("today"))
async def cmd_today(message: Message):
    """Обработчик команды /today - слова на повторение сегодня"""
    try:
        # Получаем карточки на сегодня через сервис
        today_cards = UserService.get_today_reviews(message.from_user.id)
        
        if not today_cards:
            await message.answer(Config.MESSAGES['no_reviews_today'])
            return
        
        # Форматируем карточки через сервис
        cards_text = "📚 Слова на повторение сегодня:\n\n"
        cards_text += UserService.format_cards_for_display(today_cards)
        cards_text += "\nИспользуйте команду /test для проверки знаний!"
        
        await message.answer(cards_text, parse_mode="HTML")
        
    except Exception as e:
        await message.answer(Config.MESSAGES['not_registered'])

@router.message(Command("progress"))
async def cmd_progress(message: Message):
    """Обработчик команды /progress - статистика пользователя"""
    try:
        # Получаем статистику через сервис
        progress = UserService.get_user_statistics(message.from_user.id)
        
        # Форматируем статистику через сервис
        stats_text = UserService.format_statistics_for_display(progress)
        
        await message.answer(stats_text)
        
    except Exception as e:
        await message.answer(Config.MESSAGES['not_registered'])

@router.message(Command("cards"))
async def cmd_cards(message: Message):
    """Обработчик команды /cards - список карточек"""
    await show_cards_page(message, 1)

@router.message(Command("remind"))
async def cmd_remind(message: Message):
    """Обработчик команды /remind - тестирование напоминаний"""
    try:
        # Импортируем сервис напоминаний
        from services.reminder_service import ReminderService
        
        # Создаём экземпляр сервиса с ботом
        from main import bot
        reminder_service = ReminderService(bot)
        
        # Отправляем тестовое напоминание
        await reminder_service.send_manual_reminder(message.from_user.id)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке напоминания: {str(e)}")

@router.callback_query(F.data.startswith("cards_page:"))
async def callback_cards_page(callback: CallbackQuery):
    """Обработчик навигации по карточкам"""
    page = int(callback.data.split(":")[1])
    await show_cards_page(callback.message, page)
    await callback.answer()

@router.callback_query(F.data == "cards_close")
async def callback_cards_close(callback: CallbackQuery):
    """Обработчик закрытия списка карточек"""
    await callback.message.delete()
    await callback.answer()

async def show_cards_page(message: Message, page: int):
    """Показывает страницу с карточками"""
    try:
        # Получаем карточки через сервис
        cards_data = UserService.get_user_cards_paginated(message.from_user.id, page, Config.CARDS_PER_PAGE)
        
        if not cards_data['cards']:
            await message.answer(Config.MESSAGES['no_cards'])
            return
        
        # Формируем сообщение
        cards_text = f"🗂 Ваши карточки (страница {page}/{cards_data['total_pages']}):\n\n"
        cards_text += UserService.format_cards_for_display(cards_data['cards'])
        
        # Создаём клавиатуру для навигации
        keyboard = get_cards_navigation_keyboard(page, cards_data['total_pages'])
        
        await message.answer(cards_text, parse_mode="HTML", reply_markup=keyboard)
        
    except Exception as e:
        await message.answer(Config.MESSAGES['not_registered'])

# Обработчики текстовых кнопок
@router.message(F.text == "📚 Слова на сегодня")
async def handle_today_button(message: Message):
    """Обработчик кнопки 'Слова на сегодня'"""
    await cmd_today(message)

@router.message(F.text == "📊 Статистика")
async def handle_progress_button(message: Message):
    """Обработчик кнопки 'Статистика'"""
    await cmd_progress(message)

@router.message(F.text == "🗂 Карточки")
async def handle_cards_button(message: Message):
    """Обработчик кнопки 'Карточки'"""
    await cmd_cards(message)

@router.message(F.text == "❓ Помощь")
async def handle_help_button(message: Message):
    """Обработчик кнопки 'Помощь'"""
    await cmd_help(message) 

@router.message(Command("link"))
async def link_account(message: Message):
    """Связывает Telegram аккаунт с существующим пользователем Django"""
    telegram_id = message.from_user.id
    telegram_username = message.from_user.username
    
    # Проверяем, не связан ли уже аккаунт
    try:
        user = get_user_by_telegram_id(telegram_id)
        telegram_info = get_user_telegram_info(user)
        
        if telegram_info['is_telegram_user']:
            await message.answer(
                "✅ Ваш аккаунт уже связан с системой LinguaTrack!\n\n"
                "Используйте команды:\n"
                "/today - слова на повторение\n"
                "/test - пройти тест\n"
                "/progress - статистика\n"
                "/cards - ваши карточки"
            )
            return
    except:
        pass
    
    # Отправляем инструкции по связыванию
    await message.answer(
        "🔗 Связывание аккаунта с LinguaTrack\n\n"
        "Для связывания вашего Telegram с существующим аккаунтом на сайте:\n\n"
        "1️⃣ Зарегистрируйтесь на сайте: http://127.0.0.1:8000/register/\n"
        "2️⃣ При регистрации укажите:\n"
        f"   • Telegram ID: <code>{telegram_id}</code>\n"
        f"   • Telegram Username: <code>{telegram_username or 'не указан'}</code>\n\n"
        "3️⃣ Или отправьте мне сообщение в формате:\n"
        "<code>/link_username ваш_username_с_сайта</code>\n\n"
        "После связывания вы сможете использовать одни и те же карточки на сайте и в боте!",
        parse_mode="HTML"
    )

@router.message(lambda message: message.text and message.text.startswith("/link_username "))
async def link_username(message: Message):
    """Связывает аккаунт по username"""
    try:
        # Извлекаем username из команды
        username = message.text.replace("/link_username ", "").strip()
        if not username:
            await message.answer("❌ Укажите username с сайта LinguaTrack")
            return
        
        telegram_id = message.from_user.id
        telegram_username = message.from_user.username
        
        # Связываем аккаунты
        user = link_telegram_to_existing_user(telegram_id, telegram_username, username)
        
        await message.answer(
            f"✅ Аккаунт успешно связан!\n\n"
            f"Теперь вы можете использовать бота с аккаунтом <b>{username}</b>\n\n"
            f"Попробуйте команды:\n"
            f"/today - слова на повторение\n"
            f"/test - пройти тест\n"
            f"/progress - статистика\n"
            f"/cards - ваши карточки",
            parse_mode="HTML"
        )
        
    except ValueError as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    except Exception as e:
        await message.answer("❌ Произошла ошибка при связывании аккаунта") 