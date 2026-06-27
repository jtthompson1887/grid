from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Iterable

import requests


class WeatherAdapter(ABC):
    @abstractmethod
    def fetch(self, *, latitude: float, longitude: float, start_utc: datetime, end_utc: datetime) -> list[dict]:
        raise NotImplementedError


class OpenMeteoAdapter(WeatherAdapter):
    FORECAST_URL = 'https://api.open-meteo.com/v1/forecast'
    ARCHIVE_URL = 'https://archive-api.open-meteo.com/v1/archive'

    def __init__(self, mode: str = 'forecast'):
        if mode not in {'forecast', 'historical'}:
            raise ValueError('mode must be forecast or historical')
        self.mode = mode

    def fetch(self, *, latitude: float, longitude: float, start_utc: datetime, end_utc: datetime) -> list[dict]:
        if start_utc.tzinfo is None:
            start_utc = start_utc.replace(tzinfo=UTC)
        if end_utc.tzinfo is None:
            end_utc = end_utc.replace(tzinfo=UTC)

        url = self.FORECAST_URL if self.mode == 'forecast' else self.ARCHIVE_URL
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'hourly': ','.join(
                [
                    'temperature_2m',
                    'apparent_temperature',
                    'wind_speed_10m',
                    'cloud_cover',
                    'shortwave_radiation',
                    'precipitation',
                    'relative_humidity_2m',
                ]
            ),
            'start_date': start_utc.date().isoformat(),
            'end_date': end_utc.date().isoformat(),
            'timezone': 'UTC',
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        return normalize_open_meteo_payload(payload, weather_source='Open-Meteo')


class MetOfficeAdapterPlaceholder(WeatherAdapter):
    def fetch(self, *, latitude: float, longitude: float, start_utc: datetime, end_utc: datetime) -> list[dict]:
        raise NotImplementedError('Met Office Weather DataHub adapter is not implemented in v1')


def normalize_open_meteo_payload(payload: dict, *, weather_source: str) -> list[dict]:
    hourly = payload.get('hourly', {})
    times: Iterable[str] = hourly.get('time', [])
    rows: list[dict] = []
    run_time = datetime.now(UTC)

    for index, time_value in enumerate(times):
        rows.append(
            {
                'temperature_2m_c': _get_indexed(hourly, 'temperature_2m', index),
                'apparent_temperature_c': _get_indexed(hourly, 'apparent_temperature', index),
                'wind_speed_10m_ms': _get_indexed(hourly, 'wind_speed_10m', index),
                'cloud_cover_percent': _get_indexed(hourly, 'cloud_cover', index),
                'shortwave_radiation_wm2': _get_indexed(hourly, 'shortwave_radiation', index),
                'precipitation_mm': _get_indexed(hourly, 'precipitation', index),
                'relative_humidity_percent': _get_indexed(hourly, 'relative_humidity_2m', index),
                'weather_source': weather_source,
                'weather_run_time_utc': run_time,
                'target_time_utc': datetime.fromisoformat(time_value).replace(tzinfo=UTC),
            }
        )
    return rows


def _get_indexed(source: dict, key: str, index: int):
    values = source.get(key, [])
    if index >= len(values):
        return None
    return values[index]
