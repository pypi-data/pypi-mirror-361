from math import isclose

import pytest
from ki_util.units import BaseQuantity as BQ

from ki_thermofluids.mixture import Mixture
from ki_thermofluids.thermo import TN, TS, ThermoNode, ThermoState


@pytest.fixture()
def WaterState():
    return ThermoState(media="water", temperature__K=300, pressure__Pa=101325)


@pytest.fixture()
def SteamNode():
    return ThermoNode(media="water", temperature__K=500, pressure__Pa=101325, volume__m3=1.0)


def test_TS_init(WaterState: ThermoState):
    assert isclose(WaterState.density__kg_m3, 996.56, rel_tol=1e-5)
    assert isclose(WaterState.molar_mass__kg_mol, 0.01801528, rel_tol=1e-5)
    assert isclose(WaterState.hvap__J_kg, 2256472, rel_tol=1e-5)


def test_TN_init(SteamNode: ThermoNode):
    assert isclose(SteamNode.mass__kg, 0.4409, rel_tol=1e-4)


def test_TS_fluids():
    for fluid in ["water", "ammonia", "R134a", "air"]:
        state = ThermoState(media=fluid, temperature__K=300, pressure__Pa=101325)
        try:
            temp = state.temperature__K
            pres = state.pressure__Pa
            mm = state.molar_mass__kg_mol
            spvol = state.specific_volume__m3_kg
            hvap = state.hvap__J_kg
        except:
            raise AttributeError(f"Could not compute property for {fluid}.")
        assert isclose(temp, 300, rel_tol=1e-6)
        assert isclose(pres, 101325, rel_tol=1e-6)


def test_TS_mixture():
    test_mix = Mixture(methane=0.92, ethane=0.08)
    mix_state = ThermoState(media=test_mix, temperature__K=300, pressure__Pa=101325)
    assert isclose(mix_state.density__kg_m3, 0.67822, rel_tol=1e-4)  # Approximate density for the mixture
    assert isclose(mix_state.molar_mass__kg_mol, 0.0166647, rel_tol=1e-5)  # Approximate molar mass for the mixture
    assert isclose(mix_state.hvap__J_kg, 583549.79, rel_tol=1e-5)  # Approximate hvap for the mixture
    assert mix_state.media.species_list == ["methane", "ethane"]
    assert isclose(mix_state.media.mass_fraction_list[0], 0.92)
    assert isclose(mix_state.media.mass_fraction_list[1], 0.08)


def test_TS_helpers():
    TState1 = ThermoState(media="water", temperature__K=500, pressure__Pa=101325)
    T_lift__K = 20
    eta_poly = 0.8
    pr_calc = TState1.calc_pr_for_polytropic_T_lift(T_lift__K, eta_poly)
    dh1, PolyOutletState = TState1.get_polytropic_compression_outlet(pr_calc, eta_poly, N=100)
    dh2, PolyInletState = PolyOutletState.get_polytropic_compression_inlet(pr_calc, eta_poly, N=100)
    assert isclose(PolyOutletState.temperature__K, 520, rel_tol=1e-5)
    assert isclose(PolyInletState.temperature__K, TState1.temperature__K, rel_tol=1e-4)
    assert isclose(PolyInletState.pressure__Pa, TState1.pressure__Pa, rel_tol=1e-4)
    assert isclose(dh1, dh2, rel_tol=1e-3)

    pr = 1.1
    _, IsenOutletState = TState1.get_polytropic_compression_outlet(pr, 1.0, N=100)
    TState1.isentropic_property_update("P", TState1.pressure__Pa * pr)
    assert isclose(TState1.temperature__K, IsenOutletState.temperature__K, rel_tol=1e-5)
    assert isclose(TState1.specific_enthalpy__J_kg, IsenOutletState.specific_enthalpy__J_kg, rel_tol=1e-5)


def test_unitful_wrapper():
    TState = TS(media="helium", temperature=BQ(100, "degF"), pressure=BQ(15, "psi"))
    TNode = TN(media="helium", temperature=BQ(100, "degF"), pressure=BQ(15, "psi"), volume=BQ(1.0, "ft**3"))
    assert isclose(TState.temperature__K, 310.92778, rel_tol=1e-5)
    assert isclose(TNode.temperature__K, 310.92778, rel_tol=1e-5)

    # check input pairs
    P = BQ(101325, "Pa")
    Q = BQ(0.5, "")
    pq = TS("water", pressure=P, quality=Q)
    T, D, H, S, U = pq.temperature, pq.density, pq.specific_enthalpy, pq.specific_entropy, pq.specific_internal_energy
    tq = TS("water", temperature=T, quality=Q)
    dq = TS("water", density=D, quality=Q)
    ph = TS("water", pressure=P, specific_enthalpy=H)
    ps = TS("water", pressure=P, specific_entropy=S)
    pu = TS("water", density=D, specific_internal_energy=U)
    ts = TS("water", temperature=T, specific_entropy=S)
    td = TS("water", temperature=T, density=D)
    du = TS("water", density=D, specific_internal_energy=U)
    dh = TS("water", density=D, specific_enthalpy=H)
    ds = TS("water", density=D, specific_entropy=S)


def test_polytropic_compression():
    eta_p = 0.857
    P_inlet__Pa = 88000
    H_inlet__J_kg = 2650000
    pressure_ratio = 1.5

    inletState = ThermoState(media="water", pressure__Pa=P_inlet__Pa, specific_enthalpy__J_kg=H_inlet__J_kg)

    dhp__J_kg, outletState1 = inletState.get_polytropic_compression_outlet(pressure_ratio, eta_p, N=100)
    assert isclose(outletState1.pressure__Pa, inletState.pressure__Pa * pressure_ratio, rel_tol=1e-6)
    dh__J_kg = outletState1.specific_enthalpy__J_kg - inletState.specific_enthalpy__J_kg
    assert isclose(dh__J_kg * eta_p, dhp__J_kg, rel_tol=1e-5)

    dhp2__J_kg, outletState2 = inletState.get_polytropic_compression_outlet(pressure_ratio, eta_p, N=0)
    assert isclose(outletState1.pressure__Pa, outletState2.pressure__Pa, rel_tol=1e-5)
    assert isclose(dhp__J_kg, dhp2__J_kg, rel_tol=5e-3)

    dhp3__J_kg, outletState3 = inletState.get_polytropic_compression_outlet(pressure_ratio, eta_p, N=1)
    assert isclose(outletState1.pressure__Pa, outletState3.pressure__Pa, rel_tol=1e-5)
    # assert isclose(dhp__J_kg, dhp3__J_kg, rel_tol=5e-3) # this check would fail due to the N=1 assumption of constant gamma

    outletState4 = inletState.get_polytropic_compression_outlet_dhp(dhp__J_kg=dhp__J_kg, eta_poly=eta_p, N=100)
    assert isclose(outletState1.pressure__Pa, outletState4.pressure__Pa, rel_tol=1e-5)
    dh4__J_kg = outletState4.specific_enthalpy__J_kg - inletState.specific_enthalpy__J_kg
    assert isclose(dh4__J_kg * eta_p, dhp__J_kg, rel_tol=1e-5)


# %%
if __name__ == "__main__":
    pytest.main([__file__])
