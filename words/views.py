from django.contrib.auth.decorators import login_required
from django.http import request
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import CardForm
from .models import Card

# Главная страница списка карточек
@login_required
def index(request):

    # Получаем все карточки текущего пользователя, сортируем по дате создания (новые сверху)
    cards = Card.objects.filter(user=request.user).order_by('-created_at')

    # Получаем параметры фильтрации из GET-запроса (если есть)
    level = request.GET.get('level')  # уровень сложности: beginner, intermediate, advanced
    search = request.GET.get('search')  # поисковая строка для слова

    # Если выбран уровень, фильтруем карточки по уровню
    if level:
        cards = cards.filter(level=level)

    # Если есть поисковый запрос, фильтруем карточки, где слово содержит поисковую строку (без учёта регистра)
    if search:
        cards = cards.filter(word__icontains=search)  # можно расширить и на перевод, если нужно

    # Формируем контекст для шаблона — отфильтрованные карточки и текущие параметры фильтра
    context = {
        'cards': cards,
        'level': level,
        'search': search,
    }
    # Выводим шаблон 'words/index.html' с переданным контекстом
    return render(request, 'words/index.html', context)

# Добавление карточки
@login_required
def add_card(request):
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
            return redirect('words:index')
    else:
        form = CardForm()
    return render(request, 'words/add_card.html', {'form': form})

# Редактирование карточки
@login_required
def edit_card(request, pk):
    card = get_object_or_404(Card, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            return redirect('words:card_detail', pk=card.pk)
    else:
        form = CardForm(instance=card)
    return render(request, 'words/card_form.html', {'form': form})

# Удаление карточки
@login_required
def delete_card(request, pk):
    card = get_object_or_404(Card, pk=pk, user=request.user)
    if request.method == 'POST':
        card.delete()
        return redirect('words:index')
    return render(request, 'words/confirm_delete.html', {'card': card})

# Просмотр деталей карточки
@login_required
def card_detail(request, pk):
    card = get_object_or_404(Card, pk=pk, user=request.user)
    return render(request, 'words/card_detail.html', {'card': card})

# Режим карточек
@login_required
def card_mode(request):
    # Получаем id карточки из GET параметров, если нет — первая карточка
    card_id = request.GET.get('card_id')
    cards = Card.objects.filter(user=request.user).order_by('created_at')

    if not cards.exists():
        return render(request, 'words/card_mode.html', {'message': 'У вас пока нет слов для карточек.'})

    if card_id:
        try:
            card = cards.get(pk=card_id)
        except Card.DoesNotExist:
            card = cards.first()
    else:
        card = cards.first()

    # Получим индекс текущей карточки для навигации
    card_list = list(cards)
    current_index = card_list.index(card)
    total = len(card_list)

    context = {
        'card': card,
        'current_index': current_index + 1,
        'total': total,
        'prev_card_id': card_list[current_index - 1].pk if current_index > 0 else None,
        'next_card_id': card_list[current_index + 1].pk if current_index < total - 1 else None,
    }
    return render(request, 'words/card_mode.html', context)


# Список слов на повторение сегодня
@login_required
def review_today(request):
    today = timezone.now().date()
    cards = Card.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'words/review_today.html', {'cards': cards})

# Повторение конкретного слова (карточки)
@login_required
def review_card(request, pk):
    card = get_object_or_404(Card, pk=pk, user=request.user)
    return render(request, 'words/review_card.html', {'card': card})

# Статистика
@login_required
def user_progress(request):
    total = Card.objects.filter(user=request.user).count()
    beginner = Card.objects.filter(user=request.user, level='beginner').count()
    intermediate = Card.objects.filter(user=request.user, level='intermediate').count()
    advanced = Card.objects.filter(user=request.user, level='advanced').count()
    return render(request, 'words/progress.html', {
        'total': total,
        'beginner': beginner,
        'intermediate': intermediate,
        'advanced': advanced,
    })