from math import isclose

import pytest
from ki_util.units import BaseQuantity as BQ
from ki_util.units import convert_units as convert
from numpy import pi, radians, tan

from ki_thermofluids.flow import (
    Bend,
    ExpanderReducer,
    FlowState,
    MinorLoss,
    Orifice,
    SubCooledFlow,
    SuperHeatedFlow,
    critical_pressure_ratio,
    get_SuperHeatedFS_w_Mach_total_prop,
)


@pytest.fixture()
def SuperSteamFlow():
    return SuperHeatedFlow(media="water", dT_super__K=5.0, pressure__Pa=101325, mdot__kg_s=0.5)


@pytest.fixture()
def SteamFlow():
    return FlowState(media="water", pressure__Pa=101325, quality=1.0 - 1e-6, mdot__kg_s=0.5)


@pytest.fixture()
def WaterFlow():
    return FlowState(media="water", pressure__Pa=101325, quality=1e-6, mdot__kg_s=0.5)


@pytest.fixture()
def SubWaterFlow():
    return SubCooledFlow(media="water", dT_sub__K=1.0, pressure__Pa=101325, mdot__kg_s=5.0)


@pytest.fixture()
def ArbitraryState():
    return FlowState(media="water", pressure__Pa=1e6, temperature__K=500, mdot__kg_s=100, diameter__m=1.0)


@pytest.fixture()
def TestBend():
    return Bend(
        angle__deg=90,
        bend_radius__m=2,
        diameter__m=1,
        abs_rough__m=1e-5,
    )


def test_common_FS(SteamFlow: FlowState, WaterFlow: FlowState):
    assert isclose(SteamFlow.pressure__Pa, 101325, rel_tol=1e-6)
    assert isclose(SteamFlow.temperature__K, convert(100, "degC", "K")) < 1e-4
    Hvap__J_s = SteamFlow.enthalpy_flowrate__J_s - WaterFlow.enthalpy_flowrate__J_s
    hvap__J_kg = 2256470.0
    assert isclose(Hvap__J_s, hvap__J_kg * SteamFlow.mdot__kg_s, rel_tol=1e-5)
    assert SteamFlow.Reynolds is None
    SteamFlow.diameter__m = 0.1
    assert isclose(SteamFlow.Reynolds, 522681.5, rel_tol=1e-5)


def test_FS_init():
    x = FlowState("water", pressure__Pa=101325, temperature__K=500, vdot__m3_s=1, diameter__m=0.1)
    assert isclose(x.area__m2, pi * 0.25 * 0.1 * 0.1, rel_tol=1e-6)
    assert isclose(x.specific_entropy__J_kgK, x.static_specific_entropy__J_kgK, rel_tol=1e-6)
    assert x.pressure__Pa > x.static_pressure__Pa
    assert x.temperature__K > x.static_temperature__K
    assert x.specific_enthalpy__J_kg > x.static_specific_enthalpy__J_kg
    y = FlowState("water", pressure__Pa=101325, temperature__K=500, velocity__m_s=100)
    assert isclose(y.specific_entropy__J_kgK, y.static_specific_entropy__J_kgK, rel_tol=1e-6)
    assert isclose(y.specific_enthalpy__J_kg - y.static_specific_enthalpy__J_kg, 0.5 * 100 * 100, rel_tol=1e-6)

    z = FlowState("water", pressure__Pa=101325, temperature__K=500, mdot__kg_s=0.0)
    w = z.deepcopy()


def test_SuperHeatedFS_w_Mach():
    for media in ["water"]:
        dT_sat = BQ(5.0, "K")
        T = BQ(75, "degC")
        M = 0.2
        state_dT_T = get_SuperHeatedFS_w_Mach_total_prop(
            media=media,
            offset=dT_sat,
            temperature=T,
            Mach=M,
        )
        assert isclose(state_dT_T.dT_sat__K, dT_sat.magnitude, rel_tol=1e-4)
        assert isclose(state_dT_T.temperature__K, T.magnitude, rel_tol=1e-4)
        assert isclose(state_dT_T.Mach, M, rel_tol=1e-4)
        assert state_dT_T.temperature__K > state_dT_T.static_temperature__K
        state_dT_p = get_SuperHeatedFS_w_Mach_total_prop(
            media=media,
            offset=dT_sat,
            pressure=state_dT_T.pressure,
            Mach=M,
        )
        assert isclose(state_dT_p.dT_sat__K, dT_sat.magnitude, rel_tol=1e-4)
        assert isclose(state_dT_p.temperature__K, T.magnitude, rel_tol=1e-4)
        assert isclose(state_dT_p.Mach, M, rel_tol=5e-3)
        assert isclose(state_dT_p.dT_static__K, state_dT_T.dT_static__K, rel_tol=5e-3)
        state_dp_p = get_SuperHeatedFS_w_Mach_total_prop(
            media=media,
            offset=-1 * state_dT_T.dp_sat,
            pressure=state_dT_T.pressure,
            Mach=M,
        )
        assert isclose(state_dp_p.dT_sat__K, dT_sat.magnitude, rel_tol=1e-4)
        assert isclose(state_dp_p.temperature__K, T.magnitude, rel_tol=1e-4)
        assert isclose(state_dp_p.Mach, M, rel_tol=1e-4)
        assert isclose(state_dp_p.dT_static__K, state_dT_T.dT_static__K, rel_tol=1e-4)
        state_dp_T = get_SuperHeatedFS_w_Mach_total_prop(
            media=media,
            offset=-1 * state_dT_T.dp_sat,
            temperature=T,
            Mach=M,
        )
        assert isclose(state_dp_T.dT_sat__K, dT_sat.magnitude, rel_tol=5e-3)
        assert isclose(state_dp_T.temperature__K, T.magnitude, rel_tol=1e-4)
        assert isclose(state_dp_T.Mach, M, rel_tol=5e-3)
        assert isclose(state_dp_T.dT_static__K, state_dT_T.dT_static__K, rel_tol=5e-3)


def test_Bend(TestBend: Bend, ArbitraryState: FlowState):
    # k = 0.19 per https://www.caee.utexas.edu/prof/kinnas/319LAB/notes13/Table10.5.PDF
    assert isclose(TestBend.k_factor + TestBend.k_fric(ArbitraryState.Reynolds), 0.1757, rel_tol=1e-3)
    assert isclose(TestBend.calc_dp(ArbitraryState), 314.72, rel_tol=1e-4)


def test_Expansion(ArbitraryState: FlowState):
    # [0.3, 0.25, 0.15, 0.1] per https://www.caee.utexas.edu/prof/kinnas/319LAB/notes13/Table10.5.PDF
    theta__deg = 20.0
    for R, k in zip([0.2, 0.4, 0.6, 0.8], [0.419, 0.321, 0.186, 0.059]):
        D1 = 1.0
        D2 = D1 / R
        L = 0.5 * (D2 - D1) / tan(radians(theta__deg) / 2)
        _expander = ExpanderReducer(
            D1__m=D1,
            D2__m=D2,
            L__m=L,
            abs_rough__m=1e-5,
        )
        ArbitraryState.diameter__m = D1
        assert isclose(convert(_expander.alpha__rad, "rad", "deg"), 20.0, rel_tol=1e-5)
        assert isclose(_expander.k_factor(ArbitraryState.Reynolds), k, rel_tol=5e-3)


def test_Reducer(ArbitraryState: FlowState):
    # [0.08, 0.07, 0.06] per https://www.caee.utexas.edu/prof/kinnas/319LAB/notes13/Table10.5.PDF
    theta__deg = 60.0
    for R, k in zip([0.2, 0.4, 0.6], [0.120, 0.113, 0.098]):
        D1 = 1.0
        D2 = D1 * R
        L = 0.5 * (D1 - D2) / tan(radians(theta__deg) / 2)
        _expander = ExpanderReducer(
            D1__m=D1,
            D2__m=D2,
            L__m=L,
            abs_rough__m=1e-5,
        )
        ArbitraryState.diameter__m = D1
        assert isclose(convert(_expander.alpha__rad, "rad", "deg"), 60.0, rel_tol=1e-5)
        assert isclose(_expander.k_factor(ArbitraryState.Reynolds), k, rel_tol=5e-3)


def test_Orifice():
    # check that mdot calculation works as expected for steam
    up_pres = 3e5
    down_pres = 2e5
    up_state = SuperHeatedFlow(media="water", pressure__Pa=up_pres, dT_super__K=42.0)
    pr_crit = critical_pressure_ratio(up_state.gamma)
    assert isclose(pr_crit, 0.538991516, rel_tol=1e-5)
    assert isclose(Orifice()._choked_flux(up_state), 445.7790066, rel_tol=1e-5)
    cda = 0.01
    test_orifice = Orifice(CdA__m2=cda)
    choke_mdot = test_orifice.calc_mdot(UpstreamState=up_state, p2__Pa=up_pres * pr_crit)
    mdot = test_orifice.calc_mdot(UpstreamState=up_state, p2__Pa=down_pres)
    assert isclose(choke_mdot, cda * 445.7790066, rel_tol=1e-5)
    assert isclose(mdot, 4.29815, rel_tol=1e-5)  # validated with external tool

    air_state = FlowState(media="air", pressure__Pa=2e6, temperature__K=300.0)
    air_mdot = test_orifice.calc_mdot(UpstreamState=air_state, p2__Pa=2e5)
    assert isclose(air_mdot, 47.0317, rel_tol=1e-5)  # validated with external tool

    test_state = FlowState("water", pressure__Pa=down_pres, specific_enthalpy__J_kg=up_state.specific_enthalpy__J_kg)
    us_pressure__Pa = test_orifice.calc_upstream_pressure(DownstreamState=test_state, mdot__kg_s=mdot)
    assert isclose(us_pressure__Pa, up_pres, rel_tol=1e-5)

    ds_pressure__Pa = test_orifice.calc_downstream_pressure(UpstreamState=up_state, mdot__kg_s=mdot)
    assert isclose(ds_pressure__Pa, down_pres, rel_tol=2e-5)


def test_incompressible_MinorLoss(SubWaterFlow: FlowState):
    # basic check that minor loss functions produce directionally correct, consistent results
    D = 0.1
    L = 10
    rough = convert(0.1, "mm", "m")
    some_tube = MinorLoss(diameter__m=D, length__m=L, abs_roughness__m=rough)

    ds_incompressible = some_tube.get_downstream_state(SubWaterFlow, SubWaterFlow.mdot__kg_s)
    assert SubWaterFlow.pressure__Pa > ds_incompressible.pressure__Pa
    assert isclose(SubWaterFlow.pressure__Pa - ds_incompressible.pressure__Pa, 384.07, rel_tol=1e-4)

    us_incompressible = some_tube.get_upstream_state(
        DownstreamState=ds_incompressible,
        mdot__kg_s=SubWaterFlow.mdot__kg_s,
        T1__K=SubWaterFlow.temperature__K,
    )

    assert isclose(us_incompressible.pressure__Pa, SubWaterFlow.pressure__Pa, rel_tol=1e-5)


def test_Compressible_MinorLoss(SuperSteamFlow: FlowState):
    # basic check that minor loss functions produce directionally correct, consistent results
    D = 0.1
    L = 10
    rough = convert(0.1, "mm", "m")
    some_tube = MinorLoss(diameter__m=D, length__m=L, abs_roughness__m=rough)

    ds_compressible = some_tube.get_downstream_state(SuperSteamFlow, SuperSteamFlow.mdot__kg_s)
    assert SuperSteamFlow.pressure__Pa > ds_compressible.pressure__Pa
    assert isclose(ds_compressible.pressure__Pa, 93692.44, rel_tol=1e-4)

    us_compressible = some_tube.get_upstream_state(
        DownstreamState=ds_compressible,
        mdot__kg_s=SuperSteamFlow.mdot__kg_s,
        T1__K=SuperSteamFlow.temperature__K,
    )
    assert isclose(us_compressible.pressure__Pa, SuperSteamFlow.pressure__Pa, rel_tol=5e-4)


if __name__ == "__main__":
    pytest.main([__file__])
