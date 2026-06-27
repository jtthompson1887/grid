"""Tests for grid.data.pricing"""
import pytest
from unittest.mock import patch, MagicMock
from grid.data.exceptions import DataException
from grid.data.pricing import update, _get_datum, KEYS


def _mock_response(payload):
    mock = MagicMock()
    mock.json.return_value = payload
    mock.raise_for_status = MagicMock()
    return mock


class TestGetDatum:
    def test_float_price(self):
        item = {'startTime': '2024-06-01T10:00:00Z', 'price': 45.67}
        result = _get_datum(item)
        assert len(result) == 2
        assert result[1] == 45.67

    def test_integer_price(self):
        item = {'startTime': '2024-06-01T10:00:00Z', 'price': 50}
        result = _get_datum(item)
        assert result[1] == 50

    def test_negative_price(self):
        item = {'startTime': '2024-06-01T10:00:00Z', 'price': -10.0}
        result = _get_datum(item)
        assert result[1] == -10.0

    def test_missing_start_time_raises(self):
        with pytest.raises(DataException, match='Missing time'):
            _get_datum({'price': 45.0})

    def test_missing_price_raises(self):
        with pytest.raises(DataException, match='Missing price'):
            _get_datum({'startTime': '2024-06-01T10:00:00Z'})

    def test_string_price_raises(self):
        with pytest.raises(DataException, match='Invalid price'):
            _get_datum({'startTime': '2024-06-01T10:00:00Z', 'price': '45.0'})


class TestPricingKeys:
    def test_keys(self):
        assert KEYS == ['price']


class TestUpdate:
    def test_update_calls_database(self):
        db = MagicMock()
        db.get_latest_half_hour_timestamp.return_value = 1717228800  # fixed ts

        payload = {
            'data': [
                {'startTime': '2024-06-01T10:00:00Z', 'price': 45.0},
                {'startTime': '2024-06-01T10:30:00Z', 'price': 50.0},
            ]
        }
        with patch('requests.get', return_value=_mock_response(payload)):
            update(db)

        db.update.assert_called_once()
        args = db.update.call_args[0]
        assert args[0] == KEYS

    def test_update_network_error_raises(self):
        db = MagicMock()
        db.get_latest_half_hour_timestamp.return_value = 1717228800
        with patch('requests.get', side_effect=Exception('timeout')):
            with pytest.raises(DataException, match='Failed to read data'):
                update(db)

    def test_update_bad_structure_raises(self):
        db = MagicMock()
        db.get_latest_half_hour_timestamp.return_value = 1717228800
        with patch('requests.get', return_value=_mock_response({'nope': []})):
            with pytest.raises(DataException, match='Missing data'):
                update(db)

    def test_update_data_not_list_raises(self):
        db = MagicMock()
        db.get_latest_half_hour_timestamp.return_value = 1717228800
        with patch('requests.get', return_value=_mock_response({'data': 'oops'})):
            with pytest.raises(DataException, match='Missing data'):
                update(db)

    def test_update_invalid_item_raises(self):
        db = MagicMock()
        db.get_latest_half_hour_timestamp.return_value = 1717228800
        with patch('requests.get', return_value=_mock_response({'data': ['not-a-dict']})):
            with pytest.raises(DataException, match='Invalid item'):
                update(db)
