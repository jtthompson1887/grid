"""Tests for grid.data.demand"""
import pytest
from unittest.mock import patch, MagicMock
from grid.data.exceptions import DataException
from grid.data.demand import update, _get_datum, KEYS


def _make_demand_row(date='2024-06-01', period='1', wind='1000', solar='500'):
    return [date, period, wind, solar]


class TestGetDatum:
    def test_valid_iso_date(self):
        row = _make_demand_row()
        result = _get_datum(row)
        assert len(result) == 3
        assert result[1] == 1.0
        assert result[2] == 0.5

    def test_non_integer_wind_raises(self):
        with pytest.raises(DataException, match='Non-integer value'):
            _get_datum(['2024-06-01', '1', '1000.5', '500'])

    def test_non_integer_solar_raises(self):
        with pytest.raises(DataException, match='Non-integer value'):
            _get_datum(['2024-06-01', '1', '1000', '500.1'])

    def test_invalid_period_raises(self):
        with pytest.raises(DataException, match='Invalid settlement period'):
            _get_datum(['2024-06-01', 'abc', '1000', '500'])

    def test_zero_values(self):
        result = _get_datum(['2024-06-01', '2', '0', '0'])
        assert result[1] == 0.0
        assert result[2] == 0.0


class TestDemandKeys:
    def test_keys(self):
        assert KEYS == ['embedded_wind', 'embedded_solar']


class TestUpdate:
    def test_update_calls_database(self):
        db = MagicMock()
        csv_text = (
            'SETTLEMENT_DATE,SETTLEMENT_PERIOD,EMBEDDED_WIND_GENERATION,EMBEDDED_SOLAR_GENERATION,'
            'ND,FORECAST_ACTUAL_INDICATOR,TSD,ENGLAND_WALES_DEMAND,EMBEDDED_WIND_CAPACITY,'
            'EMBEDDED_SOLAR_CAPACITY,NON_BM_STOR,PUMP_STORAGE_PUMPING,SCOTTISH_TRANSFER,'
            'IFA_FLOW,IFA2_FLOW,BRITNED_FLOW,MOYLE_FLOW,EAST_WEST_FLOW,NEMO_FLOW,'
            'NSL_FLOW,ELECLINK_FLOW,VIKING_FLOW,GREENLINK_FLOW\n'
            '2024-06-01,1,1000,500,0,A,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0\n'
        )
        mock_resp = MagicMock()
        mock_resp.text = csv_text
        mock_resp.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_resp):
            update(db)

        db.update.assert_called_once()
        args = db.update.call_args[0]
        assert args[0] == KEYS
        assert len(args[1]) == 1

    def test_update_network_error_raises(self):
        db = MagicMock()
        with patch('requests.get', side_effect=Exception('timeout')):
            with pytest.raises(DataException, match='Failed to read data'):
                update(db)
