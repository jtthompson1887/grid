
def calculate_confidence_score(
    *,
    horizon_regime: str,
    weather_partially_missing: bool,
    gas_conversion_fallback_used: bool,
    scenario_paths: int | None,
    calibrated: bool,
    baseline_only: bool,
) -> int:
    starts = {
        'operational_forecast': 90,
        'extended_weather_forecast': 70,
        'planning_scenario_forecast': 45,
    }
    score = starts.get(horizon_regime, 0)

    if weather_partially_missing:
        score -= 10
    if gas_conversion_fallback_used:
        score -= 10
    if scenario_paths is not None and scenario_paths < 30:
        score -= 15
    if not calibrated:
        score -= 10
    if baseline_only:
        score -= 20

    return max(0, min(100, score))
