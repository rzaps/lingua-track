"""
Роутер для обработки тестов в боте
"""

import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import Config
from keyboards.main_keyboard import get_test_start_keyboard, get_test_answer_keyboard
from services.test_service import TestService

router = Router()

# Состояния для теста
class TestStates(StatesGroup):
    waiting_for_start = State()
    answering_question = State()

@router.message(Command("test"))
async def cmd_test(message: Message, state: FSMContext):
    """Обработчик команды /test - начало теста"""
    try:
        # Создаём тест через сервис
        test_data = TestService.create_test(message.from_user.id)
        
        if not test_data:
            await message.answer(Config.MESSAGES['no_cards'])
            return
        
        # Показываем стартовое сообщение
        await message.answer(
            Config.MESSAGES['test_start'].format(count=len(test_data['cards'])),
            reply_markup=get_test_start_keyboard()
        )
        
        await state.set_state(TestStates.waiting_for_start)
        
    except Exception as e:
        await message.answer(Config.MESSAGES['not_registered'])

@router.message(F.text == "📝 Пройти тест")
async def handle_test_button(message: Message, state: FSMContext):
    """Обработчик кнопки 'Пройти тест'"""
    await cmd_test(message, state)

@router.callback_query(F.data == "test_start")
async def callback_test_start(callback: CallbackQuery, state: FSMContext):
    """Обработчик начала теста"""
    user_id = callback.from_user.id
    
    if not TestService.get_test(user_id):
        await callback.answer("Тест не найден. Начните заново с /test")
        return
    
    # Переходим к первому вопросу
    await ask_question(callback.message, user_id)
    await state.set_state(TestStates.answering_question)
    await callback.answer()

@router.callback_query(F.data == "test_cancel")
async def callback_test_cancel(callback: CallbackQuery, state: FSMContext):
    """Обработчик отмены теста"""
    user_id = callback.from_user.id
    
    TestService.remove_test(user_id)
    
    await callback.message.edit_text("❌ Тест отменён")
    await state.clear()
    await callback.answer()

@router.callback_query(F.data.startswith("test_answer:"))
async def callback_test_answer(callback: CallbackQuery, state: FSMContext):
    """Обработчик ответа на вопрос теста"""
    user_id = callback.from_user.id
    user_answer = callback.data.split(":", 1)[1]
    
    # Обрабатываем ответ через сервис
    result = TestService.process_answer(user_id, user_answer)
    
    if not result:
        await callback.answer("Тест не найден")
        return
    
    # Показываем результат
    if result['is_correct']:
        result_text = f"✅ Правильно! {result['word']} = {result['correct_answer']}"
    else:
        result_text = f"❌ Неправильно! {result['word']} = {result['correct_answer']}"
    
    await callback.message.edit_text(result_text)
    
    if result['is_finished']:
        # Тест завершён
        await finish_test(callback.message, user_id)
        await state.clear()
    else:
        # Есть ещё вопросы
        await asyncio.sleep(2)  # Пауза для чтения результата
        await ask_question(callback.message, user_id)
    
    await callback.answer()

async def ask_question(message: Message, user_id: int):
    """Задаёт вопрос теста"""
    # Получаем текущий вопрос через сервис
    question_data = TestService.get_current_question(user_id)
    
    if not question_data:
        return
    
    # Формируем вопрос
    question_text = f"📝 Вопрос {question_data['question_number']}/{question_data['total_questions']}\n\n"
    question_text += f"Как переводится слово <b>{question_data['card'].word}</b>?"
    
    # Создаём клавиатуру с вариантами ответов
    keyboard = get_test_answer_keyboard(question_data['answers'], question_data['correct_answer'])
    
    await message.answer(question_text, parse_mode="HTML", reply_markup=keyboard)

async def finish_test(message: Message, user_id: int):
    """Завершает тест и показывает результаты"""
    # Завершаем тест через сервис
    results = TestService.finish_test(user_id)
    
    if not results:
        await message.answer("❌ Ошибка при завершении теста")
        return
    
    # Форматируем результаты через сервис
    final_text = TestService.format_test_results(results)
    
    await message.answer(final_text)
    # Показываем главное меню
    from keyboards.main_keyboard import get_main_keyboard
    from config import Config
    await message.answer(
        Config.MESSAGES['welcome'],
        reply_markup=get_main_keyboard()
    ) 