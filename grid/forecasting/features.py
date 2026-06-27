from collections import defaultdict
from datetime import datetime, timedelta
from statistics import mean

from .config import WeatherRegion

REGION_WEATHER_FIELDS = [
    'temperature_2m_c',
    'apparent_temperature_c',
    'wind_speed_10m_ms',
    'cloud_cover_percent',
    'shortwave_radiation_wm2',
    'precipitation_mm',
    'relative_humidity_percent',
]

GB_FEATURE_MAP = {
    'temperature_2m_c': 'gb_temperature_2m_c',
    'apparent_temperature_c': 'gb_apparent_temperature_c',
    'wind_speed_10m_ms': 'gb_wind_speed_10m_ms',
    'cloud_cover_percent': 'gb_cloud_cover_percent',
    'shortwave_radiation_wm2': 'gb_shortwave_radiation_wm2',
    'precipitation_mm': 'gb_precipitation_mm',
    'relative_humidity_percent': 'gb_relative_humidity_percent',
}


def build_national_weighted_weather(regions: list[WeatherRegion], weather_rows: list[dict]) -> dict[datetime, dict]:
    rows_by_time: dict[datetime, list[dict]] = defaultdict(list)
    for row in weather_rows:
        rows_by_time[row['target_time_utc']].append(row)

    region_weights = {region.region_id: region.weight for region in regions}
    weighted: dict[datetime, dict] = {}

    for target_time, rows in rows_by_time.items():
        aggregate = {gb_name: 0.0 for gb_name in GB_FEATURE_MAP.values()}
        for row in rows:
            region_id = row.get('region_id')
            weight = region_weights.get(region_id, 0.0)
            for source_name, gb_name in GB_FEATURE_MAP.items():
                aggregate[gb_name] += float(row.get(source_name, 0.0)) * weight
        weighted[target_time] = aggregate

    ordered_times = sorted(weighted.keys())
    for target_time in ordered_times:
        current = weighted[target_time]
        temp = current['gb_temperature_2m_c']
        current['heating_degree_hours'] = max(0.0, 15.5 - temp)
        current['cooling_degree_hours'] = max(0.0, temp - 20.0)
        current['cold_snap_indicator'] = 1 if temp < 0 else 0
        current['heatwave_indicator'] = 1 if temp >= 25 else 0
        current['temperature_change_24h'] = _delta(weighted, target_time, 24, 'gb_temperature_2m_c')
        current['temperature_change_72h'] = _delta(weighted, target_time, 72, 'gb_temperature_2m_c')
        current['heating_degree_rolling_24h'] = _rolling_mean(weighted, target_time, 24, 'heating_degree_hours')
        current['heating_degree_rolling_72h'] = _rolling_mean(weighted, target_time, 72, 'heating_degree_hours')
        current['cooling_degree_rolling_24h'] = _rolling_mean(weighted, target_time, 24, 'cooling_degree_hours')
        current['cooling_degree_rolling_72h'] = _rolling_mean(weighted, target_time, 72, 'cooling_degree_hours')

    return weighted


def add_demand_lag_features(
    target_row: dict,
    *,
    target_time_utc: datetime,
    horizon_hours: int,
    history_by_time: dict[datetime, float],
    feature_prefix: str,
) -> dict:
    if horizon_hours > 840:
        target_row[f'{feature_prefix}_recent_lag_available'] = False
        for key in ['lag_1h', 'lag_2h', 'lag_24h', 'lag_48h', 'lag_168h']:
            target_row[f'{feature_prefix}_{key}'] = None
        return target_row

    target_row[f'{feature_prefix}_recent_lag_available'] = True
    lag_hours = [1, 2, 24, 48, 168]
    for lag in lag_hours:
        target_row[f'{feature_prefix}_lag_{lag}h'] = history_by_time.get(target_time_utc - timedelta(hours=lag))

    history_values = [
        history_by_time.get(target_time_utc - timedelta(hours=offset))
        for offset in range(1, 169)
    ]

    target_row[f'{feature_prefix}_rolling_mean_3h'] = _safe_mean(history_values[:3])
    target_row[f'{feature_prefix}_rolling_mean_24h'] = _safe_mean(history_values[:24])
    target_row[f'{feature_prefix}_rolling_mean_168h'] = _safe_mean(history_values[:168])
    target_row[f'{feature_prefix}_same_hour_last_week'] = history_by_time.get(target_time_utc - timedelta(hours=168))

    weekly_points = [
        history_by_time.get(target_time_utc - timedelta(hours=168 * week))
        for week in range(1, 5)
    ]
    target_row[f'{feature_prefix}_same_hour_4_week_average'] = _safe_mean(weekly_points)
    return target_row


def _delta(weighted: dict, target_time: datetime, lag_hours: int, key: str) -> float | None:
    lag_time = target_time - timedelta(hours=lag_hours)
    if lag_time not in weighted:
        return None
    return weighted[target_time][key] - weighted[lag_time][key]


def _rolling_mean(weighted: dict, target_time: datetime, window: int, key: str) -> float | None:
    values = []
    for offset in range(window):
        lag_time = target_time - timedelta(hours=offset)
        row = weighted.get(lag_time)
        if not row or row.get(key) is None:
            continue
        values.append(row[key])
    return _safe_mean(values)


def _safe_mean(values: list[float | None]) -> float | None:
    filtered = [value for value in values if value is not None]
    if not filtered:
        return None
    return mean(filtered)
