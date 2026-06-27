import csv
import io
import requests
from .exceptions import DataException


def parse(url: str, required_headers: list, ignored_headers: list) -> list:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except Exception:
        raise DataException('Failed to read data')

    reader = csv.reader(io.StringIO(response.text))

    try:
        header_row = next(reader)
    except StopIteration:
        raise DataException('Missing CSV headers')

    for header in header_row:
        if header not in required_headers and header not in ignored_headers:
            raise DataException(f'Unrecognised header: {header}')

    column_count = len(header_row)

    columns = []
    for header in required_headers:
        try:
            columns.append(header_row.index(header))
        except ValueError:
            raise DataException('Missing required header')

    data = []
    for row in reader:
        if len(row) != column_count:
            raise DataException('Column count does not match header count')
        data.append([row[col] for col in columns])

    return data
