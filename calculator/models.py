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
    weather = models.CharField(max_length=22, verbose_name='Погода')
    morning_data_charge = models.IntegerField(verbose_name='Ранковий рівень заряду')
    morning_data_price = models.FloatField(verbose_name='Вартість використаної енергії на ранок')
    afternoon_data_charge = models.IntegerField(verbose_name='Денний рівень заряду', default=0)
    afternoon_data_price = models.FloatField(verbose_name='Вартість використаної енергії на день', default=0)
    evening_data_charge = models.IntegerField(verbose_name='Вечірній рівень заряду')
    evening_data_price = models.FloatField(verbose_name='Вартість використаної енергії на вечір')
    full_day_power = models.FloatField(blank=True, verbose_name='Вироблена потужність за день')
    full_day_cost = models.FloatField(blank=True, null=True, verbose_name='Вартість виробленої енергії за день')
    power_tariff = models.FloatField(verbose_name='Вартість за Кв', default='4.32')

    def _calculate_full_day_power(self):
        try:
            if self.afternoon_data_charge > 0:
                if self.afternoon_data_charge < self.evening_data_charge:
                    return (self.evening_data_charge - self.morning_data_charge) * 20.48 + (
                            (self.evening_data_price - self.morning_data_price) / 43.2) * 10000
                # if self.afternoon_data_charge > self.evening_data_charge:
                #     watt_error = (self.afternoon_data_charge - self.evening_data_charge) * 20.48
                #     return ((((self.evening_data_price - self.afternoon_data_price) * 100) / 43.2) * 100) - watt_error
                if self.afternoon_data_charge > self.evening_data_charge:
                    if 10 < self.afternoon_data_charge - self.morning_data_charge < 50:
                        return 100
                    if self.afternoon_data_charge - self.morning_data_charge < 10:
                        return 200
            if self.afternoon_data_charge == 0:
                if self.morning_data_charge < self.evening_data_charge:
                    return ((self.evening_data_charge - self.morning_data_charge) - 6) * 20.48 + (
                            ((self.evening_data_price - self.morning_data_price) - 0.60) / 43.2) * 10000
                if self.morning_data_charge < self.evening_data_charge:
                    if self.evening_data_price - self.morning_data_price == 0:
                        return (self.evening_data_charge - self.morning_data_charge) * 20.48
                    if self.evening_data_price - self.morning_data_price == 0:
                        return (self.evening_data_charge - self.morning_data_charge) * 20.48  + (
                            ((self.evening_data_price - self.morning_data_price) - 0.60) / 43.2) * 10000
                # return (((self.evening_data_price - self.morning_data_price) - 0.60) / 43.2) * 10000
                if self.morning_data_charge > self.evening_data_charge:
                    if 10 < self.morning_data_charge - self.evening_data_charge < 50:
                        return 100
                    if self.morning_data_charge - self.evening_data_charge < 10:
                        return 200
                    # return ((self.evening_data_charge - self.morning_data_charge) - 6) * 20.48 + (
                    #         ((self.evening_data_price - self.morning_data_price) - 0.60) / 43.2) * 10000
        except(TypeError, ZeroDivisionError):
            return 0.0


    def _calculate_full_day_cost(self):
        try:
            if self.afternoon_data_price > 0:
                if self.afternoon_data_charge < self.evening_data_charge:
                    return (((self.evening_data_charge - self.afternoon_data_charge) * 20.48 + (
                            ((self.evening_data_price - self.afternoon_data_price) * 100) / 43.2) * 100) / 1000) * 4.32
                # if self.afternoon_data_charge > self.evening_data_charge:
                #     if 10 < self.evening_data_charge - self.morning_data_charge < 30:
                #         return 0.999792
                #     if self.evening_data_charge - self.morning_data_charge < 10:
                #         return 1.99584
                if self.afternoon_data_charge > self.evening_data_charge:
                    if 10 < self.afternoon_data_charge - self.evening_data_charge < 50:
                        return 4.32 / 5
                    if self.morning_data_charge - self.evening_data_charge < 10:
                        return 4.32 / 10
                    # cost_error = (self.afternoon_data_charge - self.evening_data_charge) * 20.48
                    # if cost_error < 100:
                    #     return (((((
                    #                        self.evening_data_price - self.afternoon_data_price) * 100) / 43.2) * 100) / 1000) * 4.32 - (
                    #             (cost_error / 1000) * 4.32)
                    # if cost_error >= 100:
                    #     return (((((
                    #                        self.evening_data_price - self.afternoon_data_price) * 100) / 43.2) * 100) / 1000) * 4.32 - (
                    #             (cost_error / 100) * 4.32)
                    # return 0
            if self.afternoon_data_price == 0:
                if self.morning_data_charge > self.evening_data_charge:
                    if 10 < self.morning_data_charge - self.evening_data_charge < 50:
                        return 0.43
                    if self.morning_data_charge - self.evening_data_charge < 10:
                        return 0.86
                if self.morning_data_charge < self.evening_data_charge:
                    # return ((((self.evening_data_price - (self.morning_data_price + 0.60)) / 43.2) * 100) / 1000) * 4.32
                    return (((self.evening_data_charge - (self.morning_data_charge - 6)) * 20.48 + (
                            (self.evening_data_price - (self.morning_data_price + 0.60)) / 43.2) * 100) / 1000) * 4.32
                if self.evening_data_price - self.morning_data_price == 0:
                    return (((self.evening_data_charge - self.morning_data_charge) * 20.48) / 1000) * 4.32
        except(TypeError, ZeroDivisionError):
            return 0.0


    @classmethod
    def total_generated_power(cls):
        return cls.objects.aggregate(total=models.Sum('full_day_power'))['total'] or 0


    @classmethod
    def total_cost_power(cls):
        return cls.objects.aggregate(total=models.Sum('full_day_cost'))['total'] or 0


    def save(self, *args, **kwargs):
        calculated_power = self._calculate_full_day_power()
        self.full_day_power = calculated_power

        calculated_cost = self._calculate_full_day_cost()
        self.full_day_cost = calculated_cost

        super().save(*args, **kwargs)
