from django.db import models


# Create your models here.
class DataEntryLineModel(models.Model):
    POWER = [
        ('200', '200'),
        ('400', '400'),
        ('600', '600'),
        ('800', '800'),
    ]

    date = models.DateField(default=False, verbose_name='Дата')
    power = models.CharField(choices=POWER, max_length=3, default='600', verbose_name='Потужність системи')
    weather = models.CharField(max_length=20, verbose_name='Погода')
    morning_data_charge = models.IntegerField(verbose_name='Ранковий рівень заряду')
    morning_data_price = models.FloatField(verbose_name='Вартість використаної енергії на ранок')
    afternoon_data_charge = models.IntegerField(verbose_name='Денний рівень заряду')
    afternoon_data_price = models.FloatField(verbose_name='Вартість використаної енергії на день')
    evening_data_charge = models.IntegerField(verbose_name='Вечірній рівень заряду')
    evening_data_price = models.FloatField(verbose_name='Вартість використаної енергії на вечір')
    full_day_power = models.FloatField(verbose_name='Вироблена потужність за день')
    full_day_cost = models.FloatField(verbose_name='Вартість виробленої енергії за день')
    power_tariff = models.FloatField(verbose_name='Вартість за Кв')
