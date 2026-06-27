from .price import Price
from .emissions import Emissions
from .generation import Generation
from .types import Types
from .interconnectors import Interconnectors
from .storage import Storage
from .transfers import Transfers
from .demand import Demand
from .visits import Visits

PRICE = 0
EMISSIONS = 1
GENERATION = 2
TYPES = 3
INTERCONNECTORS = 4
STORAGE = 5
TRANSFERS = 6
DEMAND = 7
VISITS = 8


class Datum:
    def __init__(self, data: dict):
        self.price = Price(data)
        self.emissions = Emissions(data)
        self.generation = Generation(data)
        self.types = Types(data)
        self.interconnectors = Interconnectors(data)
        self.storage = Storage(data)
        self.transfers = Transfers(data)
        self.demand = Demand(self.types, self.transfers)
        self.visits = Visits(data)

    def get(self, map_type: int):
        mapping = {
            PRICE:          self.price,
            EMISSIONS:      self.emissions,
            GENERATION:     self.generation,
            TYPES:          self.types,
            INTERCONNECTORS: self.interconnectors,
            STORAGE:        self.storage,
            TRANSFERS:      self.transfers,
            DEMAND:         self.demand,
            VISITS:         self.visits,
        }
        if map_type not in mapping:
            raise ValueError(f'Invalid map type: {map_type}')
        return mapping[map_type]

    def get_total(self) -> float:
        return self.generation.get_total() + self.transfers.get_total()

    def to_dict(self) -> dict:
        return {
            'price':          self.price.to_dict(),
            'emissions':      self.emissions.to_dict(),
            'generation':     self.generation.to_dict(),
            'types':          self.types.to_dict(),
            'interconnectors': self.interconnectors.to_dict(),
            'storage':        self.storage.to_dict(),
            'transfers':      self.transfers.to_dict(),
            'demand':         self.demand.to_dict(),
            'visits':         self.visits.to_dict(),
            'total':          self.get_total(),
        }
