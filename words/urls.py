from django.urls import path
from . import views

app_name = 'words'

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница списка карточек
    path('add/', views.add_card, name='add_card'),  # Добавить карточку
    path('card/<int:pk>/', views.card_detail, name='card_detail'),  # Детали карточки
    path('card/<int:pk>/edit/', views.edit_card, name='edit_card'),  # Редактировать карточку
    path('card/<int:pk>/delete/', views.delete_card, name='delete_card'),  # Удалить карточку
    path('card_mode/', views.card_mode, name='card_mode'),  # Режим карточек


    # --- Повторение слов (интервальный тренажёр) ---
    path('review/', views.review_today, name='review_today'),  # слова на повторение
    path('review/<int:pk>/', views.review_card, name='review_card'),  # конкретное слово

    # --- Озвучка ---
    path('tts/<str:word>/', views.tts_audio, name='tts_audio'),  # Озвучка слова
]
