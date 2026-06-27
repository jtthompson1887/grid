from collections import defaultdict


def build_historical_weather_analogue_paths(
    *,
    target_timestamp,
    historical_weather_rows: list[dict],
    window_days: int = 14,
) -> list[dict]:
    matches = []
    day_of_year = target_timestamp.timetuple().tm_yday

    for row in historical_weather_rows:
        ts = row['target_time_utc']
        if ts.hour != target_timestamp.hour:
            continue
        if abs(ts.timetuple().tm_yday - day_of_year) > window_days:
            continue
        matches.append(row)
    return matches


def quantiles_from_scenarios(prediction_rows: list[dict]) -> dict:
    by_target = defaultdict(list)
    for row in prediction_rows:
        by_target[row['target_time_utc']].append(float(row['prediction']))

    out = {}
    for target_time, values in by_target.items():
        values = sorted(values)
        if not values:
            continue
        out[target_time] = {
            'p05': _quantile(values, 0.05),
            'p10': _quantile(values, 0.10),
            'p25': _quantile(values, 0.25),
            'p50': _quantile(values, 0.50),
            'p75': _quantile(values, 0.75),
            'p90': _quantile(values, 0.90),
            'p95': _quantile(values, 0.95),
            'scenario_paths': len(values),
            'forecast_regime': 'planning_scenario_forecast',
            'weather_mode': 'historical_weather_analogue',
            'confidence_low': len(values) < 30,
        }
    return out


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    idx = int(round((len(values) - 1) * q))
    return values[idx]
