from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.context_processors import request
from django.urls import reverse

from calculator.forms import AddEntryForm
from calculator.models import DataEntryLineModel


# Create your views here.
def index(request):
    return render(request, 'calculator/index.html')


def add_entry(request):
    if request.method == 'POST':
        form = AddEntryForm(request.POST)
        if form.is_valid():
            DataEntryLineModel.objects.create(**form.cleaned_data)
            messages.success(request, 'New data hes been saved')

            return HttpResponseRedirect(reverse('calculator:dashboard'))
    else:
        form = AddEntryForm()

    context = {
        'form': form,
    }

    return render(request, 'calculator/add_entry.html', context=context)