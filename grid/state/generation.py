from .map import Map


class Generation(Map):
    COAL = 'coal'
    GAS = 'gas'
    SOLAR = 'solar'
    WIND = 'wind'
    HYDROELECTRIC = 'hydro'
    NUCLEAR = 'nuclear'
    BIOMASS = 'biomass'

    KEYS = {
        'coal':  'Coal',
        'gas':   'Gas',
        'solar': 'Solar',
        'wind':  'Wind',
        'hydro': 'Hydroelectric',
        'nuclear': 'Nuclear',
        'biomass': 'Biomass',
    }

    KEY_COMPONENTS = {
        'coal':    ['coal'],
        'gas':     ['ocgt', 'ccgt'],
        'solar':   ['embedded_solar'],
        'wind':    ['embedded_wind', 'wind'],
        'hydro':   ['hydro'],
        'nuclear': ['nuclear'],
        'biomass': ['biomass'],
    }
