import requests
from datetime import datetime, timezone
from .exceptions import DataException
from .time_utils import normalise

KEYS = ['emissions']


def update(database) -> None:
    now = datetime.now(timezone.utc)
    url = f'https://api.carbonintensity.org.uk/intensity/{now.strftime("%Y-%m-%dT%H:%M:%SZ")}/pt24h'

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        json_data = response.json()
    except Exception:
        raise DataException('Failed to read data')

    if not isinstance(json_data, dict) or 'data' not in json_data or not isinstance(json_data['data'], list):
        raise DataException('Missing data')

    data = []
    for item in json_data['data']:
        if not isinstance(item, dict):
            raise DataException('Invalid item')
        data.append(_get_datum(item))

    database.update(KEYS, data)


def _get_datum(item: dict) -> list:
    if 'from' not in item:
        raise DataException('Missing time')

    intensity = item.get('intensity', {})
    if 'actual' not in intensity and 'forecast' not in intensity:
        raise DataException('Missing emissions value')

    emissions = intensity.get('actual') if intensity.get('actual') is not None else intensity.get('forecast')

    if not isinstance(emissions, int):
        raise DataException(f'Invalid emissions value: {emissions}')

    return [normalise(item['from'], 30), emissions]
