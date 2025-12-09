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
