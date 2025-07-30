import warnings
from math import isclose, log
from typing import List, Self

from CoolProp import CoolProp as CP
from ki_util.geometry import Circle
from ki_util.helpers import rel_error, transpose_dict
from ki_util.units import BaseQuantity

from ki_thermofluids.mixture import Mixture

INVALID_PAIRS = ["SU", "SQ", "HQ", "HT", "UT"]

BASE_INT_PROPS = {  # intensive properties
    "pressure__Pa": "P",
    "temperature__K": "T",
    "density__kg_m3": "D",
    "specific_enthalpy__J_kg": "H",
    "specific_internal_energy__J_kg": "U",
    "specific_entropy__J_kgK": "S",
}

STATIC_PROPS = {f"static_{k}": v for k, v in BASE_INT_PROPS.items()}
INTENSIVE_PROPS = {**BASE_INT_PROPS, **STATIC_PROPS}

EXTENSIVE_PROPS = {"mass__kg": "M", "volume__m3": "VOL"}

BASE_BQ_INT_PROPS = {
    "pressure": "P",
    "temperature": "T",
    "density": "D",
    "specific_enthalpy": "H",
    "specific_internal_energy": "U",
    "specific_entropy": "S",
}

STATIC_BQ_PROPS = {f"static_{k}": v for k, v in BASE_BQ_INT_PROPS.items()}
INT_BQ_PROPS = {**BASE_BQ_INT_PROPS, **STATIC_BQ_PROPS}

EXT_BQ_PROPS = {"mass": "M", "volume": "VOL"}

QUALITY_PROP = {"quality": "Q"}

VALID_INPUTS = {**INTENSIVE_PROPS, **QUALITY_PROP}
VALID_BQ_INPUTS = {**INT_BQ_PROPS, **QUALITY_PROP}


class ThermoState:
    def __init__(self, media: str | Mixture, Allow2Phase: bool = False, **intensive_props: float) -> None:
        """Coolprop wrapper representing Thermodynamic state of a fluid or mixture. Intensive properties are stored as attributes.
        Static and Stagnation properties are equivalent since ThermoState does not have a concept of velocity.

        Args:
            media (str | Mixture): fluid string or Mixture object.
            Allow2Phase (bool, optional): set to True to allow speed of sound computation for a 2 phase fluid. Defaults to False.
            **intensive_props (float): intensive properties to define the state. Must specify exactly 2 properties.
        """
        if len(intensive_props.keys()) != 2:
            raise KeyError("Thermodynamic state is poorly defined. Must specify exactly 2 intensive properties.")
        self.properties = intensive_props
        self.media = media

        self.Allow2Phase = Allow2Phase  # by default, do not allow speed of sound calculation in 2-phase region, must be set to True after instantiation
        self.backend = "HEOS" if self.media == "water" else "?"

        for key, val in VALID_INPUTS.items():
            # initialize all intensive properties as attributes
            setattr(self, key, None)

        if isinstance(media, Mixture):
            if len(media.species_list) > 2:
                raise ValueError(
                    f"ThermoState currently only supports up to binary mixtures. Try removing minor species from mixture: {media.components}"
                )
            elif len(media.species_list) == 2:
                warnings.warn("Applying a linear mixing rule for the given binary mixture. Be wary of results.")
                self.State = media.CP_AbstractState()
                CP.set_config_bool(CP.OVERWRITE_BINARY_INTERACTION, True)
                CP.apply_simple_mixing_rule(
                    media.species_list[0].capitalize(), media.species_list[1].capitalize(), "linear"
                )
            else:
                self.State = CP.AbstractState(self.backend, media.species_list[0])
                self.State.specify_phase(CP.iphase_gas)
        else:
            self.State = CP.AbstractState(self.backend, media)
            self.State.set_mole_fractions([1.0])
            self.State.specify_phase(CP.iphase_not_imposed if self.Allow2Phase else CP.iphase_gas)

        in_props = {}
        for key, val in self.properties.items():
            setattr(self, key, val)
            if key in VALID_INPUTS.keys():
                # track which intensive properties were input
                in_props[VALID_INPUTS[key]] = val

        prop1 = list(in_props.items())[0]
        prop2 = list(in_props.items())[1]

        try:
            (
                density__kg_m3,
                specific_internal_energy__J_kg,
                pressure__Pa,
                temperature__K,
            ) = CP.PropsSI(["D", "U", "P", "T"], prop1[0], prop1[1], prop2[0], prop2[1], str(media))
        except ValueError:
            if not self.check_if_valid_pair(prop1[0], prop2[0]):
                raise ValueError(
                    f"Check input property pair: {prop1[0]}+{prop2[0]}. This pair may not yet be supported by CoolProp."
                )
            else:
                raise ValueError(
                    f"No outputs were able to be calculated for {prop1[0]}={prop1[1]:.2f}, {prop2[0]}={prop2[1]:.2f}."
                )

        # use an abstract state to get any other properties that might be of interest
        if not isinstance(media, Mixture):
            self.State.update(CP.DmassUmass_INPUTS, density__kg_m3, specific_internal_energy__J_kg)
        else:  # DU is not available for mixtures, so use PT
            self.State.update(CP.PT_INPUTS, pressure__Pa, temperature__K)
        self.StaticState = self.State
        self.update_properties()
        self.set_static_properties()

    def set_static_properties(self, refState: Self = None):
        """Set the static properties based on the intensive properties."""
        for k in BASE_INT_PROPS.keys():
            setattr(self, f"static_{k}", getattr(refState or self, k))
        for k in BASE_BQ_INT_PROPS.keys():
            setattr(self, f"static_{k}", getattr(refState or self, k))

    def update_static_properties(self, velocity__m_s: float):
        """Update the static properties of the flow state based on a velocity input."""
        StaticState = self.get_StaticState(velocity__m_s)
        self.set_static_properties(StaticState)
        self.StaticState.update(
            CP.DmassSmass_INPUTS,
            StaticState.density__kg_m3,
            StaticState.specific_entropy__J_kgK,
        )

    def get_StaticState(self, velocity__m_s: float = None):
        """Return a static state based on the current ThermoState, assuming current state was initialized with total properties.
        StaticState will contain all static properties."""
        v__m_s = velocity__m_s if velocity__m_s else 0.0
        # Not using deepcopy here because, when called from FlowState or other child classes, the overridden version of deepcopy causes issues with recursion
        StaticState = ThermoState(media=self.media, Allow2Phase=self.Allow2Phase, **self.get_DU())
        if not isclose(v__m_s, 0.0, rel_tol=1e-8):
            if self.isLiquid:
                p__Pa = self.pressure__Pa - 0.5 * self.density__kg_m3 * v__m_s * v__m_s
                StaticState.isochoric_property_update("P", p__Pa)
            else:
                h__J_kg = self.specific_enthalpy__J_kg - 0.5 * v__m_s * v__m_s
                StaticState.isentropic_property_update("H", h__J_kg)
        return StaticState

    def get_static_density__kg_m3(self, velocity__m_s: float = None) -> float:
        """Return the static density based on the current ThermoState, assuming current state was initialized with total properties."""
        v__m_s = velocity__m_s if velocity__m_s else 0.0
        if self.isLiquid:
            return self.density__kg_m3
        else:
            try:
                h__J_kg = self.specific_enthalpy__J_kg - 0.5 * v__m_s * v__m_s
                return CP.PropsSI("D", "H", h__J_kg, "S", self.specific_entropy__J_kgK, str(self.media))
            except Exception as e:
                warnings.warn(
                    f"Exception {e}: Could not calculate static density, returning total density. This is usually due to extreme velocities (for ref. Mach = {v__m_s / self.sound_speed__m_s:.4f})."
                )
                return self.density__kg_m3

    def get_static_velocity__m_s(self, mdot__kg_s: float, diameter__m: float, err_tol: float = 1e-6):
        area = Circle(D=diameter__m).area
        v__m_s = mdot__kg_s / self.density__kg_m3 / area
        rel_err = 1.0
        ix = 0
        while rel_err > err_tol and ix < 50:
            rho_static__kg_m3 = self.get_static_density__kg_m3(velocity__m_s=v__m_s)
            mdot_guess = v__m_s * rho_static__kg_m3 * area
            rel_err = rel_error(mdot__kg_s, mdot_guess)
            v__m_s = mdot__kg_s / rho_static__kg_m3 / area
            ix += 1
        if rel_err > err_tol:
            warnings.warn(
                f"Could not converge to a static velocity within {err_tol} after {ix} iterations. Returning last computed value."
            )
        return v__m_s

    def get_StagnationState(self, velocity__m_s: float = None):
        """Return a stagnation state based on the current ThermoState, assuming current state was initialized with static properties.
        StagnationState will contain all stagnation properties."""
        v__m_s = velocity__m_s if velocity__m_s else 0.0
        # Not using deepcopy here because, when called from FlowState or other child classes, the overridden version of deepcopy causes issues with recursion
        StagnationState = ThermoState(media=self.media, Allow2Phase=self.Allow2Phase, **self.get_DU())
        if self.isLiquid:
            p0__Pa = self.pressure__Pa + 0.5 * v__m_s * v__m_s * self.density__kg_m3
            StagnationState.isochoric_property_update("P", p0__Pa)
        else:
            h0__J_kg = self.specific_enthalpy__J_kg + 0.5 * v__m_s * v__m_s
            StagnationState.isentropic_property_update("H", h0__J_kg)
        return StagnationState

    def check_if_valid_pair(self, prop1: str, prop2: str) -> bool:
        for pair in INVALID_PAIRS:
            if prop1 in pair and prop2 in pair:
                return False
        else:
            return True

    def get_DU(self) -> dict:
        return {
            "density__kg_m3": self.density__kg_m3,
            "specific_internal_energy__J_kg": self.specific_internal_energy__J_kg,
        }

    def update_properties(self):
        """Update all properties of the state. This is useful when the state is modified externally."""
        self._update_intensive_properties()
        self._update_transport_properties()

    def _update_intensive_properties(self):
        self.pressure__Pa = self.State.p()
        self.temperature__K = self.State.T()
        self.density__kg_m3 = self.State.rhomass()
        self.specific_enthalpy__J_kg = self.State.hmass()
        self.specific_internal_energy__J_kg = self.State.umass()
        self.specific_entropy__J_kgK = self.State.smass()
        self.quality = self.State.Q()
        self.cp__J_kgK = self.State.cpmass()
        self.cv__J_kgK = self.State.cvmass()
        self.gamma = self.cp__J_kgK / self.cv__J_kgK

    def _update_transport_properties(self):
        self.viscosity__kg_ms = self.State.viscosity()  # dynamic viscosity
        self.kinematic_viscosity__m2_s = self.viscosity__kg_ms / self.density__kg_m3
        self.thermal_conductivity__W_mK = self.State.conductivity()
        self.beta__1_K = self.State.isobaric_expansion_coefficient()
        self.Prandtl = self.State.Prandtl()

    def _cval_property_update(self, new_value: float, cVal: float, cp_pair: int, cValSecond: bool):
        self.State.update(cp_pair, new_value if cValSecond else cVal, cVal if cValSecond else new_value)
        self.update_properties()

    @property
    def sound_speed__m_s(self):
        """Get the speed of sound in the fluid."""
        try:
            if self.is2phase and self.Allow2Phase:
                # Wood's Formula for speed of sound in a two-phase mixture
                x = self.quality
                l_rho, l_sos = CP.PropsSI(["D", "A"], "P", self.static_pressure__Pa, "Q", 1e-8, self.media)
                g_rho, g_sos = CP.PropsSI(["D", "A"], "P", self.static_pressure__Pa, "Q", 1.0 - 1e-8, self.media)
                sound_speed__m_s = (
                    (1 - x) / (l_rho * l_sos) ** 2 + x / (g_rho * g_sos) ** 2
                ) ** -0.5 / self.static_density__kg_m3
            else:
                sound_speed__m_s = self.State.speed_sound()
        except ValueError:
            warnings.warn("Speed of sound not available for this state. Returning -1.0.")
            sound_speed__m_s = -1.0
        return sound_speed__m_s

    @property
    def is2phase(self) -> bool:
        """Check if the state is in the two-phase region."""
        return 0.0 < self.quality < 1.0

    @property
    def molar_mass__kg_mol(self) -> float | None:
        return self.State.molar_mass()

    @property
    def specific_volume__m3_kg(self) -> float | None:
        return 1 / self.density__kg_m3

    @property
    def isentropic_bulk_modulus__Pa(self) -> float | None:  # change in pressure per relative change in volume
        return self.gamma * self.pressure__Pa

    @property
    def T_sat__K(self) -> float | None:
        try:
            T = CP.PropsSI("T", "Q", 1e-8, "P", self.static_pressure__Pa, self.media)
        except ValueError as e:
            warnings.warn(f"Could not calculate saturation temperature: {e}")
            T = None
        return T

    @property
    def dT_sat__K(self) -> float | None:
        """Static temperature relative to saturation.
        positive = superheated, negative = subcooled"""
        return self.static_temperature__K - self.T_sat__K if self.T_sat__K else None

    @property
    def p_sat__Pa(self) -> float | None:
        try:
            p = CP.PropsSI("P", "Q", 1e-8, "T", self.static_temperature__K, self.media)
        except ValueError as e:
            warnings.warn(f"Could not calculate saturation pressure: {e}")
            p = None
        return p

    @property
    def dp_sat__Pa(self) -> float | None:
        """Static pressure relative to saturation.
        positive = subcooled, negative = superheated"""
        return self.static_pressure__Pa - self.p_sat__Pa if self.p_sat__Pa else None

    @property
    def h_sat_vap__J_kg(self) -> float | None:
        """total specific enthalpy at saturated vapor condition"""
        try:
            h__J_kg = CP.PropsSI("H", "P", self.pressure__Pa, "Q", 1 - 1e-8, str(self.media))
            return h__J_kg
        except ValueError as e:
            warnings.warn(f"Could not calculate enthalpy of saturated vapor: {e}")
            return None

    @property
    def h_sat_liq__J_kg(self) -> float | None:
        """total specific enthalpy at saturated liquid condition"""
        try:
            h__J_kg = CP.PropsSI("H", "P", self.pressure__Pa, "Q", 1e-8, str(self.media))
            return h__J_kg
        except ValueError as e:
            warnings.warn(f"Could not calculate enthalpy of saturated liquid: {e}")
            return None

    @property
    def hvap__J_kg(self) -> float | None:
        """heat of vaporization at current pressure"""
        h_liq = self.h_sat_liq__J_kg
        h_vap = self.h_sat_vap__J_kg
        return h_vap - h_liq if h_vap and h_liq else None

    @property
    def isLiquid(self) -> bool:
        """Check if the state is in the liquid region."""
        h_sat_liq = self.h_sat_liq__J_kg
        if h_sat_liq:
            return (
                isclose(h_sat_liq, self.specific_enthalpy__J_kg, rel_tol=1e-5)
                or self.specific_enthalpy__J_kg < h_sat_liq
            )
        elif self.quality:
            return self.quality < 0.01
        else:
            return False

    # BaseQuantity properties for unitful convenience
    @property
    def pressure(self) -> BaseQuantity:
        return BaseQuantity(self.pressure__Pa, "Pa")

    @property
    def temperature(self) -> BaseQuantity:
        return BaseQuantity(self.temperature__K, "K")

    @property
    def density(self) -> BaseQuantity:
        return BaseQuantity(self.density__kg_m3, "kg/m**3")

    @property
    def specific_enthalpy(self) -> BaseQuantity:
        return BaseQuantity(self.specific_enthalpy__J_kg, "J/kg")

    @property
    def specific_internal_energy(self) -> BaseQuantity:
        return BaseQuantity(self.specific_internal_energy__J_kg, "J/kg")

    @property
    def specific_entropy(self) -> BaseQuantity:
        return BaseQuantity(self.specific_entropy__J_kgK, "J/(kg K)")

    @property
    def cp(self) -> BaseQuantity:
        return BaseQuantity(self.cp__J_kgK, "J/(kg K)")

    @property
    def cv(self) -> BaseQuantity:
        return BaseQuantity(self.cv__J_kgK, "J/(kg K)")

    @property
    def molar_mass(self) -> BaseQuantity:
        return BaseQuantity(self.molar_mass__kg_mol, "kg/mol")

    @property
    def specific_volume(self) -> BaseQuantity:
        return BaseQuantity(self.specific_volume__m3_kg, "m**3/kg")

    @property
    def viscosity(self) -> BaseQuantity:
        return BaseQuantity(self.viscosity__kg_ms, "kg/(m s)")

    @property
    def kinematic_viscosity(self) -> BaseQuantity:
        return BaseQuantity(self.kinematic_viscosity__m2_s, "m**2/s")

    @property
    def thermal_conductivity(self) -> BaseQuantity:
        return BaseQuantity(self.thermal_conductivity__W_mK, "W/(m K)")

    @property
    def beta(self) -> BaseQuantity:
        return BaseQuantity(self.beta__1_K, "1/K")

    @property
    def isentropic_bulk_modulus(self) -> BaseQuantity:
        return BaseQuantity(self.isentropic_bulk_modulus__Pa, "Pa")

    @property
    def sound_speed(self) -> BaseQuantity:
        return BaseQuantity(self.sound_speed__m_s, "m/s")

    @property
    def T_sat(self) -> BaseQuantity | None:
        return BaseQuantity(self.T_sat__K, "K") if self.T_sat__K else None

    @property
    def dT_sat(self) -> BaseQuantity | None:
        return BaseQuantity(self.dT_sat__K, "K") if self.dT_sat__K else None

    @property
    def p_sat(self) -> BaseQuantity | None:
        return BaseQuantity(self.p_sat__Pa, "Pa") if self.p_sat__Pa else None

    @property
    def dp_sat(self) -> BaseQuantity | None:
        return BaseQuantity(self.dp_sat__Pa, "Pa") if self.dp_sat__Pa else None

    @property
    def h_sat_vap(self) -> BaseQuantity | None:
        h_sat_vap = self.h_sat_vap__J_kg
        return BaseQuantity(h_sat_vap, "J/kg") if h_sat_vap else None

    @property
    def h_sat_liq(self) -> BaseQuantity | None:
        h_sat_liq = self.h_sat_liq__J_kg
        return BaseQuantity(h_sat_liq, "J/kg") if h_sat_liq else None

    @property
    def hvap(self) -> BaseQuantity:
        return BaseQuantity(self.hvap__J_kg, "J/kg") if self.hvap__J_kg else None

    def isentropic_property_update(self, p_type: str, value: float):
        """Constant entropy process"""
        cValSecond = True
        if p_type == "P":
            cp_pair = CP.PSmass_INPUTS
        elif p_type == "T":
            cp_pair = CP.SmassT_INPUTS
            cValSecond = False
        elif p_type == "D":
            cp_pair = CP.DmassSmass_INPUTS
        elif p_type == "H":
            cp_pair = CP.HmassSmass_INPUTS
        elif p_type == "U" or p_type == "Q":
            raise ValueError(f"Property pair S+{p_type} not supported by CoolProp. Use one of [P, T, D, H].")
        else:
            raise ValueError(f"Invalid property type specified: {p_type}. Use one of [P, T, D, H].")
        self._cval_property_update(value, self.specific_entropy__J_kgK, cp_pair, cValSecond)

    def isenthalpic_property_update(self, p_type: str, value: float):
        """Constant enthalpy process"""
        cValSecond = False
        if p_type == "P":
            cp_pair = CP.HmassP_INPUTS
        elif p_type == "D":
            cp_pair = CP.DmassHmass_INPUTS
            cValSecond = True
        elif p_type == "S":
            cp_pair = CP.HmassSmass_INPUTS
        elif p_type == "Q" or p_type == "T":
            raise ValueError(f"Property pair H+{p_type} not supported by CoolProp. Use one of [P, T, D, S].")
        else:
            raise ValueError(f"Invalid property type specified: {p_type}. Use one of [P, T, D, S].")
        self._cval_property_update(value, self.specific_enthalpy__J_kg, cp_pair, cValSecond)

    def isothermal_property_update(self, p_type: str, value: float):
        """Constant temperature process"""
        cValSecond = True
        if p_type == "P":
            cp_pair = CP.PT_INPUTS
        elif p_type == "D":
            cp_pair = CP.DmassT_INPUTS
        elif p_type == "S":
            cp_pair = CP.SmassT_INPUTS
        elif p_type == "Q":
            cp_pair = CP.QT_INPUTS
        elif p_type == "U" or p_type == "H":
            raise ValueError(f"Property pair T+{p_type} not supported by CoolProp. Use one of [P, D, S, Q].")
        else:
            raise ValueError(f"Invalid property type specified: {p_type}. Use one of [P, D, S, Q].")
        self._cval_property_update(value, self.temperature__K, cp_pair, cValSecond)

    def isobaric_property_update(self, p_type: str, value: float):
        """Constant pressure process"""
        cValSecond = False
        if p_type == "T":
            cp_pair = CP.PT_INPUTS
        elif p_type == "D":
            cp_pair = CP.DmassP_INPUTS
            cValSecond = True
        elif p_type == "H":
            cp_pair = CP.HmassP_INPUTS
            cValSecond = True
        elif p_type == "S":
            cp_pair = CP.PSmass_INPUTS
        elif p_type == "U":
            cp_pair = CP.PUmass_INPUTS
        elif p_type == "Q":
            cp_pair = CP.PQ_INPUTS
        else:
            raise ValueError(f"Invalid property type specified: {p_type}. Use one of {BASE_INT_PROPS.values()}")
        self._cval_property_update(value, self.pressure__Pa, cp_pair, cValSecond)

    def isochoric_property_update(self, p_type: str, value: float):
        """Constant volume process"""
        cValSecond = False
        if p_type == "P":
            cp_pair = CP.DmassP_INPUTS
        elif p_type == "T":
            cp_pair = CP.DmassT_INPUTS
        elif p_type == "H":
            cp_pair = CP.DmassHmass_INPUTS
        elif p_type == "S":
            cp_pair = CP.DmassSmass_INPUTS
        elif p_type == "U":
            cp_pair = CP.DmassUmass_INPUTS
        elif p_type == "Q":
            cp_pair = CP.DmassQ_INPUTS
        else:
            raise ValueError(f"Invalid property type specified: {p_type}. Use one of {BASE_INT_PROPS.values()}")
        self._cval_property_update(value, self.density__kg_m3, cp_pair, cValSecond)

    def _polytropic_compression(self, pressure_ratio: float, eta_poly: float, N: int) -> tuple[float, Self]:
        if N == 1:
            warnings.warn("Using N=1 for polytropic compression assumes constant gamma and is prone to overpredict dh.")
            StateN = self._semi_isentropic_compression(pressure_ratio, eta_poly)
            dhp = eta_poly * (StateN.specific_enthalpy__J_kg - self.specific_enthalpy__J_kg)
        elif N == 0:
            p2__Pa = self.pressure__Pa * pressure_ratio
            T2_min__K = (
                self.temperature__K + 1e-8
                if pressure_ratio >= 1
                else self._isentropic_temperature(pressure_ratio, 0.8 * eta_poly)
            )
            T2_max__K = (
                self.temperature__K - 1e-8
                if pressure_ratio < 1
                else self._isentropic_temperature(pressure_ratio, 0.8 * eta_poly)
            )
            StateN = self.deepcopy()

            # def eta_opt(T2__K: float) -> float:
            #    """Calculate polytropic efficiency for a given temperature.
            #       TODO, figure this out. I tried it because I thought it'd be faster, but it was unstable"""
            #    StateN.State.update(CP.PT_INPUTS, p2__Pa, T2__K)
            #    StateN._update_intensive_properties()
            #    ds = StateN.specific_entropy__J_kgK - self.specific_entropy__J_kgK
            #    dh = StateN.specific_enthalpy__J_kg - self.specific_enthalpy__J_kg
            #    eta = 1 - ds * (T2__K - self.temperature__K) / (dh * log(T2__K / self.temperature__K))
            #    return eta - eta_poly
            # T2__K = brentq(eta_opt, T2_min__K, T2_max__K, xtol=1e-5, rtol=1e-5)
            # StateN.isobaric_property_update("T", T2__K)
            # dh = StateN.specific_enthalpy__J_kg - self.specific_enthalpy__J_kg

            err = 1
            ix = 0
            while err > 1e-4 and ix < 50:
                T__K = 0.5 * (T2_max__K + T2_min__K)
                StateN.State.update(CP.PT_INPUTS, p2__Pa, T__K)
                hn__J_kg = StateN.State.hmass()
                sn__J_kgK = StateN.State.smass()
                ds = sn__J_kgK - self.specific_entropy__J_kgK
                dh = hn__J_kg - self.specific_enthalpy__J_kg
                eta = 1 - ds * (T__K - self.temperature__K) / (dh * log(T__K / self.temperature__K))
                if eta < eta_poly:
                    T2_max__K = T__K
                else:
                    T2_min__K = T__K
                err = rel_error(eta, eta_poly)
                ix += 1
            StateN.update_properties()
            dhp = dh * eta_poly
        else:
            StateN = self.deepcopy()
            pr_increment = pressure_ratio ** (1 / N)
            dhp = 0
            for _ in range(N):
                rhoN__kg_m3 = StateN.density__kg_m3
                vN__m3_kg = 1 / rhoN__kg_m3  # constant density for small dP step is fairly valid

                pN1__Pa = StateN.pressure__Pa * pr_increment
                dhp_i = (pN1__Pa - StateN.pressure__Pa) * vN__m3_kg
                dh_i = dhp_i / eta_poly

                StateN.State.update(
                    CP.HmassP_INPUTS,
                    StateN.specific_enthalpy__J_kg + dh_i,
                    pN1__Pa,
                )
                StateN.update_properties()
                dhp += dhp_i
        return dhp, StateN

    def _isentropic_temperature(self, pressure_ratio: float, eta: float = 1.0) -> float:
        gamma = self.gamma
        temperature = self.temperature__K * pressure_ratio ** ((gamma - 1) / gamma / eta)
        return temperature

    def _semi_isentropic_compression(self, pressure_ratio: float, eta: float = 1.0) -> Self:
        pressure = self.pressure__Pa * pressure_ratio
        temperature = self._isentropic_temperature(pressure_ratio, eta)
        CompressedState = ThermoState(media=self.media, pressure__Pa=pressure, temperature__K=temperature)
        return CompressedState

    def get_polytropic_compression_outlet(
        self, pressure_ratio: float, eta_poly: float, N: int = 200
    ) -> tuple[float, Self]:
        return self._polytropic_compression(pressure_ratio, eta_poly, N)

    def get_polytropic_compression_inlet(
        self, pressure_ratio: float, eta_poly: float, N: int = 200
    ) -> tuple[float, Self]:
        dh, StateN = self._polytropic_compression(1 / pressure_ratio, eta_poly, N)
        return -dh, StateN

    def get_polytropic_compression_outlet_dhp(self, dhp__J_kg: float, eta_poly: float, N: int = 200) -> Self:
        """Get outletState by applying polytropic enthalpy head, with a prescribed dhp and eta_p.

        Args:
            dhp__J_kg (float): specific enthalpy change in the polytropic process.
            eta_poly (float): polytropic efficiency of the process.
            N (int, optional): number of discrete steps. Defaults to 200.

        Returns:
            Self: compressed ThermoState after applying polytropic enthalpy head.
        """
        StateN = self.deepcopy()
        dhp_i = dhp__J_kg / N
        dh_i = dhp_i / eta_poly

        for _ in range(N):
            rhoN__kg_m3 = StateN.density__kg_m3  # constant density for small dP step is fairly valid
            pN1__Pa = StateN.pressure__Pa + dhp_i * rhoN__kg_m3

            StateN.State.update(
                CP.HmassP_INPUTS,
                StateN.specific_enthalpy__J_kg + dh_i,
                pN1__Pa,
            )
            StateN.update_properties()

        return StateN

    def calc_pr_for_polytropic_T_lift(self, dT__K: float, eta_poly: float, N: int = 200) -> float:
        T2__K = self.temperature__K + dT__K
        pr_min = T2__K / self.temperature__K
        IsentropicState = self.deepcopy()
        IsentropicState.isentropic_property_update("T", T2__K)
        pr_max = IsentropicState.pressure__Pa / self.pressure__Pa
        dT = 0
        i = 0
        while rel_error(dT__K, dT) > 1e-5 and i < 50:
            pr = (pr_min + pr_max) / 2
            _, StateN = self.get_polytropic_compression_outlet(pr, eta_poly, N)
            dT = StateN.temperature__K - self.temperature__K
            if dT < dT__K:
                pr_min = pr
            else:
                pr_max = pr
            i += 1
        return pr

    def get_required_inlet_Tsat_margin(self, pr: float, eta_poly: float = 1.0, N: int = 200) -> float:
        """Get the minimum superheat going into a given polytropic compression process to avoid re-entering vapor dome."""
        SatVapOutlet = ThermoState(media=self.media, pressure__Pa=self.pressure__Pa, quality=1 - 1e-6)
        _, ZeroMarginInlet = SatVapOutlet.get_polytropic_compression_inlet(pr, eta_poly, N)
        SatVapInlet_temp__K = CP.PropsSI("T", "Q", 1 - 1e-6, "P", ZeroMarginInlet.pressure__Pa, self.media)
        return max(0, ZeroMarginInlet.temperature__K - SatVapInlet_temp__K)

    def deepcopy(self):
        return ThermoState(
            media=self.media,
            Allow2Phase=self.Allow2Phase,
            density__kg_m3=self.density__kg_m3,
            temperature__K=self.temperature__K,
        )

    def print_str_English(self) -> str:
        sat_str = (
            f"dSat: {self.dT_sat.to('degR'):.2f} degR / {self.dp_sat.to('psi'):.0f} psi"
            if self.dT_sat__K and self.dp_sat__Pa
            else ""
        )
        str_English = f"{self.__class__.__name__}({self.media}, {self.temperature.to('degF'):.2f} degF, {self.pressure.to('psi'):.2f} psia, {sat_str})"
        print(str_English)

    def __repr__(self) -> str:
        sat_str = (
            f"dSat: {self.dT_sat__K:.2f} K / {self.dp_sat__Pa:.0f} Pa, " if self.dT_sat__K and self.dp_sat__Pa else ""
        )
        return f"{self.__class__.__name__}({self.media}, {self.temperature__K:.2f} K, {self.pressure__Pa:.0f} Pa, {sat_str}{self.density__kg_m3:.0f} kg/m^3)"


class StandardState(ThermoState):
    def __init__(self, media):
        super().__init__(media, temperature__K=294.15, pressure__Pa=101325)


class SaturationOffset(ThermoState):
    def __init__(self, media: str, dT_sat__K: float, **props: float) -> None:
        intensive_props = [(k, v) for k, v in props.items() if k in VALID_INPUTS.keys() and v is not None]
        if len(intensive_props) > 1 and dT_sat__K:
            raise ValueError(
                "State is overconstrained. If dT is specified, only one additional property needs specification."
            )
        else:
            i_prop = intensive_props[0]

            if "temperature__K" in i_prop:
                p_sat__Pa = CP.PropsSI("P", "Q", 1e-8, VALID_INPUTS[i_prop[0]], i_prop[1] - dT_sat__K, media)
                props["pressure__Pa"] = p_sat__Pa
            else:
                T_sat__K = CP.PropsSI("T", "Q", 1e-8, VALID_INPUTS[i_prop[0]], i_prop[1], media)
                props["temperature__K"] = T_sat__K + dT_sat__K
        super().__init__(media, **props)


class SuperHeatedState(SaturationOffset):
    def __init__(self, media: str, dT_super__K: float, **props: float) -> None:
        super().__init__(media, dT_sat__K=dT_super__K, **props)
        if dT_super__K < 0:
            warnings.warn(f"State specified for SuperHeatedState is actually subcooled ({self.dT_sat__K:.2f} K).")


class SubCooledState(SaturationOffset):
    def __init__(self, media: str, dT_sub__K: float, **props: float) -> None:
        super().__init__(media, dT_sat__K=-dT_sub__K, **props)
        if dT_sub__K < 0:
            warnings.warn(f"State specified for SubCooledState is actually superheated ({self.dT_sat__K:.2f} K).")


class ThermoNode(ThermoState):
    def __init__(self, media: str | Mixture, **props) -> None:
        if len(props.keys()) != 3:
            KeyError(
                "Gas node is poorly defined. Must include 3 properties, with at least 1 being extensive (i.e. mass, volume)."
            )
        self._props = props
        # separate props into extensive and intensive
        self.extensive_props = {k: v for k, v in props.items() if k in EXTENSIVE_PROPS.keys()}
        self.intensive_props = {k: v for k, v in props.items() if k in VALID_INPUTS.keys()}

        for key in EXTENSIVE_PROPS.keys():
            setattr(self, key, None)

        for key, val in self.extensive_props.items():
            setattr(self, key, val)

        if self.mass__kg and self.volume__m3:
            if "density__kg_m3" in self.intensive_props.keys():
                raise KeyError("Gas node is poorly defined. An independent intensive property must be provided.")
            self.intensive_props["density__kg_m3"] = self.mass__kg / self.volume__m3

        super().__init__(media, **self.intensive_props)

        # now that intensive properties are known, define any base extensive properties that haven't already been defined
        if self.mass__kg:
            self.volume__m3 = self.mass__kg / self.density__kg_m3
        elif self.volume__m3:
            self.mass__kg = self.density__kg_m3 * self.volume__m3

        self._update_extensive_properties()

    def remove_mass(self, dm__kg: float, process: str = "isentropic"):
        """Remove mass from the Gas Node, fixed volume, no external heat transfer.

        Args:
            dm__kg (float): Amount of mass to remove (kg), must be positive.
            process (str, optional): type of process (i.e. isentropic/adiabatic, isothermal, or isobaric). Defaults to "isentropic".

        Raises:
            KeyError: ValueError if dm__kg is less than 0
        """
        if dm__kg < 0:
            raise ValueError("dm__kg must be positive, otherwise, use add_mass() and specify enthalpy.")

        self.mass__kg += -dm__kg
        self.density__kg_m3 = self.mass__kg / self.volume__m3

        if process == "isentropic" or process == "adiabatic":
            # constant entropy
            self.isentropic_property_update("D", self.density__kg_m3)
        elif process == "isothermal":
            self.isothermal_property_update("D", self.density__kg_m3)
        elif process == "isobaric":
            self.isobaric_property_update("D", self.density__kg_m3)
        else:
            raise KeyError(f"Undefined process: {process}")

        self._update_extensive_properties()

    def add_mass(self, dm__kg: float, h__J_kg: float, process: str = "isentropic"):
        """Add mass to the Gas Node, fixed volume, no external heat transfer.
            TODO handle introduction of different gas species?

        Args:
            dm__kg (float): Amount of mass to add (kg). Negative values will remove mass.
            h__J_kg (float): Specific enthalpy of added mass. Ignored for negative values of dm__kg.
            process (str, optional): Type of process (i.e. isentropic/adiabatic, isothermal, or isobaric). Defaults to "isentropic".
        """

        if dm__kg < 0:
            self.remove_mass(abs(dm__kg), process)
            return

        self.mass__kg += dm__kg
        self.density__kg_m3 = self.mass__kg / self.volume__m3

        if process == "isentropic" or process == "adiabatic":
            # energy conserved
            self.internal_energy__J += h__J_kg * dm__kg
            self.specific_internal_energy__J_kg = self.internal_energy__J / self.mass__kg
            self.State.update(
                CP.DmassUmass_INPUTS,
                self.density__kg_m3,
                self.specific_internal_energy__J_kg,
            )
            self.update_properties()
        elif process == "isothermal":
            self.isothermal_property_update("D", self.density__kg_m3)
        elif process == "isobaric":
            self.isobaric_property_update("D", self.density__kg_m3)
        else:
            raise KeyError(f"Undefined process: {process}")

        self._update_extensive_properties()

    def add_heat(self, dQ__J: float, process: str = "isochoric"):
        """Add heat to the Gas Node, fixed mass and volume.

        Args:
            dQ__J (float): Amount of heat energy to add (J). Negative values will remove heat.
            process (str, optional): Type of process. Defaults to "isochoric".
        """

        if process == "isochoric":
            # constant volume
            self.internal_energy__J += dQ__J
            self.specific_internal_energy__J_kg = self.internal_energy__J / self.mass__kg
            self.isochoric_property_update("U", self.specific_internal_energy__J_kg)
        elif process == "isothermal":
            # constant temperature
            self.entropy__J_K += dQ__J / self.temperature__K
            self.specific_entropy__J_kgK = self.entropy__J_K / self.mass__kg
            self.isothermal_property_update("S", self.specific_entropy__J_kgK)
        elif process == "isobaric":
            # constant pressure
            self.enthalpy__J += dQ__J
            self.specific_enthalpy__J_kg = self.enthalpy__J / self.mass__kg
            self.isobaric_property_update("H", self.specific_enthalpy__J_kg)
        else:
            raise KeyError(f"Undefined process: {process}")

        self._update_extensive_properties()

    def add_volume(self, dV__m3: float, process: str = "isentropic"):
        """Add volume to the Gas Node, fixed mass.

        Args:
            dV__m3 (float): Amount of volume to add (m**3). Negative values will remove volume.
            process (str, optional): Type of process. Defaults to "isentropic".
        """
        self.volume__m3 += dV__m3
        self.density__kg_m3 = self.mass__kg / self.volume__m3
        if process == "isentropic" or process == "adiabatic":
            self.isentropic_property_update("D", self.density__kg_m3)
        elif process == "isothermal":
            self.isothermal_property_update("D", self.density__kg_m3)
        elif process == "isobaric":
            self.isobaric_property_update("D", self.density__kg_m3)
        else:
            raise KeyError(f"Undefined process: {process}")

        self._update_extensive_properties()

    def impose_volume(self, volume__m3: float, process: str = "isentropic"):
        """Apply a specfic volume to the Gas Node.

        Args:
            volume__m3 (float): volume to impose on the gas node
            process (str, optional): Type of process. Defaults to "isentropic".
        """
        self.volume__m3 = volume__m3
        self.density__kg_m3 = self.mass__kg / self.volume__m3
        if process == "isentropic" or process == "adiabatic":
            # energy conserved
            self.isentropic_property_update("D", self.density__kg_m3)
        elif process == "isothermal":
            self.isothermal_property_update("D", self.density__kg_m3)
        elif process == "isobaric":
            self.isobaric_property_update("D", self.density__kg_m3)
        else:
            raise KeyError(f"Undefined process: {process}")

        self._update_extensive_properties()

    def impose_pressure(self, pressure__Pa: float, process: str = "mass", h__J_kg: float = None):
        """Apply a specific pressure to the Gas Node, by adding or removing mass, heat, or volume.

        Args:
            pressure__Pa (float): pressure to impose (pascal)
            process (str, optional): Type of process. Defaults to "mass".
            h__J_kg (float, optional): Used for a mass addition process. Defaults to None.
        """
        dP__Pa = pressure__Pa - self.pressure__Pa
        self.pressure__Pa = pressure__Pa

        if process == "mass":
            if dP__Pa < 0:
                # constant entropy, mass removal
                self.isentropic_property_update("P", self.pressure__Pa)
            elif dP__Pa > 0:
                # add mass. if no enthalpy is specified, use starting gas enthalpy
                if h__J_kg is None:
                    warnings.warn(
                        "To increase pressure via mass addition, specific enthalpy should be specified. \
                            Using enthalpy of Gas Node itself."
                    )
                    h__J_kg = self.specific_enthalpy__J_kg
                    # TODO implement iterative solution for mass update, can maybe use a deep copy of State
            else:
                return
        elif process == "heat":
            # no change to mass or volume
            self.isochoric_property_update("P", self.pressure__Pa)
        elif process == "volume":
            self.isentropic_property_update("P", self.pressure__Pa)
            self.volume__m3 = self.mass__kg / self.density__kg_m3
        else:
            raise KeyError(f"Undefined process for imposing pressure: {process}")

        self._update_extensive_properties()

    def impose_temperature(self, temperature__K: float, process: str = "isochoric"):
        """Apply a specific temperature to the Gas Node.

        Args:
            temperature__K (float): temperature to impose (Kelvin)
            process (str, optional): Type of process. Defaults to "isochoric".
        """
        self.temperature__K = temperature__K
        if process == "isochoric":
            # mass and energy conserved
            self.isochoric_property_update("T", self.temperature__K)
        else:
            raise KeyError(f"Undefined process: {process}")

        self._update_extensive_properties()

    def _update_base_ext_properties(self):
        self.mass = BaseQuantity(self.mass__kg, "kg") if self.mass__kg else None
        self.volume = BaseQuantity(self.volume__m3, "m**3") if self.volume__m3 else None
        self.enthalpy = BaseQuantity(self.enthalpy__J, "J")
        self.internal_energy = BaseQuantity(self.internal_energy__J, "J")
        self.entropy = BaseQuantity(self.entropy__J_K, "J/K")

    def _update_extensive_properties(self):
        self.enthalpy__J = self.specific_enthalpy__J_kg * self.mass__kg
        self.internal_energy__J = self.specific_internal_energy__J_kg * self.mass__kg
        self.entropy__J_K = self.specific_entropy__J_kgK * self.mass__kg
        self._update_base_ext_properties()

    def _mix(self, Node2: "ThermoNode"):
        if Node2.media != self.media:
            raise AttributeError("Cannot combine these ThermoNodes. Mixtures not yet supported.")
        # add mass and volume, track total enthalpy
        self.mass__kg += Node2.mass__kg
        self.volume__m3 += Node2.volume__m3
        total_enthalpy__J = self.enthalpy__J + Node2.enthalpy__J
        density__kg_m3 = self.mass__kg / self.volume__m3
        specific_enthalpy__J_kg = total_enthalpy__J / self.mass__kg
        self.State.update(CP.DmassHmass_INPUTS, density__kg_m3, specific_enthalpy__J_kg)

        self.update_properties()
        self._update_extensive_properties()

    def mix(self, Nodes: "ThermoNode" | List["ThermoNode"]):
        if isinstance(Nodes, list):
            self._mix(Nodes[0])
            if len(Nodes) > 1:
                for tn in Nodes[1:]:
                    self._mix(tn)
        elif isinstance(Nodes, ThermoNode):
            self._mix(Nodes)
        else:
            raise TypeError("Input to ThermoNode.mix() must be another ThermoNode or list of ThermoNodes.")

    def deepcopy(self):
        return ThermoNode(
            media=self.media, density__kg_m3=self.density__kg_m3, pressure__Pa=self.pressure__Pa, mass__kg=self.mass__kg
        )

    def __repr__(self) -> str:
        mass_str = f", {self.mass__kg:.2f} kg" if self.mass__kg else ", nan kg"
        vol_str = f", {self.volume__m3:.3f} m^3" if self.volume__m3 else ", inf m^3"
        return super().__repr__()[:-1] + mass_str + vol_str + ")"


class TS(ThermoState):
    def __init__(self, media: str | Mixture, **intensive_props: BaseQuantity) -> None:
        for k, v in intensive_props.items():
            if not v.check_units(k.split("__")[0].split("static_")[-1]):
                raise ValueError(f"Incorrect input dimensionality for {k} property.")
        valid_super_inputs = transpose_dict({**BASE_INT_PROPS, **QUALITY_PROP})
        TSInputs = {valid_super_inputs[VALID_BQ_INPUTS[k]]: v.magnitude for k, v in intensive_props.items()}
        super().__init__(media, **TSInputs)


class SatOffsetTS(TS):
    def __init__(self, media: str, offset: BaseQuantity, **props: BaseQuantity) -> None:
        intensive_props = [(k, v) for k, v in props.items() if k in VALID_BQ_INPUTS.keys() and v is not None]
        if len(intensive_props) > 1 and offset:
            raise ValueError(
                "State is overconstrained. If offset is specified, only one additional property needs specification."
            )
        else:
            i_prop = intensive_props[0]

            if "temperature" in i_prop and offset.check_units("temperature"):
                p_sat__Pa = CP.PropsSI(
                    "P", "Q", 1e-8, VALID_BQ_INPUTS[i_prop[0]], i_prop[1].magnitude - offset.magnitude, media
                )
                props["pressure"] = BaseQuantity(p_sat__Pa, "pascal")
            elif "pressure" in i_prop and offset.check_units("pressure"):
                T_sat__K = CP.PropsSI(
                    "T", "Q", 1e-8, VALID_BQ_INPUTS[i_prop[0]], i_prop[1].magnitude - offset.magnitude, media
                )
                props["temperature"] = BaseQuantity(T_sat__K, "K")
            elif offset.check_units("temperature"):
                T_sat__K = CP.PropsSI("T", "Q", 1e-8, VALID_BQ_INPUTS[i_prop[0]], i_prop[1].magnitude, media)
                props["temperature"] = BaseQuantity(T_sat__K + offset.magnitude, "K")
            elif offset.check_units("pressure"):
                p_sat__Pa = CP.PropsSI("P", "Q", 1e-8, VALID_BQ_INPUTS[i_prop[0]], i_prop[1].magnitude, media)
                props["pressure"] = BaseQuantity(p_sat__Pa + offset.magnitude, "pascal")
            else:
                raise ValueError("Offset must be specified in terms of temperature or pressure.")
        super().__init__(media, **props)


class SuperHeatedTS(SatOffsetTS):
    def __init__(self, media: str, offset: BaseQuantity, **props: BaseQuantity) -> None:
        if offset.check_units("pressure"):
            abs_offset = -1 * offset
        else:
            abs_offset = offset

        super().__init__(media, offset=abs_offset, **props)

        if offset.check_units("temperature") and offset.magnitude < 0:
            warnings.warn(f"State specified for SuperHeatedTS is actually subcooled ({self.dT_sat__K:.2f} K).")
        elif offset.check_units("pressure") and offset.magnitude < 0:
            warnings.warn(f"State specified for SuperHeatedTS is actually subcooled ({self.dp_sat__Pa:.2f} Pa).")


class SubCooledTS(SatOffsetTS):
    def __init__(self, media: str, offset: BaseQuantity, **props: BaseQuantity) -> None:
        if offset.check_units("temperature"):
            abs_offset = -1 * offset
        else:
            abs_offset = offset

        super().__init__(media, offset=abs_offset, **props)

        if offset.check_units("temperature") and offset.magnitude < 0:
            warnings.warn(f"State specified for SubCooledTS is actually superheated ({self.dT_sat__K:.2f} K).")
        elif offset.check_units("pressure") and offset.magnitude < 0:
            warnings.warn(f"State specified for SubCooledTS is actually superheated ({self.dp_sat__Pa:.2f} Pa).")


class TN(ThermoNode):
    def __init__(self, media: str | Mixture, **props: BaseQuantity) -> None:
        valid_base_inputs = {**VALID_BQ_INPUTS, **EXT_BQ_PROPS}
        valid_super_inputs = transpose_dict({**BASE_INT_PROPS, **EXTENSIVE_PROPS})
        TSInputs = {valid_super_inputs[valid_base_inputs[k]]: v.magnitude for k, v in props.items()}
        super().__init__(media, **TSInputs)


def get_ThermoState_from_HT(
    media: str, specific_enthalpy__J_kg: float, temperature__K: float, p_max__Pa: float, p_min__Pa: float = None
) -> ThermoState:
    p_min__Pa = CP.PropsSI("PTRIPLE", media) if p_min__Pa is None else p_min__Pa
    p_max__Pa = CP.PropsSI("PCRIT", media)
    i = 0
    rel_err = 1
    while rel_err > 1e-4 and i < 50:
        p__Pa = (p_min__Pa + p_max__Pa) / 2
        h__J_kg = CP.PropsSI("H", "P", p__Pa, "T", temperature__K, media)
        rel_err = rel_error(h__J_kg, specific_enthalpy__J_kg)
        if h__J_kg < specific_enthalpy__J_kg:
            p_max__Pa = p__Pa
        else:
            p_min__Pa = p__Pa
        i += 1
    if i == 50:
        raise ValueError("No convergence in pressure calculation.")
    return ThermoState(media=media, temperature__K=temperature__K, pressure__Pa=p__Pa)


def get_dp_dT_for_saturation(media: str, pressure__Pa: float, dT_sat__K: float = 0.1) -> tuple[float, float]:
    """Get the change in saturation pressure per change in saturation temperature local to a starting pressure."""
    T_sat__K = CP.PropsSI("T", "Q", 1e-8, "P", pressure__Pa, media)
    p_sat__Pa = CP.PropsSI("P", "Q", 1e-8, "T", T_sat__K + dT_sat__K, media)
    dp_sat__Pa = p_sat__Pa - pressure__Pa
    return dp_sat__Pa / dT_sat__K


if __name__ == "__main__":
    pass
