from django.contrib import admin
from django.utils.html import format_html

from .models import DataEntryLineModel


# Register your models here.
@admin.register(DataEntryLineModel)
class DataEntryLineAdmin(admin.ModelAdmin):
    list_display = ['date', 'display_power', 'weather',
                    'display_morning_charge', 'display_morning_price',
                    'display_afternoon_charge', 'display_afternoon_price',
                    'display_evening_charge', 'display_evening_price',
                    'display_full_day_power', 'display_full_day_cost', 'display_power_tariff']


    def display_power(self,obj):
        return format_html('{}Вт', obj.power)

    display_power.short_description = 'Потужність системи'


    def display_morning_charge(self, obj):
        return format_html('{}%', obj.morning_data_charge)

    display_morning_charge.short_description = 'Ранковий рівень заряду'


    def display_afternoon_charge(self, obj):
        return format_html('{}%', obj.afternoon_data_charge)

    display_afternoon_charge.short_description = 'Денний рівень заряду'


    def display_evening_charge(self, obj):
        return format_html('{}%', obj.evening_data_charge)

    display_evening_charge.short_description = 'Вечірній рівень заряду'


    def display_morning_price(self, obj):
        return format_html('{}₴', obj.morning_data_price)

    display_morning_price.short_description = 'Вартість використаної енергії на ранок'


    def display_afternoon_price(self, obj):
        return format_html('{}₴', obj.afternoon_data_price)

    display_afternoon_price.short_description = 'Вартість використаної енергії за день'


    def display_evening_price(self, obj):
        return format_html('{}₴', obj.evening_data_price)

    display_evening_price.short_description = 'Вартість використаної енергії на вечір'


    def display_full_day_cost(self, obj):
        formatted_tariff = f"{obj.full_day_cost:.2f}"
        return format_html('{}₴', formatted_tariff)

    display_full_day_cost.short_description = 'Вартість виробленої енергії за день'


    def display_full_day_power(self,obj):
        formatted_power = f"{obj.full_day_power:.2f}"
        return format_html('{}Кв', formatted_power)

    display_full_day_power.short_description = 'Вироблена потужність за день'


    def display_power_tariff(self, obj):
        return format_html('{}₴', obj.power_tariff)

    display_power_tariff.short_description = 'Вартість за Кв'