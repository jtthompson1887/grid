import re
import time
from calendar import monthrange
from .exceptions import DataException

MONTHS = {
    'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4,
    'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8,
    'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
}


def _check_date(year: int, month: int, day: int) -> bool:
    if month < 1 or month > 12:
        return False
    if day < 1 or day > monthrange(year, month)[1]:
        return False
    return True


def normalise(time_str: str, interval: int) -> str:
    match = re.match(
        r'^(\d{4})-(\d{2})-(\d{2})[T ]'
        r'(2[0-3]|[01]\d):([0-5]\d)(?::00)?Z?$',
        time_str
    )
    if not match:
        raise DataException(f'Invalid time format: {time_str}')

    year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
    minutes = int(match.group(5))

    if not _check_date(year, month, day):
        raise DataException(f'Invalid date: {time_str}')

    if minutes % interval != 0:
        raise DataException(f'Not a multiple of {interval} minutes: {time_str}')

    normalised = re.sub(r'[TZ]', lambda m: ' ' if m.group() == 'T' else '', time_str)
    normalised = normalised.rstrip()
    # ensure seconds present
    if not re.search(r':\d{2}:\d{2}$', normalised):
        normalised += ':00'

    return f'"{normalised}"'


def get_settlement_time(date: str, period: int) -> str:
    match_iso = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', date)
    match_uk = re.match(r'^(\d{2})-([A-Z]{3})-(\d{4})$', date)

    if match_iso:
        year, month, day = int(match_iso.group(1)), int(match_iso.group(2)), int(match_iso.group(3))
    elif match_uk:
        day = int(match_uk.group(1))
        month = MONTHS.get(match_uk.group(2), 0)
        year = int(match_uk.group(3))
    else:
        raise DataException(f'Invalid settlement date format: {date}')

    if not _check_date(year, month, day):
        raise DataException(f'Invalid settlement date: {date}')

    if period < 1 or period > 50:
        raise DataException(f'Invalid settlement period: {period}')

    import calendar
    timestamp = calendar.timegm(
        time.strptime(f'{year}-{month:02d}-{day:02d} 00:00:00', '%Y-%m-%d %H:%M:%S')
    )
    # Settlement periods use local (BST-aware) midnight, so use mktime
    import datetime
    local_midnight = datetime.datetime(year, month, day, 0, 0, 0)
    local_ts = local_midnight.timestamp()
    ts = int(local_ts) + (period - 1) * 1800

    import datetime as dt
    utc_dt = dt.datetime.utcfromtimestamp(ts)
    return f'"{utc_dt.strftime("%Y-%m-%d %H:%M:%S")}"'
