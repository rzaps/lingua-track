from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Класс карточки
class Card(models.Model):
    LEVEL_CHOICES = [
        ("beginner", "Начальный"),
        ("intermediate", "Средний"),
        ("advanced", "Продвинутый"),
    ]

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="cards")  # Владелец карточки
    word = models.CharField("Слово на иностранном языке", max_length=100)
    translation = models.CharField("Перевод", max_length=100)
    example = models.CharField("Пример", max_length=250, blank=True)  # Пример использования слова
    note = models.CharField("Примечание", max_length=250, blank=True)  # Примечания/комментарии
    level = models.CharField("Уровень", max_length=20, choices=LEVEL_CHOICES, default="beginner")
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания карточки


    def __str__(self):
        return f"{self.word} → {self.translation}"

# Класс повторений
class Repetition(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_reviewed = models.DateField(null=True, blank=True)
    next_review = models.DateField(default=timezone.now)
    interval = models.IntegerField(default=1)  # дней до следующего повтора
    repetition_count = models.IntegerField(default=0)
    easiness = models.FloatField(default=2.5)  # коэффициент сложности (EF)
    
    # --- Статистика повторений ---
    total_reviews = models.IntegerField(default=0)  # Общее количество повторений
    successful_reviews = models.IntegerField(default=0)  # Успешные повторения (оценка 3-5)
    failed_reviews = models.IntegerField(default=0)  # Неуспешные повторения (оценка 0-2)
    last_quality = models.IntegerField(null=True, blank=True)  # Последняя оценка качества
    consecutive_successes = models.IntegerField(default=0)  # Подряд успешных повторений
    consecutive_failures = models.IntegerField(default=0)  # Подряд неуспешных повторений

    def __str__(self):
        return f"{self.card.word} — повтор через {self.interval} дн."

    def update_stats(self, quality):
        """Обновляет статистику повторения на основе оценки качества"""
        self.total_reviews += 1
        self.last_quality = quality
        self.last_reviewed = timezone.now().date()
        
        if quality >= 3:  # Успешное повторение
            self.successful_reviews += 1
            self.consecutive_successes += 1
            self.consecutive_failures = 0
        else:  # Неуспешное повторение
            self.failed_reviews += 1
            self.consecutive_failures += 1
            self.consecutive_successes = 0

    @property
    def success_rate(self):
        """Возвращает процент успешных повторений"""
        if self.total_reviews == 0:
            return 0
        return round((self.successful_reviews / self.total_reviews) * 100, 1)