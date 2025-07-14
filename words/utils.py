from django.utils import timezone
import os
from gtts import gTTS
from django.conf import settings


# Алгоритм интервального повторения SM-2.
# repetition — объект модели Repetition
# quality — оценка (0–5)


def update_sm2(repetition, quality):
    # Обновляем статистику повторения
    repetition.update_stats(quality)
    
    # Алгоритм интервального повторения SM-2
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



# Генерирует mp3-файл с озвучкой слова и возвращает путь к файлу.

def generate_tts(word, lang='en'):
   
    tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
    os.makedirs(tts_dir, exist_ok=True)
    filename = f"{word}_{lang}.mp3"
    filepath = os.path.join(tts_dir, filename)
    if not os.path.exists(filepath):
        tts = gTTS(text=word, lang=lang)
        tts.save(filepath)
    return os.path.join('tts', filename)
