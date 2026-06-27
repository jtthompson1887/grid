from .map import Map


class Types(Map):
    FOSSILS = 'fossils'
    RENEWABLES = 'renewables'
    OTHERS = 'others'

    KEYS = {
        'fossils':    'Fossil fuels',
        'renewables': 'Renewables',
        'others':     'Other sources',
    }

    KEY_COMPONENTS = {
        'fossils':    ['coal', 'ocgt', 'ccgt'],
        'renewables': ['embedded_solar', 'embedded_wind', 'wind', 'hydro'],
        'others':     ['nuclear', 'biomass'],
    }
