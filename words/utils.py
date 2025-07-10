from django.utils import timezone


# Алгоритм интервального повторения SM-2.
# repetition — объект модели Repetition
# quality — оценка (0–5)


def update_sm2(repetition, quality):
    if quality < 3:
        repetition.interval = 1
        repetition.repetition_count = 0
    else:
        if repetition.repetition_count == 0:
            repetition.interval = 1
        elif repetition.repetition_count == 1:
            repetition.interval = 6
        else:
            repetition.interval = int(repetition.interval * repetition.easiness)

        repetition.repetition_count += 1

    # Пересчёт коэффициента сложности (easiness factor)
    ef = repetition.easiness
    ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    repetition.easiness = max(1.3, ef)

    # Обновляем даты
    repetition.last_reviewed = timezone.now().date()
    repetition.next_review = repetition.last_reviewed + timezone.timedelta(days=repetition.interval)

    repetition.save()
