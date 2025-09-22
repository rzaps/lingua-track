from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    """Форма для отправки отзыва"""
    
    class Meta:
        model = Feedback
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Напишите, если у вас есть предложения, сообщения об ошибках или другие отзывы...'
            })
        }
        labels = {
            'text': 'Ваш отзыв'
        }
        help_texts = {
            'text': 'Опишите ваши предложения, найденные ошибки или просто поделитесь мнением о сервисе'
        } 