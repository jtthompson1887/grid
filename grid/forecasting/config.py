import csv
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class WeatherRegion:
    region_id: str
    region_name: str
    latitude: float
    longitude: float
    weight: float


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT_DIR / 'config'


def load_yaml_config(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    with path.open('r', encoding='utf-8') as handle:
        return yaml.safe_load(handle) or {}


def load_weather_regions(name: str = 'weather_regions_gb_v1.csv') -> list[WeatherRegion]:
    path = CONFIG_DIR / name
    regions: list[WeatherRegion] = []
    with path.open('r', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            regions.append(
                WeatherRegion(
                    region_id=row['region_id'],
                    region_name=row['region_name'],
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude']),
                    weight=float(row['weight']),
                )
            )

    weight_sum = sum(region.weight for region in regions)
    if not math.isclose(weight_sum, 1.0, rel_tol=0, abs_tol=1e-9):
        raise ValueError(f'weather region weights must sum to 1.0, got {weight_sum}')
    return regions


def require_environment_variables(keys: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for key in keys:
        values[key] = os.environ.get(key, '')
    return values
