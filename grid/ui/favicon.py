import math
from ..state.types import Types

RADIUS = 7.5
STROKE_WIDTH = 1
FOSSILS_COLOUR = '#c45'
RENEWABLES_COLOUR = '#5b5'
OTHERS_COLOUR = '#27c'


def create(types: Types) -> str:
    svg = (
        '<?xml version="1.0"?>'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-8 -8 16 16" width="16" height="16">'
        f'<style>path{{stroke:#fff;stroke-width:{STROKE_WIDTH};'
        '@media(prefers-color-scheme:dark){stroke:#000;}</style>'
    )

    total = types.get_total()
    if total == 0:
        total = 1

    fossils = types.get(Types.FOSSILS) / total
    renewables = types.get(Types.RENEWABLES) / total
    others = types.get(Types.OTHERS) / total

    svg += _create_arc(FOSSILS_COLOUR, 0, fossils)
    svg += _create_arc(RENEWABLES_COLOUR, fossils, renewables)
    svg += _create_arc(OTHERS_COLOUR, fossils + renewables, others)

    svg += '</svg>'
    return svg


def _create_arc(colour: str, angle_offset: float, angle: float) -> str:
    if angle == 0:
        return ''

    return (
        f'<path fill="{colour}" d="M'
        + _get_arc_point(angle_offset)
        + f'A{RADIUS},{RADIUS} 0 '
        + ('1' if angle >= 0.5 else '0')
        + ' 1 '
        + _get_arc_point(angle_offset + angle)
        + 'L0,0z"/>'
    )


def _get_arc_point(angle: float) -> str:
    x = RADIUS * math.sin(angle * 2 * math.pi)
    y = RADIUS * -math.cos(angle * 2 * math.pi)
    return f'{x:.1f},{y:.1f}'
