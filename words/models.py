from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Класс карточки
class Card(models.Model):
    LEVEL_CHOICES = [
        ("beginner", "Начальный"),
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

    def __str__(self):
        return f"{self.card.word} — повтор через {self.interval} дн."