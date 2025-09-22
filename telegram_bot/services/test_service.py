"""
Сервис для работы с тестами
"""

import time
import random
from typing import List, Dict, Any
from utils.django_utils import get_user_by_telegram_id, get_random_cards_for_test, save_test_result
from config import Config

class TestService:
    """Сервис для работы с тестами"""
    
    # Глобальное хранилище активных тестов (в продакшене лучше использовать Redis)
    active_tests = {}
    
    @classmethod
    def create_test(cls, telegram_id: int, questions_count: int = None) -> Dict[str, Any]:
        """Создаёт новый тест для пользователя"""
        if questions_count is None:
            questions_count = Config.TEST_QUESTIONS_COUNT
            
        user = get_user_by_telegram_id(telegram_id)
        cards = get_random_cards_for_test(user, questions_count)
        
        if not cards:
            return None
        
        test_data = {
            'user': user,
            'cards': cards,
            'current_question': 0,
            'correct_answers': 0,
            'wrong_answers': 0,
            'answers': [],
            'start_time': time.time()
        }
        
        cls.active_tests[telegram_id] = test_data
        return test_data
    
    @classmethod
    def get_test(cls, telegram_id: int) -> Dict[str, Any]:
        """Получает активный тест пользователя"""
        return cls.active_tests.get(telegram_id)
    
    @classmethod
    def remove_test(cls, telegram_id: int):
        """Удаляет активный тест пользователя"""
        if telegram_id in cls.active_tests:
            del cls.active_tests[telegram_id]
    
    @classmethod
    def process_answer(cls, telegram_id: int, user_answer: str) -> Dict[str, Any]:
        """Обрабатывает ответ пользователя на вопрос теста"""
        test_data = cls.active_tests.get(telegram_id)
        if not test_data:
            return None
        
        current_card = test_data['cards'][test_data['current_question']]
        correct_answer = current_card.translation
        
        is_correct = user_answer == correct_answer
        
        if is_correct:
            test_data['correct_answers'] += 1
        else:
            test_data['wrong_answers'] += 1
        
        # Сохраняем ответ
        test_data['answers'].append({
            'card': current_card,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct
        })
        
        # Переходим к следующему вопросу
        test_data['current_question'] += 1
        
        return {
            'is_correct': is_correct,
            'correct_answer': correct_answer,
            'word': current_card.word,
            'is_finished': test_data['current_question'] >= len(test_data['cards'])
        }
    
    @classmethod
    def get_current_question(cls, telegram_id: int) -> Dict[str, Any]:
        """Получает текущий вопрос теста"""
        test_data = cls.active_tests.get(telegram_id)
        if not test_data or test_data['current_question'] >= len(test_data['cards']):
            return None
        
        current_card = test_data['cards'][test_data['current_question']]
        correct_answer = current_card.translation
        
        # Получаем другие карточки для создания неправильных ответов
        other_cards = get_random_cards_for_test(test_data['user'], 10)
        wrong_answers = [card.translation for card in other_cards if card.translation != correct_answer][:3]
        
        # Добавляем правильный ответ и перемешиваем
        all_answers = [correct_answer] + wrong_answers
        random.shuffle(all_answers)
        
        return {
            'card': current_card,
            'question_number': test_data['current_question'] + 1,
            'total_questions': len(test_data['cards']),
            'answers': all_answers,
            'correct_answer': correct_answer
        }
    
    @classmethod
    def finish_test(cls, telegram_id: int) -> Dict[str, Any]:
        """Завершает тест и возвращает результаты"""
        test_data = cls.active_tests.get(telegram_id)
        if not test_data:
            return None
        
        # Вычисляем статистику
        total_questions = len(test_data['cards'])
        correct_answers = test_data['correct_answers']
        accuracy = round((correct_answers / total_questions) * 100, 1)
        
        # Определяем сообщение по результату
        if accuracy >= 90:
            result_message = Config.TEST_MESSAGES['excellent']
        elif accuracy >= 75:
            result_message = Config.TEST_MESSAGES['good']
        elif accuracy >= 60:
            result_message = Config.TEST_MESSAGES['satisfactory']
        else:
            result_message = Config.TEST_MESSAGES['poor']
        
        # Сохраняем результат в базу данных
        save_test_result(
            user=test_data['user'],
            test_type='multiple_choice',
            direction='en-ru',  # Пока только английский → русский
            score=correct_answers,
            total=total_questions,
            correct_answers=correct_answers,
            wrong_answers=test_data['wrong_answers']
        )
        
        # Удаляем тест из активных
        cls.remove_test(telegram_id)
        
        return {
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'accuracy': accuracy,
            'result_message': result_message,
            'answers': test_data['answers']
        }
    
    @staticmethod
    def format_test_results(results: Dict[str, Any]) -> str:
        """Форматирует результаты теста для отображения"""
        final_text = Config.MESSAGES['test_complete'].format(
            correct=results['correct_answers'],
            total=results['total_questions'],
            accuracy=results['accuracy'],
            message=results['result_message']
        )
        
        # Добавляем детали по вопросам
        final_text += "\n\n📋 Детали:\n"
        for i, answer in enumerate(results['answers'], 1):
            emoji = "✅" if answer['is_correct'] else "❌"
            final_text += f"{i}. {emoji} {answer['card'].word} = {answer['correct_answer']}\n"
        
        return final_text 