# 📜 Changelog

All notable changes to this project will be documented in this file.  
This project adheres to semantic versioning where possible.

---

## [0.1.0] - Initial Setup
- Added initial `calculator` Django app to manage daily solar energy generation.
- Registered app in `INSTALLED_APPS`.
- Created base `urls.py` and included in root project.
- Added initial index view and template path.

---

## [0.2.0] - Models & Admin
- Added `DataEntryLineModel` to account for daily power.
- Customized entry line view in Django admin.
- Added `verbose_name` for all model fields.

---

## [0.3.0] - Core Calculations
- Implemented automation for calculating generated solar power (Watts).
- Added cost calculation for generated solar power.
- Optimized results to show with 2 decimal places.
- Added condition for missing afternoon data.
- Fixed subtraction errors in afternoon charge/cost.
- Corrected mathematical issues in calculations.
- Updated cost and watt calculations to account for battery usage.

---

## [0.4.0] - Templates & UI
- Added `_base.html` as main template file.
- Implemented top navigation panel.
- Active link highlighting in topnav.
- Updated `_topnav.html` with padding and logo color.
- Changed app background to `#F8F9FA` (Bootstrap `bg-body-tertiary`).

---

## [0.5.0] - Charts & Data Visualization
- Added chart for solar power generation (example data).
- Added entries list for daily generation (example data).
- Implemented `AddEntryForm` in `forms.py`.
- Added entry form to save new solar energy data to DB.
- Refactored entry form handling into `services/handle_entry_form.py`.
- Linked logo to dashboard page.
- Improved design of `add_entry.html`.
- Displayed entry data on dashboard.
- Added charts for saved data visualization.
- Separated charts into tabs (power vs cost).
- Updated `index.html` entries table.

---

## [0.6.0] - Dashboard Enhancements
- Added total generated power indication.
- Redesigned topnav links.
- Implemented pagination (25 entries per page).
- Added total cost indication.
- Fixed incorrect symbols for battery level.
- Centered topnav with main content.
- Added condition for missing afternoon values.
- Ordered entries by date (newest first).

---

## [0.7.0] - Mathematics Refactoring
- Multiple fixes and optimizations in `models.py`.
- Rewrote all mathematical calculations.
- Displayed `0` message when no power generated.
- Renamed chart to "Total generated power".
- Fixed pagination issue (limited to 25 entries).
- Added singleton model for current tariff.
- Implemented tariff update functionality.
- Improved design of `settings.html` and forms.
- Added "Power tariff settings" label.

---

## [0.8.0] - Weather Integration
- Refactored models and admin to add weather conditions (many-to-many).
- Displayed weather items per day in admin.
- Changed weather field to `SelectMultiple`.
- Fixed Many-to-Many saving error in `handle_entry_form.py`.
- Removed local choices from `AddEntryForm` (imported from model for DRY).

---

## [0.9.0] - Requirements & Stability
- Created `requirements.txt` with necessary packages.
- Rolled back mathematics to stable version.
- Fixed select field initial value issue.
- Finalized DRY principles in forms.

---

## [1.0.0] - Stable Release
- Fully working version with:
  - Daily entries tracking.
  - Automated power & cost calculations.
  - Charts and dashboard with pagination.
  - Tariff management via settings.
  - Weather conditions integration.
  - Optimized mathematics and UI design.

## [2.12.0] - Bug fixes, weather logic optimizations, model field updates, authentication (JWT) improvements, addition of necessary dependencies, and complete cleanup of database migrations - #32
⚙️ Backend and Weather Services

    🌦- Optimized check_and_log_wind_alert to analyze data only for the current day within the weather widget (first 24 hours of the 16-day forecast).
    - Fixed saving wind alerts in the database by fixing date filtering and global threshold checks.
    - Updated wind_direction saving: now a specific hourly value is recorded instead of the entire forecast array.
    - Added diagnostic logging to improve monitoring of weather data processing.
    - Replaced local server time with user timezone (ZoneInfo) to match Open-Meteo hourly timestamps exactly.
    - Updated save_forecast_to_db to save hourly weather data (speed, gusts, direction) of the current hour instead of calculating daily aggregates.
- Cleaned up weather_service.py of unnecessary comments and imports.
    - Isolated forecast data for the current day (first 24 hours) for the dashboard widget instead of using data for the entire period.

💻 Frontend and Authentication (JWT)

    - Fixed infinite login page reload loop: added protection in the response interceptor so that it doesn't try to refresh the token if an error occurs at the refresh endpoint itself.
    - Added 400 status handling in addition to 401 in Axios interceptor for failed token refresh attempts.
    - Implemented a pre-check for the refresh token in localStorage to avoid unnecessary unauthorized requests.
- Ensured proper token clearing and automatic redirection to the login page in case of failed JWT validation.

🗄️ Database, Dependencies and Migrations

    - Added psycopg2-binary package to requirements.txt.
- Complete manual cleanup of migration chain (fixed issues after renaming SystemEvent to SystemEventModel that caused Django to lose historical state, create duplicate CreateModel, obsolete fields, invalid default values, and schema conflicts):
    Removed duplicate and obsolete CreateModel entries.
    Removed obsolete fields (event_timestamp, is_persistent, level, message, title) that no longer exist in the model.
    Synchronized field definitions, nullability, and default values ​​with the current model.
    Fixed migration order and dependencies.
    Synchronized schema with current model state.
    Updated fixtures to reflect cleaned model structure.
    - Fixed padding for WeatherDataModel.objects.bulk_create() to ensure complete historical weather data is preserved.
    - Changed pagination from 8 items per page to 7.
    - Changed internal paddings for the records table.
    - Renamed peak_power_kwp field to peak_power_wp, as all data is stored in watts per hour.
    - Changed peak_power_wh field type from FloatField to IntegerField.
    - Fixed conversion from watt-hours to kilowatt-hours (kWh) and applied the correct panel array multiplier (PanelsArrayModel).
    - Ensured correct display of realistic daily generation in the dashboard widget.

