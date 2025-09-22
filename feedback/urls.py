from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('', views.feedback_form, name='feedback_form'),
    path('api/v1/telegram/', views.telegram_feedback, name='telegram_feedback'),
] 