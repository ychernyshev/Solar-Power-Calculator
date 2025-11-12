from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('dashboard/', index, name='dashboard'),
    path('add_entry/', add_entry, name='add_entry'),
]