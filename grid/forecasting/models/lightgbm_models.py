from dataclasses import dataclass

try:
    import lightgbm as lgb
except Exception:  # pragma: no cover
    lgb = None


@dataclass
class QuantileModelSpec:
    fuel_type: str
    horizon_regime: str
    quantile: str


QUANTILES = {
    'p05': 0.05,
    'p10': 0.10,
    'p25': 0.25,
    'p50': 0.50,
    'p75': 0.75,
    'p90': 0.90,
    'p95': 0.95,
}


class LightGBMQuantileModel:
    def __init__(self, quantile_alpha: float):
        self.quantile_alpha = quantile_alpha
        self.model = None

    def fit(self, x_train, y_train):
        if lgb is None:
            raise RuntimeError('model_not_trained')
        self.model = lgb.LGBMRegressor(
            objective='quantile',
            alpha=self.quantile_alpha,
            n_estimators=300,
            learning_rate=0.05,
            num_leaves=31,
            min_child_samples=40,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
        )
        self.model.fit(x_train, y_train)
        return self

    def predict(self, x):
        if self.model is None:
            raise RuntimeError('model_not_trained')
        return self.model.predict(x)


class ForecastModelRegistry:
    def __init__(self):
        self._models = {}

    def register(self, fuel_type: str, horizon_regime: str, quantile: str, model):
        self._models[(fuel_type, horizon_regime, quantile)] = model

    def get(self, fuel_type: str, horizon_regime: str, quantile: str):
        return self._models.get((fuel_type, horizon_regime, quantile))

    def versions(self):
        return [
            {
                'fuel_type': fuel,
                'horizon_regime': regime,
                'quantile': quantile,
                'model_type': 'lightgbm_quantile',
            }
            for fuel, regime, quantile in sorted(self._models.keys())
        ]


def required_lightgbm_specs() -> list[QuantileModelSpec]:
    specs = []
    for fuel in ('electricity', 'gas'):
        for regime in ('short_term', 'medium_term', 'long_term'):
            for quantile in QUANTILES:
                specs.append(QuantileModelSpec(fuel_type=fuel, horizon_regime=regime, quantile=quantile))
    return specs
