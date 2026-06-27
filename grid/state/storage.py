from .map import Map


class Storage(Map):
    PUMPED_STORAGE = 'pumped'

    KEYS = {
        'pumped': 'Pumped storage',
    }

    KEY_COMPONENTS = {
        'pumped': ['pumped'],
    }
