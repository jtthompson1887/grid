"""Tests for grid.data.time_utils"""
import pytest
from grid.data.exceptions import DataException
from grid.data.time_utils import normalise, get_settlement_time


class TestNormalise:
    def test_iso_t_separator_no_seconds(self):
        result = normalise('2024-06-01T10:00Z', 5)
        assert result == '"2024-06-01 10:00:00"'

    def test_iso_space_separator_with_seconds(self):
        result = normalise('2024-06-01 10:00:00', 5)
        assert result == '"2024-06-01 10:00:00"'

    def test_interval_30_minutes(self):
        result = normalise('2024-06-01T10:30:00Z', 30)
        assert result == '"2024-06-01 10:30:00"'

    def test_interval_boundary_midnight(self):
        result = normalise('2024-06-01T00:00:00Z', 5)
        assert result == '"2024-06-01 00:00:00"'

    def test_interval_boundary_23_55(self):
        result = normalise('2024-06-01T23:55:00Z', 5)
        assert result == '"2024-06-01 23:55:00"'

    def test_invalid_format_raises(self):
        with pytest.raises(DataException, match='Invalid time format'):
            normalise('not-a-time', 5)

    def test_invalid_date_raises(self):
        with pytest.raises(DataException, match='Invalid date'):
            normalise('2024-02-30T00:00:00Z', 5)

    def test_not_multiple_of_interval_raises(self):
        with pytest.raises(DataException, match='Not a multiple of 5'):
            normalise('2024-06-01T10:03:00Z', 5)

    def test_not_multiple_of_30_raises(self):
        with pytest.raises(DataException, match='Not a multiple of 30'):
            normalise('2024-06-01T10:05:00Z', 30)

    def test_invalid_month_raises(self):
        # month 13 passes the regex (matched as \d{2}) but fails the date check
        with pytest.raises(DataException, match='Invalid date'):
            normalise('2024-13-01T00:00:00Z', 5)

    def test_t_separator_stripped(self):
        result = normalise('2024-01-15T08:30:00Z', 30)
        assert 'T' not in result

    def test_z_stripped(self):
        result = normalise('2024-01-15T08:30:00Z', 30)
        assert 'Z' not in result


class TestGetSettlementTime:
    def test_iso_date_period_1(self):
        result = get_settlement_time('2024-06-01', 1)
        assert isinstance(result, str)
        assert result.startswith('"')
        assert result.endswith('"')

    def test_iso_date_period_2(self):
        result1 = get_settlement_time('2024-06-01', 1)
        result2 = get_settlement_time('2024-06-01', 2)
        # period 2 is 30 minutes after period 1
        t1 = int(result1.strip('"').replace(' ', 'T').split('T')[1].split(':')[1])
        # just check they differ
        assert result1 != result2

    def test_uk_date_format(self):
        result = get_settlement_time('01-JAN-2024', 1)
        assert isinstance(result, str)
        assert result.startswith('"')

    def test_uk_all_months(self):
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                  'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        for i, m in enumerate(months, 1):
            result = get_settlement_time(f'01-{m}-2024', 1)
            assert result.startswith('"')

    def test_invalid_format_raises(self):
        with pytest.raises(DataException, match='Invalid settlement date format'):
            get_settlement_time('01/06/2024', 1)

    def test_invalid_date_raises(self):
        with pytest.raises(DataException, match='Invalid settlement date'):
            get_settlement_time('2024-02-30', 1)

    def test_period_zero_raises(self):
        with pytest.raises(DataException, match='Invalid settlement period'):
            get_settlement_time('2024-06-01', 0)

    def test_period_51_raises(self):
        with pytest.raises(DataException, match='Invalid settlement period'):
            get_settlement_time('2024-06-01', 51)

    def test_period_50_valid(self):
        result = get_settlement_time('2024-06-01', 50)
        assert result.startswith('"')

    def test_uk_invalid_month_raises(self):
        with pytest.raises(DataException, match='Invalid settlement date'):
            get_settlement_time('01-XYZ-2024', 1)

    def test_period_half_hour_offset(self):
        # period 1 vs period 3 should differ by 3600 seconds
        import calendar, datetime
        r1 = get_settlement_time('2024-06-01', 1).strip('"')
        r3 = get_settlement_time('2024-06-01', 3).strip('"')
        dt1 = datetime.datetime.strptime(r1, '%Y-%m-%d %H:%M:%S')
        dt3 = datetime.datetime.strptime(r3, '%Y-%m-%d %H:%M:%S')
        assert (dt3 - dt1).total_seconds() == 3600
