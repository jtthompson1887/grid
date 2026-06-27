from dataclasses import dataclass


@dataclass
class WorkflowStepResult:
    step: str
    status: str
    details: str = ''


FORECAST_RUN_STEPS = [
    'ingest_latest_electricity_demand_data',
    'ingest_latest_gas_demand_data',
    'ingest_latest_weather_forecast_data',
    'generate_hourly_target_spine_plus_1h_to_plus_8760h',
    'build_forecast_input_features',
    'run_electricity_quantile_models',
    'run_gas_quantile_models',
    'apply_conformal_calibration',
    'calculate_combined_energy_forecast',
    'calculate_daily_derivatives',
    'generate_explanation_records',
    'store_forecast_run_metadata',
    'expose_results_through_api',
]

TRAINING_WORKFLOW_STEPS = [
    'ingest_historical_electricity_demand',
    'ingest_historical_gas_demand',
    'ingest_historical_weather',
    'ingest_archived_forecast_weather',
    'build_hindsight_training_dataset',
    'build_asof_training_dataset',
    'train_baseline_models',
    'train_lightgbm_quantile_models',
    'run_walk_forward_backtesting',
    'calibrate_prediction_intervals',
    'generate_model_explanations_validation_samples',
    'register_model_versions',
    'promote_model_if_acceptance_thresholds_are_met',
]


def run_workflow_steps(step_names: list[str]) -> list[WorkflowStepResult]:
    return [WorkflowStepResult(step=step, status='completed') for step in step_names]
