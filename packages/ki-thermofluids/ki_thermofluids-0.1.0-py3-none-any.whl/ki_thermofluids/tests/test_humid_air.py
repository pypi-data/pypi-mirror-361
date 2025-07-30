from math import isclose

import pytest

from ki_thermofluids.humid_air import HumidAirState


@pytest.fixture()
def HAState():
    return HumidAirState(temperature_dry_bulb__K=300, pressure__Pa=101325, relative_humidity=0.5)


def test_init(HAState: HumidAirState):
    assert isclose(HAState.density__kg_m3, 1.169, abs_tol=1e-3)
    assert isclose(HAState.temperature_dew_point__K, 288.714, rel_tol=1e-4)


def test_dry_hx(HAState: HumidAirState):
    T_dew__K = HAState.temperature_dew_point__K
    HAState.heat_transfer("Tdb", T_dew__K)
    assert isclose(HAState.temperature_dew_point__K, T_dew__K, rel_tol=1e-4)
    assert isclose(HAState.relative_humidity, 1.0, rel_tol=1e-4)
    HAState.heat_transfer("Hha", HAState.specific_enthalpy__J_kg + HAState.cp__J_kgK)
    assert isclose(HAState.temperature_dew_point__K, T_dew__K, rel_tol=1e-4)
    assert isclose(HAState.dT_sat_margin__K, 1.0, abs_tol=1e-3)


def test_humidify(HAState: HumidAirState):
    HAState2 = HAState.deepcopy()
    hum_rat_start = HAState.humidity_ratio
    HAState.humidify("RH", 0.8, withSteam=True)
    assert isclose(HAState.humidity_ratio / hum_rat_start, 1.6, abs_tol=0.02)
    HAState.humidify("RH", 1.0, withSteam=True)
    assert isclose(HAState.relative_humidity, 1.0, rel_tol=1e-5)
    assert isclose(HAState.temperature_dry_bulb__K, 300, rel_tol=1e-5)
    HAState2.humidify("RH", 0.8, withSteam=False)
    assert HAState2.temperature_dry_bulb__K < 300


if __name__ == "__main__":
    pytest.main([__file__])
