# SPDX-License-Identifier: AGPL-3.0-or-later
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    DataEntryLineModel,
    WeatherConditionModel,
    SolarForecastRecordModel,
    WeatherDataModel,
    PanelsArrayModel,
    SystemEventModel,
    UserProfileSettingsModel,
    PeakEventModel,
    WindEventModel,
)


# Register your models here.
@admin.register(DataEntryLineModel)
class DataEntryLineAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'display_power',
        'get_weather', 'weather_scores',
        'display_morning_charge', 'display_morning_price',
        'display_afternoon_charge', 'display_afternoon_price',
        'display_evening_charge', 'display_evening_price',
        'display_extra_power', 'display_full_day_power',
        'display_full_day_cost', 'display_power_tariff',
    ]

    def get_weather(self, obj):
        return ', '.join([item.name for item in obj.weather.all()])

    get_weather.short_description = "Погода"

    def display_power(self, obj):
        return format_html('{}Вт', obj.system_power)

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

    def display_extra_power(self, obj):
        return format_html('{}₴', obj.extra_power)

    display_extra_power.short_description = 'Приблизна потужність використана на USB'

    def display_full_day_cost(self, obj):
        formatted_tariff = f"{obj.full_day_cost:.2f}"
        return format_html('{}₴', formatted_tariff)

    display_full_day_cost.short_description = 'Вартість виробленої енергії за день'

    def display_full_day_power(self, obj):
        formatted_power = f"{obj.full_day_power:.2f}"
        return format_html('{}Вт', formatted_power)

    display_full_day_power.short_description = 'Вироблена потужність за день'

    def display_power_tariff(self, obj):
        return format_html('{}₴', obj.power_tariff)

    display_power_tariff.short_description = 'Вартість за Кв'


@admin.register(WeatherConditionModel)
class WeatherConditionAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(SolarForecastRecordModel)
class SolarForecastRecordAdmin(admin.ModelAdmin):
    list_display = ['date', 'predicted_kwh', 'predicted_savings', 'peak_hour', 'sunrise', 'sunset', 'created_at']


@admin.register(WeatherDataModel)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'temperature',
                    'cloud_cover', 'pressure',
                    'humidity', 'precipitation_prob',
                    'shortwave_radiation', 'direct_radiation',
                    'diffuse_radiation', 'surface_pressure',
                    'condition_code']


@admin.register(PanelsArrayModel)
class PanelsArrayAdmin(admin.ModelAdmin):
    list_display = ['name', 'peak_power_wh', 'area', 'angle', 'azimuth', 'efficiency', 'user']


class PeakEventInline(admin.TabularInline):
    model = PeakEventModel
    extra = 0


class WindEventInline(admin.TabularInline):
    model = WindEventModel


@admin.register(SystemEventModel)
class SystemEventAdmin(admin.ModelAdmin):
    list_display = ['date', 'payload']
    inlines = [PeakEventInline, WindEventInline]


@admin.register(UserProfileSettingsModel)
class UserProfileSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'latitude', 'longitude', 'timezone', 'language', 'currency']


@admin.register(WindEventModel)
class WindEventAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'event_time', 'category', 'daily_event', 'wind_strength', 'gust_strength', 'wind_direction', 'message', 'user']


@admin.register(PeakEventModel)
class PeakEventAdmin(admin.ModelAdmin):
    list_display = ('daily_event', 'user', 'get_formatted_hour', 'status')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('daily_event__date', 'user__username')

    @admin.display(description='Hour (24h)', ordering='peak_hour')
    def get_formatted_hour(self, obj):
        return obj.formatted_hour


# DEPRECATED
# @admin.register(GeolocationModel)
# class GeolocationAdmin(admin.ModelAdmin):
#     list_display = ['latitude', 'longitude']
#
#
# @admin.register(UserTimezoneModel)
# class UserTimezoneAdmin(admin.ModelAdmin):
#     list_display = ['user', 'timezone']
#
#
# @admin.register(UserLanguageModel)
# class UserLanguageAdmin(admin.ModelAdmin):
#     list_display = ['user', 'language']
#
#
# @admin.register(UserCurrencyModel)
# class UserCurrencyAdmin(admin.ModelAdmin):
#     list_display = ['user', 'currency']