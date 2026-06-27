from dataclasses import dataclass
from enum import Enum

FORECAST_LABEL = 'Great Britain national electricity and gas demand forecast'
MIN_HORIZON_HOURS = 1
MAX_HORIZON_HOURS = 8760
QUANTILES = ('p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95')


class FuelType(str, Enum):
    ELECTRICITY = 'electricity'
    GAS = 'gas'
    COMBINED = 'combined'


class ForecastRegime(str, Enum):
    OPERATIONAL = 'operational_forecast'
    EXTENDED_WEATHER = 'extended_weather_forecast'
    PLANNING_SCENARIO = 'planning_scenario_forecast'


@dataclass(frozen=True)
class RegimeRange:
    name: ForecastRegime
    min_horizon: int
    max_horizon: int


REGIME_RANGES = (
    RegimeRange(ForecastRegime.OPERATIONAL, 1, 72),
    RegimeRange(ForecastRegime.EXTENDED_WEATHER, 73, 840),
    RegimeRange(ForecastRegime.PLANNING_SCENARIO, 841, 8760),
)


def get_regime(horizon_hours: int) -> ForecastRegime:
    if horizon_hours < MIN_HORIZON_HOURS or horizon_hours > MAX_HORIZON_HOURS:
        raise ValueError(f'horizon_hours must be between {MIN_HORIZON_HOURS} and {MAX_HORIZON_HOURS}')
    for regime in REGIME_RANGES:
        if regime.min_horizon <= horizon_hours <= regime.max_horizon:
            return regime.name
    raise ValueError('no forecast regime available for horizon')
