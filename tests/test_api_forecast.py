from fastapi.testclient import TestClient

from grid.api.main import app
from grid.forecasting.service import forecast_service


class TestForecastApi:
    def setup_method(self):
        forecast_service.seed_demo_run()

    def test_hourly_endpoint(self):
        with TestClient(app) as client:
            response = client.get(
                '/api/forecast/hourly',
                params={
                    'fuel_type': 'electricity',
                    'start_time_utc': '2026-01-01T00:00:00Z',
                    'end_time_utc': '2027-01-01T00:00:00Z',
                },
            )
        assert response.status_code == 200
        body = response.json()
        assert body['label'] == 'Great Britain national electricity and gas demand forecast'
        assert isinstance(body['rows'], list)

    def test_daily_endpoint(self):
        with TestClient(app) as client:
            response = client.get(
                '/api/forecast/daily',
                params={
                    'fuel_type': 'combined',
                    'start_date': '2026-01-01',
                    'end_date': '2026-12-31',
                },
            )
        assert response.status_code == 200
        assert isinstance(response.json()['rows'], list)

    def test_model_status_endpoint(self):
        with TestClient(app) as client:
            response = client.get('/api/forecast/model-status')
        assert response.status_code == 200
        body = response.json()
        assert 'latest_forecast_run' in body
        assert 'calibration_status' in body
