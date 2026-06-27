from collections import defaultdict


def conformal_adjustments(backtest_rows: list[dict]) -> dict[tuple, dict]:
    grouped = defaultdict(list)
    for row in backtest_rows:
        key = (row['fuel_type'], row['horizon_regime'], row['season'])
        grouped[key].append(row)

    results = {}
    for key, rows in grouped.items():
        residuals = sorted(abs(row['actual'] - row['p50']) for row in rows if row.get('actual') is not None)
        if not residuals:
            continue
        p90_index = min(len(residuals) - 1, int(len(residuals) * 0.90))
        p95_index = min(len(residuals) - 1, int(len(residuals) * 0.95))
        results[key] = {
            'p10_p90_adjustment': residuals[p90_index],
            'p05_p95_adjustment': residuals[p95_index],
            'calibration_status': 'calibrated',
        }
    return results


def apply_conformal_calibration(row: dict, adjustment: dict | None) -> dict:
    if not adjustment:
        row['calibration_status'] = 'uncalibrated'
        return row

    p90_adj = adjustment['p10_p90_adjustment']
    p95_adj = adjustment['p05_p95_adjustment']

    row['p10'] = row['p50'] - p90_adj
    row['p90'] = row['p50'] + p90_adj
    row['p05'] = row['p50'] - p95_adj
    row['p95'] = row['p50'] + p95_adj
    row['calibration_status'] = 'calibrated'
    return row
