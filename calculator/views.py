from django.contrib.admin.templatetags.admin_list import pagination
from django.core.paginator import Paginator
from django.shortcuts import render

from calculator.services.handle_entry_form import handle_entry_form
from calculator.models import DataEntryLineModel


# Create your views here.
def index(request):
    entries = DataEntryLineModel.objects.all()
    total_power = DataEntryLineModel.total_generated_power()
    total_cost = DataEntryLineModel.total_cost_power()

    form, response = handle_entry_form(request)
    if response:
        return response

    # charts
    labels = [entry.date.strftime("%d.%m.%Y") for entry in entries]
    power_values = [entry.full_day_power for entry in entries]
    cost_values = [entry.full_day_cost for entry in entries]

    # pagination
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


def add_entry(request):
    form, response = handle_entry_form(request)
    if response:
        return response

    context = {
        'form': form,
    }

    return render(request, 'calculator/add_entry.html', context=context)

def settings(request):
    return render(request, 'calculator/settings.html')