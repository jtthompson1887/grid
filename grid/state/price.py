from .map import Map


class Price(Map):
    PRICE = 'price'

    KEYS = {
        'price': 'Price',
    }

    KEY_COMPONENTS = {
        'price': ['price'],
    }
