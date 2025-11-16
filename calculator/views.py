from django.shortcuts import render

from calculator.services.handle_entry_form import handle_entry_form
from calculator.models import DataEntryLineModel


# Create your views here.
def index(request):
    entries = DataEntryLineModel.objects.all()

    form, response = handle_entry_form(request)
    if response:
        return response

    context = {
        'entries': entries,
        'form': form,
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