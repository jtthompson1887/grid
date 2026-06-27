import requests
from datetime import datetime, timezone
from .exceptions import DataException
from .time_utils import normalise

KEYS = ['price']


def update(database) -> None:
    ts = database.get_latest_half_hour_timestamp()
    from_dt = datetime.utcfromtimestamp(ts - 24 * 60 * 60)
    to_dt = datetime.utcfromtimestamp(ts)

    url = (
        f'https://data.elexon.co.uk/bmrs/api/v1/balancing/pricing/market-index'
        f'?from={from_dt.strftime("%Y-%m-%dT%H:%M:%SZ")}'
        f'&to={to_dt.strftime("%Y-%m-%dT%H:%M:%SZ")}'
        f'&dataProviders=APXMIDP'
    )

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
    if 'startTime' not in item:
        raise DataException('Missing time')
    if 'price' not in item:
        raise DataException('Missing price')
    price = item['price']
    if not isinstance(price, (float, int)):
        raise DataException(f'Invalid price: {price}')
    return [normalise(item['startTime'], 30), price]
