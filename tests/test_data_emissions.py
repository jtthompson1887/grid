"""Tests for grid.data.emissions"""
import pytest
from unittest.mock import patch, MagicMock
from grid.data.exceptions import DataException
from grid.data.emissions import update, _get_datum, KEYS


def _mock_response(payload):
    mock = MagicMock()
    mock.json.return_value = payload
    mock.raise_for_status = MagicMock()
    return mock


class TestGetDatum:
    def test_actual_intensity(self):
        item = {'from': '2024-06-01T10:00Z', 'intensity': {'actual': 200, 'forecast': 210}}
        result = _get_datum(item)
        assert len(result) == 2
        assert result[1] == 200

    def test_forecast_when_actual_none(self):
        item = {'from': '2024-06-01T10:30Z', 'intensity': {'actual': None, 'forecast': 180}}
        result = _get_datum(item)
        assert result[1] == 180

    def test_missing_from_raises(self):
        item = {'intensity': {'actual': 200}}
        with pytest.raises(DataException, match='Missing time'):
            _get_datum(item)

    def test_missing_intensity_raises(self):
        item = {'from': '2024-06-01T10:00Z', 'intensity': {}}
        with pytest.raises(DataException, match='Missing emissions value'):
            _get_datum(item)

    def test_non_integer_emissions_raises(self):
        item = {'from': '2024-06-01T10:00Z', 'intensity': {'actual': 12.5}}
        with pytest.raises(DataException, match='Invalid emissions value'):
            _get_datum(item)

    def test_string_emissions_raises(self):
        item = {'from': '2024-06-01T10:00Z', 'intensity': {'actual': '200'}}
        with pytest.raises(DataException, match='Invalid emissions value'):
            _get_datum(item)


class TestEmissionsKeys:
    def test_keys(self):
        assert KEYS == ['emissions']


class TestUpdate:
    def test_update_calls_database(self):
        db = MagicMock()
        payload = {
            'data': [
                {'from': '2024-06-01T10:00Z', 'intensity': {'actual': 200, 'forecast': 210}},
                {'from': '2024-06-01T10:30Z', 'intensity': {'actual': None, 'forecast': 180}},
            ]
        }
        with patch('requests.get', return_value=_mock_response(payload)):
            update(db)

        db.update.assert_called_once_with(KEYS, [
            ['"2024-06-01 10:00:00"', 200],
            ['"2024-06-01 10:30:00"', 180],
        ])

    def test_update_network_error_raises(self):
        db = MagicMock()
        with patch('requests.get', side_effect=Exception('timeout')):
            with pytest.raises(DataException, match='Failed to read data'):
                update(db)

    def test_update_bad_structure_raises(self):
        db = MagicMock()
        with patch('requests.get', return_value=_mock_response({'wrong': 'key'})):
            with pytest.raises(DataException, match='Missing data'):
                update(db)

    def test_update_data_not_list_raises(self):
        db = MagicMock()
        with patch('requests.get', return_value=_mock_response({'data': 'oops'})):
            with pytest.raises(DataException, match='Missing data'):
                update(db)

    def test_update_invalid_item_raises(self):
        db = MagicMock()
        with patch('requests.get', return_value=_mock_response({'data': ['not-a-dict']})):
            with pytest.raises(DataException, match='Invalid item'):
                update(db)
