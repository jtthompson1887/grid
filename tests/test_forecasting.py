from datetime import UTC, datetime

import pytest

from grid.forecasting.adapters.gas import convert_gas_to_mwh_equivalent
from grid.forecasting.config import load_weather_regions
from grid.forecasting.time_spine import generate_hourly_time_spine


class TestWeatherRegionConfig:
    def test_weights_sum_to_one(self):
        regions = load_weather_regions()
        assert regions
        assert abs(sum(region.weight for region in regions) - 1.0) < 1e-9


class TestGasConversion:
    def test_converts_kwh(self):
        config = {
            'default_fallback_calorific_value_kwh_per_m3': None,
            'units': {'kwh': {'to_mwh_factor': 0.001, 'requires_calorific_value': False}},
        }
        mwh, cv, method, fallback = convert_gas_to_mwh_equivalent(
            1250,
            'kwh',
            None,
            gas_conversion_config=config,
        )
        assert mwh == pytest.approx(1.25)
        assert cv is None
        assert method == 'unit_factor'
        assert fallback is False

    def test_volume_missing_cv_marks_missing(self):
        config = {
            'default_fallback_calorific_value_kwh_per_m3': None,
            'units': {'m3': {'conversion_method': 'volume_to_energy', 'requires_calorific_value': True}},
        }
        mwh, cv, method, fallback = convert_gas_to_mwh_equivalent(
            100,
            'm3',
            None,
            gas_conversion_config=config,
        )
        assert mwh is None
        assert cv is None
        assert method == 'missing_gas_conversion'
        assert fallback is False


class TestTimeSpine:
    def test_generates_full_hourly_range(self):
        issue = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
        rows = generate_hourly_time_spine(issue)
        assert len(rows) == 8760
        assert rows[0]['horizon_hours'] == 1
        assert rows[-1]['horizon_hours'] == 8760

    def test_regime_assignment_boundaries(self):
        issue = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
        rows = generate_hourly_time_spine(issue)
        assert rows[71]['forecast_horizon_regime'] == 'operational_forecast'
        assert rows[72]['forecast_horizon_regime'] == 'extended_weather_forecast'
        assert rows[840]['forecast_horizon_regime'] == 'planning_scenario_forecast'
