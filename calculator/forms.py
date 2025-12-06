from datetime import date

from django import forms

from calculator.models import CurrentTariffModel, WeatherCondition


class CurrentDate(forms.DateInput):
    input_type = 'date'


class AddEntryForm(forms.Form):
    date = forms.DateField(widget=CurrentDate(attrs={
        'class': 'form-control',
    }),
        initial=date.today()
    )
    power = forms.ChoiceField(label='',
                              choices=[('200', '200'),
                                       ('400', '400'),
                                       ('600', '600'),
                                       ('800', '800'), ],
                              widget=forms.Select(
                                  attrs={
                                      'class': 'form-control',
                                      'value': '600',
                                  }))
    weather = forms.ModelMultipleChoiceField(label='',
                                             queryset=WeatherCondition.objects.all(),
                                                 widget=forms.SelectMultiple(
                                                 attrs={
                                                     'class': 'form-control',
                                                 }
                                             ))
    morning_data_charge = forms.IntegerField(label='', min_value=0, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter charge level here',
        }
    ))
    morning_data_price = forms.FloatField(label='', min_value=0, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter price here'
        }
    ))
    afternoon_data_charge = forms.IntegerField(label='', min_value=0, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter charge level here',
            'value': 0,
        }
    ))
    afternoon_data_price = forms.FloatField(label='', min_value=0, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter price here',
            'value': 0,
        }
    ))
    evening_data_charge = forms.IntegerField(label='', min_value=0, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter charge level here',
        }
    ))
    evening_data_price = forms.FloatField(label='', min_value=0, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter price here'
        }
    ))


class TariffUpdateForm(forms.ModelForm):
    power_tariff = forms.FloatField(label='', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
        }
    ))

    class Meta:
        model = CurrentTariffModel
        fields = ['power_tariff']
