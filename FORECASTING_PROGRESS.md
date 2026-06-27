# National Electricity & Gas AI Forecasting Module — Progress Tracker

Branch: `copilot/national-electricity-gas-ai-forecasting-module`

## Overview

This feature adds a probabilistic demand forecasting module for Great Britain national electricity and gas to the National Grid: Live project. The module produces quantile forecasts (p05–p95) across three time horizons and exposes them through a REST API.

---

## Progress

### ✅ Completed

- [x] **Forecasting module scaffold** (`grid/forecasting/`)
  - Constants, enums, and regime definitions (`constants.py`)
  - Configuration loader (`config.py`)
  - Time spine generator (`time_spine.py`)
  - Calendar feature engineering (`calendar_features.py`)
  - Feature pipeline (`features.py`)
  - Confidence score calculation (`confidence.py`)
  - Scenario generation for long-horizon forecasts (`scenarios.py`)
  - Explanation / feature-attribution module (`explanations.py`)
  - Daily aggregation from hourly predictions (`daily.py`)
  - Backtesting framework (`backtesting.py`)
  - Error types (`errors.py`)

- [x] **Data adapters** (`grid/forecasting/adapters/`)
  - Electricity adapter (`adapters/electricity.py`)
  - Gas adapter with unit conversion (`adapters/gas.py`)
  - Weather adapter (`adapters/weather.py`)

- [x] **ML models** (`grid/forecasting/models/`)
  - LightGBM model wrapper (`models/lightgbm_models.py`)
  - Baseline models (`models/baselines.py`)
  - Calibration (`models/calibration.py`)

- [x] **Training / inference pipelines** (`grid/forecasting/pipelines/`)
  - Dataset builder (`pipelines/datasets.py`)
  - Training and inference workflow (`pipelines/workflows.py`)

- [x] **In-memory forecast service** (`grid/forecasting/service.py`)
  - `ForecastStore` for holding hourly/daily rows and metadata
  - `ForecastService` with demo-run seeding, query helpers, and status reporting

- [x] **Config files** (`config/`)
  - `forecasting.yml` — regime boundaries, confidence adjustments, quantile outputs
  - `model_features.yml` — feature group definitions
  - `explanation_feature_groups.yml` — explanation grouping
  - `gas_conversion.yml` — unit conversion rules
  - `weather_regions_gb_v1.csv` — regional weather weighting

- [x] **REST API endpoints** (`grid/api/main.py`)
  - `GET /api/forecast/hourly` — hourly probabilistic forecast
  - `GET /api/forecast/daily` — daily aggregated forecast
  - `GET /api/forecast/model-status` — model metadata and calibration status
  - `GET /api/forecast/backtest-summary` — backtesting metrics
  - `GET /api/forecast/explain/hourly` — hourly feature attributions
  - `GET /api/forecast/explain/daily` — daily feature attributions

- [x] **Tests**
  - Forecast API tests (`tests/test_api_forecast.py`) — 6 test cases covering all endpoints
  - Forecasting unit tests (`tests/test_forecasting.py`) — weather region config, gas conversion, time spine
  - CI workflow (`.github/workflows/ci.yml`)
  - Coverage gate at 90% (`pytest.ini`, `.coveragerc`)

---

## Pending / In Progress

- [ ] **Live data integration** — replace `seed_demo_run()` with real pipeline execution driven by `update.py` or a dedicated scheduler
- [ ] **Model training** — integrate `pipelines/workflows.py` with a real training data store; persist trained model artefacts
- [ ] **Calibration** — wire `models/calibration.py` into the service so `calibration_status` reflects actual state
- [ ] **Backtesting results** — populate `ForecastStore.backtest_summary` from real backtest runs
- [ ] **Feature explanations** — populate `hourly_explanations` / `daily_explanations` in the store
- [ ] **Frontend visualisation** — add forecast tab / panel to the Nuxt frontend (`frontend/`)
- [ ] **Database persistence** — store forecast runs in MariaDB/MySQL using the schema in `grid.sql`
- [ ] **Environment variables** — document and validate `ELEXON_API_KEY`, `NATIONAL_GAS_API_KEY`, and `OPEN_METEO_API_KEY_OPTIONAL` in production setup
- [ ] **Scenario path generation** — validate the long-horizon historical-weather-analogue approach end-to-end
- [ ] **Extended test coverage** — add tests for adapters, pipelines, models, and scenario generation
- [ ] **Documentation** — update `README.md` with forecasting API usage, config options, and deployment notes

---

## Key Design Decisions

| Decision | Detail |
|---|---|
| Forecast horizons | 1–72 h (operational), 73–840 h (extended weather), 841–8760 h (planning scenario) |
| Quantile outputs | p05, p10, p25, p50, p75, p90, p95 |
| Fuel types | electricity, gas, combined |
| Issue times (UTC) | 00:00, 06:00, 12:00, 18:00 |
| Long-horizon weather | Historical weather analogue (≥841 h), ≥30 scenario paths |
| ML framework | LightGBM with post-hoc quantile calibration |
| Confidence scoring | Starts at 90/70/45 for short/medium/long term; adjusted for missing data, uncalibrated model, etc. |
