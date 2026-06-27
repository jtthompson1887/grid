from .map import Map


class Emissions(Map):
    EMISSIONS = 'emissions'

    KEYS = {
        'emissions': 'Emissions',
    }

    KEY_COMPONENTS = {
        'emissions': ['emissions'],
    }
