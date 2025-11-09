from django.db import models
from django.db.models.expressions import result


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
    full_day_power = models.FloatField(blank=True, verbose_name='Вироблена потужність за день')
    full_day_cost = models.FloatField(blank=True, verbose_name='Вартість виробленої енергії за день')
    power_tariff = models.FloatField(verbose_name='Вартість за Кв', default='4.32')

    def _calculate_full_day_power(self):
        try:
            if self.afternoon_data_charge > 0:
                return (self.afternoon_data_charge - self.evening_data_charge) * 20.48 + (
                            (self.afternoon_data_price - self.evening_data_price) / 43.2) * 100
            if self.afternoon_data_charge == 0:
                return((self.morning_data_charge - 6) - self.evening_data_charge) * 20.48 + (
                        ((self.morning_data_price + 0.60) - self.evening_data_price) / 43.2) * 100
        except(TypeError, ZeroDivisionError):
            return 0.0


    def _calculate_full_day_cost(self):
        try:
            if self.afternoon_data_price > 0:
                return (((self.afternoon_data_charge - self.evening_data_charge) * 20.48 + (
                            (self.afternoon_data_price - self.evening_data_price) / 43.2) * 100) / 1000) * 4.32
            if self.afternoon_data_price == 0:
                return ((((self.morning_data_charge - 6) - self.evening_data_charge) * 20.48 + (
                        ((self.morning_data_price + 0.60) - self.evening_data_price) / 43.2) * 100) / 1000) * 4.32
        except(TypeError, ZeroDivisionError):
            return 0.0


    def save(self, *args, **kwargs):
        calculated_power = self._calculate_full_day_power()
        self.full_day_power = calculated_power

        calculated_cost = self._calculate_full_day_cost()
        self.full_day_cost = calculated_cost

        super().save(*args, **kwargs)


