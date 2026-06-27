"""Tests for grid.state.*"""
import pytest
from grid.state.map import Map
from grid.state.price import Price
from grid.state.emissions import Emissions
from grid.state.generation import Generation
from grid.state.types import Types
from grid.state.interconnectors import Interconnectors
from grid.state.storage import Storage
from grid.state.transfers import Transfers
from grid.state.demand import Demand
from grid.state.visits import Visits
from grid.state.datum import Datum, PRICE, EMISSIONS, GENERATION, TYPES, INTERCONNECTORS, STORAGE, TRANSFERS, DEMAND, VISITS
from grid.state.record import Record
from grid.state.state import State


# ---------------------------------------------------------------------------
# Map base class
# ---------------------------------------------------------------------------

class ConcreteMap(Map):
    KEY_COMPONENTS = {'a': ['x', 'y'], 'b': ['z']}


class TestMap:
    def test_values_summed(self):
        m = ConcreteMap({'x': 1.0, 'y': 2.0, 'z': 3.0})
        assert m.get('a') == 3.0
        assert m.get('b') == 3.0

    def test_missing_key_returns_zero(self):
        m = ConcreteMap({'x': 1.0})
        assert m.get('missing') == 0.0

    def test_none_values_treated_as_zero(self):
        m = ConcreteMap({'x': None, 'y': 2.0, 'z': None})
        assert m.get('a') == 2.0
        assert m.get('b') == 0.0

    def test_get_minimum(self):
        m = ConcreteMap({'x': 1.0, 'y': 2.0, 'z': 5.0})
        assert m.get_minimum() == 3.0

    def test_get_maximum(self):
        m = ConcreteMap({'x': 1.0, 'y': 2.0, 'z': 5.0})
        assert m.get_maximum() == 5.0

    def test_get_total(self):
        m = ConcreteMap({'x': 1.0, 'y': 2.0, 'z': 3.0})
        assert m.get_total() == 6.0

    def test_to_dict(self):
        m = ConcreteMap({'x': 1.0, 'y': 2.0, 'z': 3.0})
        d = m.to_dict()
        assert d == {'a': 3.0, 'b': 3.0}

    def test_empty_map_minimum_zero(self):
        m = Map({})
        assert m.get_minimum() == 0.0

    def test_empty_map_maximum_zero(self):
        m = Map({})
        assert m.get_maximum() == 0.0


# ---------------------------------------------------------------------------
# Concrete Map subclasses
# ---------------------------------------------------------------------------

def _full_data():
    return {
        'coal': 1.0, 'ccgt': 2.0, 'ocgt': 0.5,
        'nuclear': 3.0, 'oil': 0.1,
        'wind': 4.0, 'hydro': 0.3,
        'pumped': 0.2, 'biomass': 1.5,
        'battery': 0.4, 'other': 0.0,
        'ifa': 0.5, 'moyle': 0.1, 'britned': 0.3,
        'ewic': 0.2, 'nemo': 0.4, 'ifa2': 0.6,
        'nsl': 0.7, 'eleclink': 0.8, 'viking': 0.9,
        'greenlink': 0.1,
        'embedded_wind': 2.0, 'embedded_solar': 1.0,
        'price': 50.0, 'emissions': 150,
        'visits': 100,
    }


class TestPrice:
    def test_price(self):
        p = Price({'price': 45.5})
        assert p.get('price') == 45.5

    def test_to_dict(self):
        p = Price({'price': 45.5})
        assert p.to_dict() == {'price': 45.5}


class TestEmissionsState:
    def test_emissions(self):
        e = Emissions({'emissions': 200})
        assert e.get('emissions') == 200

    def test_to_dict(self):
        e = Emissions({'emissions': 200})
        assert e.to_dict() == {'emissions': 200}


class TestGeneration:
    def test_coal_and_gas(self):
        g = Generation({'coal': 1.0, 'ccgt': 2.0, 'ocgt': 0.5,
                        'embedded_solar': 1.0, 'embedded_wind': 2.0,
                        'wind': 1.0, 'hydro': 0.5, 'nuclear': 3.0,
                        'biomass': 1.0})
        assert g.get('coal') == 1.0
        assert g.get('gas') == 2.5
        assert g.get('solar') == 1.0
        assert g.get('wind') == 3.0

    def test_keys_defined(self):
        assert 'coal' in Generation.KEYS
        assert 'nuclear' in Generation.KEYS


class TestTypes:
    def test_fossils(self):
        t = Types({'coal': 1.0, 'ccgt': 2.0, 'ocgt': 0.5,
                   'embedded_solar': 1.0, 'embedded_wind': 2.0,
                   'wind': 1.0, 'hydro': 0.5,
                   'nuclear': 3.0, 'biomass': 1.0})
        assert t.get(Types.FOSSILS) == pytest.approx(3.5)
        assert t.get(Types.RENEWABLES) == pytest.approx(4.5)
        assert t.get(Types.OTHERS) == pytest.approx(4.0)


class TestInterconnectors:
    def test_france(self):
        ic = Interconnectors({'ifa': 0.5, 'ifa2': 0.6, 'eleclink': 0.8})
        assert ic.get('france') == pytest.approx(1.9)

    def test_ireland(self):
        ic = Interconnectors({'moyle': 0.1, 'ewic': 0.2, 'greenlink': 0.1})
        assert ic.get('ireland') == pytest.approx(0.4)


class TestStorage:
    def test_pumped(self):
        s = Storage({'pumped': 0.2})
        assert s.get('pumped') == 0.2


class TestTransfers:
    def test_includes_pumped(self):
        t = Transfers({'pumped': 0.2, 'nemo': 0.4})
        assert t.get('pumped') == 0.2
        assert t.get('belgium') == 0.4


class TestDemandState:
    def _make_demand(self, data=None):
        d = data or _full_data()
        types = Types(d)
        transfers = Transfers(d)
        return Demand(types, transfers)

    def test_demand_total_positive(self):
        d = self._make_demand()
        assert d.get('demand') > 0

    def test_fossils_key(self):
        d = self._make_demand()
        assert d.get('fossils') >= 0

    def test_get_generation(self):
        d = self._make_demand()
        assert d.get_generation() > 0

    def test_to_dict_has_all_keys(self):
        d = self._make_demand()
        result = d.to_dict()
        assert set(result.keys()) == {'demand', 'fossils', 'renewables', 'others', 'transfers'}


class TestVisits:
    def test_visits(self):
        v = Visits({'visits': 42})
        assert v.get('visits') == 42


# ---------------------------------------------------------------------------
# Datum
# ---------------------------------------------------------------------------

class TestDatum:
    def _make(self, overrides=None):
        data = _full_data()
        if overrides:
            data.update(overrides)
        return Datum(data)

    def test_price_accessible(self):
        d = self._make()
        assert d.price.get('price') == 50.0

    def test_emissions_accessible(self):
        d = self._make()
        assert d.emissions.get('emissions') == 150

    def test_get_price(self):
        d = self._make()
        assert d.get(PRICE) is d.price

    def test_get_emissions(self):
        d = self._make()
        assert d.get(EMISSIONS) is d.emissions

    def test_get_generation(self):
        d = self._make()
        assert d.get(GENERATION) is d.generation

    def test_get_types(self):
        d = self._make()
        assert d.get(TYPES) is d.types

    def test_get_interconnectors(self):
        d = self._make()
        assert d.get(INTERCONNECTORS) is d.interconnectors

    def test_get_storage(self):
        d = self._make()
        assert d.get(STORAGE) is d.storage

    def test_get_transfers(self):
        d = self._make()
        assert d.get(TRANSFERS) is d.transfers

    def test_get_demand(self):
        d = self._make()
        assert d.get(DEMAND) is d.demand

    def test_get_visits(self):
        d = self._make()
        assert d.get(VISITS) is d.visits

    def test_invalid_map_type_raises(self):
        d = self._make()
        with pytest.raises(ValueError, match='Invalid map type'):
            d.get(999)

    def test_get_total(self):
        d = self._make()
        assert d.get_total() > 0

    def test_to_dict_keys(self):
        d = self._make()
        result = d.to_dict()
        expected_keys = {
            'price', 'emissions', 'generation', 'types',
            'interconnectors', 'storage', 'transfers', 'demand', 'visits', 'total'
        }
        assert set(result.keys()) == expected_keys

    def test_to_dict_total_matches(self):
        d = self._make()
        result = d.to_dict()
        assert result['total'] == d.get_total()


# ---------------------------------------------------------------------------
# Record
# ---------------------------------------------------------------------------

class TestRecord:
    def test_fields(self):
        r = Record(time=1717228800, power=12.5)
        assert r.time == 1717228800
        assert r.power == 12.5


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class TestState:
    def _make_state(self):
        datum = Datum(_full_data())
        record = Record(time=1717228800, power=20.0)
        series = {1717228800: datum, 1717232400: datum}
        return State(
            time=1717228800,
            latest=datum,
            past_day=datum,
            past_week=datum,
            past_year=datum,
            all_time=datum,
            past_day_series=series,
            past_week_series=series,
            past_year_series=series,
            all_time_series=series,
            wind_record=record,
            wind_milestones={20: 1717228800, 15: 1717225200},
            yearly_visits=9999,
        )

    def test_to_dict_top_level_keys(self):
        s = self._make_state()
        d = s.to_dict()
        expected = {
            'time', 'latest', 'past_day', 'past_week', 'past_year', 'all_time',
            'past_day_series', 'past_week_series', 'past_year_series', 'all_time_series',
            'wind_record', 'wind_milestones', 'yearly_visits',
        }
        assert set(d.keys()) == expected

    def test_series_is_list(self):
        s = self._make_state()
        d = s.to_dict()
        assert isinstance(d['past_day_series'], list)
        for entry in d['past_day_series']:
            assert 'time' in entry
            assert 'datum' in entry

    def test_wind_record_dict(self):
        s = self._make_state()
        d = s.to_dict()
        assert d['wind_record'] == {'time': 1717228800, 'power': 20.0}

    def test_milestones_list(self):
        s = self._make_state()
        d = s.to_dict()
        assert isinstance(d['wind_milestones'], list)
        for entry in d['wind_milestones']:
            assert 'power' in entry
            assert 'time' in entry

    def test_yearly_visits(self):
        s = self._make_state()
        d = s.to_dict()
        assert d['yearly_visits'] == 9999

    def test_time_value(self):
        s = self._make_state()
        d = s.to_dict()
        assert d['time'] == 1717228800
