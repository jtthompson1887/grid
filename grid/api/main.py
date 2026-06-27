import os
import json
from datetime import UTC, date, datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response, JSONResponse
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

from ..database import Database
from ..ui.favicon import create as create_favicon
from ..forecasting.constants import FORECAST_LABEL, FuelType
from ..forecasting.service import service as forecast_service

app = FastAPI()


@app.get('/api/state')
def get_state():
    db = Database()
    state = db.get_state()
    return JSONResponse(content=state.to_dict())


@app.get('/api/favicon.svg')
def get_favicon():
    db = Database()
    state = db.get_state()
    svg = create_favicon(state.latest.types)
    return Response(content=svg, media_type='image/svg+xml')


def _parse_utc_datetime(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _ensure_forecast_data():
    if not forecast_service.store.latest_forecast_run:
        forecast_service.seed_demo_run()


@app.get('/api/forecast/hourly')
def get_hourly_forecast(
    fuel_type: FuelType = Query(...),
    start_time_utc: str = Query(...),
    end_time_utc: str = Query(...),
):
    _ensure_forecast_data()
    start = _parse_utc_datetime(start_time_utc)
    end = _parse_utc_datetime(end_time_utc)
    rows = forecast_service.get_hourly(fuel_type.value, start, end)
    return JSONResponse(
        content={
            'label': FORECAST_LABEL,
            'rows': [
                {
                    **row,
                    'target_time_utc': row['target_time_utc'].isoformat(),
                    'target_time_local': row['target_time_local'].isoformat(),
                }
                for row in rows
            ],
        }
    )


@app.get('/api/forecast/daily')
def get_daily_forecast(
    fuel_type: FuelType = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
):
    _ensure_forecast_data()
    rows = forecast_service.get_daily(
        fuel_type.value,
        date.fromisoformat(start_date),
        date.fromisoformat(end_date),
    )
    return JSONResponse(content={'label': FORECAST_LABEL, 'rows': rows})


@app.get('/api/forecast/explain/hourly')
def get_hourly_explanation(
    forecast_run_id: str = Query(...),
    fuel_type: FuelType = Query(...),
    target_time_utc: str = Query(...),
):
    _ensure_forecast_data()
    row = forecast_service.get_hourly_explanation(
        forecast_run_id,
        fuel_type.value,
        _parse_utc_datetime(target_time_utc),
    )
    if row is None:
        raise HTTPException(status_code=404, detail='not found')
    return JSONResponse(content=row)


@app.get('/api/forecast/explain/daily')
def get_daily_explanation(
    forecast_run_id: str = Query(...),
    fuel_type: FuelType = Query(...),
    date_local: str = Query(...),
):
    _ensure_forecast_data()
    row = forecast_service.get_daily_explanation(forecast_run_id, fuel_type.value, date_local)
    if row is None:
        raise HTTPException(status_code=404, detail='not found')
    return JSONResponse(content=row)


@app.get('/api/forecast/model-status')
def get_model_status():
    _ensure_forecast_data()
    status = forecast_service.get_model_status()
    return JSONResponse(content=status.__dict__)


@app.get('/api/forecast/backtest-summary')
def get_backtest_summary():
    _ensure_forecast_data()
    return JSONResponse(content={'rows': forecast_service.get_backtest_summary()})
