from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from calculator.forms import AddEntryForm
from calculator.models import DataEntryLineModel


def handle_entry_form(request):
    if request.method == 'POST':
        form = AddEntryForm(request.POST)
        if form.is_valid():
            # --- ВИПРАВЛЕННЯ ПОМИЛКИ MANY-TO-MANY ---

            # 1. Копіюємо cleaned_data, щоб можна було безпечно видалити Many-to-Many поле.
            data = form.cleaned_data.copy()

            # 2. Витягуємо Many-to-Many поле ('weather') зі словника.
            # selected_weather тепер містить QuerySet об'єктів WeatherCondition.
            # data більше не містить ключа 'weather'.
            selected_weather = data.pop('weather')

            # 3. ЕТАП 1: Створення об'єкта DataEntryLineModel.
            # Створюємо об'єкт лише з простими полями. Він зберігається в БД і отримує PK.
            new_entry = DataEntryLineModel.objects.create(**data)

            # 4. ЕТАП 2: Встановлення зв'язку Many-to-Many.
            # Використовуємо метод .set() для коректного збереження зв'язку в проміжній таблиці.
            new_entry.weather.set(selected_weather)

            messages.success(request, 'New data has been saved')
            return form, HttpResponseRedirect(reverse('calculator:dashboard'))
    else:
        form = AddEntryForm()

    return form, None