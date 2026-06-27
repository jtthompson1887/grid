from .map import Map
from .types import Types
from .transfers import Transfers


class Demand(Map):
    DEMAND = 'demand'
    FOSSILS = 'fossils'
    RENEWABLES = 'renewables'
    OTHERS = 'others'
    TRANSFERS = 'transfers'

    KEYS = {
        'demand':     'Demand',
        'fossils':    'Fossil fuels',
        'renewables': 'Renewables',
        'others':     'Other sources',
        'transfers':  'Transfers',
    }

    KEY_COMPONENTS = {}

    def __init__(self, types: Types, transfers: Transfers):
        fossils = round(types.get(Types.FOSSILS), 1)
        renewables = round(types.get(Types.RENEWABLES), 1)
        others = round(types.get(Types.OTHERS), 1)
        transfers_total = round(transfers.get_total(), 1)

        self._generation = fossils + renewables + others

        self._map = {
            self.DEMAND:     self._generation + transfers_total,
            self.FOSSILS:    fossils,
            self.RENEWABLES: renewables,
            self.OTHERS:     others,
            self.TRANSFERS:  transfers_total,
        }

    def get_generation(self) -> float:
        return self._generation
