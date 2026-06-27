from collections import defaultdict

try:
    import shap
except Exception:  # pragma: no cover
    shap = None


ELECTRICITY_TEMPLATE = (
    'Electricity forecast is above seasonal normal mainly because of recent demand strength, '
    'time-of-day pattern and colder-than-normal temperature.'
)
GAS_TEMPLATE = (
    'Gas forecast is above seasonal normal mainly because of heating degree hours, '
    'accumulated cold over the previous 72 hours and winter seasonality.'
)
HIGH_UNCERTAINTY_TEMPLATE = (
    'Forecast uncertainty is high because the target time is outside the reliable deterministic weather forecast range.'
)


def build_hourly_explanation(
    *,
    forecast_run_id: str,
    target_time_utc,
    fuel_type: str,
    top_features: list[str],
    top_contributions: list[float],
    feature_group_contributions: dict[str, float],
    high_uncertainty: bool,
) -> dict:
    summary = ELECTRICITY_TEMPLATE if fuel_type == 'electricity' else GAS_TEMPLATE
    if high_uncertainty:
        summary = f'{summary} {HIGH_UNCERTAINTY_TEMPLATE}'

    return {
        'forecast_run_id': forecast_run_id,
        'target_time_utc': target_time_utc,
        'fuel_type': fuel_type,
        'top_10_features': top_features[:10],
        'top_10_feature_contributions': top_contributions[:10],
        'feature_group_contributions': feature_group_contributions,
        'plain_language_summary': summary,
    }


def aggregate_daily_explanations(hourly_rows: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for row in hourly_rows:
        grouped[(row['forecast_run_id'], row['fuel_type'], row['date_local'])].append(row)

    results = []
    for (run_id, fuel_type, date_local), rows in grouped.items():
        group_totals = defaultdict(float)
        for row in rows:
            for group_name, value in row.get('feature_group_contributions', {}).items():
                group_totals[group_name] += value

        sorted_features = sorted(group_totals.items(), key=lambda item: abs(item[1]), reverse=True)[:10]
        summary = ELECTRICITY_TEMPLATE if fuel_type == 'electricity' else GAS_TEMPLATE
        results.append(
            {
                'forecast_run_id': run_id,
                'date_local': date_local,
                'fuel_type': fuel_type,
                'top_10_features': [name for name, _ in sorted_features],
                'feature_group_contributions': dict(group_totals),
                'plain_language_summary': summary,
            }
        )
    return results


def compute_shap_values(model, feature_matrix):
    if shap is None:
        raise RuntimeError('model_not_trained')
    explainer = shap.TreeExplainer(model)
    return explainer.shap_values(feature_matrix)
