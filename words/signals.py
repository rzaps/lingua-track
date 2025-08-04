from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Card, Repetition

@receiver(post_save, sender=Card)
def create_repetition_for_card(sender, instance, created, **kwargs):
    """
    Автоматически создаёт Repetition при создании новой карточки
    """
    if created:
        # Проверяем, не существует ли уже Repetition для этой карточки
        if not Repetition.objects.filter(card=instance, user=instance.user).exists():
            Repetition.objects.create(
                card=instance,
                user=instance.user,
                next_review=instance.created_at.date(),
                interval=1,
                easiness=2.5,
                total_reviews=0,
                successful_reviews=0,
                failed_reviews=0,
                consecutive_failures=0,
            ) 