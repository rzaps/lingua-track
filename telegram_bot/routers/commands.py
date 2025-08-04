"""
Роутер для основных команд бота
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.django_init import *

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import re
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

from config import Config
from keyboards.main_keyboard import get_main_keyboard, get_cards_navigation_keyboard
from services.user_service import UserService
from utils.django_utils import get_user_by_telegram_id, link_telegram_to_existing_user, get_user_telegram_info

router = Router()

# Клавиатура для новых пользователей (только одна кнопка)
def get_link_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔗 Привязать аккаунт")]],
        resize_keyboard=True
    )

# Инлайн-клавиатура для привязки аккаунта
def get_link_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📧 Указать email", callback_data="add_email"),
                InlineKeyboardButton(text="🔗 Связать с аккаунтом", callback_data="link_account")
            ]
        ]
    )

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    user = await sync_to_async(get_user_by_telegram_id)(telegram_id)
    # Проверяем, есть ли у пользователя реальный email (а не технический)
    if user.email.startswith("telegram_") and user.email.endswith("@linguatrack.local"):
        # Новый пользователь — только Telegram
        await message.answer(
            "👋 Добро пожаловать в LinguaTrack!\n\n"
            "LinguaTrack — это сервис для изучения иностранных слов с помощью карточек, интервального повторения, тестов и статистики.\n\n"
            "🔗 Для добавления слов, прохождения тестов и синхронизации прогресса вам нужно зарегистрироваться на сайте и привязать аккаунт.\n\n"
            "👉 Нажмите кнопку ниже, чтобы зарегистрироваться и связать аккаунт с Telegram. После этого вы сможете пользоваться всеми возможностями бота и сайта!",
            reply_markup=get_link_keyboard()
        )
    else:
        # Обычный пользователь — показываем главное меню
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
        today_cards = await sync_to_async(UserService.get_today_reviews)(message.from_user.id)
        
        if not today_cards:
            await message.answer(Config.MESSAGES['no_reviews_today'])
            return
        
        # Форматируем карточки через сервис
        cards_text = "📚 Слова на повторение сегодня:\n\n"
        cards_text += await sync_to_async(UserService.format_cards_for_display)(today_cards)
        cards_text += "\nИспользуйте команду /test для проверки знаний!"
        
        await message.answer(cards_text, parse_mode="HTML")
        
    except Exception as e:
        await message.answer(Config.MESSAGES['not_registered'])

@router.message(Command("progress"))
async def cmd_progress(message: Message):
    """Обработчик команды /progress - статистика пользователя"""
    try:
        # Получаем статистику через сервис
        progress = await sync_to_async(UserService.get_user_statistics)(message.from_user.id)
        
        # Форматируем статистику через сервис
        stats_text = await sync_to_async(UserService.format_statistics_for_display)(progress)
        
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
        cards_data = await sync_to_async(UserService.get_user_cards_paginated)(message.from_user.id, page, Config.CARDS_PER_PAGE)
        
        if not cards_data['cards']:
            await message.answer(Config.MESSAGES['no_cards'])
            return
        
        # Формируем сообщение
        cards_text = f"🗂 Ваши карточки (страница {page}/{cards_data['total_pages']}):\n\n"
        cards_text += await sync_to_async(UserService.format_cards_for_display)(cards_data['cards'])
        
        # Создаём клавиатуру для навигации
        keyboard = get_cards_navigation_keyboard(page, cards_data['total_pages'])
        
        await message.answer(cards_text, parse_mode="HTML", reply_markup=keyboard)
        
    except Exception as e:
        await message.answer(Config.MESSAGES['not_registered'])

# Обработчики кнопок клавиатуры (используют те же функции)
@router.message(F.text == "📚 Слова на сегодня")
async def handle_today_button(message: Message):
    await cmd_today(message)

@router.message(F.text == "📊 Статистика")
async def handle_progress_button(message: Message):
    await cmd_progress(message)

@router.message(F.text == "🗂 Карточки")
async def handle_cards_button(message: Message):
    await cmd_cards(message)

@router.message(F.text == "❓ Помощь")
async def handle_help_button(message: Message):
    await cmd_help(message)

@router.message(Command("link"))
async def link_account(message: Message):
    """Связывает Telegram аккаунт с существующим пользователем Django"""
    telegram_id = message.from_user.id
    telegram_username = message.from_user.username
    
    # Проверяем, не связан ли уже аккаунт
    try:
        user = await sync_to_async(get_user_by_telegram_id)(telegram_id)
        telegram_info = await sync_to_async(get_user_telegram_info)(user)
        
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
        user = await sync_to_async(link_telegram_to_existing_user)(telegram_id, telegram_username, username)
        
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

class AddEmailStates(StatesGroup):
    waiting_for_email = State()

@router.message(Command("add_email"))
async def cmd_add_email(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите ваш email для привязки к аккаунту:")
    await state.set_state(AddEmailStates.waiting_for_email)

EMAIL_REGEX = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

@router.message(AddEmailStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    email = message.text.strip()
    if not re.match(EMAIL_REGEX, email):
        await message.answer("❌ Некорректный email. Попробуйте ещё раз:")
        return

    # Проверка уникальности email
    email_exists = await sync_to_async(User.objects.filter(email=email).exists)()
    if email_exists:
        await message.answer("❌ Этот email уже используется. Попробуйте другой:")
        return

    # Получаем пользователя по telegram_id
    user = await sync_to_async(get_user_by_telegram_id)(message.from_user.id)
    user.email = email
    await sync_to_async(user.save)()

    await message.answer(
        "✅ Email успешно привязан к вашему аккаунту!\n\n"
        "Теперь вы можете войти на сайт по email. Если не знаете пароль — воспользуйтесь функцией 'Забыли пароль?' на сайте."
    )
    await state.clear()
    # Показываем главное меню
    await message.answer(
        Config.MESSAGES['welcome'],
        reply_markup=get_main_keyboard()
    )

# Обработка нажатия на кнопку "🔗 Привязать аккаунт"
@router.message(F.text == "🔗 Привязать аккаунт")
async def handle_link_button(message: Message):
    await message.answer(
        "Для связи вашего Telegram с сайтом LinguaTrack выберите способ:",
        reply_markup=get_link_inline_keyboard()
    )

# Обработчики инлайн-кнопок
@router.callback_query(F.data == "add_email")
async def handle_add_email_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Пожалуйста, введите ваш email для привязки к аккаунту:")
    await state.set_state(AddEmailStates.waiting_for_email)
    await callback.answer()

@router.callback_query(F.data == "link_account")
async def handle_link_account_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "Для связи с существующим аккаунтом на сайте:\n\n"
        "1️⃣ Зарегистрируйтесь на сайте: http://127.0.0.1:8000/register/\n"
        "2️⃣ Или отправьте команду:\n"
        "<code>/link_username ваш_username_с_сайта</code>\n\n"
        "После регистрации/привязки вернитесь в бот и используйте /start.",
        parse_mode="HTML"
    )
    await callback.answer() 