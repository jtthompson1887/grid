from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo

from .confidence import calculate_confidence_score
from .constants import FuelType, get_regime
from .daily import aggregate_daily_predictions


@dataclass
class ForecastStatus:
    latest_forecast_run: str | None
    model_versions: list[dict]
    training_data_range: dict[str, str | None]
    latest_backtest_metrics: list[dict]
    calibration_status: str
    data_source_status: dict[str, str]


class ForecastStore:
    def __init__(self):
        self.hourly_rows: list[dict] = []
        self.daily_rows: list[dict] = []
        self.hourly_explanations: list[dict] = []
        self.daily_explanations: list[dict] = []
        self.backtest_summary: list[dict] = []
        self.latest_forecast_run: str | None = None
        self.model_versions: list[dict] = []
        self.training_data_range = {'start': None, 'end': None}
        self.calibration_status = 'model_not_calibrated'
        self.data_source_status = {}


class ForecastService:
    def __init__(self, store: ForecastStore | None = None):
        self.store = store or ForecastStore()

    def seed_demo_run(self, issue_time_utc: datetime | None = None):
        issue_time = issue_time_utc or datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
        london = ZoneInfo('Europe/London')
        run_id = str(uuid4())
        self.store.latest_forecast_run = run_id
        self.store.hourly_rows.clear()

        for horizon in range(1, 49):
            target = issue_time.replace(tzinfo=UTC) + timedelta(hours=horizon)
            regime = get_regime(horizon).value
            score = calculate_confidence_score(
                horizon_regime=regime,
                weather_partially_missing=False,
                gas_conversion_fallback_used=False,
                scenario_paths=100 if horizon > 840 else None,
                calibrated=True,
                baseline_only=False,
            )
            for fuel_type, base in (('electricity', 30000.0), ('gas', 25000.0)):
                p50 = base + (horizon * 5)
                row = {
                    'forecast_run_id': run_id,
                    'target_time_utc': target,
                    'target_time_local': target.astimezone(london),
                    'fuel_type': fuel_type,
                    'p05': p50 * 0.9,
                    'p10': p50 * 0.93,
                    'p25': p50 * 0.97,
                    'p50': p50,
                    'p75': p50 * 1.03,
                    'p90': p50 * 1.07,
                    'p95': p50 * 1.10,
                    'mean_prediction': p50,
                    'unit': 'MWh',
                    'forecast_regime': regime,
                    'weather_mode': 'historical_weather_analogue' if horizon > 840 else 'deterministic_weather_forecast',
                    'confidence_score': score,
                    'calibration_status': 'calibrated',
                    'date_local': target.astimezone(london).date().isoformat(),
                }
                self.store.hourly_rows.append(row)

        self._derive_combined_rows(run_id)
        self.store.daily_rows = aggregate_daily_predictions(self.store.hourly_rows)

    def _derive_combined_rows(self, run_id: str):
        by_target = {}
        for row in self.store.hourly_rows:
            by_target.setdefault(row['target_time_utc'], {})[row['fuel_type']] = row

        combined_rows = []
        for target, fuels in by_target.items():
            elec = fuels.get(FuelType.ELECTRICITY.value)
            gas = fuels.get(FuelType.GAS.value)
            if not elec or not gas:
                continue
            combined = {
                **elec,
                'fuel_type': FuelType.COMBINED.value,
                'forecast_run_id': run_id,
            }
            for key in ('p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'mean_prediction'):
                combined[key] = elec[key] + gas[key]
            combined_rows.append(combined)
        self.store.hourly_rows.extend(combined_rows)

    def get_hourly(self, fuel_type: str, start_time_utc: datetime, end_time_utc: datetime) -> list[dict]:
        return [
            row
            for row in self.store.hourly_rows
            if row['fuel_type'] == fuel_type and start_time_utc <= row['target_time_utc'] <= end_time_utc
        ]

    def get_daily(self, fuel_type: str, start_date: date, end_date: date) -> list[dict]:
        return [
            row
            for row in self.store.daily_rows
            if row['fuel_type'] == fuel_type and start_date <= date.fromisoformat(row['date_local']) <= end_date
        ]

    def get_hourly_explanation(self, forecast_run_id: str, fuel_type: str, target_time_utc: datetime) -> dict[str, Any] | None:
        for row in self.store.hourly_explanations:
            if (
                row['forecast_run_id'] == forecast_run_id
                and row['fuel_type'] == fuel_type
                and row['target_time_utc'] == target_time_utc
            ):
                return row
        return None

    def get_daily_explanation(self, forecast_run_id: str, fuel_type: str, date_local: str) -> dict[str, Any] | None:
        for row in self.store.daily_explanations:
            if (
                row['forecast_run_id'] == forecast_run_id
                and row['fuel_type'] == fuel_type
                and row['date_local'] == date_local
            ):
                return row
        return None

    def get_model_status(self) -> ForecastStatus:
        return ForecastStatus(
            latest_forecast_run=self.store.latest_forecast_run,
            model_versions=self.store.model_versions,
            training_data_range=self.store.training_data_range,
            latest_backtest_metrics=self.store.backtest_summary,
            calibration_status=self.store.calibration_status,
            data_source_status=self.store.data_source_status,
        )

    def get_backtest_summary(self) -> list[dict]:
        return self.store.backtest_summary


service = ForecastService()
