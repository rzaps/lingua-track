from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .forms import FeedbackForm
from .models import Feedback

def feedback_form(request):
    """Представление для отображения формы отзывов"""
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            
            # Если пользователь авторизован, привязываем к нему
            if request.user.is_authenticated:
                feedback.user = request.user
            
            feedback.save()
            
            messages.success(request, 'Спасибо за ваш отзыв! Мы обязательно его рассмотрим.')
            return redirect('feedback:feedback_form')
    else:
        form = FeedbackForm()
    
    return render(request, 'feedback/feedback_form.html', {
        'form': form,
        'title': 'Оставить отзыв'
    })

@csrf_exempt
@require_http_methods(["POST"])
def telegram_feedback(request):
    """API endpoint для получения отзывов из Telegram бота"""
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        telegram_id = data.get('telegram_id')
        
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Текст отзыва не может быть пустым'
            })
        
        # Создаем отзыв
        feedback = Feedback.objects.create(
            text=text,
            telegram_id=telegram_id
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Отзыв успешно отправлен'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат JSON'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
