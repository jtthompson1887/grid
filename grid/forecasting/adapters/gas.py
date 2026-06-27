from datetime import UTC, datetime
from typing import Any

from ..config import load_yaml_config


def _to_datetime(ts: str | datetime) -> datetime:
    if isinstance(ts, datetime):
        dt = ts
    else:
        dt = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _convert_with_calorific_volume_mwh(value: float, calorific_value: float) -> float:
    return (value * calorific_value) / 1000.0


def convert_gas_to_mwh_equivalent(
    value: float,
    unit: str,
    calorific_value: float | None,
    *,
    gas_conversion_config: dict[str, Any],
) -> tuple[float | None, float | None, str, bool]:
    units = gas_conversion_config.get('units', {})
    fallback = gas_conversion_config.get('default_fallback_calorific_value_kwh_per_m3')

    normalized_unit = unit.strip().lower()
    if normalized_unit not in units:
        return None, None, 'missing_gas_conversion', False

    config = units[normalized_unit]
    if config.get('requires_calorific_value'):
        effective_cv = calorific_value if calorific_value is not None else fallback
        if effective_cv is None:
            return None, None, 'missing_gas_conversion', False
        m3 = value * float(config.get('m3_per_mcm', 1.0)) if normalized_unit == 'mcm' else value
        return _convert_with_calorific_volume_mwh(m3, float(effective_cv)), float(effective_cv), 'volume_to_energy', calorific_value is None

    return value * float(config.get('to_mwh_factor', 0.0)), calorific_value, 'unit_factor', False


def normalize_gas_rows(
    rows: list[dict],
    *,
    source_name: str,
    source_dataset: str,
    source_publish_time_utc: str | datetime,
    gas_conversion_config: dict[str, Any] | None = None,
) -> list[dict]:
    config = gas_conversion_config or load_yaml_config('gas_conversion.yml')
    publish_time = _to_datetime(source_publish_time_utc)

    normalized: list[dict] = []
    for row in rows:
        mwh, cv, method, used_fallback = convert_gas_to_mwh_equivalent(
            float(row['gas_demand_original_value']),
            str(row['gas_demand_original_unit']),
            row.get('calorific_value'),
            gas_conversion_config=config,
        )

        valid = mwh is not None
        normalized.append(
            {
                'timestamp_utc': _to_datetime(row['timestamp_utc']),
                'gas_demand_original_value': float(row['gas_demand_original_value']),
                'gas_demand_original_unit': str(row['gas_demand_original_unit']),
                'gas_demand_mwh_equivalent': mwh,
                'calorific_value_used': cv,
                'conversion_method': method,
                'source_name': source_name,
                'source_dataset': source_dataset,
                'source_publish_time_utc': publish_time,
                'valid_for_training': valid,
                'used_fallback_calorific_value': used_fallback,
            }
        )
    return normalized
