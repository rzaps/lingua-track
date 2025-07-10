from django import forms
from .models import Card

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['word', 'translation', 'example', 'note', 'level']
        labels = {
            'word': 'Слово (иностранное)',
            'translation': 'Перевод',
            'example': 'Пример использования',
            'note': 'Примечание',
            'level': 'Уровень сложности',
        }
        widgets = {
            'example': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'word': forms.TextInput(attrs={'class': 'form-control'}),
            'translation': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
        }
