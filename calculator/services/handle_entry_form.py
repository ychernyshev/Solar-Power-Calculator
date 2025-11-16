from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from calculator.forms import AddEntryForm
from calculator.models import DataEntryLineModel

def handle_entry_form(request):
    if request.method == 'POST':
        form = AddEntryForm(request.POST)
        if form.is_valid():
            DataEntryLineModel.objects.create(**form.cleaned_data)
            messages.success(request, 'New data has been saved')
            return form, HttpResponseRedirect(reverse('calculator:dashboard'))
    else:
        form = AddEntryForm()

    return form, None
