from datetime import timedelta
from statistics import mean


def same_hour_yesterday(history: dict, target_time):
    return history.get(target_time - timedelta(hours=24))


def same_hour_last_week(history: dict, target_time):
    return history.get(target_time - timedelta(hours=168))


def seasonal_hour_day_month_average(history_rows: list[dict], target_time):
    matches = [
        row['value']
        for row in history_rows
        if row['timestamp_utc'].hour == target_time.hour
        and row['timestamp_utc'].day == target_time.day
        and row['timestamp_utc'].month == target_time.month
    ]
    if not matches:
        return None
    return mean(matches)


def official_forecast_where_available(forecast_rows: dict, target_time):
    return forecast_rows.get(target_time)
