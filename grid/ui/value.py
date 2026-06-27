def format_power(value: float) -> str:
    return _format(value, 2)


def format_total_power(value: float) -> str:
    return _format(value, 1)


def format_percentage(value: float) -> str:
    return _format(100 * value, 1)


def format_price(value: float) -> str:
    return _format(value, 2, '£')


def _format(value: float, decimal_places: int, prefix: str = '') -> str:
    sign = '−' if value < 0 else ''
    return f'{sign}{prefix}{abs(value):.{decimal_places}f}'
