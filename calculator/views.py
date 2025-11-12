from django.shortcuts import render
from django.template.context_processors import request


# Create your views here.
def index(request):
    return render(request, 'calculator/index.html')


def add_entry(request):
    return render(request, 'calculator/add_entry.html')