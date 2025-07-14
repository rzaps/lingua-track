from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.choose_test, name='choose_test'),  # Главная страница выбора теста
    path('multiple-choice/', views.multiple_choice_test, name='multiple_choice'),
    path('typing/', views.typing_test, name='typing'),  # Тест с вводом с клавиатуры
    path('matching/', views.matching_test, name='matching'),  # Тест с сопоставлением
] 