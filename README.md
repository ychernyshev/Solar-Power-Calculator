## Solar Energy Statistics App

A Django application for tracking daily solar energy generation and visualizing it with charts.  
The project demonstrates principles of autonomy, transparency, and UI clarity.

---

### 🚀 Features
- Track daily solar energy generation.
- Automatic calculations of generated power (Watts) and cost.
- Visualization of data with charts (power, cost).
- Dashboard with pagination and sorting.
- Tariff management via singleton model.
- Weather conditions stored as many-to-many relations.
- Responsive interface with top navigation and base template.

---

### Tech Stack
- Backend: Django
- Frontend: Bootstrap + custom templates
- Database: PostgreSQL
- Visualization: Django templates + JS charts

---

### 📦 Installation
```shell
git clone https://github.com/your-username/solar-energy-app.git
cd solar-energy-app
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

### ⚡ Usage

- Add new entries via the Add Entry form.
- View daily data in the dashboard table with pagination.
- Visualize data in tabs:
    - 📈 Generated Power
    - 💰 Generated Cost
- Manage tariffs via the Settings page.
- View weather conditions for each day.

---

### 📂 Project Structure

```
solar-energy-app/
│
├── calculator/         # Main Django app
│   ├── models.py       # Models and calculations
│   ├── views.py        # Views and logic
│   ├── forms.py        # Forms for data entry and tariff update
│   ├── services/       # handle_entry_form.py
│   └── templates/      # _base.html, _topnav.html, index.html
│
├── static/             # CSS, JS, Bootstrap
├── requirements.txt
└── README.md
```

---

### 📜 Code Examples
#### 🔗 urls.py
```python
from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('dashboard/', index, name='dashboard'),
    path('add_entry/', add_entry, name='add_entry'),
    path('settings/', settings, name='settings'),
]
```

#### views.py
```python
def index(request):
    entries = DataEntryLineModel.objects.all()
    total_power = DataEntryLineModel.total_generated_power()
    total_cost = DataEntryLineModel.total_cost_power()

    form, response = handle_entry_form(request)
    if response:
        return response

    labels = [entry.date.strftime("%d.%m.%Y") for entry in entries]
    power_values = [entry.full_day_power for entry in entries]
    cost_values = [entry.full_day_cost for entry in entries]

    entries_paginator = Paginator(entries, 25)
    entries_number = request.GET.get('page')
    entries_numbers = entries_paginator.get_page(entries_number)

    context = {
        'total_power': total_power,
        'total_cost': total_cost,
        'form': form,
        'labels': labels,
        'power_values': power_values,
        'cost_values': cost_values,
        'entries_numbers': entries_numbers
    }

    return render(request, 'calculator/index.html', context=context)
```

#### 📝 forms.py
```python
class AddEntryForm(forms.Form):
    date = forms.DateField(widget=CurrentDate(attrs={'class': 'form-control'}), initial=date.today())
    power = forms.ChoiceField(choices=DataEntryLineModel.POWER, initial='600', widget=forms.Select(attrs={'class': 'form-control'}))
    weather = forms.ModelMultipleChoiceField(queryset=WeatherCondition.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    morning_data_charge = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    ...
```

#### ⚡ models.py
```python
class CurrentTariffModel(models.Model):
    power_tariff = models.FloatField(verbose_name='Current tariff per kWh', default=4.32)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        try:
            return cls.objects.get(pk=1)
        except cls.DoesNotExist:
            return cls.objects.create(pk=1)
        
        
class DataEntryLineModel(models.Model):
    date = models.DateField(verbose_name='Date')
    power = models.CharField(choices=POWER, max_length=3, default='600')
    weather = models.ManyToManyField('WeatherCondition')
    ...
    def save(self, *args, **kwargs):
        if not self.pk:
            current_tariff_obj = CurrentTariffModel.load()
            self.power_tariff = current_tariff_obj.power_tariff
        self.full_day_power = self._calculate_full_day_power()
        self.full_day_cost = self._calculate_full_day_cost()
        super().save(*args, **kwargs)
```

#### admin.py
```python
@admin.register(DataEntryLineModel)
class DataEntryLineAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'display_power', 'get_weather',
        'display_morning_charge', 'display_morning_price',
        ...
    ]
```

### 📜 Development History
#### Highlights from commit evolution:

- Initial app structure → created calculator app, base urls, index view.
- Models & Admin → added power tracking model, customized admin panel.
- Math automation → automated calculations of power and cost.
- Templates → _base.html, topnav, active links, background design.
- Charts → daily power and cost charts with tab separation.
- Forms → AddEntryForm, refactored logic into services/handle_entry_form.py.
- Dashboard → entries table with pagination and sorting.
- Settings → singleton tariff model, settings page with update form.
- Weather → many-to-many weather conditions, admin integration.
- Fixes & Refactoring → optimized math, DRY principles in forms, bug fixes.

### 📜 License
MIT License — free to use, modify, and distribute.

