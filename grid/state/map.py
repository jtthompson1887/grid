class Map:
    KEYS: dict = {}
    KEY_COMPONENTS: dict = {}

    def __init__(self, data: dict):
        self._map = {
            key: sum(float(data.get(comp) or 0) for comp in components)
            for key, components in self.__class__.KEY_COMPONENTS.items()
        }

    def get(self, key: str) -> float:
        return self._map.get(key, 0.0)

    def get_minimum(self) -> float:
        if not self._map:
            return 0.0
        return min(self._map.values())

    def get_maximum(self) -> float:
        if not self._map:
            return 0.0
        return max(self._map.values())

    def get_total(self) -> float:
        return sum(self._map.values())

    def to_dict(self) -> dict:
        return dict(self._map)
