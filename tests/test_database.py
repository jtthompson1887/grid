"""Tests for grid.database (Database class — MySQL mocked)"""
import calendar
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, call

from grid.database import (
    Database,
    _all_columns,
    _averages_expression,
    _on_duplicate_key_update,
    _parse_time_to_timestamp,
    _sql_value,
)


# ---------------------------------------------------------------------------
# Pure helper functions
# ---------------------------------------------------------------------------

class TestAllColumns:
    def test_returns_list(self):
        cols = _all_columns()
        assert isinstance(cols, list)
        assert len(cols) > 0

    def test_includes_core_keys(self):
        cols = _all_columns()
        assert 'coal' in cols
        assert 'embedded_wind' in cols
        assert 'price' in cols
        assert 'emissions' in cols
        assert 'visits' in cols


class TestAveragesExpression:
    def test_single_column(self):
        expr = _averages_expression(['foo'])
        assert expr == 'AVG(foo) AS foo'

    def test_multiple_columns(self):
        expr = _averages_expression(['a', 'b'])
        assert 'AVG(a) AS a' in expr
        assert 'AVG(b) AS b' in expr
        assert expr.index('AVG(a)') < expr.index('AVG(b)')


class TestOnDuplicateKeyUpdate:
    def test_single_column(self):
        sql = _on_duplicate_key_update(['x'])
        assert 'ON DUPLICATE KEY UPDATE' in sql
        assert 'x=VALUES(x)' in sql

    def test_multiple_columns(self):
        sql = _on_duplicate_key_update(['x', 'y'])
        assert 'x=VALUES(x)' in sql
        assert 'y=VALUES(y)' in sql


class TestParseTimeToTimestamp:
    def test_valid_datetime(self):
        ts = _parse_time_to_timestamp('2024-06-01 10:00:00')
        assert ts == calendar.timegm(datetime(2024, 6, 1, 10, 0, 0).timetuple())

    def test_zero_datetime(self):
        assert _parse_time_to_timestamp('0000-00-00 00:00:00') == 0

    def test_empty_string(self):
        assert _parse_time_to_timestamp('') == 0


class TestSqlValue:
    def test_integer(self):
        assert _sql_value(5) == '5.0'

    def test_float(self):
        assert _sql_value(3.14) == '3.14'

    def test_none_returns_zero(self):
        assert _sql_value(None) == '0'

    def test_empty_string_returns_zero(self):
        assert _sql_value('') == '0'

    def test_non_numeric_string_returns_zero(self):
        assert _sql_value('abc') == '0'


# ---------------------------------------------------------------------------
# Database class (MySQL fully mocked)
# ---------------------------------------------------------------------------

def _make_cursor(dictionary=False):
    """Return a fresh MagicMock cursor."""
    cur = MagicMock()
    if dictionary:
        row = {col: 0.0 for col in _all_columns()}
        row['time'] = '2024-06-01 10:00:00'
        cur.fetchone.return_value = row
        cur.fetchall.return_value = []
    else:
        cur.fetchone.return_value = (None,)
        cur.fetchall.return_value = []
    return cur


def _make_db():
    """Build a Database with a fully mocked connection."""
    conn = MagicMock()
    conn.cursor.return_value = _make_cursor()
    with patch('mysql.connector.connect', return_value=conn):
        db = Database()
    # replace the stored connection so tests can override cursor behaviour
    db._conn = conn
    return db, conn


@pytest.fixture
def db_env(monkeypatch):
    monkeypatch.setenv('DATABASE_HOSTNAME', 'localhost')
    monkeypatch.setenv('DATABASE_USERNAME', 'user')
    monkeypatch.setenv('DATABASE_DATABASE', 'grid')
    monkeypatch.setenv('DATABASE_PASSWORD', 'pass')


@pytest.fixture
def db(db_env):
    database, conn = _make_db()
    return database


def _set_cursor(db, row=None, rows=None, dictionary=False):
    """Helper: configure db._conn.cursor() to return a mock with given data."""
    cur = MagicMock()
    cur.fetchone.return_value = row
    cur.fetchall.return_value = rows or []
    # Remove any side_effect so return_value is used
    db._conn.cursor.side_effect = None
    db._conn.cursor.return_value = cur
    return cur


class TestDatabaseInit:
    def test_connects_on_init(self, db_env):
        conn = MagicMock()
        conn.cursor.return_value = MagicMock()
        with patch('mysql.connector.connect', return_value=conn) as mock_connect:
            db = Database()
        mock_connect.assert_called_once()
        kwargs = mock_connect.call_args[1]
        assert kwargs['host'] == 'localhost'
        assert kwargs['user'] == 'user'
        assert kwargs['database'] == 'grid'


class TestGetEarliestHalfHour:
    def test_returns_string(self, db):
        result = db.get_earliest_half_hour()
        assert isinstance(result, str)
        datetime.strptime(result, '%Y-%m-%d %H:%M:%S')


class TestGetLatestHalfHour:
    def test_returns_none_when_no_data(self, db):
        _set_cursor(db, row=(None,))
        result = db.get_latest_half_hour()
        assert result is None

    def test_returns_string_when_data(self, db):
        _set_cursor(db, row=('2024-06-01 10:00:00',))
        result = db.get_latest_half_hour()
        assert result == '2024-06-01 10:00:00'


class TestGetLatestHalfHourTimestamp:
    def test_returns_zero_when_no_data(self, db):
        _set_cursor(db, row=(None,))
        result = db.get_latest_half_hour_timestamp()
        assert result == 0

    def test_returns_timestamp_when_data(self, db):
        _set_cursor(db, row=('2024-06-01 10:00:00',))
        result = db.get_latest_half_hour_timestamp()
        assert isinstance(result, int)
        assert result > 0


class TestGetState:
    def _setup_full_cursor(self, db):
        """Provide safe dict/row cursors for all DB calls made by get_state."""
        call_count = [0]

        def cursor_factory(dictionary=False):
            cur = MagicMock()
            call_count[0] += 1
            if dictionary:
                row = {col: 0.0 for col in _all_columns()}
                row['time'] = '2024-06-01 10:00:00'
                cur.fetchone.return_value = row
                cur.fetchall.return_value = []
            else:
                cur.fetchone.return_value = (None,)
                cur.fetchall.return_value = []
            return cur

        db._conn.cursor.side_effect = cursor_factory

    def test_get_state_returns_state(self, db):
        from grid.state.state import State
        self._setup_full_cursor(db)
        state = db.get_state()
        assert isinstance(state, State)


class TestUpdateGeneration:
    def test_delegates_to_helpers(self, db):
        db._update_past_time_series = MagicMock()
        db._delete_old_generation = MagicMock()
        db._aggregate_generation = MagicMock()
        data = [['"2024-06-01 10:00:00"', 1.0, 2.0]]
        db.update_generation(data)
        db._update_past_time_series.assert_called_once()
        db._delete_old_generation.assert_called_once()
        db._aggregate_generation.assert_called_once()


class TestUpdate:
    def test_skips_when_no_latest(self, db):
        db.get_latest_half_hour = MagicMock(return_value=None)
        db._update_past_time_series = MagicMock()
        db.update(['price'], [['"2024-06-01 10:00:00"', 45.0]])
        db._update_past_time_series.assert_not_called()

    def test_filters_outside_range(self, db):
        db.get_latest_half_hour = MagicMock(return_value='2024-06-01 10:30:00')
        db._update_past_time_series = MagicMock()
        # datum time is far in the future — should be filtered out
        db.update(['price'], [['"2099-01-01 00:00:00"', 45.0]])
        db._update_past_time_series.assert_called_once()
        filtered = db._update_past_time_series.call_args[0][2]
        assert filtered == []

    def test_passes_valid_data(self, db):
        # Use a date very close to "today" so it passes the earliest cutoff
        from datetime import timedelta
        import datetime as _dt
        now = _dt.datetime.utcnow()
        recent = (now - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        latest = now.strftime('%Y-%m-%d %H:%M:%S')

        db.get_latest_half_hour = MagicMock(return_value=latest)
        db._update_past_time_series = MagicMock()
        db.update(['price'], [[f'"{recent}"', 45.0]])
        filtered = db._update_past_time_series.call_args[0][2]
        assert len(filtered) == 1


class TestClearErrors:
    def test_executes_delete(self, db):
        cur = _set_cursor(db)
        db.clear_errors('test_action')
        cur.execute.assert_called_once()
        sql = cur.execute.call_args[0][0]
        assert 'DELETE FROM errors' in sql


class TestGetErrorCount:
    def test_returns_count(self, db):
        # get_error_count creates two cursors: one for INSERT, one for SELECT
        cursors = []

        def cursor_factory(dictionary=False):
            cur = MagicMock()
            cur.fetchone.return_value = (3,)
            cursors.append(cur)
            return cur

        db._conn.cursor.side_effect = cursor_factory
        result = db.get_error_count('action', 'error msg')
        assert result == 3

    def test_returns_zero_when_no_row(self, db):
        def cursor_factory(dictionary=False):
            cur = MagicMock()
            cur.fetchone.return_value = None
            return cur

        db._conn.cursor.side_effect = cursor_factory
        result = db.get_error_count('action', 'error msg')
        assert result == 0


class TestUpdatePastTimeSeries:
    def test_skips_empty_data(self, db):
        db._execute = MagicMock()
        db._update_past_time_series('past_five_minutes', ['coal'], [])
        db._execute.assert_not_called()

    def test_inserts_rows(self, db):
        db._execute = MagicMock()
        db._update_past_time_series(
            'past_five_minutes',
            ['coal'],
            [['"2024-06-01 10:00:00"', 1.0]]
        )
        db._execute.assert_called_once()
        sql = db._execute.call_args[0][0]
        assert 'INSERT INTO past_five_minutes' in sql


class TestGetYearlyVisits:
    def test_returns_integer(self, db):
        _set_cursor(db, row=(42,))
        result = db._get_yearly_visits()
        assert result == 42

    def test_returns_zero_when_null(self, db):
        _set_cursor(db, row=(None,))
        result = db._get_yearly_visits()
        assert result == 0

