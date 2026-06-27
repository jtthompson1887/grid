from datetime import datetime


def build_hindsight_dataset(rows: list[dict]) -> list[dict]:
    result = []
    for row in rows:
        if row.get('target_value') is None:
            continue
        result.append({**row, 'dataset_mode': 'hindsight'})
    return result


def build_asof_dataset(rows: list[dict]) -> list[dict]:
    result = []
    for row in rows:
        issue_time: datetime = row['forecast_issue_time_utc']
        publish_time: datetime | None = row.get('source_publish_time_utc')
        weather_run_time: datetime | None = row.get('weather_run_time_utc')
        target_value = row.get('target_value')

        if target_value is None:
            continue
        if publish_time is not None and publish_time > issue_time:
            continue
        if weather_run_time is not None and weather_run_time > issue_time:
            continue
        if row.get('uses_actual_future_weather', False):
            continue
        result.append({**row, 'dataset_mode': 'asof'})
    return result
