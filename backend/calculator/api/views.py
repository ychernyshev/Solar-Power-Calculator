# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import os
from calendar import monthrange
from datetime import datetime, date, timedelta

import requests
from django.db.models import Min, Max
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from timezonefinder import TimezoneFinder

from calculator.api.serializers import (
    DataEntrySerializer,
    CurrentTariffSerializer,
    WeatherConditionSerializer,
    WeatherDataSerializer,
    SolarForecastRecordSerializer,
    PanelsArraySerializer,
    UserProfileSettingsSerializer,
    SystemEventSerializer, )
from calculator.models import (
    DataEntryLineModel,
    CurrentTariffModel,
    WeatherConditionModel,
    SolarForecastRecordModel,
    WeatherDataModel,
    PanelsArrayModel,
    UserProfileSettingsModel,
    SystemEventModel, )
from calculator.services.PanelPowerCalculationService import PanelPowerCalculationService
from calculator.services.data_export import export_data_logic
from calculator.services.data_import import import_data_logic
from calculator.services.weather_service import WeatherForecastService

tf = TimezoneFinder()


@csrf_exempt
@permission_classes([IsAuthenticated])
def get_timezone_by_coords(request):
    if request.method == 'GET':
        lat = float(request.GET.get('lat'))
        lon = float(request.GET.get('lon'))
        tz = tf.timezone_at(lng=lon, lat=lat) or "UTC"
        return JsonResponse({'timezone': tz})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    return Response({'username': request.user.username})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_client_weather(request):
    try:
        weather_data = request.data
        service = WeatherForecastService()
        result_dict = service.get_solar_forecast(weather_data, user=request.user)
        return Response({"status": "success", "data": result_dict})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)


# CURRENT DAY WEATHER
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_weather_day_data(request):
    today = timezone.localtime().date()
    records = WeatherDataModel.objects.filter(timestamp__date=today).order_by('timestamp')

    result = [
        {
            "time": rec.timestamp.isoformat(),
            "shortwave_radiation": rec.shortwave_radiation,
            "weather_code": rec.condition_code,
            "temperature": rec.temperature,
        }
        for rec in records
    ]
    return Response({"status": "success", "data": result})


# @csrf_exempt
# def process_client_weather(request):
#     if request.method == 'POST':
#         try:
#             weather_data = json.loads(request.body)
#             service = WeatherForecastService()
#
#             result_dict = service.get_solar_forecast(weather_data)
#
#             return JsonResponse(result_dict)
#
#         except json.JSONDecodeError:
#             return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
#         except Exception as e:
#             print(f"Error in process_client_weather: {e}")
#             return JsonResponse({"status": "error", "message": str(e)}, status=500)


def current_month():
    return datetime.now().month


class PanelsArrayViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PanelsArraySerializer

    def get_queryset(self):
        return PanelsArrayModel.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DataExportView(APIView):
    def get(self, request):
        return export_data_logic(request)

# @permission_classes([IsAuthenticated])
# class DataExportView(APIView):
#     def get(self, request):
#         if not request.user.is_authenticated:
#             return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
#
#         entries = DataEntryLineModel.objects.filter(user_id=request.user.id).order_by('date')
#
#         return export_data_logic(entries)


# @api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
# def data_export_view(request):
#     print(f"DEBUG: User object: {request.user}")
#     print(f"DEBUG: Is authenticated: {request.user.is_authenticated}")
#
#     entries = DataEntryLineModel.objects.filter(user=request.user).order_by('date')
#     return export_data_logic(entries)


class DataEntryViewSet(viewsets.ModelViewSet):
    serializer_class = DataEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DataEntryLineModel.objects.filter(user=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='import')
    def import_data(self, request):
        result = import_data_logic(request.FILES.get('file'), user=request.user)
        return Response(result, status=status.HTTP_201_CREATED)


# DEPRECATED
# class DataEntryViewSet(viewsets.ModelViewSet):
#     queryset = DataEntryLineModel.objects.all().order_by('-date')
#     serializer_class = DataEntrySerializer
#
#     @action(detail=False, methods=['post'], url_path='import')
#     def import_data(self, request):
#         result = import_data_logic(request.FILES.get('file'))
#         return Response(result, status=status.HTTP_201_CREATED)


class CurrentTariffViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = CurrentTariffModel.objects.all()
    serializer_class = CurrentTariffSerializer

    def get_object(self):
        return CurrentTariffModel.load()


class StatsViewApiView(APIView):
    def get(self, request):
        return Response({
            "total_power": DataEntryLineModel.total_generated_power(),
            "total_cost": DataEntryLineModel.total_cost_power(),
        })


class CurrentMothStatsApiView(APIView):
    def get(self, request):
        entries = DataEntryLineModel.objects.filter(date__month=current_month())

        if not entries.exists():
            return Response({
                "sun_days": 0,
                "average_temperature": 0,
                "average_power": 0,
                "current_month_total_power": 0,
                "current_month_savings": 0,
                "difference_power_percentage": None,
                "is_empty": True
            }, status=200)

        return Response({
            "sun_days": DataEntryLineModel.get_count_of_sun_days(),
            "average_temperature": DataEntryLineModel.get_count_of_month_average_temperature(),
            "average_power": DataEntryLineModel.get_count_of_month_average_power(),
            "current_month_total_power": DataEntryLineModel.get_count_of_month_total_power(),
            "current_month_savings": DataEntryLineModel.get_count_of_month_total_savings(),
            "difference_power_percentage":
                DataEntryLineModel.get_power_difference(),
        })


class DifferenceMonthsStatsApiView(APIView):
    def get(self, request):
        chart_data = DataEntryLineModel.get_monthly_comparison_data()

        if not chart_data:
            return Response({
                "is_empty": True,
                "months_data": []
            }, status=200)

        return Response({
            "is_empty": False,
            "months_data": chart_data
        }, status=200)


class WeatherUpdateTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_settings = UserProfileSettingsModel.objects.get(user=request.user)

            if user_settings.latitude is None or user_settings.longitude is None:
                return Response({"error": "Coordinates not set"}, status=400)

            api_url = "https://api.open-meteo.com/v1/forecast"

            params = {
                "latitude": user_settings.latitude,
                "longitude": user_settings.longitude,
                "hourly": "shortwave_radiation,temperature_2m,weather_code,cloud_cover,relative_humidity_2m,surface_pressure,wind_speed_10m,wind_gusts_10m,wind_direction_10m",
                "daily": "sunrise,sunset",
                "wind_speed_unit": "ms",
                "timezone": "Europe/Kyiv",
                "forecast_days": 1
            }

            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            weather_data = response.json()

            service = WeatherForecastService()
            result = service.get_solar_forecast(weather_data, user=request.user)

            return Response({"status": "success", "data": result})


        except UserProfileSettingsModel.DoesNotExist:
            return Response({"error": "Settings not found"}, status=404)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=500)


# DEPRECATED
# class WeatherUpdateTaskView(APIView):
#     def get(self, request):
#         auth_header = request.headers.get('Authorization')
#         cron_secret = os.environ.get('CRON_SECRET')
#
#         if auth_header != f"Bearer {cron_secret}":
#             return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
#
#         try:
#             api_url = "https://api.open-meteo.com/v1/forecast"
#             coords = UserProfileSettingsModel.objects.first()
#
#             if not coords:
#                 return Response({"error": "No coordinates found in database"}, status=404)
#
#             params = {
#                 "latitude": coords.latitude,
#                 "longitude": coords.longitude,
#                 "hourly": "shortwave_radiation,temperature_2m,weather_code,cloud_cover,relative_humidity_2m,surface_pressure,wind_speed_10m,wind_gusts_10m,wind_direction_10m",
#                 "daily": "sunrise,sunset",
#                 "wind_speed_unit": "ms",
#                 "timezone": "Europe/Kyiv",
#                 "forecast_days": 1
#             }
#             response = requests.get(api_url, params=params, timeout=10)
#             response.raise_for_status()
#             weather_data = response.json()
#
#             service = WeatherForecastService()
#             # result = service.get_solar_forecast(weather_data)
#             result = service.get_solar_forecast(weather_data, user=None)
#
#             return Response({"status": "success", "data": result})
#         except Exception as e:
#             return Response({"status": "error", "message": str(e)}, status=500)


class WeatherConditionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WeatherConditionModel.objects.all()
    serializer_class = WeatherConditionSerializer


class SolarForecastAPIView(APIView):
    def get(self, request, *args, **kwargs):
        today = timezone.localtime(timezone.now()).date()

        record = SolarForecastRecordModel.objects.filter(date=today).first()

        if record:
            return Response({
                "status": "success",
                "predicted_total_kwh": float(record.predicted_kwh),
                "predicted_savings": float(record.predicted_savings),
                "peak_hour": record.peak_hour,
                "currency": "UAH",
                "wind_speed_10m": float(record.wind_speed_10m) if record.wind_speed_10m else 0.0,
                "wind_gusts_10m": float(record.wind_gusts_10m) if record.wind_gusts_10m else 0.0,
                "wind_direction_10m": record.wind_direction_10m or 0,
            }, status=status.HTTP_200_OK)

        return Response(
            {"status": "error", "message": "No forecast data available for today yet. Please wait for frontend sync."},
            status=status.HTTP_404_NOT_FOUND
        )


class SolarYearAnalyticsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            current_year = date.today().year

            entries = DataEntryLineModel.objects.filter(
                date__year=current_year
            ).prefetch_related('weather')

            categories = {
                "sunny": {"label": "Sunny Days", "days_count": 0, "total_power": 0.0, "total_cost": 0.0},
                "cloudy": {"label": "Cloudy Days", "days_count": 0, "total_power": 0.0, "total_cost": 0.0},
                "rain_snow": {"label": "Rain / Snow", "days_count": 0, "total_power": 0.0, "total_cost": 0.0},
                "other": {"label": "Other Weather", "days_count": 0, "total_power": 0.0, "total_cost": 0.0},
            }

            for entry in entries:
                weather_names = [w.name.lower() for w in entry.weather.all()]

                try:
                    power = float(entry.full_day_power) if entry.full_day_power is not None else 0.0
                except (TypeError, ValueError):
                    power = 0.0

                try:
                    cost = float(entry.full_day_cost) if entry.full_day_cost is not None else 0.0
                except (TypeError, ValueError):
                    cost = 0.0

                if any("sunny" in name for name in weather_names):
                    categories["sunny"]["days_count"] += 1
                    categories["sunny"]["total_power"] += power
                    categories["sunny"]["total_cost"] += cost

                elif any("cloudy" in name for name in weather_names):
                    categories["cloudy"]["days_count"] += 1
                    categories["cloudy"]["total_power"] += power
                    categories["cloudy"]["total_cost"] += cost

                elif any("rain" in name or "snow" in name for name in weather_names):
                    categories["rain_snow"]["days_count"] += 1
                    categories["rain_snow"]["total_power"] += power
                    categories["rain_snow"]["total_cost"] += cost

                else:
                    categories["other"]["days_count"] += 1
                    categories["other"]["total_power"] += power
                    categories["other"]["total_cost"] += cost

            for key in categories:
                categories[key]["total_power"] = round(categories[key]["total_power"], 2)
                categories[key]["total_cost"] = round(categories[key]["total_cost"], 2)

            response_data = {
                "year": current_year,
                "categories": categories
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Failed to calculate analytics", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SolarMonthAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    _cached_raw_weather = None

    def get(self, request, *args, **kwargs):
        try:
            today = date.today()

            try:
                year = int(request.GET.get('year', today.year))
                month = int(request.GET.get('month', today.month))
            except (ValueError, TypeError):
                year = today.year
                month = today.month

            compare_last_year = request.GET.get('compare_last_year') == 'true'
            compare_two_years_ago = request.GET.get('compare_two_years_ago') == 'true'

            start_date = date(year, month, 1)
            _, last_day = monthrange(year, month)
            end_date = date(year, month, last_day)
            total_days = last_day

            def get_month_actuals(target_year, target_month):
                s_date = date(target_year, target_month, 1)
                _, l_day = monthrange(target_year, target_month)
                e_date = date(target_year, target_month, l_day)

                qs = DataEntryLineModel.objects.filter(user=request.user, date__range=(s_date, e_date))
                data_dict = {q.date.day: round(float(q.full_day_power) / 1000.0, 2) for q in qs if
                             q.full_day_power is not None}

                return [data_dict.get(d, None) for d in range(1, total_days + 1)]

            effective_today = today if (year == today.year and month == today.month) else end_date
            if (year, month) > (today.year, today.month):
                effective_today = date(year, month, 1) - timedelta(days=1)

            actual_qs = DataEntryLineModel.objects.filter(user=request.user, date__range=(start_date, effective_today))
            actual_dict = {
                q.date.day: round(float(q.full_day_power) / 1000.0, 2)
                for q in actual_qs if q.full_day_power is not None
            }

            forecast_qs = SolarForecastRecordModel.objects.filter(date__range=(start_date, end_date))
            forecast_dict = {q.date.day: float(q.predicted_kwh) for q in forecast_qs if q.predicted_kwh is not None}

            api_forecast_dict = {}

            is_current_or_future_month = (year > today.year) or (year == today.year and month >= today.month)

            if is_current_or_future_month:
                try:
                    user_settings = UserProfileSettingsModel.objects.get(user=request.user)
                    if user_settings.latitude is not None and user_settings.longitude is not None:
                        service = WeatherForecastService()
                        raw_data = service._fetch_raw_weather_from_api(user_settings.latitude, user_settings.longitude)

                        if raw_data:
                            calibration_factor = service._calculate_calibration_factor()
                            calc_service = PanelPowerCalculationService()

                            radiation_data = raw_data.get('hourly', {}).get('shortwave_radiation', [])
                            times = raw_data.get('hourly', {}).get('time', [])

                            total_hourly_wh, _ = calc_service.get_total_forecast(
                                radiation_data, calibration_factor, request.user
                            )

                            temp_daily_wh = {}
                            for idx, time_str in enumerate(times):
                                dt = datetime.fromisoformat(time_str).date()
                                if dt.month == month and dt.year == year:
                                    if idx < len(total_hourly_wh):
                                        temp_daily_wh[dt.day] = temp_daily_wh.get(dt.day, 0.0) + total_hourly_wh[idx]

                            for day_num, total_wh in temp_daily_wh.items():
                                if total_wh > 0:
                                    api_forecast_dict[day_num] = round(total_wh / 1000.0, 2)
                except Exception as ex:
                    print(f"Error fetching live forecast in analytics: {ex}")

            labels = list(range(1, total_days + 1))
            actual_power = [actual_dict.get(d, None) if date(year, month, d) <= effective_today else None for d in
                            labels]
            forecast_power = [api_forecast_dict.get(d, forecast_dict.get(d, None)) for d in labels]

            # DEPRECATED
            # labels = []
            # actual_power = []
            # forecast_power = []

            # for day in range(1, total_days + 1):
            #     labels.append(day)
            #
            #     current_loop_date = date(year, month, day)
            #
            #     if current_loop_date <= effective_today:
            #         actual_power.append(actual_dict.get(day, None))
            #     else:
            #         actual_power.append(None)
            #
            #     if day in api_forecast_dict:
            #         forecast_power.append(api_forecast_dict[day])
            #     elif day in forecast_dict:
            #         forecast_power.append(round(forecast_dict[day], 2))
            #     else:
            #         forecast_power.append(None)

            ly_start = date(year - 1, month, 1)
            _, ly_last = monthrange(year - 1, month)
            ly_end = date(year - 1, month, ly_last)
            has_ly_data = DataEntryLineModel.objects.filter(
                user=request.user, date__range=(ly_start, ly_end), full_day_power__isnull=False
            ).exists()

            tya_start = date(year - 2, month, 1)
            _, tya_last = monthrange(year - 2, month)
            tya_end = date(year - 2, month, tya_last)
            has_tya_data = DataEntryLineModel.objects.filter(
                user=request.user, date__range=(tya_start, tya_end), full_day_power__isnull=False
            ).exists()

            result = {
                "status": "success",
                "month_name": start_date.strftime("%B"),
                "labels": labels,
                "actual_power": actual_power,
                "forecast_power": forecast_power,
                "has_last_year_data": has_ly_data,
                "has_two_years_ago_data": has_tya_data,
            }

            if compare_last_year:
                ly = year - 1
                result["last_year_label"] = f"Actual {ly}"
                result["last_year_power"] = get_month_actuals(ly, month)

            if compare_two_years_ago:
                tya = year - 2
                result["two_years_ago_label"] = f"Actual {tya}"
                result["two_years_ago_power"] = get_month_actuals(tya, month)

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# DEPRACATED
# class SolarMonthAnalyticsAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request, *args, **kwargs):
#         try:
#             today = date.today()
#             year = today.year
#             month = today.month
#
#             start_date = date(year, month, 1)
#             if month == 12:
#                 end_date = date(year + 1, 1, 1) - timedelta(days=1)
#             else:
#                 end_date = date(year, month + 1, 1) - timedelta(days=1)
#
#             total_days = end_date.day
#
#             actual_qs = DataEntryLineModel.objects.filter(user=request.user, date__range=(start_date, today))
#             actual_dict = {
#                 q.date.day: round(float(q.full_day_power) / 1000.0, 2)
#                 for q in actual_qs if q.full_day_power is not None
#             }
#
#             forecast_qs = SolarForecastRecordModel.objects.filter(date__range=(start_date, today))
#             forecast_dict = {q.date.day: float(q.predicted_kwh) for q in forecast_qs if q.predicted_kwh is not None}
#
#             api_forecast_dict = {}
#
#             if today <= end_date:
#                 try:
#                     user_settings = UserProfileSettingsModel.objects.get(user=request.user)
#                     if user_settings.latitude is not None and user_settings.longitude is not None:
#                         service = WeatherForecastService()
#                         raw_data = service._fetch_raw_weather_from_api(user_settings.latitude, user_settings.longitude)
#
#                         if raw_data:
#                             calibration_factor = service._calculate_calibration_factor()
#                             calc_service = PanelPowerCalculationService()
#
#                             radiation_data = raw_data.get('hourly', {}).get('shortwave_radiation', [])
#                             times = raw_data.get('hourly', {}).get('time', [])
#
#                             total_hourly_wh, _ = calc_service.get_total_forecast(
#                                 radiation_data, calibration_factor, request.user
#                             )
#
#                             temp_daily_wh = {}
#                             for idx, time_str in enumerate(times):
#                                 dt = datetime.fromisoformat(time_str).date()
#                                 if dt.month == month and dt.year == year:
#                                     if idx < len(total_hourly_wh):
#                                         temp_daily_wh[dt.day] = temp_daily_wh.get(dt.day, 0.0) + total_hourly_wh[idx]
#
#                             for day_num, total_wh in temp_daily_wh.items():
#                                 if total_wh > 0:
#                                     api_forecast_dict[day_num] = round(total_wh / 1000.0, 2)
#                 except Exception as ex:
#                     print(f"Error fetching live forecast in analytics: {ex}")
#
#             labels = []
#             actual_power = []
#             forecast_power = []
#
#             for day in range(1, total_days + 1):
#                 labels.append(day)
#
#                 if day <= today.day:
#                     actual_power.append(actual_dict.get(day, None))
#                 else:
#                     actual_power.append(None)
#
#                 if day in api_forecast_dict:
#                     forecast_power.append(api_forecast_dict[day])
#                 elif day in forecast_dict:
#                     forecast_power.append(round(forecast_dict[day], 2))
#                 else:
#                     forecast_power.append(None)
#
#             result = {
#                 "status": "success",
#                 "month_name": today.strftime("%B"),
#                 "labels": labels,
#                 "actual_power": actual_power,
#                 "forecast_power": forecast_power
#             }
#
#             return Response(result, status=status.HTTP_200_OK)
#
#         except Exception as e:
#             return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# DEPRECATED
# class SolarMonthAnalyticsAPIView(APIView):
#     def get(self, request, *args, **kwargs):
#         try:
#             today = date.today()
#             year = today.year
#             month = today.month
#
#             start_date = date(year, month, 1)
#             if month == 12:
#                 end_date = date(year + 1, 1, 1) - timedelta(days=1)
#             else:
#                 end_date = date(year, month + 1, 1) - timedelta(days=1)
#
#             total_days = end_date.day
#
#             actual_qs = DataEntryLineModel.objects.filter(date__range=(start_date, today))
#             actual_dict = {
#                 q.date.day: round(float(q.full_day_power) / 1000.0, 2)
#                 for q in actual_qs if q.full_day_power is not None
#             }
#
#             forecast_qs = SolarForecastRecordModel.objects.filter(date__range=(start_date, today))
#             forecast_dict = {q.date.day: float(q.predicted_kwh) for q in forecast_qs if q.predicted_kwh is not None}
#
#             api_forecast_dict = {}
#             if today < end_date:
#                 system_factor = 3.45 * 0.23 * 0.85
#
#                 api_url = "https://api.open-meteo.com/v1/forecast"
#                 params = {
#                     "latitude": 49.8383,
#                     "longitude": 24.0232,
#                     "hourly": "shortwave_radiation",
#                     "timezone": "auto",
#                     "forecast_days": 16
#                 }
#
#                 response = requests.get(api_url, params=params, timeout=10)
#                 if response.status_code == 200:
#                     api_data = response.json()
#                     rad_data = api_data.get('hourly', {}).get('shortwave_radiation', [])
#                     times = api_data.get('hourly', {}).get('time', [])
#
#                     total_real = 0.0
#                     total_pred_db = 0.0
#
#                     for day_idx in actual_dict.keys():
#                         if day_idx in forecast_dict and forecast_dict[day_idx] > 0:
#                             total_real += actual_dict[day_idx]
#                             total_pred_db += forecast_dict[day_idx]
#
#                     calibration_factor = 1.0
#                     if total_pred_db > 0 and total_real > 0:
#                         calibration_factor = total_real / total_pred_db
#
#                     base_system_factor = 3.45 * 0.23 * 0.85
#
#                     calibrated_factor = base_system_factor * calibration_factor
#
#                     for i in range(min(len(times), len(rad_data))):
#                         if rad_data[i] is None:
#                             continue
#
#                         dt = datetime.strptime(times[i][:10], "%Y-%m-%d").date()
#
#                         if dt.month == month and dt.year == year:
#                             day_num = dt.day
#                             wh = float(rad_data[i]) * calibrated_factor
#
#                             if day_num not in api_forecast_dict:
#                                 api_forecast_dict[day_num] = 0.0
#                             api_forecast_dict[day_num] += wh
#
#                     for day_num in list(api_forecast_dict.keys()):
#                         if api_forecast_dict[day_num] <= 0:
#                             del api_forecast_dict[day_num]
#                         else:
#                             api_forecast_dict[day_num] = round(api_forecast_dict[day_num] / 1000, 2)
#
#             labels = []
#             actual_power = []
#             forecast_power = []
#
#             for day in range(1, total_days + 1):
#                 labels.append(day)
#
#                 if day <= today.day:
#                     actual_power.append(actual_dict.get(day, None))
#                 else:
#                     actual_power.append(None)
#
#                 if day in api_forecast_dict:
#                     forecast_power.append(api_forecast_dict[day])
#                 elif day in forecast_dict:
#                     forecast_power.append(round(forecast_dict[day], 2))
#                 else:
#                     forecast_power.append(None)
#
#             result = {
#                 "status": "success",
#                 "month_name": today.strftime("%B"),
#                 "labels": labels,
#                 "actual_power": actual_power,
#                 "forecast_power": forecast_power
#             }
#
#             return Response(result, status=status.HTTP_200_OK)
#
#         except Exception as e:
#             return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SolarComparisonAPIView(APIView):
    def get(self, request):
        records = SolarForecastRecordModel.objects.all()[:7]
        data = []

        for r in records:
            actual = r.get_actual_data()
            data.append({
                "date": r.date,
                "predicted": r.predicted_kwh,
                "actual": round(actual.full_day_power / 1000, 2) if actual else 0,
                "accuracy": r.accuracy_percentage,
                "savings_diff": round(actual.full_day_cost - r.predicted_savings, 2) if actual else 0
            })

        return Response(data)


class WeatherDataViewSet(viewsets.ModelViewSet):
    queryset = WeatherDataModel.objects.all()
    serializer_class = WeatherDataSerializer


class SolarForecastRecordViewSet(viewsets.ModelViewSet):
    serializer_class = SolarForecastRecordSerializer

    def get_queryset(self):
        queryset = SolarForecastRecordModel.objects.all()
        date_param = self.request.query_params.get('date')

        if date_param:
            naive_dt = parse_datetime(date_param)
            if naive_dt:
                aware_dt = timezone.make_aware(naive_dt)
                queryset = queryset.filter(date=aware_dt.date())

        return queryset.order_by('-date')


class UserProfileSettingsAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSettingsSerializer

    def get_object(self):
        obj, created = UserProfileSettingsModel.objects.get_or_create(user=self.request.user)
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        data = request.data.copy()
        new_method = data.get('receive_data_method')
        authorization_code = data.get('authorization_code')

        if new_method == 'automatic' and not instance.is_automatic_active:
            if not authorization_code:
                return Response(
                    {"authorization_code": ["Voucher code is required for automatic mode."]},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                is_valid, expires_at = self._verify_voucher_with_license_server(authorization_code, request.user)

                if not is_valid:
                    return Response(
                        {"authorization_code": ["Invalid, expired, or already used authorization code."]},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                data['is_automatic_active'] = True
                data['license_expires_at'] = expires_at

            except Exception as e:
                return Response(
                    {"error": "Licensing server error", "details": str(e)},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def _verify_voucher_with_license_server(self, authorization_code, user):
        # Activation code verification stub
        if authorization_code.startswith("AU-") and len(authorization_code) >= 25:
            # Success request imitation
            expires_at = timezone.now() + timedelta(days=365)
            return True, expires_at

        return False, None


class SystemEventAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SystemEventSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = SystemEventModel.objects.all().prefetch_related('wind_records', 'peak_records')
        date_param = self.request.query_params.get('date')

        if date_param:
            naive_dt = parse_datetime(date_param)
            if naive_dt:
                aware_dt = timezone.make_aware(naive_dt)
                queryset = queryset.filter(created_at__date=aware_dt.date())

        return queryset.order_by('-created_at')


# DEPRECATED
# class SystemEventAPIView(ListAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = SystemEventSerializer
#
#     def get_queryset(self):
#         queryset = SystemEventModel.objects.all()
#         date_param = self.request.query_params.get('date')
#
#         if date_param:
#             naive_dt = parse_datetime(date_param)
#             if naive_dt:
#                 aware_dt = timezone.make_aware(naive_dt)
#                 queryset = queryset.filter(created_at__date=aware_dt.date())
#
#         return queryset.order_by('-created_at')


# class GeolocationViewSet(viewsets.ModelViewSet):
#     queryset = GeolocationModel.objects.all()
#     serializer_class = GeolocationSerializer
#
#
# class UserTimezoneViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = UserTimezoneModel.objects.all()
#     serializer_class = UserTimezoneSerializer
#
#     def get_queryset(self):
#         return UserTimezoneModel.objects.filter(user=self.request.user)
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         obj, created = UserTimezoneModel.objects.update_or_create(
#             user=request.user,
#             defaults={'timezone': serializer.validated_data['timezone']}
#         )
#
#         status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
#         return Response(serializer.data, status=status_code)
#
#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         obj = queryset.first()
#         if not obj:
#             return Response({"timezone": ""}, status=status.HTTP_200_OK)
#         serializer = self.get_serializer(obj)
#         return Response(serializer.data)
#
#
# class UserLanguageViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = UserLanguageModel.objects.all()
#     serializer_class = UserLanguageSerializer
#
#     def get_queryset(self):
#         return UserLanguageModel.objects.filter(user=self.request.user)
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         obj, created = UserLanguageModel.objects.update_or_create(
#             user=request.user,
#             defaults={'language': serializer.validated_data['language']}
#         )
#
#         status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
#         return Response(serializer.data, status=status_code)
#
#
# class UserCurrencyViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = UserCurrencyModel.objects.all()
#     serializer_class = UserCurrencySerializer
#
#     def get_queryset(self):
#         return UserCurrencyModel.objects.filter(user=self.request.user)
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         obj, created = UserCurrencyModel.objects.update_or_create(
#             user=request.user,
#             defaults={'currency': serializer.validated_data['currency']}
#         )
#
#         status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
#         return Response(serializer.data, status=status_code)


class CalculatorDateRangeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_range = DataEntryLineModel.objects.filter(user=request.user).aggregate(
            min_date=Min('date'),
            max_date=Max('date')
        )

        return Response({
            'min_date': date_range['min_date'],
            'max_date': date_range['max_date']
        })