from datetime import UTC, datetime, timedelta

from .constants import MAX_HORIZON_HOURS, MIN_HORIZON_HOURS, get_regime
from .calendar_features import build_calendar_row


def generate_hourly_time_spine(forecast_issue_time_utc: datetime) -> list[dict]:
    if forecast_issue_time_utc.tzinfo is None:
        forecast_issue_time_utc = forecast_issue_time_utc.replace(tzinfo=UTC)
    forecast_issue_time_utc = forecast_issue_time_utc.astimezone(UTC)

    rows: list[dict] = []
    for horizon_hours in range(MIN_HORIZON_HOURS, MAX_HORIZON_HOURS + 1):
        target_time_utc = forecast_issue_time_utc + timedelta(hours=horizon_hours)
        calendar = build_calendar_row(target_time_utc).to_dict()
        rows.append(
            {
                'forecast_issue_time_utc': forecast_issue_time_utc,
                'target_time_utc': target_time_utc,
                'horizon_hours': horizon_hours,
                'forecast_horizon_hours': horizon_hours,
                'forecast_horizon_regime': get_regime(horizon_hours).value,
                **calendar,
            }
        )
    return rows


def validate_horizon(horizon_hours: int) -> None:
    if horizon_hours < MIN_HORIZON_HOURS or horizon_hours > MAX_HORIZON_HOURS:
        raise ValueError('horizon_hours must be between 1 and 8760')
