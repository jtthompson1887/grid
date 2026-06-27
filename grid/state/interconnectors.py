from .map import Map


class Interconnectors(Map):
    BELGIUM = 'belgium'
    DENMARK = 'denmark'
    FRANCE = 'france'
    IRELAND = 'ireland'
    NETHERLANDS = 'netherlands'
    NORWAY = 'norway'

    KEYS = {
        'belgium':     'Belgium',
        'denmark':     'Denmark',
        'france':      'France',
        'ireland':     'Ireland',
        'netherlands': 'Netherlands',
        'norway':      'Norway',
    }

    KEY_COMPONENTS = {
        'belgium':     ['nemo'],
        'denmark':     ['viking'],
        'france':      ['ifa', 'ifa2', 'eleclink'],
        'ireland':     ['moyle', 'ewic', 'greenlink'],
        'netherlands': ['britned'],
        'norway':      ['nsl'],
    }
