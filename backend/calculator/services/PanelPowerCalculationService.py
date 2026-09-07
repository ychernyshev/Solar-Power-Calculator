# SPDX-License-Identifier: AGPL-3.0-or-later

import math

from calculator.models import PanelsArrayModel

class PanelPowerCalculationService:
#     def calculate_array_production(self, array, radiation_data, calibration_factor, cloud_cover_data=None):
#         efficiency = array.efficiency
#         if efficiency > 1.0:
#             efficiency = efficiency / 100.0
#
#         array_factor = array.area * efficiency * 0.85 * calibration_factor
#         tilt_factor = math.cos(math.radians(abs(array.angle - 30)))
#
#         production = []
#         for i, rad in enumerate(radiation_data):
#             cloud_factor = 1.0
#             if cloud_cover_data and i < len(cloud_cover_data):
#                 cloud_cover = cloud_cover_data[i] or 0.0
#                 cloud_factor = max(0.1, 1.0 - (cloud_cover / 100.0) * 0.75)
#
#             hourly_val = rad * array_factor * tilt_factor * cloud_factor
#             production.append(round(hourly_val, 2))
#
#         return production

    def calculate_array_production(self, array, radiation_data, calibration_factor, cloud_cover_data=None):
        efficiency = array.efficiency
        if efficiency > 1.0:
            efficiency = efficiency / 100.0

        area = array.area if array.area is not None else 0.0
        cal_factor = calibration_factor if calibration_factor is not None else 1.0
        angle = array.angle if array.angle is not None else 30.0

        array_factor = array.area * efficiency * 0.85 * calibration_factor
        tilt_factor = math.cos(math.radians(abs(array.angle - 30)))

        # production = [round(rad * array_factor * tilt_factor, 2) for rad in radiation_data]
        production = []
        has_missing_data = False

        for i, rad in enumerate(radiation_data):
            if rad is None:
                rad = 0.0
                has_missing_data = True

            cloud_factor = 1.0
            if cloud_cover_data and i < len(cloud_cover_data):
                cloud_cover = cloud_cover_data[i]
                if cloud_cover is None:
                    cloud_cover = 0.0
                    has_missing_data = True
                cloud_factor = max(0.1, 1.0 - (cloud_cover / 100.0) * 0.75)
            # if cloud_cover_data and i < len(cloud_cover_data):
            #     cloud_cover = cloud_cover_data[i] or 0.0
            #     cloud_factor = max(0.1, 1.0 - (cloud_cover / 100.0) * 0.75)

            hourly_val = rad * array_factor * tilt_factor * cloud_factor
            production.append(round(hourly_val, 2) / 10)

        if has_missing_data:
            print("⚠️ Warning: Open-Meteo returned missing values (None) for radiation or cloudiness.")
            # ==> add the system event to the SystemEventModel <==

        print("PRODUCTION - calculate_array_production: ", production[:24], sum(production))
        return production
        # return [round(rad * array_factor, 2) for rad in radiation_data]

    def get_total_forecast(self, radiation_data, calibration_factor, user):
        if user:
            arrays = PanelsArrayModel.objects.filter(user=user)
        else:
            arrays = PanelsArrayModel.objects.all()

        total_hourly_wh = [0.0] * len(radiation_data)
        detailed_reports = []

        for array in arrays:
            production = self.calculate_array_production(array, radiation_data, calibration_factor)
            # print('PRODUCTION - get_total_forecast', production[:24])
            detailed_reports.append({
                "name": array.name,
                "hourly_wh": production,
                "peak_power": max(production) if production else 0
            })
            for i in range(len(total_hourly_wh)):
                total_hourly_wh[i] += production[i]

        return total_hourly_wh, detailed_reports