from .exceptions import DataException
from .csv_parser import parse
from .time_utils import get_settlement_time

KEYS = ['embedded_wind', 'embedded_solar']


def update(database) -> None:
    rows = parse(
        'https://api.neso.energy/dataset/7a12172a-939c-404c-b581-a6128b74f588/resource/177f6fa4-ae49-4182-81ea-0c6b35f26ca6/download/demanddataupdate.csv',
        [
            'SETTLEMENT_DATE',
            'SETTLEMENT_PERIOD',
            'EMBEDDED_WIND_GENERATION',
            'EMBEDDED_SOLAR_GENERATION'
        ],
        [
            'ND',
            'FORECAST_ACTUAL_INDICATOR',
            'TSD',
            'ENGLAND_WALES_DEMAND',
            'EMBEDDED_WIND_CAPACITY',
            'EMBEDDED_SOLAR_CAPACITY',
            'NON_BM_STOR',
            'PUMP_STORAGE_PUMPING',
            'SCOTTISH_TRANSFER',
            'IFA_FLOW',
            'IFA2_FLOW',
            'BRITNED_FLOW',
            'MOYLE_FLOW',
            'EAST_WEST_FLOW',
            'NEMO_FLOW',
            'NSL_FLOW',
            'ELECLINK_FLOW',
            'VIKING_FLOW',
            'GREENLINK_FLOW'
        ]
    )

    database.update(KEYS, [_get_datum(item) for item in rows])


def _get_datum(item: list) -> list:
    for i in (2, 3):
        if not item[i].isdigit():
            raise DataException(f'Non-integer value: {item[i]}')

    try:
        period = int(item[1])
    except ValueError:
        raise DataException(f'Invalid settlement period: {item[1]}')

    return [
        get_settlement_time(item[0], period),
        int(item[2]) / 1000,
        int(item[3]) / 1000
    ]
