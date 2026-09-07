# SPDX-License-Identifier: AGPL-3.0-or-later
from zoneinfo import ZoneInfo

from django.utils import timezone
from rest_framework import serializers

from calculator.models import (DataEntryLineModel,
                               CurrentTariffModel,
                               WeatherConditionModel,
                               WeatherDataModel,
                               SolarForecastRecordModel,
                               PanelsArrayModel,
                               UserProfileSettingsModel,
                               SystemEventModel,
                               PeakEventModel,
                               WindEventModel, )


class WeatherConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherConditionModel
        fields = ['id', 'name']


class CurrentTariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentTariffModel
        fields = ['power_tariff', 'last_updated']


class DataEntrySerializer(serializers.ModelSerializer):
    empty_day_message = serializers.ReadOnlyField(source='get_empty_day_message')
    weather_details = WeatherConditionSerializer(source='weather', many=True, read_only=True)

    weather = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=WeatherConditionModel.objects.all(),
        required=False
    )
    weather_scores = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = DataEntryLineModel
        fields = '__all__'
        read_only_fields = ['full_day_power', 'full_day_cost', 'power_tariff', 'system_power', 'user']

    def get_weather_details(self, obj):
        scores = obj.weather_scores or {}
        return [
            {
                "id": condition.id,
                "name": condition.name,
                "score": scores.get(str(condition.id), 3)
            }
            for condition in obj.weather.all()
        ]

    def create(self, validated_data):
        weather_conditions = validated_data.pop('weather', [])
        weather_scores_data = validated_data.pop('weather_scores', {})

        instance = super().create(validated_data)

        if weather_conditions:
            instance.weather.set(weather_conditions)

        if weather_scores_data:
            instance.weather_scores = {str(k): int(v) for k, v in weather_scores_data.items()}
            instance.save()

        return instance

    def update(self, instance, validated_data):
        weather_conditions = validated_data.pop('weather', None)
        weather_scores_data = validated_data.pop('weather_scores', None)

        instance = super().update(instance, validated_data)

        if weather_conditions is not None:
            instance.weather.set(weather_conditions)

        if weather_scores_data is not None:
            instance.weather_scores = {str(k): int(v) for k, v in weather_scores_data.items()}
            instance.save()

        return instance


class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherDataModel
        fields = '__all__'


class SolarForecastRecordSerializer(serializers.ModelSerializer):
    day_length = serializers.ReadOnlyField(source='get_day_length')
    wind_speed_alert = serializers.ReadOnlyField(source='check_wind_speed')

    class Meta:
        model = SolarForecastRecordModel
        fields = '__all__'
        read_only_fields = ['sunrise', 'sunset']


class PanelsArraySerializer(serializers.ModelSerializer):
    class Meta:
        model = PanelsArrayModel
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False},
            'peak_power_kwp': {'required': False}
        }

    def validate_efficiency(self, value):
        if value > 1.0:
            return value / 100.0
        return value


class UserProfileSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileSettingsModel
        fields = '__all__'
        read_only_fields = ['user']


class PeakEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeakEventModel
        fields = '__all__'
        read_only_fields = ['user']


class WindEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WindEventModel
        fields = '__all__'
        read_only_fields = ['user']


class SystemEventSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    formatted_hour = serializers.SerializerMethodField()
    formatted_time_range = serializers.SerializerMethodField()

    wind_records = WindEventSerializer(many=True, read_only=True)
    peak_records = PeakEventSerializer(many=True, read_only=True)

    title = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    msg_type = serializers.SerializerMethodField()

    wind_speed = serializers.SerializerMethodField()
    wind_gust = serializers.SerializerMethodField()
    peak_time_range = serializers.SerializerMethodField()

    event_time = serializers.SerializerMethodField()
    wind_strength = serializers.SerializerMethodField()
    gust_strength = serializers.SerializerMethodField()
    wind_direction = serializers.SerializerMethodField()

    created_at = serializers.SerializerMethodField()

    class Meta:
        model = SystemEventModel
        fields = [
            'id', 'date', 'payload', 'created_at', 'updated_at',
            'formatted_hour', 'formatted_time_range',
            'title', 'text', 'level', 'msg_type', 'event_time',
            'wind_strength', 'gust_strength', 'wind_direction',
            'wind_speed', 'wind_gust', 'peak_time_range',
            'wind_records', 'peak_records', 'created_at'
        ]
        read_only_fields = ['user']

    def get_date(self, obj):
        raw_date = None
        if hasattr(obj, 'daily_event') and obj.daily_event and obj.daily_event.date:
            raw_date = obj.daily_event.date
        elif hasattr(obj, 'date') and obj.date:
            raw_date = obj.date
        elif obj.created_at:
            raw_date = obj.created_at.date()

        if not raw_date:
            return None

        user = getattr(obj, 'user', None)
        if not user and 'request' in self.context:
            user = self.context['request'].user

        lang = 'uk'
        if user and hasattr(user, 'settings') and user.settings:
            lang = (user.settings.language or 'uk').lower()

        if lang == 'en-us':
            return raw_date.strftime('%m/%d/%Y')

        return raw_date.strftime('%d.%m.%Y')

    def get_formatted_hour(self, obj):
        peak = obj.peak_records.first()
        return peak.formatted_hour if peak else None

    def get_formatted_time_range(self, obj):
        peak = obj.peak_records.first()
        return peak.formatted_time_range if peak else None

    def get_title(self, obj):
        if obj.wind_records.exists():
            return obj.wind_records.first().title
        if obj.peak_records.exists():
            return f"Peak Generation ({obj.peak_records.first().status})"
        return obj.payload.get('title', 'Notification')

    def get_text(self, obj):
        if obj.wind_records.exists():
            return obj.wind_records.first().message
        if obj.peak_records.exists():
            peak = obj.peak_records.first()
            return f"Peak hour slot: {peak.formatted_time_range}"
        return obj.payload.get('message', '')

    def get_level(self, obj):
        if obj.wind_records.exists():
            return obj.wind_records.first().category.lower()
        return obj.payload.get('level', 'info')

    def get_msg_type(self, obj):
        if obj.peak_records.exists():
            return obj.peak_records.first().status.lower()
        return obj.payload.get('category', 'info')

    def get_wind_speed(self, obj):
        wind = obj.wind_records.first()
        return wind.message if wind else None

    def get_wind_gust(self, obj):
        return None

    def get_peak_time_range(self, obj):
        peak = obj.peak_records.first()
        return peak.formatted_time_range if peak else None

    def get_wind_strength(self, obj):
        wind = obj.wind_records.first()
        return wind.wind_strength if wind else None

    def get_gust_strength(self, obj):
        wind = obj.wind_records.first()
        return wind.gust_strength if wind else None

    def get_wind_direction(self, obj):
        wind = obj.wind_records.first()
        return wind.wind_direction if wind else []

    def get_event_time(self, obj):
        user = getattr(obj, 'user', None)

        user_tz_str = 'UTC'
        if user and hasattr(user, 'settings'):
            user_tz_str = user.settings.timezone or 'UTC'

        try:
            user_tz = ZoneInfo(user_tz_str)
        except Exception:
            user_tz = ZoneInfo('UTC')

        now_user_time = timezone.now().astimezone(user_tz)
        current_time_only = now_user_time.time()

        records = obj.wind_records.all()
        if not records.exists():
            return None

        next_or_current = records.filter(event_time__gte=current_time_only).order_by('event_time').first()

        if next_or_current:
            return next_or_current.event_time.strftime('%H:%M') if next_or_current.event_time else None

        last_available = records.order_by('-event_time').first()

        return last_available.event_time.strftime('%H:%M') if last_available and last_available.event_time else None

    def get_created_at(self, obj):
        wind = obj.wind_records.first()
        if not wind or not wind.created_at:
            return None

        user = getattr(obj, 'user', None)
        user_tz_str = 'UTC'
        if user and hasattr(user, 'settings'):
            user_tz_str = user.settings.timezone or 'UTC'

        try:
            user_tz = ZoneInfo(user_tz_str)
        except Exception:
            user_tz = ZoneInfo('UTC')

        user_local_time = wind.created_at.astimezone(user_tz)

        return user_local_time.strftime('%Y-%m-%d %H:%M:%S')

# DEPRECATED
# class GeolocationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GeolocationModel
#         fields = '__all__'
#
#
# class UserTimezoneSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserTimezoneModel
#         fields = '__all__'
#         read_only_fields = ['user']
#
#
# class UserLanguageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserLanguageModel
#         fields = '__all__'
#         read_only_fields = ['user']
#
#
# class UserCurrencySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserCurrencyModel
#         fields = '__all__'
#         read_only_fields = ['user']
