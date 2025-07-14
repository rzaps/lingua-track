from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Модель для хранения результатов тестов
# Содержит статистику по всем типам тестов: множественный выбор, ввод, сопоставление
class TestResult(models.Model):
    TEST_TYPE_CHOICES = [
        ('multiple_choice', 'Множественный выбор'),
        ('typing', 'Ввод с клавиатуры'),
        ('matching', 'Сопоставление'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    test_type = models.CharField(max_length=20, choices=TEST_TYPE_CHOICES)  # Тип теста
    direction = models.CharField(max_length=10)  # Направление: en-ru или ru-en
    score = models.IntegerField()  # Количество правильных ответов
    total = models.IntegerField()  # Общее количество вопросов
    completed_at = models.DateTimeField(auto_now_add=True)  # Дата и время завершения теста
    
    # --- Детальная статистика ---
    correct_answers = models.IntegerField(default=0)  # Правильные ответы
    wrong_answers = models.IntegerField(default=0)  # Неправильные ответы
    time_taken = models.IntegerField(null=True, blank=True)  # Время прохождения в секундах (опционально)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_test_type_display()} ({self.score}/{self.total})"
    
    # Метод для вычисления процента правильных ответов
    @property
    def accuracy(self):
        """Возвращает процент правильных ответов"""
        if self.total == 0:
            return 0
        return round((self.score / self.total) * 100, 1)
    
    # Метод для определения результата теста
    @property
    def result_level(self):
        """Возвращает уровень результата: отлично, хорошо, удовлетворительно, плохо"""
        accuracy = self.accuracy
        if accuracy >= 90:
            return "Отлично"
        elif accuracy >= 75:
            return "Хорошо"
        elif accuracy >= 60:
            return "Удовлетворительно"
        else:
            return "Плохо"

# Модель для общей статистики пользователя
# Агрегирует данные по карточкам, повторениям и тестам
class UserStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='stats')
    
    # --- Статистика карточек ---
    total_cards = models.IntegerField(default=0)  # Общее количество карточек
    beginner_cards = models.IntegerField(default=0)  # Карточки начального уровня
    intermediate_cards = models.IntegerField(default=0)  # Карточки среднего уровня
    advanced_cards = models.IntegerField(default=0)  # Карточки продвинутого уровня
    
    # --- Статистика повторений ---
    total_reviews = models.IntegerField(default=0)  # Общее количество повторений
    successful_reviews = models.IntegerField(default=0)  # Успешные повторения
    failed_reviews = models.IntegerField(default=0)  # Неуспешные повторения
    
    # --- Статистика тестов ---
    total_tests = models.IntegerField(default=0)  # Общее количество пройденных тестов
    tests_accuracy = models.FloatField(default=0.0)  # Средняя точность тестов
    
    # --- Метаданные ---
    last_activity = models.DateTimeField(auto_now=True)  # Последняя активность
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания статистики
    
    def __str__(self):
        return f"Статистика {self.user.username}"
    
    # Метод для вычисления процента успешности повторений
    @property
    def review_success_rate(self):
        """Возвращает процент успешных повторений"""
        if self.total_reviews == 0:
            return 0
        return round((self.successful_reviews / self.total_reviews) * 100, 1)
    
    # Метод для получения рекомендаций
    def get_recommendations(self):
        """Возвращает список рекомендаций на основе статистики"""
        recommendations = []
        
        # Рекомендации по уровням
        if self.beginner_cards > 0 and self.beginner_cards < 10:
            recommendations.append("Добавьте больше слов начального уровня")
        if self.intermediate_cards > 0 and self.intermediate_cards < 5:
            recommendations.append("Попробуйте добавить слова среднего уровня")
        if self.advanced_cards == 0:
            recommendations.append("Попробуйте добавить слова продвинутого уровня")
        
        # Рекомендации по повторениям
        if self.review_success_rate < 70:
            recommendations.append("Уделите больше внимания повторению слов")
        if self.total_reviews < 10:
            recommendations.append("Регулярно повторяйте слова для лучшего запоминания")
        
        # Рекомендации по тестам
        if self.total_tests < 5:
            recommendations.append("Попробуйте пройти тесты для проверки знаний")
        if self.tests_accuracy < 80:
            recommendations.append("Повторите слова перед прохождением тестов")
        
        return recommendations
