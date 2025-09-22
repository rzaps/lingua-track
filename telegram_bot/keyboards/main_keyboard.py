"""
Основная клавиатура бота
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура с главными командами"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📚 Слова на сегодня"),
                KeyboardButton(text="📝 Пройти тест")
            ],
            [
                KeyboardButton(text="📊 Статистика"),
                KeyboardButton(text="🗂 Карточки")
            ],
            [
                KeyboardButton(text="🔊 Озвучить слово"),
                KeyboardButton(text="❓ Помощь")
            ],
            [
                KeyboardButton(text="💬 Оставить отзыв")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )
    return keyboard

def get_test_start_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для начала теста"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Начать тест",
                    callback_data="test_start"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="test_cancel"
                )
            ]
        ]
    )
    return keyboard

def get_test_answer_keyboard(answers: list, correct_answer: str) -> InlineKeyboardMarkup:
    """Клавиатура с вариантами ответов для теста"""
    import random
    
    # Перемешиваем ответы
    shuffled_answers = answers.copy()
    random.shuffle(shuffled_answers)
    
    keyboard_buttons = []
    for answer in shuffled_answers:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=answer,
                callback_data=f"test_answer:{answer}"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard

def get_review_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для оценки качества повторения"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="😞 Забыл", callback_data="review_0"),
                InlineKeyboardButton(text="😐 Сложно", callback_data="review_1"),
                InlineKeyboardButton(text="😊 Помню", callback_data="review_2")
            ],
            [
                InlineKeyboardButton(text="😄 Легко", callback_data="review_3"),
                InlineKeyboardButton(text="🤩 Отлично", callback_data="review_4"),
                InlineKeyboardButton(text="🎯 Идеально", callback_data="review_5")
            ]
        ]
    )
    return keyboard

def get_cards_navigation_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Клавиатура для навигации по карточкам"""
    keyboard_buttons = []
    
    # Кнопки навигации
    nav_buttons = []
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(text="◀️", callback_data=f"cards_page:{page-1}")
        )
    
    nav_buttons.append(
        InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="cards_info")
    )
    
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(text="▶️", callback_data=f"cards_page:{page+1}")
        )
    
    keyboard_buttons.append(nav_buttons)
    
    # Кнопка закрытия
    keyboard_buttons.append([
        InlineKeyboardButton(text="❌ Закрыть", callback_data="cards_close")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard

def get_yes_no_keyboard() -> InlineKeyboardMarkup:
    """Простая клавиатура Да/Нет"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data="yes"),
                InlineKeyboardButton(text="❌ Нет", callback_data="no")
            ]
        ]
    )
    return keyboard 