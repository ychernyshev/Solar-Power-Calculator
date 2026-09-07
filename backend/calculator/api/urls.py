# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView

from calculator.api.views import (DataEntryViewSet,
                                  CurrentTariffViewSet,
                                  StatsViewApiView,
                                  CurrentMothStatsApiView,
                                  WeatherConditionViewSet,
                                  SolarForecastAPIView,
                                  SolarComparisonAPIView,
                                  WeatherDataViewSet,
                                  SolarMonthAnalyticsAPIView,
                                  DifferenceMonthsStatsApiView,
                                  SolarForecastRecordViewSet,
                                  process_client_weather,
                                  SolarYearAnalyticsAPIView,
                                  get_user_profile,
                                  PanelsArrayViewSet,
                                  DataExportView,
                                  get_timezone_by_coords,
                                  UserProfileSettingsAPIView,
                                  get_weather_day_data,
                                  SystemEventAPIView,
                                  CalculatorDateRangeView, )

router = DefaultRouter()
router.register(r'entries', DataEntryViewSet, basename='entries')
router.register(r'weather-conditions', WeatherConditionViewSet, basename='weather-conditions')
router.register(r'forecast/details', WeatherDataViewSet, basename='forecast-details')
router.register('sunrise-sunset-time', SolarForecastRecordViewSet, basename='sunrise-sinset-time')
router.register(r'panels', PanelsArrayViewSet, basename='panels')
# DEPRECATED
# router.register(r'station_coordinates', GeolocationViewSet, basename='station_coordinated')
# router.register(r'user_timezone', UserTimezoneViewSet, basename='user_timezone')
# router.register(r'user_language', UserLanguageViewSet, basename='user_language')
# router.register(r'user_currency', UserCurrencyViewSet, basename='user_currency')

urlpatterns = [
    path('', include(router.urls)),
    path('user-profile/', get_user_profile, name='user-profile'),
    path('current-tariff/', CurrentTariffViewSet.as_view({'get': 'retrieve'}), name='current-tariff'),
    path('stats/', StatsViewApiView.as_view(), name='stats'),
    path('current_month_stats/', CurrentMothStatsApiView.as_view(), name='current_month_stats'),
    path('difference_months_stats/', DifferenceMonthsStatsApiView.as_view(), name='difference_months_stats'),
    path('forecast/', SolarForecastAPIView.as_view(), name='forecast'),
    path('power_generation_month_analytics/', SolarMonthAnalyticsAPIView.as_view(), name='month_analytics'),
    path('power_generation_year_analytics/', SolarYearAnalyticsAPIView.as_view(), name='year_analytics'),
    path('forecast/comparison/', SolarComparisonAPIView.as_view(), name='comparison'),
    path('data-export/', DataExportView.as_view(), name='data-export'),
    # path('data-export/', data_export_view, name='data-export'),
    path('process_weather/', process_client_weather, name='process_client_weather'),
    path('current_day_weather/', get_weather_day_data, name='current_day_weather_data'),
    path('get_timezone/', get_timezone_by_coords, name='get_timezone'),
    path('user_settings/', UserProfileSettingsAPIView.as_view(), name='user-settings'),
    path('system_event/', SystemEventAPIView.as_view(), name='system_event'),
    path('date_range/', CalculatorDateRangeView.as_view(), name='date_range'),
]
