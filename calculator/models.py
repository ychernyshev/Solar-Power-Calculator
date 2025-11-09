from django.db import models


# Create your models here.
class DataEntryLineModel(models.Model):
    POWER = [
        ('200', '200'),
        ('400', '400'),
        ('600', '600'),
        ('800', '800'),
    ]

    date = models.DateField(default=False)
    power = models.CharField(choices=POWER, max_length=3, default='600')
    weather = models.CharField(max_length=20)
    morning_data_charge = models.IntegerField()
    morning_data_price = models.FloatField()
    afternoon_data_charge = models.IntegerField()
    afternoon_data_price = models.FloatField()
    evening_data_charge = models.IntegerField()
    evening_data_price = models.FloatField()
    full_day_power = models.FloatField()
    full_day_cost = models.FloatField()
    power_tariff = models.FloatField()
    