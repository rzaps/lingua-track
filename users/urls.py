from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('telegram-link/', views.telegram_link, name='telegram_link'),
] 