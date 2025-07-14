# 👥 Приложение Users

Приложение для управления пользователями и их профилями в системе LinguaTrack.

## 🎯 Назначение

Приложение `users` отвечает за:
- Регистрацию новых пользователей
- Управление профилями пользователей
- Интеграцию с Telegram
- Аутентификацию и авторизацию

## 📁 Структура

```
users/
├── models.py          # Модели пользователей
├── views.py           # Представления
├── forms.py           # Формы
├── admin.py           # Админка
├── urls.py            # URL маршруты
├── templates/         # Шаблоны
│   └── users/
│       └── telegram_link.html
└── README.md          # Документация
```

## 🗄️ Модели

### UserProfile
Расширенный профиль пользователя для интеграции с Telegram:

- `user` - связь с Django User
- `telegram_id` - уникальный ID в Telegram
- `telegram_username` - username в Telegram
- `is_telegram_user` - флаг регистрации через Telegram
- `created_at` / `updated_at` - метаданные

## 📝 Формы

### UserRegistrationForm
Расширенная форма регистрации с полями для Telegram:
- Стандартные поля Django User
- `telegram_id` - для связи с ботом
- `telegram_username` - для удобства

## 🌐 URL маршруты

- `/users/register/` - регистрация новых пользователей
- `/users/telegram-link/` - управление связью с Telegram

## 🔗 Интеграция с Telegram

### Способы связывания:
1. **При регистрации** - указать Telegram ID в форме
2. **Через бота** - команда `/link_username username`
3. **Через веб-интерфейс** - страница управления профилем

### Преимущества связи:
- ✅ Синхронизация карточек между платформами
- ✅ Общая статистика и прогресс
- ✅ Автоматические напоминания в Telegram
- ✅ Тесты и озвучка в боте

## 🛠️ Использование

### В коде Django:
```python
from users.models import UserProfile

# Получить профиль пользователя
profile = user.profile

# Проверить связь с Telegram
if profile.is_telegram_user:
    telegram_id = profile.telegram_id
```

### В Telegram боте:
```python
from users.models import UserProfile

# Найти пользователя по Telegram ID
profile = UserProfile.objects.get(telegram_id=123456789)
user = profile.user
```

## 🔒 Безопасность

- Валидация Telegram ID
- Проверка уникальности связей
- Безопасное создание профилей
- Обработка ошибок при связывании

## 📊 Админка

В Django Admin доступны:
- Просмотр всех профилей пользователей
- Фильтрация по статусу Telegram
- Поиск по username и email
- Редактирование связей с Telegram

## 🔄 Миграции

При изменении моделей:
```bash
python manage.py makemigrations users
python manage.py migrate
```

---

**Приложение Users** - централизованное управление пользователями LinguaTrack! 👥 