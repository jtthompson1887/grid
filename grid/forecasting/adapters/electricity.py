from collections import defaultdict
from datetime import UTC, datetime
from typing import Iterable


def _to_datetime(ts: str | datetime) -> datetime:
    if isinstance(ts, datetime):
        dt = ts
    else:
        dt = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def normalize_electricity_rows(
    rows: Iterable[dict],
    *,
    source_name: str,
    source_dataset: str,
    source_publish_time_utc: str | datetime,
    value_field: str = 'electricity_demand_mw',
    granularity_minutes: int = 60,
) -> list[dict]:
    publish_time = _to_datetime(source_publish_time_utc)
    normalized: list[dict] = []

    if granularity_minutes == 30:
        buckets: dict[datetime, list[float]] = defaultdict(list)
        for row in rows:
            ts = _to_datetime(row['timestamp_utc'])
            hour = ts.replace(minute=0, second=0, microsecond=0)
            buckets[hour].append(float(row[value_field]))

        for hour, values in sorted(buckets.items(), key=lambda item: item[0]):
            hourly_mwh = sum(value * 0.5 for value in values)
            normalized.append(
                {
                    'timestamp_utc': hour,
                    'electricity_demand_mw': None,
                    'electricity_demand_mwh': hourly_mwh,
                    'electricity_national_demand_mwh': hourly_mwh,
                    'source_name': source_name,
                    'source_dataset': source_dataset,
                    'source_publish_time_utc': publish_time,
                }
            )
        return normalized

    for row in rows:
        ts = _to_datetime(row['timestamp_utc'])
        hourly_value = float(row.get('electricity_demand_mwh', row.get(value_field, 0.0)))
        normalized.append(
            {
                'timestamp_utc': ts,
                'electricity_demand_mw': float(row.get(value_field, 0.0)) if value_field in row else None,
                'electricity_demand_mwh': hourly_value,
                'electricity_national_demand_mwh': hourly_value,
                'source_name': source_name,
                'source_dataset': source_dataset,
                'source_publish_time_utc': publish_time,
            }
        )
    return normalized
