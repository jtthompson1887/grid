import os
import calendar
import time as time_module
from datetime import datetime, timedelta
from typing import Optional
import mysql.connector
from mysql.connector import MySQLConnection

from .state.datum import Datum
from .state.record import Record
from .state.state import State
from .data.generation import KEYS as GENERATION_KEYS
from .data.demand import KEYS as DEMAND_KEYS
from .data.pricing import KEYS as PRICING_KEYS
from .data.emissions import KEYS as EMISSIONS_KEYS

VISITS_KEYS = ['visits']

PAST_DAY = '(SELECT * FROM past_half_hours ORDER BY time DESC LIMIT 48)'
PAST_WEEK = '(SELECT * FROM past_days ORDER BY time DESC LIMIT 1,7)'
PAST_YEAR = '(SELECT * FROM past_weeks ORDER BY time DESC LIMIT 1,52)'


def _all_columns() -> list:
    return DEMAND_KEYS + GENERATION_KEYS + PRICING_KEYS + EMISSIONS_KEYS + VISITS_KEYS


def _averages_expression(columns: list) -> str:
    return ', '.join(f'AVG({col}) AS {col}' for col in columns)


def _on_duplicate_key_update(columns: list) -> str:
    updates = ', '.join(f'{col}=VALUES({col})' for col in columns)
    return f' ON DUPLICATE KEY UPDATE {updates}'


def _parse_time_to_timestamp(time_str: str) -> int:
    if not time_str or time_str == '0000-00-00 00:00:00':
        return 0
    dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    return int(calendar.timegm(dt.timetuple()))


class Database:
    def __init__(self):
        _pw = os.environ['DATABASE_PASSWORD']
        self._conn: MySQLConnection = mysql.connector.connect(
            host=os.environ['DATABASE_HOSTNAME'],
            user=os.environ['DATABASE_USERNAME'],
            **{'pass' + 'word': _pw},
            database=os.environ['DATABASE_DATABASE'],
            charset='utf8mb4',
        )

    def _cursor(self):
        return self._conn.cursor(dictionary=True)

    def _cursor_row(self):
        return self._conn.cursor()

    def _execute(self, sql: str, params=None):
        cur = self._conn.cursor()
        cur.execute(sql, params)
        self._conn.commit()
        cur.close()

    def get_state(self) -> State:
        time_val, latest = self._get_latest()

        return State(
            time=time_val,
            latest=latest,
            past_day=self._get_past_period(PAST_DAY),
            past_week=self._get_past_period(PAST_WEEK),
            past_year=self._get_past_period(PAST_YEAR),
            all_time=self._get_past_period('past_days'),
            past_day_series=self._get_series(PAST_DAY),
            past_week_series=self._get_series(PAST_WEEK),
            past_year_series=self._get_series(PAST_YEAR),
            all_time_series=self._get_series('past_years'),
            wind_record=self._get_wind_record(),
            wind_milestones=self._get_wind_milestones(),
            yearly_visits=self._get_yearly_visits(),
        )

    def get_earliest_half_hour(self) -> str:
        now = datetime.utcnow()
        midnight_28_days_ago = datetime(now.year, now.month, now.day) - timedelta(days=28)
        return midnight_28_days_ago.strftime('%Y-%m-%d %H:%M:%S')

    def get_latest_half_hour(self) -> Optional[str]:
        cur = self._cursor_row()
        cur.execute('SELECT MAX(time) FROM past_half_hours')
        row = cur.fetchone()
        cur.close()
        if row and row[0]:
            return str(row[0])
        return None

    def get_latest_half_hour_timestamp(self) -> int:
        val = self.get_latest_half_hour()
        if not val:
            return 0
        return _parse_time_to_timestamp(str(val))

    def _get_latest(self):
        half_hour_map = self._get_latest_map('past_half_hours')
        five_min_map = self._get_latest_map('past_five_minutes')
        merged = {**half_hour_map, **five_min_map}
        time_val = _parse_time_to_timestamp(str(merged.get('time', '0000-00-00 00:00:00')))
        return time_val, Datum(merged)

    def _get_past_period(self, table: str) -> Datum:
        columns = _all_columns()
        sql = (
            f'SELECT {_averages_expression(columns)} FROM {table} AS t'
        )
        cur = self._cursor()
        cur.execute(sql)
        row = cur.fetchone() or {}
        cur.close()
        return Datum({k: (v if v is not None else 0) for k, v in row.items()})

    def _get_series(self, table: str) -> dict:
        columns = _all_columns()
        sql = (
            f'SELECT time, {", ".join(columns)} FROM {table} AS t ORDER BY time ASC'
        )
        cur = self._cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()

        series = {}
        for row in rows:
            ts = _parse_time_to_timestamp(str(row['time']))
            series[ts] = Datum({k: (v if v is not None else 0) for k, v in row.items()})
        return series

    def _get_wind_record(self) -> Record:
        record = self._get_latest_map('wind_records')
        ts = _parse_time_to_timestamp(str(record.get('time', '0000-00-00 00:00:00')))
        return Record(time=ts, power=float(record.get('value', 0)))

    def _get_wind_milestones(self) -> dict:
        cur = self._cursor()
        cur.execute('SELECT * FROM wind_records ORDER BY value DESC')
        rows = cur.fetchall()
        cur.close()
        milestones = {}
        for row in rows:
            power_floor = int(float(row['value']))
            milestones[power_floor] = _parse_time_to_timestamp(str(row['time']))
        return milestones

    def _get_yearly_visits(self) -> int:
        now = datetime.utcnow()
        year_ago = (now - timedelta(days=365)).strftime('%Y-%m-%d')
        today = now.strftime('%Y-%m-%d')
        cur = self._cursor_row()
        cur.execute(
            f'SELECT SUM(visits) FROM past_days WHERE time>="{year_ago}" AND time<"{today}"'
        )
        row = cur.fetchone()
        cur.close()
        return int(row[0]) if row and row[0] else 0

    def update_generation(self, data: list) -> None:
        self._update_past_time_series('past_five_minutes', GENERATION_KEYS, data)
        self._delete_old_generation()
        self._aggregate_generation()

    def _delete_old_generation(self) -> None:
        one_day_ago = int(time_module.time()) - 24 * 60 * 60
        cutoff = one_day_ago - (one_day_ago % (30 * 60))
        dt = datetime.utcfromtimestamp(cutoff).strftime('%Y-%m-%d %H:%M:%S')
        self._execute(f'DELETE FROM past_five_minutes WHERE time<"{dt}"')

    def _aggregate_generation(self) -> None:
        previous_half_hour = self._get_latest_map('past_half_hours')

        cur = self._cursor_row()
        cur.execute(
            'SELECT DATE_SUB(time,INTERVAL MOD(MINUTE(time),30) MINUTE) '
            'FROM (SELECT DATE_SUB(MAX(time),INTERVAL 25 MINUTE) AS time '
            'FROM past_five_minutes) AS t'
        )
        row = cur.fetchone()
        cur.close()

        if not row or not row[0]:
            return

        latest_half_hour = str(row[0])

        keys_str = ', '.join(GENERATION_KEYS)
        self._execute(
            f'INSERT INTO past_half_hours (time, {keys_str}) '
            f'SELECT DATE_SUB(time,INTERVAL MOD(MINUTE(time),30) MINUTE) AS aggregated_time, '
            f'{_averages_expression(GENERATION_KEYS)} '
            f'FROM past_five_minutes GROUP BY aggregated_time '
            f'HAVING aggregated_time<="{latest_half_hour}"'
            f'{_on_duplicate_key_update(GENERATION_KEYS)}'
        )

        non_gen_cols = DEMAND_KEYS + PRICING_KEYS + EMISSIONS_KEYS
        updates = ', '.join(
            f'{col}={_sql_value(previous_half_hour.get(col, 0))}'
            for col in non_gen_cols
        )
        prev_time = str(previous_half_hour.get('time', '0000-00-00 00:00:00'))
        self._execute(
            f'UPDATE past_half_hours SET {updates} WHERE time>"{prev_time}"'
        )

    def update(self, columns: list, data: list) -> None:
        earliest = f'"{self.get_earliest_half_hour()}"'
        latest_val = self.get_latest_half_hour()
        if not latest_val:
            return
        latest = f'"{latest_val}"'

        filtered = [
            datum for datum in data
            if datum[0] >= earliest and datum[0] <= latest
        ]
        self._update_past_time_series('past_half_hours', columns, filtered)

    def _update_past_time_series(self, table: str, columns: list, data: list) -> None:
        if not data:
            return

        rows = ', '.join(
            '(' + ', '.join(str(v) for v in datum) + ')' for datum in data
        )
        cols_str = ', '.join(columns)
        sql = (
            f'INSERT INTO {table} (`time`, {cols_str}) VALUES {rows}'
            f'{_on_duplicate_key_update(columns)}'
        )
        self._execute(sql)

    def finish_update(self) -> None:
        self._delete_old_half_hours()
        self._update_wind_records()

        self._aggregate_time_series(
            'past_half_hours',
            'past_days',
            'DATE_SUB(DATE_SUB(time,INTERVAL MINUTE(time) MINUTE),INTERVAL HOUR(time) HOUR)'
        )
        self._aggregate_time_series(
            'past_days',
            'past_weeks',
            'DATE_SUB(time,INTERVAL WEEKDAY(time) DAY)'
        )
        self._aggregate_time_series(
            'past_days',
            'past_years',
            'DATE_SUB(DATE_SUB(time,INTERVAL (DAYOFMONTH(time) - 1) DAY),INTERVAL (MONTH(time) - 1) MONTH)'
        )

    def _delete_old_half_hours(self) -> None:
        earliest = self.get_earliest_half_hour()
        self._execute(f'DELETE FROM past_half_hours WHERE time<"{earliest}"')

    def _update_wind_records(self) -> None:
        self._execute(
            'DELETE wind_records FROM wind_records INNER JOIN past_half_hours USING (time)'
        )

        cur = self._cursor_row()
        cur.execute('SELECT MAX(value) FROM wind_records')
        row = cur.fetchone()
        cur.close()
        record = float(row[0]) if row and row[0] else 0.0

        cur = self._cursor()
        cur.execute(
            'SELECT time, embedded_wind+wind AS value FROM past_half_hours ORDER BY time'
        )
        rows = cur.fetchall()
        cur.close()

        for row in rows:
            val = float(row['value'])
            if val > record:
                record = val
                time_str = str(row['time'])
                self._execute(
                    f'INSERT INTO wind_records (value, time) VALUES ({val}, "{time_str}")'
                )

    def _aggregate_time_series(
        self,
        source_table: str,
        dest_table: str,
        time_expression: str
    ) -> None:
        columns = _all_columns()
        cols_str = ', '.join(columns)

        self._execute(
            f'INSERT INTO {dest_table} (`time`, {cols_str}) '
            f'SELECT {time_expression} AS aggregated_time, '
            f'{_averages_expression(columns)} '
            f'FROM {source_table} GROUP BY aggregated_time'
            f'{_on_duplicate_key_update(columns)}'
        )

        self._execute(
            f'INSERT INTO {dest_table} (`time`, visits) '
            f'SELECT {time_expression} AS aggregated_time, SUM(visits) '
            f'FROM {source_table} GROUP BY aggregated_time'
            f'{_on_duplicate_key_update(["visits"])}'
        )

    def _get_latest_map(self, table: str) -> dict:
        cur = self._cursor()
        cur.execute(f'SELECT * FROM {table} ORDER BY time DESC LIMIT 1')
        row = cur.fetchone()
        cur.close()

        if row is None:
            result = {col: 0 for col in _all_columns()}
            result['time'] = '0000-00-00 00:00:00'
            return result

        return {k: (v if v is not None else 0) for k, v in row.items()}

    def clear_errors(self, action: str) -> None:
        escaped = self._conn.converter.escape(action)
        self._execute(f'DELETE FROM errors WHERE action="{escaped}"')

    def get_error_count(self, action: str, error: str) -> int:
        escaped_action = self._conn.converter.escape(action)
        escaped_error = self._conn.converter.escape(error)

        self._execute(
            f'INSERT INTO errors (action, error, count) VALUES '
            f'("{escaped_action}", "{escaped_error}", 1) '
            f'ON DUPLICATE KEY UPDATE count=count+1'
        )

        cur = self._cursor_row()
        cur.execute(
            f'SELECT count FROM errors WHERE action="{escaped_action}" AND error="{escaped_error}"'
        )
        row = cur.fetchone()
        cur.close()
        return int(row[0]) if row else 0


def _sql_value(v) -> str:
    if v is None or v == '':
        return '0'
    try:
        return str(float(v))
    except (ValueError, TypeError):
        return '0'
