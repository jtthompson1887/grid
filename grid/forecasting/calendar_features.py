import math
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

try:
    import holidays
except Exception:  # pragma: no cover
    holidays = None

UK_TZ = ZoneInfo('Europe/London')


@dataclass(frozen=True)
class CalendarFeatureRow:
    timestamp_utc: datetime
    timestamp_local: datetime
    date_local: str
    hour_local: int
    day_of_week: int
    day_of_month: int
    month: int
    day_of_year: int
    is_weekend: bool
    is_bank_holiday: bool
    days_to_next_bank_holiday: int
    days_since_previous_bank_holiday: int
    is_christmas_period: bool
    is_new_year_period: bool
    is_dst_transition_day: bool

    def to_dict(self) -> dict:
        return {
            'timestamp_utc': self.timestamp_utc,
            'timestamp_local': self.timestamp_local,
            'date_local': self.date_local,
            'hour_local': self.hour_local,
            'day_of_week': self.day_of_week,
            'day_of_month': self.day_of_month,
            'month': self.month,
            'day_of_year': self.day_of_year,
            'is_weekend': self.is_weekend,
            'is_bank_holiday': self.is_bank_holiday,
            'days_to_next_bank_holiday': self.days_to_next_bank_holiday,
            'days_since_previous_bank_holiday': self.days_since_previous_bank_holiday,
            'is_christmas_period': self.is_christmas_period,
            'is_new_year_period': self.is_new_year_period,
            'is_dst_transition_day': self.is_dst_transition_day,
            'hour_of_day_sin': math.sin(2.0 * math.pi * self.hour_local / 24.0),
            'hour_of_day_cos': math.cos(2.0 * math.pi * self.hour_local / 24.0),
            'month_sin': math.sin(2.0 * math.pi * self.month / 12.0),
            'month_cos': math.cos(2.0 * math.pi * self.month / 12.0),
            'day_of_year_sin': math.sin(2.0 * math.pi * self.day_of_year / 366.0),
            'day_of_year_cos': math.cos(2.0 * math.pi * self.day_of_year / 366.0),
        }


def _uk_bank_holidays(year: int) -> set:
    if holidays is not None:
        return set(holidays.country_holidays('GB', years=[year]).keys())

    fixed = {
        datetime(year, 1, 1).date(),
        datetime(year, 12, 25).date(),
        datetime(year, 12, 26).date(),
    }
    return fixed


def _is_dst_transition_day(ts_local: datetime) -> bool:
    start = ts_local.replace(hour=0, minute=0, second=0, microsecond=0)
    offsets = set((start + timedelta(hours=offset)).utcoffset() for offset in range(0, 24))
    return len(offsets) > 1


def build_calendar_row(timestamp_utc: datetime) -> CalendarFeatureRow:
    if timestamp_utc.tzinfo is None:
        timestamp_utc = timestamp_utc.replace(tzinfo=UTC)
    timestamp_utc = timestamp_utc.astimezone(UTC)
    local = timestamp_utc.astimezone(UK_TZ)
    local_date = local.date()

    holidays_this = _uk_bank_holidays(local.year)
    holidays_next = _uk_bank_holidays(local.year + 1)
    all_holidays = sorted(holidays_this.union(holidays_next))

    is_bank_holiday = local_date in holidays_this
    next_holiday = min((d for d in all_holidays if d >= local_date), default=local_date)
    previous_holiday = max((d for d in all_holidays if d <= local_date), default=local_date)

    is_christmas_period = (
        (local.month == 12 and local.day >= 20)
        or (local.month == 1 and local.day <= 2)
    )
    is_new_year_period = (local.month == 12 and local.day == 31) or (local.month == 1 and local.day <= 2)

    return CalendarFeatureRow(
        timestamp_utc=timestamp_utc,
        timestamp_local=local,
        date_local=local_date.isoformat(),
        hour_local=local.hour,
        day_of_week=local.weekday(),
        day_of_month=local.day,
        month=local.month,
        day_of_year=local.timetuple().tm_yday,
        is_weekend=local.weekday() >= 5,
        is_bank_holiday=is_bank_holiday,
        days_to_next_bank_holiday=(next_holiday - local_date).days,
        days_since_previous_bank_holiday=(local_date - previous_holiday).days,
        is_christmas_period=is_christmas_period,
        is_new_year_period=is_new_year_period,
        is_dst_transition_day=_is_dst_transition_day(local),
    )
