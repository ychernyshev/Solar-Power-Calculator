from datetime import datetime

from django import forms


class CurrentDate(forms.DateInput):
    current_date = 'date'


class AddEntryForm(forms.Form):
    date = forms.DateField(widget=CurrentDate(attrs={
        'class': 'form-control',
    }),
        initial=datetime.today()
    )
    power = forms.ChoiceField(label='', widget=forms.Select(
        attrs={
            'class': 'form-control',
        }))
    weather = forms.CharField(label='', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }
    ))
    morning_data_charge = forms.IntegerField(label='', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Morning charge level in %',
        }
    ))
    morning_data_price = forms.FloatField(label='', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Morning charge level in %'
        }
    ))
    afternoon_data_charge = forms.IntegerField(label='', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Afternoon charge level in %',
        }
    ))
    afternoon_data_price = forms.FloatField(label='', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Afternoon charge level in %'
        }
    ))
    evening_data_charge = forms.IntegerField(label='', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Evening charge level in %',
        }
    ))
    evening_data_price = forms.FloatField(label='', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Evening charge level in %'
        }
    ))
    all_day_power = forms.IntegerField(label='', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'All-day generation'
        }
    ))
    all_day_cost = forms.FloatField(label='', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'All-day cost'
        }
    ))
