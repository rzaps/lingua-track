"""
Роутер для обработки озвучки слов
"""

import os
from aiogram import Router, F
from aiogram.types import Message, Voice
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import Config
from services.tts_service import TTSService

router = Router()

@router.message(Command("say"))
async def cmd_say(message: Message):
    """Обработчик команды /say - озвучка слова"""
    # Получаем текст после команды
    text = message.text.replace('/say', '').strip()
    
    if not text:
        await message.answer(TTSService.get_usage_message())
        return
    
    await process_tts_request(message, text)

@router.message(F.text == "🔊 Озвучить слово")
async def handle_say_button(message: Message):
    """Обработчик кнопки 'Озвучить слово'"""
    await message.answer(
        "🔊 Введите слово для озвучки:\n\n"
        "Примеры:\n"
        "• hello\n"
        "• beautiful\n"
        "• привет\n\n"
        "Или используйте команду /say слово"
    )

@router.message(lambda message: message.text and message.text.startswith('/say '))
async def handle_say_command(message: Message):
    """Обработчик команды /say с пробелом"""
    text = message.text.replace('/say ', '').strip()
    if text:
        await process_tts_request(message, text)

async def process_tts_request(message: Message, word: str):
    """Обрабатывает запрос на озвучку слова"""
    try:
        # Очищаем и валидируем слово через сервис
        cleaned_word = TTSService.clean_word(word)
        
        if not TTSService.validate_word(cleaned_word):
            await message.answer("❌ Неверный формат слова")
            return
        
        # Определяем язык слова через сервис
        lang = TTSService.detect_language(cleaned_word)
        
        # Отправляем сообщение о начале обработки
        processing_msg = await message.answer(TTSService.get_processing_message(cleaned_word))
        
        # Генерируем аудио через сервис
        audio_path = await TTSService.generate_audio(cleaned_word, lang)
        
        if audio_path and os.path.exists(audio_path):
            # Отправляем аудиофайл
            with open(audio_path, 'rb') as audio_file:
                await message.answer_voice(
                    voice=audio_file,
                    caption=TTSService.format_audio_caption(cleaned_word, lang)
                )
            
            # Удаляем сообщение о обработке
            await processing_msg.delete()
            
        else:
            await processing_msg.edit_text(TTSService.get_error_message(cleaned_word))
            
    except Exception as e:
        await message.answer(f"❌ Ошибка при озвучке: {str(e)}") 