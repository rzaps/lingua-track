from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Главная страница статистики
    path('charts/', views.charts, name='charts'),  # Графики и диаграммы
    path('recommendations/', views.recommendations, name='recommendations'),  # Рекомендации
    path('test-history/', views.test_history, name='test_history'),  # История тестов
] 