from django.db import models
from django.db.models import Sum


# ====================================================================
# MODEL 1: SINGLETON FOR CURRENT TARIFF
# ====================================================================

class CurrentTariffModel(models.Model):
    power_tariff = models.FloatField(verbose_name='Актуальна вартість за Кв', default=4.32)
    last_updated = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')

    class Meta:
        verbose_name = 'Актуальний Тариф'
        verbose_name_plural = 'Актуальний Тариф'

    def __str__(self):
        return f"Актуальний тариф: {self.power_tariff} UAH/Кв"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        try:
            return cls.objects.get(pk=1)
        except cls.DoesNotExist:
            return cls.objects.create(pk=1)


# ====================================================================
# MODEL 2: ENTRIES
# ====================================================================

class DataEntryLineModel(models.Model):
    # --- КОНСТАНТИ ---
    POWER = [
        ('200', '200'), ('400', '400'), ('600', '600'), ('800', '800'),
    ]

    UNIT_CONVERSION_FACTOR = 20.48  # Коефіцієнт перетворення заряду в потужність
    CHARGE_DIFFERENCE_THRESHOLD = 10  # Порогова різниця заряду
    MORNING_CORRECTION_CHARGE = 6  # Корекція ранкового заряду
    MORNING_CORRECTION_PRICE = 0.6  # Корекція ранкової ціни

    date = models.DateField(verbose_name='Дата')
    power = models.CharField(choices=POWER, max_length=3, default='600', verbose_name='Потужність системи')
    weather = models.ManyToManyField('WeatherCondition', db_index=True, related_name='weather', verbose_name='Погода')
    morning_data_charge = models.IntegerField(verbose_name='Ранковий рівень заряду')
    morning_data_price = models.FloatField(verbose_name='Вартість використаної енергії на ранок')
    afternoon_data_charge = models.IntegerField(verbose_name='Денний рівень заряду', default=0)
    afternoon_data_price = models.FloatField(verbose_name='Вартість використаної енергії на день', default=0)
    evening_data_charge = models.IntegerField(verbose_name='Вечірній рівень заряду')
    evening_data_price = models.FloatField(verbose_name='Вартість використаної енергії на вечір')
    full_day_power = models.FloatField(blank=True, verbose_name='Вироблена потужність за день')
    full_day_cost = models.FloatField(blank=True, null=True, verbose_name='Вартість виробленої енергії за день')
    power_tariff = models.FloatField(verbose_name='Вартість за Кв')

    def _calculate_power_delta_based_on_price(self, start_cost, end_cost):
        price_diff = end_cost - start_cost

        # Look like: round((((evening_cost - morning_cost) * 100) / TARIFF) * 100, 2)
        if self.power_tariff == 0:
            return 0

        # Look like: round((((evening_cost - morning_cost) * 100) / TARIFF) * 100, 2)
        return round(((price_diff * 100) / self.power_tariff) * 100, 2)

    def _handle_charge_difference(self, charge_diff):
        """This calculates when the solar charge decreased (afternoon > evening or morning > evening)."""
        if charge_diff <= self.CHARGE_DIFFERENCE_THRESHOLD:
            return 200
        else:
            return 100

    # def _calculate_full_day_power(self):
    #     try:
    #         # 1. Scenario: 0 energy generation during the day
    #         if self.morning_data_charge == self.afternoon_data_charge == self.evening_data_charge == 0:
    #             return 0
    #
    #         # 2. Scenario: There is a daytime charge, and it is smaller than the evening charge
    #         if 0 < self.afternoon_data_charge < self.evening_data_charge:
    #             charge_diff = self.evening_data_charge - self.afternoon_data_charge
    #             base_power = charge_diff * self.UNIT_CONVERSION_FACTOR
    #
    #             # processing constants under the same low-light scenarios
    #             if self.afternoon_data_price == self.evening_data_price:
    #                 return base_power
    #             else:
    #                 delta_power = self._calculate_power_delta_based_on_price(
    #                     self.afternoon_data_price, self.evening_data_price)
    #                 return base_power + delta_power
    #
    #         # 3. Scenario: The daytime solar charge is greater than the evening charge.
    #         if self.afternoon_data_charge > 0 and self.afternoon_data_charge > self.evening_data_charge:
    #             charge_diff = self.afternoon_data_charge - self.evening_data_charge
    #             return self._handle_charge_difference(charge_diff)
    #
    #         # 4. Scenario: The daytime solar charge is equal to 0 (afternoon_data_charge == 0)
    #         if self.afternoon_data_charge == 0:
    #
    #             # 4.1. Solar charge is growing (morning < evening)
    #             if self.morning_data_charge < self.evening_data_charge:
    #                 charge_diff = self.evening_data_charge - self.morning_data_charge - self.MORNING_CORRECTION_CHARGE
    #                 base_power = charge_diff * self.UNIT_CONVERSION_FACTOR
    #
    #                 price_start = self.morning_data_price + self.MORNING_CORRECTION_PRICE
    #                 delta_power = self._calculate_power_delta_based_on_price(
    #                     price_start, self.evening_data_price)
    #                 return base_power + delta_power
    #
    #             # 4.2. Solar charge is falling (morning > evening)
    #             elif self.morning_data_charge > self.evening_data_charge:
    #                 charge_diff = self.morning_data_charge - self.evening_data_charge
    #                 return self._handle_charge_difference(charge_diff)
    #
    #             # 4.3. Solar Charge is the same (morning == evening)
    #             elif self.morning_data_charge == self.evening_data_charge:
    #                 return (self.evening_data_charge - self.afternoon_data_charge) * self.UNIT_CONVERSION_FACTOR
    #
    #         # 5. Default scenario (if no one condition is true)
    #         return 0
    #
    #     except (TypeError, ZeroDivisionError):
    #         return 0

    # def _calculate_full_day_cost(self):
    #     try:
    #         # 1. 0 energy generation during the day.
    #         if self.morning_data_charge == self.afternoon_data_charge == self.evening_data_charge == 0:
    #             return 0
    #
    #         # Function that returns the base cost from the charge difference
    #         def get_base_cost(charge_diff):
    #             return ((charge_diff * self.UNIT_CONVERSION_FACTOR) / 1000) * self.power_tariff
    #
    #         # 2. Scenario: There is a daytime charge, and it is smaller than the evening charge
    #         if 0 < self.afternoon_data_charge < self.evening_data_charge:
    #             charge_diff = self.evening_data_charge - self.afternoon_data_charge
    #             base_cost = get_base_cost(charge_diff)
    #
    #             if self.afternoon_data_price == self.evening_data_price:
    #                 return base_cost
    #             else:
    #                 return base_cost + (self.evening_data_price - self.afternoon_data_price)
    #
    #         # 3. Scenario: The daytime solar charge is greater than the evening charge
    #         if 0 < self.afternoon_data_charge > self.evening_data_charge:
    #             charge_diff = self.afternoon_data_charge - self.evening_data_charge
    #
    #             if charge_diff <= self.CHARGE_DIFFERENCE_THRESHOLD:
    #                 return 0.86
    #             else:
    #                 return 0.43
    #
    #         # 4. Scenario: The daytime solar charge is equal to 0 (afternoon_data_charge == 0)
    #         if self.afternoon_data_price == 0:
    #
    #             # 4.1. Solar charge is growing (morning < evening)
    #             if self.morning_data_charge < self.evening_data_charge:
    #                 charge_diff = self.evening_data_charge - self.morning_data_charge - self.MORNING_CORRECTION_CHARGE
    #                 base_cost = get_base_cost(charge_diff)
    #
    #                 price_diff = self.evening_data_price - (self.morning_data_price + self.MORNING_CORRECTION_PRICE)
    #                 return base_cost + price_diff
    #
    #             # 4.2. Solar Charge is the same (morning == evening)
    #             elif self.morning_data_charge > self.evening_data_charge:
    #                 charge_diff = self.morning_data_charge - self.evening_data_charge
    #                 if charge_diff <= self.CHARGE_DIFFERENCE_THRESHOLD:
    #                     return 0.86
    #                 else:
    #                     return 0.43
    #
    #             # 4.3. Solar Charge is the same (morning == evening)
    #             elif self.morning_data_charge == self.evening_data_charge:
    #                 charge_diff = self.evening_data_charge - self.afternoon_data_charge
    #                 return get_base_cost(charge_diff)
    #
    #         # 5. Default scenario (if no one condition is true)
    #         return 0
    #
    #     except (TypeError, ZeroDivisionError):
    #         return 0

    def _calculate_full_day_power(self):
        try:
            if self.morning_data_charge == self.afternoon_data_charge == self.evening_data_charge == 0:
                return 0
            if self.afternoon_data_price == self.evening_data_price or self.morning_data_price == self.evening_data_price:
                return (self.evening_data_charge - self.afternoon_data_charge) * 20.48
            if 0 < self.afternoon_data_charge < self.evening_data_charge:
                return (self.evening_data_charge - self.afternoon_data_charge) * 20.48 + round(
                    (((self.evening_data_price - self.afternoon_data_price) * 100) / 43.2) * 100, 2)
            if 0 < self.afternoon_data_charge > self.evening_data_charge:
                if self.afternoon_data_charge - self.evening_data_charge <= 10:
                    return 200
                if self.afternoon_data_charge - self.afternoon_data_charge > 10:
                    return 100
            if self.afternoon_data_charge == 0:
                if self.morning_data_charge < self.evening_data_charge:
                    return (self.evening_data_charge - self.morning_data_charge - 6) * 20.48 + round(
                        (((self.evening_data_price - self.morning_data_price - .6) * 100) / 43.2) * 100, 2)
                if self.morning_data_charge - self.evening_data_charge <= 10:
                    return 200
                if self.morning_data_charge - self.evening_data_charge > 10:
                    return 100
            return 0.1
        except(TypeError, ZeroDivisionError):
            return 0.0

    def _calculate_full_day_cost(self):
        try:
            if self.morning_data_charge == self.afternoon_data_charge == self.evening_data_charge == 0:
                return 0.0
            if self.afternoon_data_price == self.evening_data_price or self.morning_data_price == self.evening_data_price:
                return (((self.evening_data_charge - self.afternoon_data_charge) * 20.48) / 1000) * 4.32
            if 0 < self.afternoon_data_charge < self.evening_data_charge:
                return (((self.evening_data_charge - self.afternoon_data_charge) * 20.48) / 1000) * 4.32 + (
                        self.evening_data_price - self.afternoon_data_price)
            if 0 < self.afternoon_data_charge > self.evening_data_charge:
                if self.afternoon_data_charge - self.evening_data_charge <= 10:
                    return 0.86
                if self.afternoon_data_charge - self.evening_data_charge > 10:
                    return 0.43
            if self.afternoon_data_price == 0:
                if self.morning_data_charge < self.evening_data_charge:
                    return (((self.evening_data_charge - self.morning_data_charge - 6) * 20.48) / 1000) * 4.32 + (
                            self.evening_data_price - self.morning_data_price - 0.6)
                if self.morning_data_charge - self.evening_data_charge <= 10:
                    return 0.86
                if self.morning_data_charge - self.evening_data_charge > 10:
                    return 0.43
            return 0.1
        except(TypeError, ZeroDivisionError):
            return 0.0

    def get_empty_day_message(self):
        if self.morning_data_charge == self.afternoon_data_charge == self.evening_data_charge == 0:
            return '0% - 0.0 UAH'
        return None

    @classmethod
    def total_generated_power(cls):
        return cls.objects.aggregate(total=Sum('full_day_power'))['total'] or 0

    @classmethod
    def total_cost_power(cls):
        return cls.objects.aggregate(total=Sum('full_day_cost'))['total'] or 0

    def save(self, *args, **kwargs):
        if not self.pk:
            current_tariff_obj = CurrentTariffModel.load()
            self.power_tariff = current_tariff_obj.power_tariff

        self.full_day_power = self._calculate_full_day_power()
        self.full_day_cost = self._calculate_full_day_cost()

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date']
        verbose_name = 'entry'
        verbose_name_plural = 'Entries'


class WeatherCondition(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
