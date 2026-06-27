from collections import defaultdict
from statistics import mean


def aggregate_daily_predictions(hourly_rows: list[dict], *, method: str = 'quantile_aggregation') -> list[dict]:
    grouped = defaultdict(list)
    for row in hourly_rows:
        grouped[(row['forecast_run_id'], row['fuel_type'], row['date_local'])].append(row)

    results = []
    for (run_id, fuel_type, date_local), rows in grouped.items():
        ordered = sorted(rows, key=lambda item: item['target_time_local'])
        peak_row = max(ordered, key=lambda item: item['p50'])
        forecast_regime = ordered[-1]['forecast_regime']
        confidence_score = min(int(row['confidence_score']) for row in ordered)
        daily = {
            'forecast_run_id': run_id,
            'date_local': date_local,
            'fuel_type': fuel_type,
            'daily_peak_time_local': peak_row['target_time_local'].strftime('%H:%M'),
            'daily_quantile_method': method,
            'unit': 'MWh',
            'forecast_regime': forecast_regime,
            'confidence_score': confidence_score,
        }

        for q in ('p05', 'p50', 'p95'):
            values = [float(row[q]) for row in ordered]
            daily[f'daily_total_{q}'] = sum(values)
            daily[f'daily_average_{q}'] = mean(values)
            daily[f'daily_peak_{q}'] = max(values)
        results.append(daily)

    return results
