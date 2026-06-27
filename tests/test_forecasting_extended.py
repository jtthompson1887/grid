"""Extended tests for the grid.forecasting package.

Covers all modules that were previously excluded from the coverage gate:
calendar_features, features, scenarios, backtesting, explanations,
confidence, daily, adapters (electricity/gas/weather), models (baselines,
lightgbm_models, calibration), pipelines (datasets, workflows), service,
constants, config, time_spine, and errors.
"""

from __future__ import annotations

import math
import os
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------
from grid.forecasting.constants import (
    FORECAST_LABEL,
    MAX_HORIZON_HOURS,
    MIN_HORIZON_HOURS,
    QUANTILES,
    ForecastRegime,
    FuelType,
    get_regime,
)


class TestConstants:
    def test_fuel_type_values(self):
        assert FuelType.ELECTRICITY.value == 'electricity'
        assert FuelType.GAS.value == 'gas'
        assert FuelType.COMBINED.value == 'combined'

    def test_forecast_regime_values(self):
        assert ForecastRegime.OPERATIONAL.value == 'operational_forecast'
        assert ForecastRegime.EXTENDED_WEATHER.value == 'extended_weather_forecast'
        assert ForecastRegime.PLANNING_SCENARIO.value == 'planning_scenario_forecast'

    def test_label_is_string(self):
        assert isinstance(FORECAST_LABEL, str)
        assert len(FORECAST_LABEL) > 0

    def test_quantiles_tuple(self):
        assert 'p05' in QUANTILES
        assert 'p95' in QUANTILES

    def test_get_regime_operational(self):
        assert get_regime(1) == ForecastRegime.OPERATIONAL
        assert get_regime(72) == ForecastRegime.OPERATIONAL

    def test_get_regime_extended(self):
        assert get_regime(73) == ForecastRegime.EXTENDED_WEATHER
        assert get_regime(840) == ForecastRegime.EXTENDED_WEATHER

    def test_get_regime_planning(self):
        assert get_regime(841) == ForecastRegime.PLANNING_SCENARIO
        assert get_regime(MAX_HORIZON_HOURS) == ForecastRegime.PLANNING_SCENARIO

    def test_get_regime_below_min_raises(self):
        with pytest.raises(ValueError):
            get_regime(0)

    def test_get_regime_above_max_raises(self):
        with pytest.raises(ValueError):
            get_regime(MAX_HORIZON_HOURS + 1)


# ---------------------------------------------------------------------------
# errors
# ---------------------------------------------------------------------------
from grid.forecasting.errors import (
    BASELINE_ONLY,
    FORECAST_COMPLETE,
    FORECAST_PARTIAL,
    INSUFFICIENT_HISTORY,
    MISSING_GAS_CONVERSION,
    MISSING_WEATHER,
    MODEL_NOT_CALIBRATED,
    MODEL_NOT_TRAINED,
    SOURCE_UNAVAILABLE,
)


class TestErrors:
    def test_all_error_constants_are_strings(self):
        for const in (
            SOURCE_UNAVAILABLE,
            INSUFFICIENT_HISTORY,
            MISSING_WEATHER,
            MISSING_GAS_CONVERSION,
            MODEL_NOT_TRAINED,
            MODEL_NOT_CALIBRATED,
            FORECAST_PARTIAL,
            FORECAST_COMPLETE,
            BASELINE_ONLY,
        ):
            assert isinstance(const, str)


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------
from grid.forecasting.config import WeatherRegion, load_weather_regions, load_yaml_config, require_environment_variables


class TestConfig:
    def test_load_yaml_config_returns_dict(self):
        result = load_yaml_config('forecasting.yml')
        assert isinstance(result, dict)
        assert 'forecast' in result

    def test_load_weather_regions_returns_list(self):
        regions = load_weather_regions()
        assert len(regions) > 0
        assert all(isinstance(r, WeatherRegion) for r in regions)

    def test_weather_region_has_required_fields(self):
        regions = load_weather_regions()
        for region in regions:
            assert isinstance(region.region_id, str)
            assert isinstance(region.region_name, str)
            assert isinstance(region.latitude, float)
            assert isinstance(region.longitude, float)
            assert isinstance(region.weight, float)

    def test_weather_region_weights_sum_to_one(self):
        regions = load_weather_regions()
        total = sum(r.weight for r in regions)
        assert abs(total - 1.0) < 1e-9

    def test_require_environment_variables_present(self, monkeypatch):
        monkeypatch.setenv('TEST_VAR_A', 'hello')
        result = require_environment_variables(['TEST_VAR_A', 'TEST_VAR_MISSING'])
        assert result['TEST_VAR_A'] == 'hello'
        assert result['TEST_VAR_MISSING'] == ''

    def test_require_environment_variables_empty(self):
        result = require_environment_variables([])
        assert result == {}


# ---------------------------------------------------------------------------
# time_spine
# ---------------------------------------------------------------------------
from grid.forecasting.time_spine import generate_hourly_time_spine, validate_horizon


class TestTimeSpine:
    def test_time_spine_length(self):
        issue = datetime(2026, 6, 1, 12, tzinfo=UTC)
        rows = generate_hourly_time_spine(issue)
        assert len(rows) == MAX_HORIZON_HOURS

    def test_time_spine_naive_issue_time(self):
        issue = datetime(2026, 6, 1, 12)
        rows = generate_hourly_time_spine(issue)
        assert len(rows) == MAX_HORIZON_HOURS

    def test_time_spine_first_row(self):
        issue = datetime(2026, 6, 1, 12, tzinfo=UTC)
        rows = generate_hourly_time_spine(issue)
        first = rows[0]
        assert first['horizon_hours'] == 1
        assert first['target_time_utc'] == issue + timedelta(hours=1)

    def test_time_spine_regime_fields_present(self):
        issue = datetime(2026, 1, 1, tzinfo=UTC)
        rows = generate_hourly_time_spine(issue)
        for row in rows[:5]:
            assert 'forecast_horizon_regime' in row
            assert 'date_local' in row
            assert 'hour_local' in row

    def test_validate_horizon_valid(self):
        validate_horizon(1)
        validate_horizon(MAX_HORIZON_HOURS)

    def test_validate_horizon_below_min_raises(self):
        with pytest.raises(ValueError):
            validate_horizon(0)

    def test_validate_horizon_above_max_raises(self):
        with pytest.raises(ValueError):
            validate_horizon(MAX_HORIZON_HOURS + 1)


# ---------------------------------------------------------------------------
# calendar_features
# ---------------------------------------------------------------------------
from grid.forecasting.calendar_features import build_calendar_row


class TestCalendarFeatures:
    def test_basic_row_fields(self):
        ts = datetime(2026, 6, 15, 9, tzinfo=UTC)
        row = build_calendar_row(ts)
        d = row.to_dict()
        assert d['month'] == 6
        assert d['day_of_month'] == 15
        assert 'hour_of_day_sin' in d
        assert 'hour_of_day_cos' in d
        assert 'month_sin' in d
        assert 'month_cos' in d
        assert 'day_of_year_sin' in d
        assert 'day_of_year_cos' in d

    def test_is_weekend(self):
        # 2026-06-20 is Saturday
        saturday = datetime(2026, 6, 20, 12, tzinfo=UTC)
        row = build_calendar_row(saturday)
        assert row.is_weekend is True

    def test_is_weekday(self):
        # 2026-06-15 is Monday
        monday = datetime(2026, 6, 15, 12, tzinfo=UTC)
        row = build_calendar_row(monday)
        assert row.is_weekend is False

    def test_christmas_period_dec25(self):
        ts = datetime(2026, 12, 25, 12, tzinfo=UTC)
        row = build_calendar_row(ts)
        assert row.is_christmas_period is True

    def test_christmas_period_jan1(self):
        ts = datetime(2026, 1, 1, 12, tzinfo=UTC)
        row = build_calendar_row(ts)
        assert row.is_christmas_period is True

    def test_not_christmas_period_june(self):
        ts = datetime(2026, 6, 15, 12, tzinfo=UTC)
        row = build_calendar_row(ts)
        assert row.is_christmas_period is False

    def test_new_year_period_jan1(self):
        ts = datetime(2026, 1, 1, 12, tzinfo=UTC)
        row = build_calendar_row(ts)
        assert row.is_new_year_period is True

    def test_new_year_period_jan2(self):
        ts = datetime(2026, 1, 2, 12, tzinfo=UTC)
        row = build_calendar_row(ts)
        assert row.is_new_year_period is True

    def test_not_new_year_mid_jan(self):
        ts = datetime(2026, 1, 10, 12, tzinfo=UTC)
        row = build_calendar_row(ts)
        assert row.is_new_year_period is False

    def test_sin_cos_hour_bounds(self):
        for hour in (0, 6, 12, 18, 23):
            ts = datetime(2026, 6, 1, hour, tzinfo=UTC)
            row = build_calendar_row(ts).to_dict()
            assert -1.0 <= row['hour_of_day_sin'] <= 1.0
            assert -1.0 <= row['hour_of_day_cos'] <= 1.0

    def test_naive_datetime_accepted(self):
        ts = datetime(2026, 6, 1, 10)
        row = build_calendar_row(ts)
        assert row.month == 6


# ---------------------------------------------------------------------------
# confidence
# ---------------------------------------------------------------------------
from grid.forecasting.confidence import calculate_confidence_score


class TestConfidence:
    def test_operational_full_confidence(self):
        score = calculate_confidence_score(
            horizon_regime='operational_forecast',
            weather_partially_missing=False,
            gas_conversion_fallback_used=False,
            scenario_paths=None,
            calibrated=True,
            baseline_only=False,
        )
        assert score == 90

    def test_extended_full_confidence(self):
        score = calculate_confidence_score(
            horizon_regime='extended_weather_forecast',
            weather_partially_missing=False,
            gas_conversion_fallback_used=False,
            scenario_paths=None,
            calibrated=True,
            baseline_only=False,
        )
        assert score == 70

    def test_planning_full_confidence(self):
        score = calculate_confidence_score(
            horizon_regime='planning_scenario_forecast',
            weather_partially_missing=False,
            gas_conversion_fallback_used=False,
            scenario_paths=100,
            calibrated=True,
            baseline_only=False,
        )
        assert score == 45

    def test_weather_missing_penalty(self):
        score = calculate_confidence_score(
            horizon_regime='operational_forecast',
            weather_partially_missing=True,
            gas_conversion_fallback_used=False,
            scenario_paths=None,
            calibrated=True,
            baseline_only=False,
        )
        assert score == 80

    def test_gas_fallback_penalty(self):
        score = calculate_confidence_score(
            horizon_regime='operational_forecast',
            weather_partially_missing=False,
            gas_conversion_fallback_used=True,
            scenario_paths=None,
            calibrated=True,
            baseline_only=False,
        )
        assert score == 80

    def test_low_scenario_paths_penalty(self):
        score = calculate_confidence_score(
            horizon_regime='planning_scenario_forecast',
            weather_partially_missing=False,
            gas_conversion_fallback_used=False,
            scenario_paths=10,
            calibrated=True,
            baseline_only=False,
        )
        assert score == 30

    def test_uncalibrated_penalty(self):
        score = calculate_confidence_score(
            horizon_regime='operational_forecast',
            weather_partially_missing=False,
            gas_conversion_fallback_used=False,
            scenario_paths=None,
            calibrated=False,
            baseline_only=False,
        )
        assert score == 80

    def test_baseline_only_penalty(self):
        score = calculate_confidence_score(
            horizon_regime='operational_forecast',
            weather_partially_missing=False,
            gas_conversion_fallback_used=False,
            scenario_paths=None,
            calibrated=True,
            baseline_only=True,
        )
        assert score == 70

    def test_score_clamped_at_zero(self):
        score = calculate_confidence_score(
            horizon_regime='planning_scenario_forecast',
            weather_partially_missing=True,
            gas_conversion_fallback_used=True,
            scenario_paths=5,
            calibrated=False,
            baseline_only=True,
        )
        assert score == 0

    def test_unknown_regime_returns_zero_base(self):
        score = calculate_confidence_score(
            horizon_regime='unknown_regime',
            weather_partially_missing=False,
            gas_conversion_fallback_used=False,
            scenario_paths=None,
            calibrated=True,
            baseline_only=False,
        )
        assert score == 0


# ---------------------------------------------------------------------------
# daily
# ---------------------------------------------------------------------------
from grid.forecasting.daily import aggregate_daily_predictions


def _make_hourly_rows(n: int = 4, run_id: str = 'run1', fuel: str = 'electricity') -> list[dict]:
    from zoneinfo import ZoneInfo

    london = ZoneInfo('Europe/London')
    base = datetime(2026, 6, 15, 0, tzinfo=UTC)
    rows = []
    for i in range(n):
        target = base + timedelta(hours=i + 1)
        rows.append(
            {
                'forecast_run_id': run_id,
                'fuel_type': fuel,
                'date_local': '2026-06-15',
                'target_time_local': target.astimezone(london),
                'p05': 28000.0 + i * 100,
                'p50': 30000.0 + i * 100,
                'p95': 32000.0 + i * 100,
                'forecast_regime': 'operational_forecast',
                'confidence_score': 85,
            }
        )
    return rows


class TestDailyAggregation:
    def test_returns_one_row_per_group(self):
        rows = _make_hourly_rows()
        result = aggregate_daily_predictions(rows)
        assert len(result) == 1

    def test_result_fields(self):
        rows = _make_hourly_rows()
        result = aggregate_daily_predictions(rows)
        row = result[0]
        assert row['forecast_run_id'] == 'run1'
        assert row['fuel_type'] == 'electricity'
        assert row['date_local'] == '2026-06-15'
        assert 'daily_total_p50' in row
        assert 'daily_total_p05' in row
        assert 'daily_total_p95' in row
        assert 'daily_average_p50' in row
        assert 'daily_peak_p50' in row
        assert 'daily_peak_time_local' in row

    def test_daily_total_p50_is_sum(self):
        rows = _make_hourly_rows(n=4)
        result = aggregate_daily_predictions(rows)
        expected = sum(row['p50'] for row in rows)
        assert result[0]['daily_total_p50'] == pytest.approx(expected)

    def test_confidence_score_is_min(self):
        rows = _make_hourly_rows()
        rows[0]['confidence_score'] = 50
        result = aggregate_daily_predictions(rows)
        assert result[0]['confidence_score'] == 50

    def test_multiple_fuel_types(self):
        elec = _make_hourly_rows(fuel='electricity')
        gas = _make_hourly_rows(fuel='gas')
        result = aggregate_daily_predictions(elec + gas)
        fuel_types = {row['fuel_type'] for row in result}
        assert fuel_types == {'electricity', 'gas'}

    def test_multiple_run_ids(self):
        rows1 = _make_hourly_rows(run_id='run1')
        rows2 = _make_hourly_rows(run_id='run2')
        result = aggregate_daily_predictions(rows1 + rows2)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# scenarios
# ---------------------------------------------------------------------------
from grid.forecasting.scenarios import (
    _quantile,
    build_historical_weather_analogue_paths,
    quantiles_from_scenarios,
)


class TestScenarios:
    def _make_weather_rows(self, base_time: datetime, n: int = 20) -> list[dict]:
        rows = []
        for i in range(n):
            ts = base_time.replace(year=base_time.year - 1) + timedelta(days=i - n // 2)
            rows.append({'target_time_utc': ts.replace(hour=base_time.hour), 'temperature_2m_c': 10.0 + i})
        return rows

    def test_analogue_filter_by_hour(self):
        target = datetime(2026, 6, 15, 12, tzinfo=UTC)
        rows = [
            {'target_time_utc': datetime(2025, 6, 16, 12, tzinfo=UTC), 'temperature_2m_c': 15.0},
            {'target_time_utc': datetime(2025, 6, 16, 13, tzinfo=UTC), 'temperature_2m_c': 16.0},
        ]
        result = build_historical_weather_analogue_paths(
            target_timestamp=target,
            historical_weather_rows=rows,
            window_days=30,
        )
        assert len(result) == 1
        assert result[0]['temperature_2m_c'] == 15.0

    def test_analogue_filter_by_day_of_year_window(self):
        target = datetime(2026, 6, 15, 12, tzinfo=UTC)
        close = datetime(2025, 6, 18, 12, tzinfo=UTC)  # within 14 days
        far = datetime(2025, 1, 1, 12, tzinfo=UTC)     # outside 14 days
        result = build_historical_weather_analogue_paths(
            target_timestamp=target,
            historical_weather_rows=[
                {'target_time_utc': close, 'temperature_2m_c': 10.0},
                {'target_time_utc': far, 'temperature_2m_c': 5.0},
            ],
            window_days=14,
        )
        assert len(result) == 1
        assert result[0]['temperature_2m_c'] == 10.0

    def test_quantiles_from_scenarios(self):
        target = datetime(2026, 6, 15, 12, tzinfo=UTC)
        rows = [{'target_time_utc': target, 'prediction': float(v)} for v in range(1, 101)]
        result = quantiles_from_scenarios(rows)
        assert target in result
        r = result[target]
        assert 'p05' in r
        assert 'p50' in r
        assert 'p95' in r
        assert r['scenario_paths'] == 100
        assert r['confidence_low'] is False

    def test_quantiles_below_30_paths_flags_low_confidence(self):
        target = datetime(2026, 6, 15, 12, tzinfo=UTC)
        rows = [{'target_time_utc': target, 'prediction': float(v)} for v in range(1, 20)]
        result = quantiles_from_scenarios(rows)
        assert result[target]['confidence_low'] is True

    def test_quantile_helper_single_value(self):
        assert _quantile([42.0], 0.5) == 42.0

    def test_quantile_helper_empty(self):
        assert _quantile([], 0.5) == 0.0

    def test_quantile_helper_median(self):
        values = sorted([1.0, 2.0, 3.0, 4.0, 5.0])
        assert _quantile(values, 0.5) == 3.0


# ---------------------------------------------------------------------------
# backtesting
# ---------------------------------------------------------------------------
from grid.forecasting.backtesting import compute_metrics, evaluate_interval_coverage, promotion_allowed


class TestBacktesting:
    def _rows(self):
        return [
            {'predicted': 100.0, 'actual': 90.0},
            {'predicted': 110.0, 'actual': 115.0},
            {'predicted': 95.0, 'actual': 100.0},
        ]

    def test_compute_metrics_keys(self):
        result = compute_metrics(self._rows())
        assert 'MAE' in result
        assert 'RMSE' in result
        assert 'WAPE' in result
        assert 'sMAPE' in result

    def test_compute_metrics_mae_positive(self):
        result = compute_metrics(self._rows())
        assert result['MAE'] is not None
        assert result['MAE'] >= 0

    def test_compute_metrics_rmse_gte_mae(self):
        result = compute_metrics(self._rows())
        assert result['RMSE'] >= result['MAE']

    def test_compute_metrics_empty_rows(self):
        result = compute_metrics([])
        assert result['MAE'] is None
        assert result['RMSE'] is None

    def test_compute_metrics_no_actual_skipped(self):
        rows = [{'predicted': 100.0}]
        result = compute_metrics(rows)
        assert result['MAE'] is None

    def test_evaluate_interval_coverage_all_covered(self):
        rows = [
            {'actual': 100.0, 'p10': 90.0, 'p90': 110.0},
            {'actual': 95.0, 'p10': 90.0, 'p90': 110.0},
        ]
        coverage = evaluate_interval_coverage(rows, 'p10', 'p90')
        assert coverage == 1.0

    def test_evaluate_interval_coverage_none_covered(self):
        rows = [
            {'actual': 200.0, 'p10': 90.0, 'p90': 110.0},
        ]
        coverage = evaluate_interval_coverage(rows, 'p10', 'p90')
        assert coverage == 0.0

    def test_evaluate_interval_coverage_empty(self):
        assert evaluate_interval_coverage([], 'p10', 'p90') is None

    def test_evaluate_interval_coverage_missing_values(self):
        rows = [{'actual': None, 'p10': 90.0, 'p90': 110.0}]
        assert evaluate_interval_coverage(rows, 'p10', 'p90') is None

    def test_promotion_allowed_passing(self):
        result = {
            'electricity_wape_beats_baseline': True,
            'gas_wape_beats_baseline': True,
            'interval_coverage_p10_p90': 0.82,
            'interval_coverage_p05_p95': 0.92,
            'missing_feature_group': False,
            'future_leakage_detected': False,
        }
        assert promotion_allowed(result) is True

    def test_promotion_blocked_by_electricity_wape(self):
        result = {
            'electricity_wape_beats_baseline': False,
            'gas_wape_beats_baseline': True,
            'interval_coverage_p10_p90': 0.82,
            'interval_coverage_p05_p95': 0.92,
            'missing_feature_group': False,
            'future_leakage_detected': False,
        }
        assert promotion_allowed(result) is False

    def test_promotion_blocked_by_interval_coverage_out_of_range(self):
        result = {
            'electricity_wape_beats_baseline': True,
            'gas_wape_beats_baseline': True,
            'interval_coverage_p10_p90': 0.50,
            'interval_coverage_p05_p95': 0.92,
            'missing_feature_group': False,
            'future_leakage_detected': False,
        }
        assert promotion_allowed(result) is False

    def test_promotion_blocked_by_future_leakage(self):
        result = {
            'electricity_wape_beats_baseline': True,
            'gas_wape_beats_baseline': True,
            'interval_coverage_p10_p90': 0.82,
            'interval_coverage_p05_p95': 0.92,
            'missing_feature_group': False,
            'future_leakage_detected': True,
        }
        assert promotion_allowed(result) is False

    def test_promotion_blocked_by_missing_feature_group(self):
        result = {
            'electricity_wape_beats_baseline': True,
            'gas_wape_beats_baseline': True,
            'interval_coverage_p10_p90': 0.82,
            'interval_coverage_p05_p95': 0.92,
            'missing_feature_group': True,
            'future_leakage_detected': False,
        }
        assert promotion_allowed(result) is False

    def test_promotion_blocked_by_none_interval(self):
        result = {
            'electricity_wape_beats_baseline': True,
            'gas_wape_beats_baseline': True,
            'interval_coverage_p10_p90': None,
            'interval_coverage_p05_p95': 0.92,
            'missing_feature_group': False,
            'future_leakage_detected': False,
        }
        assert promotion_allowed(result) is False


# ---------------------------------------------------------------------------
# explanations
# ---------------------------------------------------------------------------
from grid.forecasting.explanations import (
    ELECTRICITY_TEMPLATE,
    GAS_TEMPLATE,
    HIGH_UNCERTAINTY_TEMPLATE,
    aggregate_daily_explanations,
    build_hourly_explanation,
)


class TestExplanations:
    def _hourly_row(self, fuel='electricity', high_uncertainty=False):
        return build_hourly_explanation(
            forecast_run_id='run1',
            target_time_utc=datetime(2026, 6, 15, 12, tzinfo=UTC),
            fuel_type=fuel,
            top_features=['f1', 'f2', 'f3'],
            top_contributions=[0.5, 0.3, 0.2],
            feature_group_contributions={'weather': 0.5, 'calendar': 0.3, 'demand_lag': 0.2},
            high_uncertainty=high_uncertainty,
        )

    def test_build_hourly_electricity(self):
        row = self._hourly_row('electricity')
        assert row['fuel_type'] == 'electricity'
        assert ELECTRICITY_TEMPLATE in row['plain_language_summary']
        assert HIGH_UNCERTAINTY_TEMPLATE not in row['plain_language_summary']

    def test_build_hourly_gas(self):
        row = self._hourly_row('gas')
        assert GAS_TEMPLATE in row['plain_language_summary']

    def test_build_hourly_high_uncertainty(self):
        row = self._hourly_row(high_uncertainty=True)
        assert HIGH_UNCERTAINTY_TEMPLATE in row['plain_language_summary']

    def test_top_features_capped_at_10(self):
        row = build_hourly_explanation(
            forecast_run_id='run1',
            target_time_utc=datetime(2026, 6, 15, 12, tzinfo=UTC),
            fuel_type='electricity',
            top_features=[f'f{i}' for i in range(20)],
            top_contributions=[float(i) for i in range(20)],
            feature_group_contributions={},
            high_uncertainty=False,
        )
        assert len(row['top_10_features']) == 10
        assert len(row['top_10_feature_contributions']) == 10

    def test_aggregate_daily_explanations_groups_by_date(self):
        target = datetime(2026, 6, 15, 12, tzinfo=UTC)
        hourly_rows = []
        for hour in (12, 13, 14):
            hourly_rows.append(
                build_hourly_explanation(
                    forecast_run_id='run1',
                    target_time_utc=target.replace(hour=hour),
                    fuel_type='electricity',
                    top_features=['weather'],
                    top_contributions=[1.0],
                    feature_group_contributions={'weather': 1.0},
                    high_uncertainty=False,
                )
            )
            hourly_rows[-1]['date_local'] = '2026-06-15'

        result = aggregate_daily_explanations(hourly_rows)
        assert len(result) == 1
        assert result[0]['date_local'] == '2026-06-15'
        assert result[0]['fuel_type'] == 'electricity'
        assert result[0]['feature_group_contributions']['weather'] == pytest.approx(3.0)

    def test_aggregate_daily_explanations_multiple_fuel_types(self):
        rows = []
        for fuel in ('electricity', 'gas'):
            row = self._hourly_row(fuel)
            row['date_local'] = '2026-06-15'
            rows.append(row)
        result = aggregate_daily_explanations(rows)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# features
# ---------------------------------------------------------------------------
from grid.forecasting.features import (
    GB_FEATURE_MAP,
    add_demand_lag_features,
    build_national_weighted_weather,
)


class TestWeatherFeatures:
    def _make_weather_rows(self, n: int = 3) -> list[dict]:
        regions = load_weather_regions()
        rows = []
        for region in regions[:2]:
            for i in range(n):
                ts = datetime(2026, 6, 15, i, tzinfo=UTC)
                rows.append(
                    {
                        'region_id': region.region_id,
                        'target_time_utc': ts,
                        'temperature_2m_c': 15.0,
                        'apparent_temperature_c': 14.0,
                        'wind_speed_10m_ms': 5.0,
                        'cloud_cover_percent': 60.0,
                        'shortwave_radiation_wm2': 100.0,
                        'precipitation_mm': 0.0,
                        'relative_humidity_percent': 70.0,
                    }
                )
        return rows

    def test_weighted_weather_returns_dict(self):
        regions = load_weather_regions()
        rows = self._make_weather_rows()
        result = build_national_weighted_weather(regions, rows)
        assert isinstance(result, dict)

    def test_weighted_weather_gb_keys_present(self):
        regions = load_weather_regions()
        rows = self._make_weather_rows()
        result = build_national_weighted_weather(regions, rows)
        for ts, entry in result.items():
            for gb_name in GB_FEATURE_MAP.values():
                assert gb_name in entry

    def test_weighted_weather_derived_features(self):
        regions = load_weather_regions()
        rows = self._make_weather_rows(n=24)
        result = build_national_weighted_weather(regions, rows)
        # derived features should be present
        for ts, entry in result.items():
            assert 'heating_degree_hours' in entry
            assert 'cooling_degree_hours' in entry
            assert 'cold_snap_indicator' in entry
            assert 'heatwave_indicator' in entry

    def test_weighted_weather_empty_rows(self):
        regions = load_weather_regions()
        result = build_national_weighted_weather(regions, [])
        assert result == {}


class TestDemandLagFeatures:
    def _history(self) -> dict:
        base = datetime(2026, 6, 15, 12, tzinfo=UTC)
        return {base - timedelta(hours=i): 30000.0 + i for i in range(1, 200)}

    def test_short_horizon_adds_lags(self):
        target = datetime(2026, 6, 15, 12, tzinfo=UTC)
        history = self._history()
        row = {}
        result = add_demand_lag_features(
            row,
            target_time_utc=target,
            horizon_hours=12,
            history_by_time=history,
            feature_prefix='electricity',
        )
        assert result['electricity_lag_1h'] is not None
        assert result['electricity_lag_24h'] is not None
        assert result['electricity_recent_lag_available'] is True

    def test_long_horizon_disables_lags(self):
        target = datetime(2026, 6, 15, 12, tzinfo=UTC)
        history = self._history()
        row = {}
        result = add_demand_lag_features(
            row,
            target_time_utc=target,
            horizon_hours=900,
            history_by_time=history,
            feature_prefix='gas',
        )
        assert result['gas_recent_lag_available'] is False
        assert result['gas_lag_1h'] is None

    def test_missing_history_returns_none_lags(self):
        target = datetime(2026, 6, 15, 12, tzinfo=UTC)
        row = {}
        result = add_demand_lag_features(
            row,
            target_time_utc=target,
            horizon_hours=12,
            history_by_time={},
            feature_prefix='electricity',
        )
        assert result['electricity_lag_1h'] is None


# ---------------------------------------------------------------------------
# adapters — electricity
# ---------------------------------------------------------------------------
from grid.forecasting.adapters.electricity import normalize_electricity_rows


class TestElectricityAdapter:
    def _row(self, ts: str, value: float) -> dict:
        return {'timestamp_utc': ts, 'electricity_demand_mw': value}

    def test_hourly_granularity(self):
        rows = [
            {'timestamp_utc': '2026-06-15T12:00:00+00:00', 'electricity_demand_mwh': 30000.0},
        ]
        result = normalize_electricity_rows(
            rows,
            source_name='test',
            source_dataset='test_ds',
            source_publish_time_utc='2026-06-15T12:00:00+00:00',
            granularity_minutes=60,
        )
        assert len(result) == 1
        assert result[0]['electricity_demand_mwh'] == pytest.approx(30000.0)

    def test_30min_granularity_aggregates_to_hourly(self):
        rows = [
            {'timestamp_utc': '2026-06-15T12:00:00+00:00', 'electricity_demand_mw': 30000.0},
            {'timestamp_utc': '2026-06-15T12:30:00+00:00', 'electricity_demand_mw': 32000.0},
        ]
        result = normalize_electricity_rows(
            rows,
            source_name='test',
            source_dataset='test_ds',
            source_publish_time_utc='2026-06-15T12:00:00+00:00',
            granularity_minutes=30,
        )
        assert len(result) == 1
        expected_mwh = 30000.0 * 0.5 + 32000.0 * 0.5
        assert result[0]['electricity_demand_mwh'] == pytest.approx(expected_mwh)

    def test_30min_granularity_multiple_hours(self):
        rows = [
            {'timestamp_utc': '2026-06-15T12:00:00+00:00', 'electricity_demand_mw': 30000.0},
            {'timestamp_utc': '2026-06-15T12:30:00+00:00', 'electricity_demand_mw': 32000.0},
            {'timestamp_utc': '2026-06-15T13:00:00+00:00', 'electricity_demand_mw': 28000.0},
            {'timestamp_utc': '2026-06-15T13:30:00+00:00', 'electricity_demand_mw': 29000.0},
        ]
        result = normalize_electricity_rows(
            rows,
            source_name='test',
            source_dataset='test_ds',
            source_publish_time_utc='2026-06-15T12:00:00+00:00',
            granularity_minutes=30,
        )
        assert len(result) == 2

    def test_source_fields_set(self):
        rows = [{'timestamp_utc': '2026-06-15T12:00:00+00:00', 'electricity_demand_mwh': 30000.0}]
        result = normalize_electricity_rows(
            rows,
            source_name='elexon',
            source_dataset='B0620',
            source_publish_time_utc='2026-06-15T12:00:00+00:00',
        )
        assert result[0]['source_name'] == 'elexon'
        assert result[0]['source_dataset'] == 'B0620'

    def test_datetime_publish_time_accepted(self):
        rows = [{'timestamp_utc': '2026-06-15T12:00:00+00:00', 'electricity_demand_mwh': 30000.0}]
        result = normalize_electricity_rows(
            rows,
            source_name='test',
            source_dataset='ds',
            source_publish_time_utc=datetime(2026, 6, 15, 12, tzinfo=UTC),
        )
        assert len(result) == 1


# ---------------------------------------------------------------------------
# adapters — gas
# ---------------------------------------------------------------------------
from grid.forecasting.adapters.gas import convert_gas_to_mwh_equivalent, normalize_gas_rows


class TestGasAdapter:
    def _config(self):
        return {
            'default_fallback_calorific_value_kwh_per_m3': 10.5,
            'units': {
                'kwh': {'to_mwh_factor': 0.001, 'requires_calorific_value': False},
                'm3': {'conversion_method': 'volume_to_energy', 'requires_calorific_value': True},
                'mcm': {'conversion_method': 'volume_to_energy', 'requires_calorific_value': True, 'm3_per_mcm': 1_000_000},
            },
        }

    def test_kwh_unit_conversion(self):
        mwh, cv, method, fallback = convert_gas_to_mwh_equivalent(
            2000, 'kwh', None, gas_conversion_config=self._config()
        )
        assert mwh == pytest.approx(2.0)
        assert fallback is False
        assert method == 'unit_factor'

    def test_m3_with_known_cv(self):
        mwh, cv, method, fallback = convert_gas_to_mwh_equivalent(
            1000, 'm3', 11.0, gas_conversion_config=self._config()
        )
        assert mwh == pytest.approx(1000 * 11.0 / 1000.0)
        assert fallback is False
        assert method == 'volume_to_energy'

    def test_m3_with_no_cv_uses_fallback(self):
        mwh, cv, method, fallback = convert_gas_to_mwh_equivalent(
            1000, 'm3', None, gas_conversion_config=self._config()
        )
        assert mwh == pytest.approx(1000 * 10.5 / 1000.0)
        assert fallback is True

    def test_unknown_unit_returns_missing(self):
        mwh, cv, method, fallback = convert_gas_to_mwh_equivalent(
            100, 'barrels', None, gas_conversion_config=self._config()
        )
        assert mwh is None
        assert method == 'missing_gas_conversion'

    def test_mcm_conversion(self):
        mwh, cv, method, fallback = convert_gas_to_mwh_equivalent(
            0.001, 'mcm', 11.0, gas_conversion_config=self._config()
        )
        expected = (0.001 * 1_000_000 * 11.0) / 1000.0
        assert mwh == pytest.approx(expected)

    def test_normalize_gas_rows_valid(self):
        config = self._config()
        rows = [
            {
                'timestamp_utc': '2026-06-15T12:00:00+00:00',
                'gas_demand_original_value': 1000.0,
                'gas_demand_original_unit': 'kwh',
                'calorific_value': None,
            }
        ]
        result = normalize_gas_rows(
            rows,
            source_name='national_gas',
            source_dataset='gas_ds',
            source_publish_time_utc='2026-06-15T12:00:00+00:00',
            gas_conversion_config=config,
        )
        assert len(result) == 1
        assert result[0]['valid_for_training'] is True
        assert result[0]['gas_demand_mwh_equivalent'] == pytest.approx(1.0)

    def test_normalize_gas_rows_invalid_unit(self):
        config = self._config()
        rows = [
            {
                'timestamp_utc': '2026-06-15T12:00:00+00:00',
                'gas_demand_original_value': 100.0,
                'gas_demand_original_unit': 'barrels',
                'calorific_value': None,
            }
        ]
        result = normalize_gas_rows(
            rows,
            source_name='test',
            source_dataset='ds',
            source_publish_time_utc='2026-06-15T12:00:00+00:00',
            gas_conversion_config=config,
        )
        assert result[0]['valid_for_training'] is False


# ---------------------------------------------------------------------------
# adapters — weather
# ---------------------------------------------------------------------------
from grid.forecasting.adapters.weather import (
    MetOfficeAdapterPlaceholder,
    OpenMeteoAdapter,
    normalize_open_meteo_payload,
)


class TestWeatherAdapter:
    def _payload(self, n: int = 3) -> dict:
        times = [(datetime(2026, 6, 15, i, tzinfo=UTC)).isoformat() for i in range(n)]
        return {
            'hourly': {
                'time': times,
                'temperature_2m': [15.0] * n,
                'apparent_temperature': [14.0] * n,
                'wind_speed_10m': [5.0] * n,
                'cloud_cover': [60.0] * n,
                'shortwave_radiation': [100.0] * n,
                'precipitation': [0.0] * n,
                'relative_humidity_2m': [70.0] * n,
            }
        }

    def test_normalize_returns_correct_count(self):
        result = normalize_open_meteo_payload(self._payload(3), weather_source='Open-Meteo')
        assert len(result) == 3

    def test_normalize_fields_present(self):
        result = normalize_open_meteo_payload(self._payload(1), weather_source='Open-Meteo')
        row = result[0]
        assert 'temperature_2m_c' in row
        assert 'wind_speed_10m_ms' in row
        assert 'cloud_cover_percent' in row
        assert 'shortwave_radiation_wm2' in row
        assert 'precipitation_mm' in row
        assert 'relative_humidity_percent' in row
        assert 'weather_source' in row
        assert row['weather_source'] == 'Open-Meteo'

    def test_normalize_empty_payload(self):
        result = normalize_open_meteo_payload({}, weather_source='Open-Meteo')
        assert result == []

    def test_open_meteo_adapter_invalid_mode(self):
        with pytest.raises(ValueError):
            OpenMeteoAdapter(mode='invalid')

    def test_open_meteo_adapter_valid_modes(self):
        assert OpenMeteoAdapter(mode='forecast').mode == 'forecast'
        assert OpenMeteoAdapter(mode='historical').mode == 'historical'

    def test_open_meteo_adapter_fetch_calls_requests(self):
        adapter = OpenMeteoAdapter(mode='forecast')
        mock_response = MagicMock()
        mock_response.json.return_value = self._payload(2)
        mock_response.raise_for_status.return_value = None
        with patch('grid.forecasting.adapters.weather.requests.get', return_value=mock_response) as mock_get:
            rows = adapter.fetch(
                latitude=51.5,
                longitude=-0.1,
                start_utc=datetime(2026, 6, 15, tzinfo=UTC),
                end_utc=datetime(2026, 6, 16, tzinfo=UTC),
            )
        assert mock_get.called
        assert len(rows) == 2

    def test_open_meteo_archive_adapter_uses_archive_url(self):
        adapter = OpenMeteoAdapter(mode='historical')
        mock_response = MagicMock()
        mock_response.json.return_value = self._payload(1)
        mock_response.raise_for_status.return_value = None
        with patch('grid.forecasting.adapters.weather.requests.get', return_value=mock_response) as mock_get:
            adapter.fetch(
                latitude=51.5,
                longitude=-0.1,
                start_utc=datetime(2026, 6, 15, tzinfo=UTC),
                end_utc=datetime(2026, 6, 16, tzinfo=UTC),
            )
        url_called = mock_get.call_args[0][0]
        assert 'archive' in url_called

    def test_met_office_adapter_raises(self):
        adapter = MetOfficeAdapterPlaceholder()
        with pytest.raises(NotImplementedError):
            adapter.fetch(
                latitude=51.5,
                longitude=-0.1,
                start_utc=datetime(2026, 6, 15, tzinfo=UTC),
                end_utc=datetime(2026, 6, 16, tzinfo=UTC),
            )

    def test_normalize_missing_keys_returns_none(self):
        payload = {'hourly': {'time': ['2026-06-15T00:00:00'], 'temperature_2m': [15.0]}}
        result = normalize_open_meteo_payload(payload, weather_source='Open-Meteo')
        assert len(result) == 1
        assert result[0]['wind_speed_10m_ms'] is None


# ---------------------------------------------------------------------------
# models — baselines
# ---------------------------------------------------------------------------
from grid.forecasting.models.baselines import (
    official_forecast_where_available,
    same_hour_last_week,
    same_hour_yesterday,
    seasonal_hour_day_month_average,
)


class TestBaselines:
    def _history(self) -> dict:
        base = datetime(2026, 6, 15, 12, tzinfo=UTC)
        return {base - timedelta(hours=i): 30000.0 + i for i in range(200)}

    def test_same_hour_yesterday(self):
        target = datetime(2026, 6, 15, 12, tzinfo=UTC)
        history = {target - timedelta(hours=24): 29000.0}
        assert same_hour_yesterday(history, target) == 29000.0

    def test_same_hour_yesterday_missing(self):
        target = datetime(2026, 6, 15, 12, tzinfo=UTC)
        assert same_hour_yesterday({}, target) is None

    def test_same_hour_last_week(self):
        target = datetime(2026, 6, 15, 12, tzinfo=UTC)
        history = {target - timedelta(hours=168): 27000.0}
        assert same_hour_last_week(history, target) == 27000.0

    def test_seasonal_average_match(self):
        target = datetime(2026, 6, 15, 12, tzinfo=UTC)
        history_rows = [
            {'timestamp_utc': datetime(2025, 6, 15, 12, tzinfo=UTC), 'value': 28000.0},
            {'timestamp_utc': datetime(2024, 6, 15, 12, tzinfo=UTC), 'value': 30000.0},
        ]
        result = seasonal_hour_day_month_average(history_rows, target)
        assert result == pytest.approx(29000.0)

    def test_seasonal_average_no_match(self):
        target = datetime(2026, 6, 15, 12, tzinfo=UTC)
        result = seasonal_hour_day_month_average([], target)
        assert result is None

    def test_official_forecast_where_available_found(self):
        target = datetime(2026, 6, 15, 12, tzinfo=UTC)
        forecasts = {target: 31000.0}
        assert official_forecast_where_available(forecasts, target) == 31000.0

    def test_official_forecast_where_available_missing(self):
        target = datetime(2026, 6, 15, 12, tzinfo=UTC)
        assert official_forecast_where_available({}, target) is None


# ---------------------------------------------------------------------------
# models — calibration
# ---------------------------------------------------------------------------
from grid.forecasting.models.calibration import apply_conformal_calibration, conformal_adjustments


class TestCalibration:
    def _backtest_rows(self):
        return [
            {'fuel_type': 'electricity', 'horizon_regime': 'operational_forecast', 'season': 'winter', 'actual': 100.0, 'p50': 98.0},
            {'fuel_type': 'electricity', 'horizon_regime': 'operational_forecast', 'season': 'winter', 'actual': 110.0, 'p50': 107.0},
            {'fuel_type': 'electricity', 'horizon_regime': 'operational_forecast', 'season': 'winter', 'actual': 90.0, 'p50': 91.0},
        ]

    def test_conformal_adjustments_returns_dict(self):
        result = conformal_adjustments(self._backtest_rows())
        assert isinstance(result, dict)

    def test_conformal_adjustments_key_structure(self):
        result = conformal_adjustments(self._backtest_rows())
        key = ('electricity', 'operational_forecast', 'winter')
        assert key in result
        assert 'p10_p90_adjustment' in result[key]
        assert 'p05_p95_adjustment' in result[key]
        assert result[key]['calibration_status'] == 'calibrated'

    def test_conformal_adjustments_empty(self):
        result = conformal_adjustments([])
        assert result == {}

    def test_apply_conformal_calibration_with_adjustment(self):
        row = {'p50': 100.0, 'p10': None, 'p90': None, 'p05': None, 'p95': None}
        adjustment = {'p10_p90_adjustment': 5.0, 'p05_p95_adjustment': 10.0}
        result = apply_conformal_calibration(row, adjustment)
        assert result['p10'] == pytest.approx(95.0)
        assert result['p90'] == pytest.approx(105.0)
        assert result['p05'] == pytest.approx(90.0)
        assert result['p95'] == pytest.approx(110.0)
        assert result['calibration_status'] == 'calibrated'

    def test_apply_conformal_calibration_no_adjustment(self):
        row = {'p50': 100.0}
        result = apply_conformal_calibration(row, None)
        assert result['calibration_status'] == 'uncalibrated'


# ---------------------------------------------------------------------------
# models — lightgbm_models
# ---------------------------------------------------------------------------
from grid.forecasting.models.lightgbm_models import (
    ForecastModelRegistry,
    LightGBMQuantileModel,
    required_lightgbm_specs,
)


class TestLightGBMModels:
    def test_required_specs_count(self):
        specs = required_lightgbm_specs()
        # 2 fuels × 3 regimes × 7 quantiles = 42
        assert len(specs) == 42

    def test_required_specs_fuel_types(self):
        specs = required_lightgbm_specs()
        fuels = {s.fuel_type for s in specs}
        assert fuels == {'electricity', 'gas'}

    def test_registry_register_and_get(self):
        registry = ForecastModelRegistry()
        mock_model = object()
        registry.register('electricity', 'operational_forecast', 'p50', mock_model)
        assert registry.get('electricity', 'operational_forecast', 'p50') is mock_model

    def test_registry_get_missing_returns_none(self):
        registry = ForecastModelRegistry()
        assert registry.get('electricity', 'operational_forecast', 'p50') is None

    def test_registry_versions(self):
        registry = ForecastModelRegistry()
        registry.register('electricity', 'operational_forecast', 'p50', object())
        versions = registry.versions()
        assert len(versions) == 1
        assert versions[0]['fuel_type'] == 'electricity'
        assert versions[0]['quantile'] == 'p50'

    def test_lightgbm_model_predict_before_fit_raises(self):
        model = LightGBMQuantileModel(0.5)
        with pytest.raises(RuntimeError, match='model_not_trained'):
            model.predict([[1.0, 2.0]])


# ---------------------------------------------------------------------------
# pipelines — datasets
# ---------------------------------------------------------------------------
from grid.forecasting.pipelines.datasets import build_asof_dataset, build_hindsight_dataset


class TestDatasets:
    def _rows(self) -> list[dict]:
        issue = datetime(2026, 6, 15, 12, tzinfo=UTC)
        return [
            {
                'forecast_issue_time_utc': issue,
                'target_value': 30000.0,
                'source_publish_time_utc': issue - timedelta(hours=1),
                'weather_run_time_utc': issue - timedelta(hours=2),
                'uses_actual_future_weather': False,
            },
            {
                'forecast_issue_time_utc': issue,
                'target_value': None,
                'source_publish_time_utc': issue - timedelta(hours=1),
                'weather_run_time_utc': None,
                'uses_actual_future_weather': False,
            },
        ]

    def test_hindsight_excludes_missing_target(self):
        result = build_hindsight_dataset(self._rows())
        assert len(result) == 1
        assert result[0]['dataset_mode'] == 'hindsight'

    def test_hindsight_includes_valid_rows(self):
        result = build_hindsight_dataset(self._rows())
        assert result[0]['target_value'] == 30000.0

    def test_asof_excludes_missing_target(self):
        result = build_asof_dataset(self._rows())
        assert all(row['target_value'] is not None for row in result)

    def test_asof_excludes_future_publish_time(self):
        issue = datetime(2026, 6, 15, 12, tzinfo=UTC)
        rows = [
            {
                'forecast_issue_time_utc': issue,
                'target_value': 30000.0,
                'source_publish_time_utc': issue + timedelta(hours=1),
                'weather_run_time_utc': None,
                'uses_actual_future_weather': False,
            }
        ]
        result = build_asof_dataset(rows)
        assert len(result) == 0

    def test_asof_excludes_future_weather_run(self):
        issue = datetime(2026, 6, 15, 12, tzinfo=UTC)
        rows = [
            {
                'forecast_issue_time_utc': issue,
                'target_value': 30000.0,
                'source_publish_time_utc': None,
                'weather_run_time_utc': issue + timedelta(hours=1),
                'uses_actual_future_weather': False,
            }
        ]
        result = build_asof_dataset(rows)
        assert len(result) == 0

    def test_asof_excludes_actual_future_weather(self):
        issue = datetime(2026, 6, 15, 12, tzinfo=UTC)
        rows = [
            {
                'forecast_issue_time_utc': issue,
                'target_value': 30000.0,
                'source_publish_time_utc': None,
                'weather_run_time_utc': None,
                'uses_actual_future_weather': True,
            }
        ]
        result = build_asof_dataset(rows)
        assert len(result) == 0

    def test_asof_valid_row_included(self):
        issue = datetime(2026, 6, 15, 12, tzinfo=UTC)
        rows = [
            {
                'forecast_issue_time_utc': issue,
                'target_value': 30000.0,
                'source_publish_time_utc': issue - timedelta(hours=1),
                'weather_run_time_utc': None,
                'uses_actual_future_weather': False,
            }
        ]
        result = build_asof_dataset(rows)
        assert len(result) == 1
        assert result[0]['dataset_mode'] == 'asof'


# ---------------------------------------------------------------------------
# pipelines — workflows
# ---------------------------------------------------------------------------
from grid.forecasting.pipelines.workflows import (
    FORECAST_RUN_STEPS,
    TRAINING_WORKFLOW_STEPS,
    run_workflow_steps,
)


class TestWorkflows:
    def test_forecast_run_steps_non_empty(self):
        assert len(FORECAST_RUN_STEPS) > 0

    def test_training_workflow_steps_non_empty(self):
        assert len(TRAINING_WORKFLOW_STEPS) > 0

    def test_run_workflow_steps_returns_one_per_step(self):
        steps = ['step_a', 'step_b']
        results = run_workflow_steps(steps)
        assert len(results) == 2

    def test_run_workflow_steps_all_completed(self):
        results = run_workflow_steps(FORECAST_RUN_STEPS)
        assert all(r.status == 'completed' for r in results)

    def test_run_workflow_steps_names_preserved(self):
        results = run_workflow_steps(['my_step'])
        assert results[0].step == 'my_step'


# ---------------------------------------------------------------------------
# service — extended
# ---------------------------------------------------------------------------
from grid.forecasting.service import ForecastService, ForecastStore


class TestForecastServiceExtended:
    def setup_method(self):
        self.store = ForecastStore()
        self.service = ForecastService(self.store)
        self.service.seed_demo_run()

    def test_get_hourly_returns_matching_fuel_type(self):
        start = datetime(2020, 1, 1, tzinfo=UTC)
        end = datetime(2030, 1, 1, tzinfo=UTC)
        rows = self.service.get_hourly('electricity', start, end)
        assert all(row['fuel_type'] == 'electricity' for row in rows)

    def test_get_hourly_filters_by_time(self):
        from datetime import UTC
        issue = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
        start = issue + timedelta(hours=1)
        end = issue + timedelta(hours=1)
        rows = self.service.get_hourly('electricity', start, end)
        assert len(rows) >= 1

    def test_get_daily_returns_rows(self):
        from datetime import date
        rows = self.service.get_daily('electricity', date(2020, 1, 1), date(2035, 1, 1))
        assert len(rows) > 0

    def test_get_daily_fuel_type_filter(self):
        from datetime import date
        rows = self.service.get_daily('gas', date(2020, 1, 1), date(2035, 1, 1))
        assert all(row['fuel_type'] == 'gas' for row in rows)

    def test_get_hourly_explanation_not_found(self):
        result = self.service.get_hourly_explanation('nonexistent', 'electricity', datetime(2026, 1, 1, tzinfo=UTC))
        assert result is None

    def test_get_daily_explanation_not_found(self):
        result = self.service.get_daily_explanation('nonexistent', 'electricity', '2026-01-01')
        assert result is None

    def test_get_model_status(self):
        status = self.service.get_model_status()
        assert status.latest_forecast_run is not None
        assert isinstance(status.model_versions, list)
        assert isinstance(status.training_data_range, dict)
        assert isinstance(status.latest_backtest_metrics, list)
        assert isinstance(status.data_source_status, dict)

    def test_get_backtest_summary_empty(self):
        result = self.service.get_backtest_summary()
        assert isinstance(result, list)

    def test_combined_rows_present(self):
        start = datetime(2020, 1, 1, tzinfo=UTC)
        end = datetime(2030, 1, 1, tzinfo=UTC)
        combined = self.service.get_hourly('combined', start, end)
        assert len(combined) > 0

    def test_seed_with_explicit_issue_time(self):
        issue = datetime(2026, 1, 1, 6, tzinfo=UTC)
        self.service.seed_demo_run(issue_time_utc=issue)
        assert self.store.latest_forecast_run is not None

    def test_store_initializes_empty(self):
        store = ForecastStore()
        assert store.hourly_rows == []
        assert store.daily_rows == []
        assert store.latest_forecast_run is None
