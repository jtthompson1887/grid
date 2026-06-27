import requests
from datetime import datetime, timezone
from .exceptions import DataException
from .time_utils import normalise

KEYS = [
    'coal', 'ccgt', 'ocgt', 'nuclear', 'oil', 'wind', 'hydro',
    'pumped', 'biomass', 'battery', 'other',
    'ifa', 'moyle', 'britned', 'ewic', 'nemo', 'ifa2', 'nsl',
    'eleclink', 'viking', 'greenlink'
]

COLUMNS = {
    'COAL':    1,
    'CCGT':    2,
    'OCGT':    3,
    'NUCLEAR': 4,
    'OIL':     5,
    'WIND':    6,
    'NPSHYD':  7,
    'PS':      8,
    'BIOMASS': 9,
    'BESS':    10,
    'OTHER':   11,
    'INTFR':   12,
    'INTIRL':  13,
    'INTNED':  14,
    'INTEW':   15,
    'INTNEM':  16,
    'INTIFA2': 17,
    'INTNSL':  18,
    'INTELEC': 19,
    'INTVKL':  20,
    'INTGRNL': 21
}


def update(database) -> None:
    now = datetime.now(timezone.utc)
    from_dt = datetime.utcfromtimestamp(now.timestamp() - 24 * 60 * 60)
    url = (
        f'https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELINST/stream'
        f'?publishDateTimeFrom={from_dt.strftime("%Y-%m-%dT%H:%M:%SZ")}'
        f'&publishDateTimeTo={now.strftime("%Y-%m-%dT%H:%M:%SZ")}'
    )

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        json_data = response.json()
    except Exception:
        raise DataException('Failed to read data')

    if not isinstance(json_data, list):
        raise DataException('Missing data')

    data = {}

    for item in json_data:
        if not isinstance(item, dict):
            raise DataException('Invalid item')

        time_key = _get_time(item)

        if time_key not in data:
            row = [0] * (len(COLUMNS) + 1)
            row[0] = time_key
            data[time_key] = row

        data[time_key][_get_column(item)] = _get_generation(item)

    database.update_generation(list(data.values()))


def _get_time(item: dict) -> str:
    if 'startTime' not in item:
        raise DataException('Missing start time')
    time_val = item['startTime']
    if not isinstance(time_val, str):
        raise DataException(f'Invalid start time: {time_val}')
    return normalise(time_val, 5)


def _get_column(item: dict) -> int:
    if 'fuelType' not in item:
        raise DataException('Missing fuel type')
    fuel_type = item['fuelType']
    if not isinstance(fuel_type, str) or fuel_type not in COLUMNS:
        raise DataException(f'Invalid fuel type: {fuel_type}')
    return COLUMNS[fuel_type]


def _get_generation(item: dict) -> float:
    if 'generation' not in item:
        raise DataException('Missing generation')
    generation = item['generation']
    if not isinstance(generation, int):
        raise DataException(f'Invalid generation value: {generation}')
    return round(generation / 1000, 2)
