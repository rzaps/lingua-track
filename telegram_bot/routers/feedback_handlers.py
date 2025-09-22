"""
Роутер для обработки отзывов в боте
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import Config
from services.feedback_service import FeedbackService
from services.user_service import UserService
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)

router = Router()

# Состояния для сбора отзыва
class FeedbackStates(StatesGroup):
    waiting_for_feedback = State()

@router.message(Command("feedback"))
async def cmd_feedback(message: Message, state: FSMContext):
    """Обработчик команды /feedback - оставить отзыв"""
    try:
        # Проверяем, что пользователь существует
        await sync_to_async(UserService.get_or_create_user)(message.from_user.id)
        
        await message.answer(
            "💬 Оставить отзыв\n\n"
            "Напишите, если у вас есть предложения, сообщения об ошибках или другие отзывы о сервисе LinguaTrack.\n\n"
            "Мы ценим ваше мнение и обязательно рассмотрим все сообщения!\n\n"
            "📝 Просто напишите ваш отзыв в следующем сообщении:"
        )
        
        await state.set_state(FeedbackStates.waiting_for_feedback)
        
    except Exception as e:
        logger.exception("Ошибка в /feedback")
        await message.answer(Config.MESSAGES['not_registered'])

@router.message(F.text == "💬 Оставить отзыв")
async def handle_feedback_button(message: Message, state: FSMContext):
    """Обработчик кнопки 'Оставить отзыв'"""
    await cmd_feedback(message, state)

@router.message(FeedbackStates.waiting_for_feedback)
async def handle_feedback_text(message: Message, state: FSMContext):
    """Обработчик текста отзыва"""
    try:
        feedback_text = message.text.strip()
        
        if not feedback_text:
            await message.answer("❌ Текст отзыва не может быть пустым. Попробуйте ещё раз:")
            return
        
        # Отправляем отзыв через сервис
        result = await FeedbackService.send_feedback(feedback_text, message.from_user.id)
        
        if result.get('success'):
            await message.answer(
                "✅ Спасибо за ваш отзыв!\n\n"
                "Мы обязательно его рассмотрим и учтём при дальнейшем развитии сервиса.\n\n"
                "Если у вас есть ещё предложения, используйте команду /feedback снова."
            )
        else:
            error_msg = result.get('error', 'Неизвестная ошибка')
            await message.answer(
                f"❌ Ошибка при отправке отзыва: {error_msg}\n\n"
                "Попробуйте позже или обратитесь к администратору."
            )
        
        await state.clear()
        
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка: {str(e)}\n\nПопробуйте позже."
        )
        await state.clear() 