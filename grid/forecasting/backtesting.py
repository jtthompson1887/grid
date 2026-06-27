import math
from statistics import mean


def compute_metrics(rows: list[dict]) -> dict:
    errors = [row['predicted'] - row['actual'] for row in rows if row.get('actual') is not None]
    abs_errors = [abs(e) for e in errors]
    squared = [e * e for e in errors]
    actuals = [row['actual'] for row in rows if row.get('actual') is not None]

    mae = mean(abs_errors) if abs_errors else None
    rmse = math.sqrt(mean(squared)) if squared else None
    wape = (sum(abs_errors) / sum(abs(a) for a in actuals)) if actuals and sum(abs(a) for a in actuals) else None

    smape_values = []
    for row in rows:
        actual = row.get('actual')
        pred = row.get('predicted')
        if actual is None or pred is None:
            continue
        denom = (abs(actual) + abs(pred)) / 2
        if denom == 0:
            continue
        smape_values.append(abs(pred - actual) / denom)

    return {
        'MAE': mae,
        'RMSE': rmse,
        'WAPE': wape,
        'sMAPE': mean(smape_values) if smape_values else None,
    }


def evaluate_interval_coverage(rows: list[dict], low_key: str, high_key: str) -> float | None:
    covered = 0
    total = 0
    for row in rows:
        actual = row.get('actual')
        low = row.get(low_key)
        high = row.get(high_key)
        if actual is None or low is None or high is None:
            continue
        total += 1
        if low <= actual <= high:
            covered += 1
    return (covered / total) if total else None


def promotion_allowed(result: dict) -> bool:
    if not result.get('electricity_wape_beats_baseline'):
        return False
    if not result.get('gas_wape_beats_baseline'):
        return False

    p10_p90 = result.get('interval_coverage_p10_p90')
    p05_p95 = result.get('interval_coverage_p05_p95')
    if p10_p90 is None or not (0.75 <= p10_p90 <= 0.95):
        return False
    if p05_p95 is None or not (0.85 <= p05_p95 <= 0.99):
        return False

    if result.get('missing_feature_group'):
        return False
    if result.get('future_leakage_detected'):
        return False
    return True
