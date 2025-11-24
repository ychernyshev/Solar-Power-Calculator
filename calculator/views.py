from pyexpat.errors import messages
from django.contrib import messages

from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from calculator.services.handle_entry_form import handle_entry_form
from calculator.models import DataEntryLineModel, CurrentTariffModel
from calculator.forms import TariffUpdateForm


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
    tariff_instance = CurrentTariffModel.load()

    if request.method == 'POST':
        form = TariffUpdateForm(request.POST, instance=tariff_instance)
        if form.is_valid():
            form.save()
            messages.success(request, f'The power tariff has been updated to {tariff_instance.power_tariff:.2f} ₴')
            return HttpResponseRedirect(reverse('calculator:settings'))
    else:
        form = TariffUpdateForm(instance=tariff_instance)

    context = {
        'form': form,
        'current_tariff': tariff_instance.power_tariff,
    }

    return render(request, 'calculator/settings.html', context=context)
