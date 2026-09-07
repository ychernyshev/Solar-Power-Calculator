# SPDX-License-Identifier: AGPL-3.0-or-later
import datetime
from zoneinfo import ZoneInfo

from django.core.cache import cache
from django.db.models import Model
from django.utils import timezone

from calculator.models import (
    CurrentTariffModel,
    SolarForecastRecordModel,
    WeatherDataModel,
    DataEntryLineModel,
    SystemEventModel,
    PeakEventModel,
    WindEventModel, PanelsArrayModel,
)
from calculator.services.PanelPowerCalculationService import PanelPowerCalculationService


class WeatherForecastService:
    def _get_error_response(self, tariff):
        return {
            "predicted_total_kwh": 0.0, "predicted_savings": 0.0, "hourly_forecast_wh": [0.0] * 24,
            "currency": "UAH", "peak_hour": 0, "status": "error", "tariff_used": tariff,
            "current_temp": 0.0, "weather_condition": "Unavailable", "weather_code": 0, "calibration_factor": 1.0
        }
    # 1
    # def _calculate_calibration_factor(self):
    #     today = datetime.date.today()
    #     start_date = datetime.date(today.year, today.month, 1)
    #     yesterday = today - datetime.timedelta(days=1)
    #     if yesterday < start_date:
    #         return 0.5
    #
    #     actual_qs = DataEntryLineModel.objects.filter(date__range=(start_date, yesterday))
    #     forecast_qs = SolarForecastRecordModel.objects.filter(date__range=(start_date, yesterday))
    #
    #     actual_dict = {q.date.day: float(q.full_day_power)
    #                    for q in actual_qs
    #                    if q.full_day_power is not None and q.full_day_power > 0}
    #
    #     forecast_dict = {q.date.day: float(q.predicted_kwh)
    #                      for q in forecast_qs
    #                      if q.predicted_kwh is not None}
    #
    #     total_real = 0.0
    #     total_pred = 0.0
    #
    #     for day, real_power in actual_dict.items():
    #         if day in forecast_dict:
    #             total_real = sum(actual_dict.values()) / 1000.0
    #             total_pred = sum(forecast_dict.values())
    #
    #     return (total_real / total_pred) if total_pred > 0 else 0.5
        # return 1.0

    # 2
    # def _calculate_calibration_factor(self):
    #     today = datetime.date.today()
    #     yesterday = today - datetime.timedelta(days=1)
    #     start_date = datetime.date(yesterday.year, yesterday.month, 1)
    #     if yesterday < start_date:
    #         return 1
    #
    #     actual_qs = DataEntryLineModel.objects.filter(date__range=(start_date, yesterday))
    #     forecast_qs = SolarForecastRecordModel.objects.filter(date__range=(start_date, yesterday))
    #
    #     actual_dict = {q.date.day: float(q.full_day_power)
    #                    for q in actual_qs
    #                    if q.full_day_power is not None and q.full_day_power > 0}
    #
    #     forecast_dict = {q.date.day: float(q.predicted_kwh)
    #                      for q in forecast_qs
    #                      if q.predicted_kwh is not None}
    #
    #     common_days = set(actual_dict.keys()).intersection(set(forecast_dict.keys()))
    #     if not common_days:
    #         return 1
    #
    #     total_real = sum(actual_dict[day] for day in common_days) / 1000.0
    #     total_pred = sum(forecast_dict[day] for day in common_days)
    #
    #     print(f"DEBUG CALIBRATION: total_real={total_real}, total_pred={total_pred}")
    #
    #     return (total_real / total_pred) if total_pred > 0 else 1

    #3 for last 14 days
    def _calculate_calibration_factor(self):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        start_date = yesterday - datetime.timedelta(days=14)

        actual_qs = DataEntryLineModel.objects.filter(date__range=(start_date, yesterday))
        forecast_qs = SolarForecastRecordModel.objects.filter(date__range=(start_date, yesterday))

        actual_dict = {
            q.date: float(q.full_day_power)
            for q in actual_qs
            if q.full_day_power is not None and float(q.full_day_power) > 0
        }

        forecast_dict = {
            q.date: float(q.predicted_kwh)
            for q in forecast_qs
            if q.predicted_kwh is not None
        }

        common_dates = set(actual_dict.keys()).intersection(set(forecast_dict.keys()))
        if not common_dates:
            return 1.0

        total_real = sum(actual_dict[d] for d in common_dates) / 1000.0
        total_pred = sum(forecast_dict[d] for d in common_dates)

        print(f"DEBUG CALIBRATION (Last 14 days): total_real={total_real}, total_pred={total_pred}")

        return (total_real / total_pred) if total_pred > 0 else 1.0

    def get_solar_forecast(self, data, user, current_tariff=None):
        if not data or 'hourly' not in data:
            return self._get_error_response(current_tariff)

        api_lat, api_lon = round(data.get('latitude', 0.0), 2), round(data.get('longitude', 0.0), 2)
        cache_key = f'solar_forecast_{api_lat}_{api_lon}'
        if (cached := cache.get(cache_key)): return cached

        if current_tariff is None:
            current_tariff = CurrentTariffModel.load().power_tariff

        radiation_data = data.get('hourly', {}).get('shortwave_radiation', [])
        if not radiation_data: return self._get_error_response(current_tariff)

        surface_pressure = data.get('hourly', {}).get('surface_pressure', [])

        try:
            calibration_factor = self._calculate_calibration_factor()
            print(f"DEBUG: Calibration Factor: {calibration_factor}")

            calc_service = PanelPowerCalculationService()
            total_hourly_wh, detailed_reports = calc_service.get_total_forecast(
                radiation_data, calibration_factor, user
            )

            total_hourly_wh = [h * calibration_factor for h in total_hourly_wh]

            weather_h = data.get('hourly', {})
            wmo_codes = {0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog",
                         95: "Thunderstorm"}

            current_hour = datetime.datetime.now().hour
            safe_h = min(current_hour, len(weather_h.get('temperature_2m', [])) - 1)

            temp = weather_h.get('temperature_2m', [0])[safe_h]
            code = weather_h.get('weather_code', [0])[safe_h]
            wind_dir = weather_h.get('wind_direction_10m', [0])[safe_h]

            today_day_watt = total_hourly_wh[:24] if len(total_hourly_wh) >= 24 else total_hourly_wh
            print('total_hourly_wh[:24]', total_hourly_wh[:24])
            # prepared_day_watt = (sum(today_day_watt) / 1000) * PanelsArrayModel.objects.filter(user=user).count()
            prepared_day_watt = sum(today_day_watt) / 1000.0
            today_peak_hour = today_day_watt.index(max(today_day_watt)) if today_day_watt else 0

            result_dict = {
                "predicted_total_kwh": round(prepared_day_watt, 2),
                "predicted_savings": round(prepared_day_watt * current_tariff, 2),
                "hourly_forecast_wh": [round(h, 2) for h in total_hourly_wh],
                "detailed_arrays": detailed_reports,
                "status": "success",
                "current_temp": round(temp, 1),
                "weather_condition": wmo_codes.get(code, "Unknown"),
                "weather_code": code,
                "calibration_factor": round(calibration_factor, 2),
                "peak_hour": today_peak_hour,
                # "peak_hour": total_hourly_wh.index(max(total_hourly_wh)) if total_hourly_wh else 0,
                "wind_direction": wind_dir,
            }

            cache.set(cache_key, result_dict, 3600)
            self.save_forecast_to_db(total_hourly_wh, data, calibration_factor)
            # self.save_forecast_to_db(result_dict, data)
            self.check_and_log_wind_alert(data, user=user)

            self.check_and_log_peak_events(data, result_dict.get('peak_hour'), user=user)

            return result_dict
        except Exception as e:
            print(f"WeatherService Error: {e}")
            return self._get_error_response(current_tariff)

    def convert_iso_to_datetime(self, data):
        sunrise_str = data.get('daily', {}).get('sunrise', [''])[0]
        sunset_str = data.get('daily', {}).get('sunset', [''])[0]

        sunrise = datetime.datetime.fromisoformat(sunrise_str)
        sunset = datetime.datetime.fromisoformat(sunset_str)

        return timezone.make_aware(sunrise), timezone.make_aware(sunset)

    # CELERY
    def _fetch_raw_weather_from_api(self, lat, lon):
        import requests
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=temperature_2m,relative_humidity_2m,surface_pressure,cloud_cover,"
            f"shortwave_radiation,direct_radiation,diffuse_radiation,wind_speed_10m,"
            f"wind_gusts_10m,wind_direction_10m,weather_code"
            f"&daily=sunrise,sunset&timezone=auto"
            f"&forecast_days=16"
            f"&wind_speed_unit=ms"
        )
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Weather API Fetch Error: {e}")
        return None

    def update_forecast_for_user(self, user):
        try:
            settings = getattr(user, 'settings', None)
            if not settings or settings.latitude is None or settings.longitude is None:
                return False

            raw_data = self._fetch_raw_weather_from_api(settings.latitude, settings.longitude)
            if not raw_data:
                return False

            self.get_solar_forecast(raw_data, user)
            return True

        except Exception as e:
            print(f"Error updating forecast for user {user.username}: {e}")
            return False

    # END

    def save_forecast_to_db(self, total_hourly_wh, raw_api_data, calibration_factor=1.0, user=None):
        try:
            today = timezone.localtime(timezone.now()).date()
            sunrise_dt, sunset_dt = self.convert_iso_to_datetime(raw_api_data)

            hourly_raw = raw_api_data.get('hourly', {})
            wind_speeds = hourly_raw.get('wind_speed_10m', [])
            wind_gusts = hourly_raw.get('wind_gusts_10m', [])
            wind_directions = hourly_raw.get('wind_direction_10m', [])

            # avg_speed = round(sum(wind_speeds) / len(wind_speeds), 1) if wind_speeds else None
            # max_gust = max(wind_gusts) if wind_gusts else None
            # avg_direction = int(sum(wind_directions) / len(wind_directions)) if wind_directions else None

            user_settings = getattr(user, 'settings', None) if user else None
            user_tz_name = getattr(user_settings, 'timezone', None) or 'Europe/Kyiv'

            try:
                user_tz = ZoneInfo(user_tz_name)
            except Exception:
                user_tz = timezone.utc

            now_user = datetime.datetime.now(user_tz)
            current_target_str = now_user.strftime('%Y-%m-%dT%H:00')

            timestamps = hourly_raw.get('time', [])
            safe_h = 0

            if current_target_str in timestamps:
                safe_h = timestamps.index(current_target_str)
            else:
                safe_h = min(now_user.hour, len(wind_speeds) - 1) if wind_speeds else 0

            current_speed = round(wind_speeds[safe_h]) if safe_h < len(wind_speeds) and wind_speeds[
                safe_h] is not None else None
            current_gust = round(wind_gusts[safe_h]) if safe_h < len(wind_gusts) and wind_gusts[
                safe_h] is not None else None
            current_direction = int(wind_directions[safe_h]) if safe_h < len(wind_directions) and wind_directions[
                safe_h] is not None else None

            today_wh = total_hourly_wh[:24] if len(total_hourly_wh) >= 24 else total_hourly_wh
            today_kwh = round(sum(today_wh) / 1000.0, 2)
            peak_hour_idx = today_wh.index(max(today_wh)) if today_wh else 0

            SolarForecastRecordModel.objects.update_or_create(
                date=today,
                defaults={
                    'predicted_kwh': today_kwh,
                    'predicted_savings': round(today_kwh * CurrentTariffModel.load().power_tariff, 2),
                    'peak_hour': peak_hour_idx,
                    'sunrise': sunrise_dt,
                    'sunset': sunset_dt,
                    'wind_speed_10m': current_speed,
                    'wind_gusts_10m': current_gust,
                    'wind_direction_10m': current_direction,
                    # 'wind_speed_10m': avg_speed,
                    # 'wind_gusts_10m': max_gust,
                    # 'wind_direction_10m': avg_direction,
                }
            )

            hourly = raw_api_data.get('hourly', {})
            timestamps = hourly.get('time', [])
            if not timestamps:
                return True

            temps = hourly.get('temperature_2m', [])
            codes = hourly.get('weather_code', [])
            clouds = hourly.get('cloud_cover', [])
            humidities = hourly.get('relative_humidity_2m', [])
            surface_pressure = hourly.get('surface_pressure', [])
            shortwave = hourly.get('shortwave_radiation', [])
            direct = hourly.get('direct_radiation', [])
            diffuse = hourly.get('diffuse_radiation', [])

            parsed_timestamps = []
            for ts in timestamps:
                naive_dt = datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M')
                parsed_timestamps.append(timezone.make_aware(naive_dt))

            WeatherDataModel.objects.filter(timestamp__in=parsed_timestamps).delete()

            weather_objects = []
            for i in range(len(timestamps)):
                def get_val(arr, idx):
                    return arr[idx] if idx < len(arr) else None

                weather_objects.append(
                    WeatherDataModel(
                        timestamp=parsed_timestamps[i],
                        temperature=get_val(temps, i),
                        condition_code=str(get_val(codes, i)) if get_val(codes, i) is not None else "0",
                        cloud_cover=get_val(clouds, i),
                        humidity=get_val(humidities, i),
                        surface_pressure=get_val(surface_pressure, i),
                        shortwave_radiation=get_val(shortwave, i) or 0.0,
                        direct_radiation=get_val(direct, i) or 0.0,
                        diffuse_radiation=get_val(diffuse, i) or 0.0,
                    )
                )

            WeatherDataModel.objects.bulk_create(weather_objects)
            return True

        except Exception as e:
            print(f"DB loading error: {e}")
            return False

    # def save_forecast_to_db(self, forecast_data, raw_api_data):
    #     try:
    #         today = timezone.localtime(timezone.now()).date()
    #         sunrise_dt, sunset_dt = self.convert_iso_to_datetime(raw_api_data)
    #
    #         hourly_raw = raw_api_data.get('hourly', {})
    #         wind_speeds = hourly_raw.get('wind_speed_10m', [])
    #         wind_gusts = hourly_raw.get('wind_gusts_10m', [])
    #         wind_directions = hourly_raw.get('wind_direction_10m', [])
    #
    #         avg_speed = round(sum(wind_speeds) / len(wind_speeds), 1) if wind_speeds else None
    #         max_gust = max(wind_gusts) if wind_gusts else None
    #         avg_direction = int(sum(wind_directions) / len(wind_directions)) if wind_directions else None
    #
    #         SolarForecastRecordModel.objects.update_or_create(
    #             date=today,
    #             defaults={
    #                 'predicted_kwh': forecast_data.get('predicted_total_kwh', 0.0),
    #                 'predicted_savings': forecast_data.get('predicted_savings', 0.0),
    #                 'peak_hour': forecast_data.get('peak_hour', 0),
    #                 'sunrise': sunrise_dt,
    #                 'sunset': sunset_dt,
    #                 'wind_speed_10m': avg_speed,
    #                 'wind_gusts_10m': max_gust,
    #                 'wind_direction_10m': avg_direction,
    #             }
    #         )
    #
    #         hourly = raw_api_data.get('hourly', {})
    #         timestamps = hourly.get('time', [])
    #         if not timestamps:
    #             return True
    #
    #         temps = hourly.get('temperature_2m', [])
    #         codes = hourly.get('weather_code', [])
    #         clouds = hourly.get('cloud_cover', [])
    #         humidities = hourly.get('relative_humidity_2m', [])
    #         surface_pressure = hourly.get('surface_pressure', [])
    #         shortwave = hourly.get('shortwave_radiation', [])
    #         direct = hourly.get('direct_radiation', [])
    #         diffuse = hourly.get('diffuse_radiation', [])
    #
    #         parsed_timestamps = []
    #         for ts in timestamps:
    #             naive_dt = datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M')
    #             parsed_timestamps.append(timezone.make_aware(naive_dt))
    #
    #         WeatherDataModel.objects.filter(timestamp__in=parsed_timestamps).delete()
    #
    #         weather_objects = []
    #         for i in range(len(timestamps)):
    #             def get_val(arr, idx):
    #                 return arr[idx] if idx < len(arr) else None
    #
    #             weather_objects.append(
    #                 WeatherDataModel(
    #                     timestamp=parsed_timestamps[i],
    #                     temperature=get_val(temps, i),
    #                     condition_code=str(get_val(codes, i)) if get_val(codes, i) is not None else "0",
    #                     cloud_cover=get_val(clouds, i),
    #                     humidity=get_val(humidities, i),
    #                     surface_pressure=get_val(surface_pressure, i),
    #                     shortwave_radiation=get_val(shortwave, i) or 0.0,
    #                     direct_radiation=get_val(direct, i) or 0.0,
    #                     diffuse_radiation=get_val(diffuse, i) or 0.0,
    #                 )
    #             )
    #
    #         WeatherDataModel.objects.bulk_create(weather_objects)
    #         return True
    #
    #     except Exception as e:
    #         print(f"DB loading error: {e}")
    #         return False

    def check_and_log_wind_alert(self, raw_api_data, user=None):
        if not user:
            print("DEBUG WIND: User not transferred, skipping wind alerts.")
            return

        threshold = 15.0

        hourly_raw = raw_api_data.get('hourly', {})
        wind_speeds = hourly_raw.get('wind_speed_10m', [])
        wind_gusts = hourly_raw.get('wind_gusts_10m', [])
        wind_direction = hourly_raw.get('wind_direction_10m', [])
        timestamps = hourly_raw.get('time', [])

        if not timestamps or not wind_speeds:
            return

        today = timezone.localtime(timezone.now()).date()

        # Беремо тільки перші 24 години (сьогоднішній день із 384 годин)
        today_hours_count = min(24, len(timestamps))

        today_wind_speeds = wind_speeds[:today_hours_count]
        today_wind_gusts = wind_gusts[:today_hours_count]

        daily_event, _ = SystemEventModel.objects.update_or_create(
            date=today,
            user=user,
            defaults={
                "payload": {
                    "title": "Wind alert",
                    "message": "Strong wind detected",
                    "level": "warning",
                    "category": "warning",
                    "max_wind_speed": max(today_wind_speeds) if today_wind_speeds else None,
                    "max_wind_gust": max(today_wind_gusts) if today_wind_gusts else None,
                }
            }
        )

        for i in range(today_hours_count):
            dt = datetime.datetime.fromisoformat(timestamps[i])
            aware_dt = timezone.make_aware(dt)

            max_wind = wind_speeds[i]
            max_gust = wind_gusts[i]

            if max_wind is None or max_gust is None:
                continue

            if max_wind >= threshold or max_gust >= threshold:
                time_str = dt.strftime("%H:%M")
                title_str = f'Wind alert at {time_str}'

                current_direction = [wind_direction[i]] if i < len(wind_direction) and wind_direction[
                    i] is not None else []

                WindEventModel.objects.update_or_create(
                    daily_event=daily_event,
                    user=user,
                    event_timestamp=aware_dt,
                    defaults={
                        'category': 'WARNING',
                        'title': title_str,
                        'message': f"Wind {max_wind} m/s, Gust {max_gust} m/s",
                        'event_time': dt.time(),
                        'wind_strength': max_wind,
                        'gust_strength': max_gust,
                        'wind_direction': current_direction,
                        'is_persistent': True,
                    }
                )
                print(f"✅ DEBUG WIND: Logged wind event for today at {time_str} (Wind: {max_wind})")

    # def check_and_log_wind_alert(self, raw_api_data, user=None):
    #     if not user:
    #         print("DEBUG WIND: User not transferred, skipping wind alerts.")
    #         return
    #
    #     threshold = 15.0
    #
    #     hourly_raw = raw_api_data.get('hourly', {})
    #     wind_speeds = hourly_raw.get('wind_speed_10m', [])
    #     wind_gusts = hourly_raw.get('wind_gusts_10m', [])
    #     wind_direction = hourly_raw.get('wind_direction_10m', [])
    #     timestamps = hourly_raw.get('time', [])
    #
    #     today = timezone.localtime(timezone.now()).date()
    #
    #     daily_event, _ = SystemEventModel.objects.update_or_create(
    #         date=today,
    #         user=user,
    #         defaults={
    #             "payload": {
    #                 "title": "Wind alert",
    #                 "message": "Strong wind detected",
    #                 "level": "warning",
    #                 "category": "warning",
    #                 "max_wind_speed": max(wind_speeds) if wind_speeds else None,
    #                 "max_wind_gust": max(wind_gusts) if wind_gusts else None,
    #             }
    #         }
    #     )

        # for i in range(len(wind_speeds)):
        #     dt = datetime.datetime.fromisoformat(timestamps[i])
        #     aware_dt = timezone.make_aware(dt)
        #
        #     if aware_dt.date() != today:
        #         continue
        #
        #     max_wind = wind_speeds[i]
        #     max_gust = wind_gusts[i]
        #
        #     if max_wind is None or max_gust is None:
        #         continue
        #
        #     if max_wind >= threshold or max_gust >= threshold:
        #         time_str = dt.strftime("%H:%M")
        #         title_str = f'Wind alert at {time_str}'
        #
        #         current_direction = [wind_direction[i]] if i < len(wind_direction) and wind_direction[
        #             i] is not None else []
        #
        #         WindEventModel.objects.update_or_create(
        #             daily_event=daily_event,
        #             user=user,
        #             event_timestamp=aware_dt,
        #             defaults={
        #                 'category': 'WARNING',
        #                 'title': title_str,
        #                 'message': f"Wind {max_wind} m/s, Gust {max_gust} m/s",
        #                 'event_time': dt.time(),
        #                 'wind_strength': max_wind,
        #                 'gust_strength': max_gust,
        #                 'wind_direction': current_direction,
        #                 'is_persistent': True,
        #                 'user': user,
        #             }
        #         )






                # if not WindEventModel.objects.filter(
                #         daily_event=daily_event,
                #         event_timestamp=aware_dt
                # ).exists():
                #     event_data = {
                #         'wind': max_wind,
                #         'gust': max_gust,
                #         'direction': wind_direction[i] if i < len(wind_direction) else None,
                #         'status': 'CRITICAL' if (max_wind >= threshold and max_gust >= threshold) else 'WARNING'
                #     }
                #
                #     WindEventModel.objects.update_or_create(
                #         daily_event=daily_event,
                #         user=user,
                #         event_timestamp=aware_dt,
                #         defaults={
                #             'category': 'WARNING',
                #             'title': title_str,
                #             'message': f"Wind {max_wind} m/s, Gust {max_gust} m/s",
                #             'wind_time': dt.strftime("%H:%M"),
                #             'wind_strength': max_wind,
                #             'gust_strength': max_gust,
                #             'wind_direction': wind_direction,
                #             'is_persistent': True,
                #             'user': user
                #         }
                #     )

    def check_and_log_peak_events(self, raw_api_data, peak_hour, user=None):
        if not user:
            print("DEBUG PEAK: User not transferred, skipping peak generation hours.")
            return

        if peak_hour is None:
            print("DEBUG PEAK: peak_hour is None")
            return

        hourly_raw = raw_api_data.get('hourly', {})
        timestamps = hourly_raw.get('time', [])
        if not timestamps or peak_hour >= len(timestamps):
            print("DEBUG PEAK: Invalid timestamps or peak_hour index out of range")
            return

        today = timezone.localtime(timezone.now()).date()

        target_index = None
        for i, ts in enumerate(timestamps):
            dt = datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M')
            aware_dt = timezone.make_aware(dt)
            if aware_dt.date() == today and aware_dt.hour == peak_hour:
                target_index = i
                break

        if target_index is None or target_index >= len(timestamps):
            print("DEBUG PEAK: Could not find today's peak hour in timestamps")
            return

        daily_event, _ = SystemEventModel.objects.update_or_create(
            date=today,
            user=user,
            defaults={
                "payload": {
                    "title": "Wind alert",
                    "message": "Strong wind detected",
                    "level": "warning",
                    "category": "warning",
                }
            }
        )

        peak_start_str = timestamps[target_index]
        peak_start_dt = datetime.datetime.strptime(peak_start_str, '%Y-%m-%dT%H:%M')
        peak_start_aware = timezone.make_aware(peak_start_dt)

        end_index = target_index + 1
        peak_end_aware = None
        if end_index < len(timestamps):
            peak_end_dt = datetime.datetime.strptime(timestamps[end_index], '%Y-%m-%dT%H:%M')
            peak_end_aware = timezone.make_aware(peak_end_dt)

        PeakEventModel.objects.get_or_create(
            daily_event=daily_event,
            user=user,
            peak_hour=peak_hour,
            status='PEAK_START',
            defaults={
                'created_at': timezone.now()
            }
        )
        print(f"DEBUG PEAK: Created/Checked PeakEvent START for {peak_start_dt.strftime('%H:%M')}")

        if peak_end_aware and peak_end_aware.date() == today:
            PeakEventModel.objects.get_or_create(
                daily_event=daily_event,
                user=user,
                peak_hour=peak_hour,
                status='PEAK_END',
                defaults={
                    'created_at': timezone.now()
                }
            )
            print(f"DEBUG PEAK: Created/Checked PeakEvent END for {peak_end_dt.strftime('%H:%M')}")

    # def check_and_log_peak_events(self, raw_api_data, peak_hour, user=None):
    #     if peak_hour is None:
    #         return
    #
    #     hourly_raw = raw_api_data.get('hourly', {})
    #     timestamps = hourly_raw.get('time', [])
    #     if not timestamps or peak_hour >= len(timestamps):
    #         return
    #
    #     now = timezone.localtime(timezone.now())
    #
    #     peak_start_dt = datetime.datetime.fromisoformat(timestamps[peak_hour])
    #     peak_start_aware = timezone.make_aware(peak_start_dt)
    #
    #     end_index = peak_hour + 1
    #     if end_index < len(timestamps):
    #         peak_end_dt = datetime.datetime.fromisoformat(timestamps[end_index])
    #         peak_end_aware = timezone.make_aware(peak_end_dt)
    #     else:
    #         peak_end_aware = None
    #
    #     base_filter = {'category': 'FORECAST'}
    #     if user:
    #         base_filter['user'] = user
    #
    #     if now.hour >= peak_start_dt.hour:
    #         if not SystemEventModel.objects.filter(
    #                 **base_filter,
    #                 event_timestamp=peak_start_aware,
    #                 title__icontains='Peak generation started'
    #         ).exists():
    #             SystemEventModel.objects.update_or_create(
    #                 **base_filter,
    #                 event_timestamp=peak_start_aware,
    #                 defaults={
    #                     'level': 'SUCC',
    #                     'title': f'Peak generation started at {peak_start_dt.strftime("%H:%M")} ☀️',
    #                     'payload': {'peak_hour': peak_hour, 'status': 'PEAK_START'},
    #                     'is_persistent': True,
    #                     'user': user
    #                 }
    #             )
    #
    #     if peak_end_aware and now.hour >= peak_end_dt.hour:
    #         if not SystemEventModel.objects.filter(
    #                 **base_filter,
    #                 event_timestamp=peak_end_aware,
    #                 title__icontains='Peak generation ended'
    #         ).exists():
    #             SystemEventModel.objects.update_or_create(
    #                 **base_filter,
    #                 event_timestamp=peak_end_aware,
    #                 defaults={
    #                     'level': 'INFO',
    #                     'title': f'Peak generation ended at {peak_end_dt.strftime("%H:%M")} ⛅',
    #                     'payload': {'peak_hour': peak_hour, 'status': 'PEAK_END'},
    #                     'is_persistent': True,
    #                     'user': user
    #                 }
    #             )
