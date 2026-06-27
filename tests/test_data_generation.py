"""Tests for grid.data.generation"""
import pytest
from unittest.mock import patch, MagicMock
from grid.data.exceptions import DataException
from grid.data import generation as gen_module
from grid.data.generation import _get_time, _get_column, _get_generation, update, COLUMNS, KEYS


def _make_item(**kwargs):
    base = {'startTime': '2024-06-01T10:00:00Z', 'fuelType': 'COAL', 'generation': 1000}
    base.update(kwargs)
    return base


class TestGetTime:
    def test_valid(self):
        item = _make_item(startTime='2024-06-01T10:00:00Z')
        result = _get_time(item)
        assert result == '"2024-06-01 10:00:00"'

    def test_missing_start_time(self):
        with pytest.raises(DataException, match='Missing start time'):
            _get_time({})

    def test_non_string_start_time(self):
        with pytest.raises(DataException, match='Invalid start time'):
            _get_time({'startTime': 12345})

    def test_invalid_format(self):
        with pytest.raises(DataException):
            _get_time({'startTime': 'not-a-time'})


class TestGetColumn:
    def test_known_fuel_types(self):
        for fuel, col in COLUMNS.items():
            assert _get_column({'fuelType': fuel}) == col

    def test_missing_fuel_type(self):
        with pytest.raises(DataException, match='Missing fuel type'):
            _get_column({})

    def test_unknown_fuel_type(self):
        with pytest.raises(DataException, match='Invalid fuel type'):
            _get_column({'fuelType': 'UNKNOWN'})

    def test_non_string_fuel_type(self):
        with pytest.raises(DataException, match='Invalid fuel type'):
            _get_column({'fuelType': 123})


class TestGetGeneration:
    def test_valid_integer(self):
        result = _get_generation({'generation': 5000})
        assert result == 5.0

    def test_rounds_to_two_dp(self):
        result = _get_generation({'generation': 1001})
        assert result == round(1001 / 1000, 2)

    def test_zero(self):
        result = _get_generation({'generation': 0})
        assert result == 0.0

    def test_missing_generation(self):
        with pytest.raises(DataException, match='Missing generation'):
            _get_generation({})

    def test_non_integer_generation(self):
        with pytest.raises(DataException, match='Invalid generation value'):
            _get_generation({'generation': 1.5})

    def test_string_generation(self):
        with pytest.raises(DataException, match='Invalid generation value'):
            _get_generation({'generation': '1000'})


class TestUpdate:
    def test_update_calls_database(self):
        db = MagicMock()
        items = [
            {'startTime': '2024-06-01T10:00:00Z', 'fuelType': 'COAL', 'generation': 1000},
            {'startTime': '2024-06-01T10:00:00Z', 'fuelType': 'CCGT', 'generation': 2000},
            {'startTime': '2024-06-01T10:05:00Z', 'fuelType': 'WIND', 'generation': 500},
        ]
        mock_resp = MagicMock()
        mock_resp.json.return_value = items
        mock_resp.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_resp):
            update(db)

        db.update_generation.assert_called_once()
        call_args = db.update_generation.call_args[0][0]
        assert isinstance(call_args, list)
        assert len(call_args) == 2  # two unique time slots

    def test_update_non_list_response_raises(self):
        db = MagicMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {'error': 'bad'}
        mock_resp.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_resp):
            with pytest.raises(DataException, match='Missing data'):
                update(db)

    def test_update_network_error_raises(self):
        db = MagicMock()
        with patch('requests.get', side_effect=Exception('timeout')):
            with pytest.raises(DataException, match='Failed to read data'):
                update(db)

    def test_update_invalid_item_raises(self):
        db = MagicMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = ['not-a-dict']
        mock_resp.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_resp):
            with pytest.raises(DataException, match='Invalid item'):
                update(db)


class TestKeys:
    def test_keys_list(self):
        assert 'coal' in KEYS
        assert 'wind' in KEYS
        assert len(KEYS) == 21
