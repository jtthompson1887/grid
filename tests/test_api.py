"""Tests for grid.api.main (FastAPI endpoints)"""
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from grid.state.datum import Datum
from grid.state.record import Record
from grid.state.state import State


def _full_data():
    return {
        'coal': 1.0, 'ccgt': 2.0, 'ocgt': 0.5,
        'nuclear': 3.0, 'oil': 0.1,
        'wind': 4.0, 'hydro': 0.3,
        'pumped': 0.2, 'biomass': 1.5,
        'battery': 0.4, 'other': 0.0,
        'ifa': 0.5, 'moyle': 0.1, 'britned': 0.3,
        'ewic': 0.2, 'nemo': 0.4, 'ifa2': 0.6,
        'nsl': 0.7, 'eleclink': 0.8, 'viking': 0.9,
        'greenlink': 0.1,
        'embedded_wind': 2.0, 'embedded_solar': 1.0,
        'price': 50.0, 'emissions': 150,
        'visits': 100,
    }


def _make_state():
    datum = Datum(_full_data())
    record = Record(time=1717228800, power=20.0)
    series = {1717228800: datum}
    return State(
        time=1717228800,
        latest=datum,
        past_day=datum,
        past_week=datum,
        past_year=datum,
        all_time=datum,
        past_day_series=series,
        past_week_series=series,
        past_year_series=series,
        all_time_series=series,
        wind_record=record,
        wind_milestones={20: 1717228800},
        yearly_visits=5000,
    )


@pytest.fixture
def client():
    import os
    os.environ.setdefault('DATABASE_HOSTNAME', 'localhost')
    os.environ.setdefault('DATABASE_USERNAME', 'user')
    os.environ.setdefault('DATABASE_DATABASE', 'grid')
    os.environ.setdefault('DATABASE_PASSWORD', 'pass')

    with patch('grid.api.main.Database') as MockDB:
        mock_db_instance = MagicMock()
        mock_db_instance.get_state.return_value = _make_state()
        MockDB.return_value = mock_db_instance

        from grid.api.main import app
        with TestClient(app) as c:
            yield c, MockDB


class TestGetState:
    def test_status_200(self, client):
        c, _ = client
        response = c.get('/api/state')
        assert response.status_code == 200

    def test_response_is_json(self, client):
        c, _ = client
        response = c.get('/api/state')
        data = response.json()
        assert isinstance(data, dict)

    def test_top_level_keys(self, client):
        c, _ = client
        data = c.get('/api/state').json()
        expected = {
            'time', 'latest', 'past_day', 'past_week', 'past_year', 'all_time',
            'past_day_series', 'past_week_series', 'past_year_series', 'all_time_series',
            'wind_record', 'wind_milestones', 'yearly_visits',
        }
        assert set(data.keys()) == expected

    def test_time_value(self, client):
        c, _ = client
        data = c.get('/api/state').json()
        assert data['time'] == 1717228800

    def test_series_is_list(self, client):
        c, _ = client
        data = c.get('/api/state').json()
        assert isinstance(data['past_day_series'], list)

    def test_database_instantiated(self, client):
        c, MockDB = client
        c.get('/api/state')
        MockDB.assert_called()


class TestGetFavicon:
    def test_status_200(self, client):
        c, _ = client
        response = c.get('/api/favicon.svg')
        assert response.status_code == 200

    def test_content_type(self, client):
        c, _ = client
        response = c.get('/api/favicon.svg')
        assert 'image/svg+xml' in response.headers['content-type']

    def test_svg_content(self, client):
        c, _ = client
        response = c.get('/api/favicon.svg')
        assert b'<svg' in response.content
