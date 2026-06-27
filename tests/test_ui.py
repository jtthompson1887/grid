"""Tests for grid.ui.favicon and grid.ui.value"""
import math
import pytest
from grid.state.types import Types
from grid.ui.favicon import create, _create_arc, _get_arc_point, RADIUS
from grid.ui import value


# ---------------------------------------------------------------------------
# favicon
# ---------------------------------------------------------------------------

def _types(**kwargs):
    defaults = {'coal': 0.0, 'ccgt': 0.0, 'ocgt': 0.0,
                'embedded_solar': 0.0, 'embedded_wind': 0.0,
                'wind': 0.0, 'hydro': 0.0, 'nuclear': 0.0, 'biomass': 0.0}
    defaults.update(kwargs)
    return Types(defaults)


class TestFavicon:
    def test_returns_svg_string(self):
        t = _types(coal=1.0, wind=1.0, nuclear=1.0)
        result = create(t)
        assert isinstance(result, str)
        assert '<svg' in result
        assert '</svg>' in result

    def test_all_fossils(self):
        t = _types(coal=10.0)
        result = create(t)
        assert '#c45' in result  # fossils colour

    def test_all_renewables(self):
        t = _types(wind=10.0)
        result = create(t)
        assert '#5b5' in result  # renewables colour

    def test_all_others(self):
        t = _types(nuclear=10.0)
        result = create(t)
        assert '#27c' in result  # others colour

    def test_zero_total_no_crash(self):
        t = _types()
        result = create(t)
        assert isinstance(result, str)

    def test_arc_greater_than_half_uses_large_arc(self):
        path = _create_arc('#c45', 0, 0.7)
        assert ' 1 1 ' in path  # large-arc-flag=1

    def test_arc_less_than_half_uses_small_arc(self):
        path = _create_arc('#c45', 0, 0.3)
        assert ' 0 1 ' in path  # large-arc-flag=0

    def test_zero_angle_returns_empty(self):
        assert _create_arc('#c45', 0, 0) == ''

    def test_arc_point_at_zero(self):
        pt = _get_arc_point(0)
        x, y = map(float, pt.split(','))
        assert abs(x) < 0.01  # sin(0) = 0
        assert abs(y + RADIUS) < 0.01  # -cos(0)*R = -R

    def test_arc_point_at_quarter(self):
        pt = _get_arc_point(0.25)
        x, y = map(float, pt.split(','))
        assert abs(x - RADIUS) < 0.1  # sin(pi/2)*R ≈ R
        assert abs(y) < 0.1           # -cos(pi/2)*R ≈ 0

    def test_svg_well_formed(self):
        t = _types(coal=1.0, wind=2.0, nuclear=1.0)
        svg = create(t)
        assert svg.startswith('<?xml')
        assert svg.count('<svg') == 1
        assert svg.count('</svg>') == 1


# ---------------------------------------------------------------------------
# value formatters
# ---------------------------------------------------------------------------

class TestFormatPower:
    def test_positive(self):
        assert value.format_power(3.456) == '3.46'

    def test_zero(self):
        assert value.format_power(0) == '0.00'

    def test_negative(self):
        assert value.format_power(-1.5) == '−1.50'


class TestFormatTotalPower:
    def test_positive(self):
        assert value.format_total_power(12.3456) == '12.3'

    def test_negative(self):
        assert value.format_total_power(-5.5) == '−5.5'


class TestFormatPercentage:
    def test_half(self):
        assert value.format_percentage(0.5) == '50.0'

    def test_zero(self):
        assert value.format_percentage(0) == '0.0'

    def test_one(self):
        assert value.format_percentage(1.0) == '100.0'

    def test_negative(self):
        assert value.format_percentage(-0.1) == '−10.0'


class TestFormatPrice:
    def test_positive(self):
        assert value.format_price(45.6) == '£45.60'

    def test_negative(self):
        assert value.format_price(-10.5) == '−£10.50'

    def test_zero(self):
        assert value.format_price(0) == '£0.00'
