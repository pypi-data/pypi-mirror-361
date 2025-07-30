import warnings
from math import isclose
from typing import List

import numpy as np
from CoolProp.CoolProp import PropsSI
from ki_util.constants import molar_vol_STP__m3_mol
from ki_util.geometry import Circle, Cylinder, D_from_A, Rectangle
from ki_util.helpers import args_defined, rel_error, str_in_keys, transpose_dict
from ki_util.units import BaseQuantity
from ki_util.units import convert_units as convert
from numpy.polynomial import Polynomial

from ki_thermofluids.mixture import Mixture
from ki_thermofluids.thermo import (
    BASE_BQ_INT_PROPS,
    INT_BQ_PROPS,
    INTENSIVE_PROPS,
    QUALITY_PROP,
    StandardState,
    ThermoState,
    get_dp_dT_for_saturation,
)

VALID_INPUTS = {**INTENSIVE_PROPS, **QUALITY_PROP}

VALID_FLOW_PROPS = {
    "mdot__kg_s": "Md",
    "vdot__m3_s": "Vd",
    "velocity__m_s": "v",
}
VALID_AREA_PROPS = {
    "diameter__m": "Dhyd",
    "radius__m": "Rhyd",
    "area__m2": "area",
}

VALID_BQ_FLOW_PROPS = {
    "mdot": "Md",
    "vdot": "Vd",
    "velocity": "v",
}
VALID_BQ_AREA_PROPS = {
    "diameter": "Dhyd",
    "radius": "Rhyd",
    "area": "area",
}


def velocity_is_definable(props: dict) -> bool:
    """Check if velocity is defined in the given properties."""
    fkeys = [k for k, v in props.items() if k in VALID_FLOW_PROPS.keys() and v is not None]
    akeys = [k for k, v in props.items() if k in VALID_AREA_PROPS.keys() and v is not None]
    return (
        "velocity__m_s" in fkeys
        or (len(akeys) == 1 and len(fkeys) == 1)
        or ("mdot__kg_s" in fkeys and "vdot__m3_s" in fkeys)
    )


class FlowState(ThermoState):
    def __init__(self, media: str | Mixture, Allow2Phase: bool = False, **props: float) -> None:
        """Represents Thermodynamic state of a fluid or mixture. Intensive properties are stored as attributes.
        Static or total properties can be specified, but not a mix of both (yet).

        Args:
            media (str | Mixture): fluid string or Mixture object.
            Allow2Phase (bool, optional): set to True to allow speed of sound computation for a 2 phase fluid. Defaults to False.
            **props (float): {**intensive, **flow, **area}.
                intensive: properties to define the state. Must specify exactly 2 intensive properties.
                flow: properties to define the flow. Can specify mdot or vdot and/or velocity or Mach
                area: properties to define the area. Can specify only one of diameter, radius, or area. If mdot or vdot is specified w/ velocity, area is inferred.
        """
        # separate inputs into intensive properties and flow properties
        intensive_props = {k: v for k, v in props.items() if k in VALID_INPUTS.keys() and v is not None}
        self._f_props = {k: v for k, v in props.items() if k in VALID_FLOW_PROPS.keys() and v is not None}
        self._a_props = {k: v for k, v in props.items() if k in VALID_AREA_PROPS.keys() and v is not None}

        if len(self._a_props.keys()) > 1:
            raise KeyError(
                f"State is over-specified. Only one area-defining property should be specified: {list(self._a_props.keys())} provided."
            )
        elif len(self._a_props.keys()) == 1:
            # define the diameter based on the provided area property
            if str_in_keys("diameter", self._a_props):
                D = list(self._a_props.values())[0]
            elif str_in_keys("radius", self._a_props):
                R = list(self._a_props.values())[0]
                D = 2 * R
            elif str_in_keys("area", self._a_props):
                A = list(self._a_props.values())[0]
                D = D_from_A(A)
            else:
                D = np.inf
        else:
            D = np.inf

        self._D__m = D

        # if input properties are not specified as static or total, assume total

        # extract velocity from given properties
        if velocity_is_definable(props):
            input_intensive_prop_types = list(intensive_props.keys())
            prop0_is_static = "static" in input_intensive_prop_types[0]
            prop1_is_static = "static" in input_intensive_prop_types[1]

            if not prop0_is_static and not prop1_is_static:
                # if all properties are total, init with total properties, then set the static properties
                StagnationState = ThermoState(media, Allow2Phase, **intensive_props)
                if "velocity__m_s" in self._f_props.keys() and args_defined(self._f_props["velocity__m_s"]):
                    _vel = self._f_props["velocity__m_s"]
                    if "mdot__kg_s" in self._f_props.keys() and "vdot__m3_s" in self._f_props.keys():
                        raise KeyError("State is over-specified. Mass and volumetric flowrates are redundant.")
                    elif "vdot__m3_s" in self._f_props.keys():
                        self._D__m = D_from_A(self._f_props["vdot__m3_s"] / _vel) if _vel else np.inf
                    elif "mdot__kg_s" in self._f_props.keys() and args_defined(self._f_props["mdot__kg_s"]):
                        _mdot = self._f_props["mdot__kg_s"]
                        StaticState = StagnationState.get_StaticState(velocity__m_s=_vel)
                        _area = _mdot / StagnationState.density__kg_m3 / _vel if _vel else np.inf

                        if self._D__m is not np.inf:
                            _input_area = Circle(D=self._D__m).area
                            if not isclose(_input_area, _area, rel_tol=1e-5):
                                warnings.warn(
                                    f"Input diameter {self._D__m:.4f} [m] does not match calculated diameter {D_from_A(_area):.4f} [m]. Using calculated value."
                                )

                        self._D__m = D_from_A(_area) if _area else np.inf

                elif "vdot__m3_s" in self._f_props.keys():
                    _vdot = self._f_props["vdot__m3_s"]
                    _vel = _vdot / self.area__m2
                elif "mdot__kg_s" in self._f_props.keys() and args_defined(self._f_props["mdot__kg_s"]):
                    # this will require iteration to find the correct velocity since only total density is known, velocity is a function of static density
                    _mdot = self._f_props["mdot__kg_s"]
                    _vel = StagnationState.get_static_velocity__m_s(mdot__kg_s=_mdot, diameter__m=self._D__m)
                    StaticState = StagnationState.get_StaticState(velocity__m_s=_vel)
                else:
                    raise KeyError("Something went wrong with the flow properties, velocity could not be determined.")

            elif prop0_is_static and prop1_is_static:
                # if all properties are static, init ThermoState with static properties, then set the total properties
                StaticState = ThermoState(media, Allow2Phase, **intensive_props)
                if "velocity__m_s" in self._f_props.keys() and args_defined(self._f_props["velocity__m_s"]):
                    _vel = self._f_props["velocity__m_s"]
                    if "mdot__kg_s" in self._f_props.keys() and "vdot__m3_s" in self._f_props.keys():
                        raise KeyError("State is over-specified. Mass and volumetric flowrates are redundant.")
                    elif "vdot__m3_s" in self._f_props.keys():
                        self._D__m = D_from_A(self._f_props["vdot__m3_s"] / _vel) if _vel else np.inf
                    elif "mdot__kg_s" in self._f_props.keys():
                        self._D__m = (
                            D_from_A(self._f_props["mdot__kg_s"] / (StaticState.density__kg_m3 * _vel))
                            if _vel
                            else np.inf
                        )
                elif "vdot__m3_s" in self._f_props.keys():
                    _vdot = self._f_props["vdot__m3_s"]
                    _vel = _vdot / self.area__m2
                elif "mdot__kg_s" in self._f_props.keys():
                    _mdot = self._f_props["mdot__kg_s"]
                    _vel = _mdot / StaticState.density__kg_m3 / self.area__m2
                StagnationState = StaticState.get_StagnationState(velocity__m_s=_vel)
            else:
                # if one property is static and the other is total, guess the second static property and iterate to find the correct value
                static_prop_type = input_intensive_prop_types[0 if prop0_is_static else 1]
                stag_prop_type = input_intensive_prop_types[1 if prop0_is_static else 0]
                static_prop = intensive_props[static_prop_type]
                stag_prop = intensive_props[stag_prop_type]

                other_static_prop_max = stag_prop
                other_static_prop_min = 0
                other_prop_static = other_static_prop_max
                ix = 0
                while not isclose(other_static_prop_max, other_static_prop_min, rel_tol=1e-7) and ix < 100:
                    StateFromStatic = FlowState(
                        media,
                        Allow2Phase,
                        **{
                            static_prop_type: static_prop,
                            f"static_{stag_prop_type}": other_prop_static,
                            **self._f_props,
                            **self._a_props,
                        },
                    )
                    if getattr(StateFromStatic, stag_prop_type) < stag_prop:
                        other_static_prop_min = other_prop_static
                        other_prop_static = other_static_prop_max * 0.2 + other_static_prop_min * 0.8
                    else:
                        other_static_prop_max = other_prop_static
                        other_prop_static = other_static_prop_max * 0.8 + other_static_prop_min * 0.2
                    ix += 1
                _vel = StateFromStatic.velocity__m_s
                StagnationState = StateFromStatic.get_StagnationState(velocity__m_s=_vel)
            super().__init__(media, Allow2Phase, **StagnationState.get_DU())
            self._vel = _vel
        else:
            # if no velocity is defined, init super with whatever properties are provided
            super().__init__(media, Allow2Phase, **intensive_props)
            self._vel = 0.0

        self.update_static_properties(velocity__m_s=self._vel)

        if "mdot__kg_s" in self._f_props.keys():
            self._mdot = self._f_props["mdot__kg_s"]
        elif "vdot__m3_s" in self._f_props.keys():
            _vdot = self._f_props["vdot__m3_s"]
            self._mdot = _vdot * self.static_density__kg_m3
            if self._D__m == np.inf:
                self._D__m = D_from_A(_vdot / self._vel) if self._vel else np.inf
        elif "velocity__m_s" in self._f_props.keys() and self._D__m != np.inf:
            self._mdot = _vel * self.area__m2 * self.static_density__kg_m3
        else:
            self._mdot = None

    @property
    def mdot__kg_s(self):
        return self._mdot

    @mdot__kg_s.setter
    def mdot__kg_s(self, new_mdot):
        self._mdot = new_mdot
        self._vel = (
            new_mdot / self.static_density__kg_m3 / self.area__m2 if new_mdot is not None and self.area__m2 else None
        )

    @property
    def velocity__m_s(self):
        return self._vel

    @velocity__m_s.setter
    def velocity__m_s(self, new_vel):
        self._vel = new_vel
        self._mdot = new_vel * self.static_density__kg_m3 * self.area__m2
        self.update_static_properties(new_vel)

    @property
    def diameter__m(self):
        return self._D__m

    @diameter__m.setter
    def diameter__m(self, new_D):
        self._D__m = new_D
        if self._mdot is not None and self.area__m2:
            self._vel = self.get_static_velocity__m_s(mdot__kg_s=self._mdot, diameter__m=new_D)
            self.update_static_properties(self._vel)

    @property
    def mdot(self) -> BaseQuantity:
        return BaseQuantity(self.mdot__kg_s, "kg/s") if self.mdot__kg_s is not None else None

    @mdot.setter
    def mdot(self, new_mdot: BaseQuantity):
        if not new_mdot.check_units("mdot"):
            raise ValueError(f"Incorrect input dimensionality for mdot property: {new_mdot}")
        self.mdot__kg_s = new_mdot.magnitude

    @property
    def velocity(self) -> BaseQuantity:
        return BaseQuantity(self.velocity__m_s, "m/s") if self.velocity__m_s is not None else None

    @velocity.setter
    def velocity(self, new_velocity: BaseQuantity):
        if not new_velocity.check_units("velocity"):
            raise ValueError(f"Incorrect input dimensionality for velocity property: {new_velocity}")
        self.velocity__m_s = new_velocity.magnitude

    @property
    def diameter(self) -> BaseQuantity:
        return BaseQuantity(self.diameter__m, "m") if self.diameter__m is not None else None

    @diameter.setter
    def diameter(self, new_diameter: BaseQuantity):
        if not new_diameter.check_units("length"):
            raise ValueError(f"Incorrect input dimensionality for diameter property: {new_diameter}")
        self.diameter__m = new_diameter.magnitude

    @property
    def area__m2(self):
        return Circle(D=self.diameter__m).area

    @property
    def vdot__m3_s(self):
        return self.mdot__kg_s / self.static_density__kg_m3 if self.mdot__kg_s else 0.0

    @property
    def Reynolds(self):
        return (
            self.static_density__kg_m3 * self.velocity__m_s * self.diameter__m / self.viscosity__kg_ms
            if self.velocity__m_s
            else None
        )

    @property
    def Mach(self):
        return self.velocity__m_s / self.sound_speed__m_s if self.velocity__m_s is not None else None

    @property
    def enthalpy_flowrate__J_s(self):
        return self.specific_enthalpy__J_kg * self.mdot__kg_s if self.mdot__kg_s else 0.0

    @property
    def dynamic_pressure__Pa(self):
        return 0.5 * self.static_density__kg_m3 * self.velocity__m_s * self.velocity__m_s if self.velocity__m_s else 0.0

    @property
    def acfm(self):
        return convert(self.vdot__m3_s, "m**3/s", "ft**3/min")

    @property
    def scfm(self):
        return kg_s_to_scfm(media=self.media, kg_s=self.mdot__kg_s)

    @property
    def dp_static__Pa(self) -> float:
        """Static pressure relative to saturation as a float."""
        return self.pressure__Pa - self.static_pressure__Pa

    @property
    def dT_static__K(self) -> float:
        """Static temperature relative to saturation as a float."""
        return self.temperature__K - self.static_temperature__K

    @property
    def dp_static(self) -> BaseQuantity:
        """Static pressure relative to saturation as a BaseQuantity."""
        return self.pressure - self.static_pressure

    @property
    def dT_static(self) -> BaseQuantity:
        """Static temperature relative to saturation as a BaseQuantity."""
        return self.temperature - self.static_temperature

    @property
    def area(self) -> BaseQuantity:
        """Cross-sectional area of the flow as a BaseQuantity."""
        return BaseQuantity(self.area__m2, "m**2") if self.area__m2 is not None else None

    @property
    def vdot(self) -> BaseQuantity:
        """Volumetric flow rate as a BaseQuantity."""
        return BaseQuantity(self.vdot__m3_s, "m**3/s") if self.vdot__m3_s is not None else None

    @property
    def enthalpy_flowrate(self) -> BaseQuantity:
        """Enthalpy flow rate as a BaseQuantity."""
        return BaseQuantity(self.enthalpy_flowrate__J_s, "W") if self.enthalpy_flowrate__J_s is not None else None

    @property
    def dynamic_pressure(self) -> BaseQuantity:
        """Dynamic pressure of the flow as a BaseQuantity."""
        return BaseQuantity(self.dynamic_pressure__Pa, "Pa") if self.dynamic_pressure__Pa is not None else None

    def get_ThermoState(self):
        return ThermoState(self.media, self.Allow2Phase, **self.get_DU())

    def _mix(self, FlowState2: "FlowState"):
        if FlowState2.media != self.media:
            raise AttributeError("Cannot combine these FlowStates. Mixtures not yet supported.")
        if rel_error(self.pressure__Pa, FlowState2.pressure__Pa) > 1e-4:
            raise ValueError("Cannot combine these FlowStates since they are at different pressures.")
        enthalpy_rate1__W = self.mdot__kg_s * self.specific_enthalpy__J_kg
        enthalpy_rate2__W = FlowState2.mdot__kg_s * FlowState2.specific_enthalpy__J_kg
        total_enthalpy_rate__W = enthalpy_rate1__W + enthalpy_rate2__W
        self.mdot__kg_s = self._mdot + FlowState2.mdot__kg_s
        self.specific_enthalpy__J_kg = total_enthalpy_rate__W / self.mdot__kg_s
        self.isobaric_property_update("H", self.specific_enthalpy__J_kg)

    def mix(self, FlowStates: "FlowState" | List["FlowState"]):
        if isinstance(FlowStates, list):
            self._mix(FlowStates[0])
            if len(FlowStates) > 1:
                for fs in FlowStates[1:]:
                    self._mix(fs)
        elif isinstance(FlowStates, FlowState):
            self._mix(FlowStates)
        else:
            raise TypeError("Input to FlowState.mix() must be another FlowState or list of FlowStates.")

    def set_D_from_Mach(self, Mach: float):
        """Set the diameter of the flow based on a Mach number limit."""
        v_target__m_s = Mach * self.sound_speed__m_s
        area_target__m2 = self.vdot__m3_s / v_target__m_s
        D_target__m = D_from_A(area_target__m2)
        self.diameter__m = D_target__m

    def attemperate(self, AttemperationState: ThermoState, dT_super__K: float):
        """Reduce the superheat of the flow to the specified superheat value

        Args:
            dT_super__K (float): target superheat value
            AttemperationState (ThermoState): fluid state to be used for attemperation
        Returns:
            targetState (FlowState): new state at specified superheat
        """
        if self.dT_sat__K <= dT_super__K:
            warnings.warn("This FlowState is already below the specified superheat, returning self.")
            targetState = self.deepcopy()
        else:
            targetState = FlowState(
                self.media,
                temperature__K=self.T_sat__K + dT_super__K,
                pressure__Pa=self.pressure__Pa,
                diameter__m=self.diameter__m,
            )
            if AttemperationState.specific_enthalpy__J_kg >= targetState.specific_enthalpy__J_kg:
                warnings.warn(
                    "The given AttemperationState is higher enthalpy than the target, so cannot be used for attemperation, returning self."
                )
                targetState = self.deepcopy()
            elif self.mdot__kg_s is None:
                warnings.warn(
                    "mdot is not defined for the current state, so attemperation is not possible, returning self."
                )
                targetState = self.deepcopy()
            else:
                mdot_new__kg_s = (
                    self.mdot__kg_s
                    * (self.specific_enthalpy__J_kg - AttemperationState.specific_enthalpy__J_kg)
                    / (targetState.specific_enthalpy__J_kg - AttemperationState.specific_enthalpy__J_kg)
                )
                targetState.mdot__kg_s = mdot_new__kg_s
        return targetState

    def get_PreMixState(self, MixedFlowState: "FlowState"):
        """Get the state of the stream required to achieve the specified MixedFlowState."""
        if self.mdot__kg_s is None or MixedFlowState.mdot__kg_s is None:
            raise ValueError("Cannot get PreMixState if mdot is not defined for both states.")
        if self.media != MixedFlowState.media:
            raise NotImplementedError("get_PreMixState does not yet support mixing of multiple media.")
        if self.pressure__Pa != MixedFlowState.pressure__Pa:
            raise ValueError("Cannot get PreMixState if pressure is not the same for both states.")

        mdot__kg_s = MixedFlowState.mdot__kg_s - self.mdot__kg_s
        h__J_kg = (MixedFlowState.enthalpy_flowrate__J_s - self.enthalpy_flowrate__J_s) / mdot__kg_s
        return FlowState(
            self.media,
            Allow2Phase=self.Allow2Phase,
            pressure__Pa=self.pressure__Pa,
            specific_enthalpy__J_kg=h__J_kg,
            mdot__kg_s=mdot__kg_s,
        )

    def deepcopy(self):
        area_props = {"diameter__m": self._D__m}
        flow_props = {"mdot__kg_s": self._mdot, "velocity__m_s": self._vel}
        intensive_props = {"density__kg_m3": self.density__kg_m3, "pressure__Pa": self.pressure__Pa}
        return FlowState(
            media=self.media,
            Allow2Phase=self.Allow2Phase,
            **{**intensive_props, **flow_props, **area_props},
        )

    @property
    def str_English(self) -> str:
        mdot_str = (
            f", {convert(self.mdot__kg_s, 'kg/s', 'klbm/hr'):.2f} klbm/hr" if self.mdot__kg_s else ", nan klbm/hr"
        )
        diam_str = f", {convert(self.diameter__m, 'm', 'in'):.2f} in" if self.diameter__m else ", inf in"
        return super().str_English[:-1] + mdot_str + diam_str + ")"

    def __repr__(self) -> str:
        mdot_str = f", {self.mdot__kg_s:.2f} kg/s" if self.mdot__kg_s else ", nan kg/s"
        diam_str = f", {self.diameter__m:.2f} m" if self.diameter__m else ", inf m"
        return super().__repr__()[:-1] + mdot_str + diam_str + ")"


class SaturationOffset(FlowState):
    # TODO deprecate this and its children, replace with SatOffsetFS and its children
    def __init__(self, media: str, dT_sat__K: float, **props: float) -> None:
        warnings.warn(
            "SaturationOffset and its children, SuperHeatedFlow and SubCooledFlow, will be deprecated. Use SatOffsetFS and its children, SuperHeatedFS and SubCooledFS, instead. This will be removed in a future version.",
        )
        intensive_props = [(k, v) for k, v in props.items() if k in VALID_INPUTS.keys() and v is not None]

        if len(intensive_props) > 1 and dT_sat__K:
            raise ValueError(
                "State is overconstrained. If dT is specified, only one additional property needs specification."
            )
        else:
            self.i_prop = intensive_props[0]

            if "temperature__K" in self.i_prop or "static_temperature__K" in self.i_prop:
                p_sat__Pa = PropsSI("P", "Q", 1e-9, VALID_INPUTS[self.i_prop[0]], self.i_prop[1] - dT_sat__K, media)
                props["static_pressure__Pa"] = p_sat__Pa
            else:
                T_sat__K = PropsSI("T", "Q", 1e-9, VALID_INPUTS[self.i_prop[0]], self.i_prop[1], media)
                props["static_temperature__K"] = T_sat__K + dT_sat__K
        super().__init__(media, **props)

    def dT_for_static_conditions(self, dT_target__K: float, velocity__m_s: float = None):
        dT_sat_static__K = self.get_StaticState(velocity__m_s).temperature__K - self.T_sat__K
        dT_offset__K = dT_target__K - dT_sat_static__K
        return dT_target__K + dT_offset__K

    def adjust_dT_for_static_conditions(self, dT_target__K: float, velocity__m_s: float = None):
        flow_props = {"mdot__kg_s": self._mdot}
        area_props = {"diameter__m": self._D__m}
        intensive_props = {self.i_prop[0]: self.i_prop[1]}
        return SaturationOffset(
            media=self.media,
            dT_sat__K=self.dT_for_static_conditions(dT_target__K, velocity__m_s),
            **{**intensive_props, **flow_props, **area_props},
        )


class SuperHeatedFlow(SaturationOffset):
    def __init__(self, media: str, dT_super__K: float, **props: float) -> None:
        super().__init__(media, dT_sat__K=dT_super__K, **props)
        if dT_super__K < 0:
            warnings.warn(f"State specified for SuperHeatedFlow is actually subcooled ({self.dT_sat__K:.2f} K).")


class SubCooledFlow(SaturationOffset):
    def __init__(self, media: str, dT_sub__K: float, **props: float) -> None:
        super().__init__(media, dT_sat__K=-dT_sub__K, **props)
        if dT_sub__K < 0:
            warnings.warn(f"State specified for SubCooledFlow is actually superheated ({self.dT_sat__K:.2f} K).")


class FS(FlowState):
    def __init__(self, media: str, Allow2Phase: bool = False, **props: BaseQuantity) -> None:
        for k, v in props.items():
            if v is not None:
                if not v.check_units(k.split("__")[0].split("static_")[-1]):
                    raise ValueError(f"Incorrect input dimensionality for {k} property.")

        valid_base_inputs = {**INT_BQ_PROPS, **VALID_BQ_FLOW_PROPS, **VALID_BQ_AREA_PROPS}
        valid_super_inputs = transpose_dict({**VALID_INPUTS, **VALID_FLOW_PROPS, **VALID_AREA_PROPS})
        FSInputs = {valid_super_inputs[valid_base_inputs[k]]: v.magnitude for k, v in props.items() if v is not None}
        super().__init__(media, Allow2Phase, **FSInputs)


class SatOffsetFS(FS):
    def __init__(self, media: str, offset: BaseQuantity, **props: BaseQuantity) -> None:
        """Allows initialization of a FlowState using a temperature or pressure delta relative to a saturated static state.

        Args:
            media (str): CoolProp media string
            offset (BaseQuantity): Difference from saturation (must be specified in terms of temperature or pressure)
        """
        intensive_props = [(k, v) for k, v in props.items() if k in INT_BQ_PROPS.keys() and v is not None]

        if len(intensive_props) > 1 and offset:
            raise ValueError(
                "State is overconstrained. If offset is specified, only one additional property needs specification."
            )

        i_prop = intensive_props[0]  # the only intensive property explicitly specified

        prop_magnitude = i_prop[1].magnitude
        offset_magnitude = offset.magnitude
        if ("temperature" in i_prop or "static_temperature" in i_prop) and offset.check_units("temperature"):
            if offset_magnitude > 200:
                warnings.warn(
                    f"Large temperature offset ({offset_magnitude:.2f} K) specified, check that input unit is absolute (K or degR)."
                )

            p_sat__Pa = PropsSI("P", "Q", 1e-9, INT_BQ_PROPS[i_prop[0]], prop_magnitude - offset_magnitude, media)
            props["static_pressure"] = BaseQuantity(p_sat__Pa, "pascal")
        elif ("pressure" in i_prop or "static_pressure" in i_prop) and offset.check_units("pressure"):
            T_sat__K = PropsSI("T", "Q", 1e-9, INT_BQ_PROPS[i_prop[0]], prop_magnitude - offset_magnitude, media)
            props["static_temperature"] = BaseQuantity(T_sat__K, "K")
        elif offset.check_units("temperature"):
            T_sat__K = PropsSI("T", "Q", 1e-9, INT_BQ_PROPS[i_prop[0]], prop_magnitude, media)
            props["static_temperature"] = BaseQuantity(T_sat__K + offset_magnitude, "K")
        elif offset.check_units("pressure"):
            p_sat__Pa = PropsSI("P", "Q", 1e-9, INT_BQ_PROPS[i_prop[0]], prop_magnitude, media)
            props["static_pressure"] = BaseQuantity(p_sat__Pa + offset_magnitude, "pascal")
        else:
            raise ValueError("Offset must be specified in terms of temperature or pressure.")

        super().__init__(media, **props)


class SuperHeatedFS(SatOffsetFS):
    def __init__(self, media: str, offset: BaseQuantity, **props: BaseQuantity) -> None:
        if offset.check_units("pressure"):
            abs_offset = -1 * offset
        else:
            abs_offset = offset

        super().__init__(media, offset=abs_offset, **props)

        offset_magnitude = offset.magnitude
        if offset.check_units("temperature") and offset_magnitude < 0:
            warnings.warn(f"State specified for SuperHeatedFS is actually subcooled ({self.dT_sat__K:.2f} K).")
        elif offset.check_units("pressure") and offset_magnitude < 0:
            warnings.warn(f"State specified for SuperHeatedFS is actually subcooled ({self.dp_sat__Pa:.2f} Pa).")


class SubCooledFS(SatOffsetFS):
    def __init__(self, media: str, offset: BaseQuantity, **props: BaseQuantity) -> None:
        if offset.check_units("temperature"):
            abs_offset = -1 * offset
        else:
            abs_offset = offset

        super().__init__(media, offset=abs_offset, **props)

        offset_magnitude = offset.magnitude
        if offset.check_units("temperature") and offset_magnitude < 0:
            warnings.warn(f"State specified for SubCooledFS is actually superheated ({self.dT_sat__K:.2f} K).")
        elif offset.check_units("pressure") and offset_magnitude < 0:
            warnings.warn(f"State specified for SubCooledFS is actually superheated ({self.dp_sat__Pa:.2f} Pa).")


def get_SuperHeatedFS_w_Mach_total_prop(
    media: str, offset: BaseQuantity, Mach: float, **props: BaseQuantity
) -> SuperHeatedFS:
    """Get a SuperHeatedFS from a superheat offset (dT or dp), Mach number, and a total property."""
    total_props = [(k, v) for k, v in props.items() if k in BASE_BQ_INT_PROPS.keys() and v is not None]

    if len(total_props) > 1 and offset:
        raise ValueError(
            "State is overconstrained. If offset is specified, only one additional property needs specification."
        )
    elif len(total_props) == 0:
        raise ValueError("At least one total property must be specified.")

    base_tot_prop_type = total_props[0][0]
    tot_prop_type = f"{base_tot_prop_type}__{'Pa' if 'pressure' in base_tot_prop_type else 'K'}"
    tot_prop = total_props[0][1]  # the only static property explicitly specified
    tot_prop_val = tot_prop.magnitude

    if offset.check_units("temperature"):
        offset_type = "temperature"
        dT_sat__K = offset.magnitude
        dp_sat__Pa = dT_sat__K * get_dp_dT_for_saturation(media, PropsSI("PTRIPLE", media) + 10000)  # err low
    elif offset.check_units("pressure"):
        offset_type = "pressure"
        dp_sat__Pa = offset.magnitude
        dT_sat__K = dp_sat__Pa / get_dp_dT_for_saturation(media, PropsSI("PCRIT", media) - 100000)  # err low
    else:
        raise ValueError("Offset must be specified in terms of temperature or pressure.")

    static_prop_max = tot_prop_val
    static_prop_min = (
        PropsSI("PTRIPLE", media) + dp_sat__Pa + 1000
        if tot_prop.check_units("pressure")
        else PropsSI("TTRIPLE", media) + dT_sat__K + 1.0
    )

    ix = 0
    rel_err = 1.0
    while rel_err > 1e-5 and ix < 50:
        static_prop = 0.5 * (static_prop_max + static_prop_min)
        if "pressure__Pa" in tot_prop_type:  # static prop is pressure
            if offset_type == "temperature":  # put offset in terms of pressure
                dp_sat__Pa = dT_sat__K * get_dp_dT_for_saturation(media, static_prop)

            static_temp__K = PropsSI("T", "P", static_prop + dp_sat__Pa, "Q", 1e-9, media)
            StaticState = ThermoState(media, static_pressure__Pa=static_prop, static_temperature__K=static_temp__K)
        else:  # static prop is temperature
            if offset_type == "pressure":  # put offset in terms of temperature
                static_pres__Pa = PropsSI("P", "T", static_prop - dT_sat__K, "Q", 1e-9, media)
                dT_sat__K = dp_sat__Pa / get_dp_dT_for_saturation(media, static_pres__Pa)

            static_pres__Pa = PropsSI("P", "T", static_prop - dT_sat__K, "Q", 1e-9, media)
            StaticState = ThermoState(media, static_pressure__Pa=static_pres__Pa, static_temperature__K=static_prop)

        velocity__m_s = Mach * StaticState.sound_speed__m_s
        StagnationState = StaticState.get_StagnationState(velocity__m_s=velocity__m_s)

        if getattr(StagnationState, tot_prop_type) < tot_prop_val:
            static_prop_min = static_prop
        else:
            static_prop_max = static_prop

        rel_err = rel_error(getattr(StagnationState, tot_prop_type), tot_prop_val)
        ix += 1

    props["static_" + base_tot_prop_type] = BaseQuantity(static_prop, tot_prop.units)
    props.pop(base_tot_prop_type)  # remove total property from props
    return SuperHeatedFS(
        media,
        offset=offset,
        velocity=BaseQuantity(velocity__m_s, "m/s"),
        **props,
    )


def ThermoState_to_FlowState(State: ThermoState, **flow_props: dict) -> FlowState:
    """Create a FlowState from a ThermoState.

    Args:
        State (ThermoState): initial state
        **flow_props (dict): flow properties

    Returns:
        FlowState: new state
    """
    return FlowState(State.media, **{**State.get_DU(), **flow_props})


class Orifice:
    def __init__(self, CdA__m2: float = None, valve_Cv_curve_fit: Polynomial = None) -> None:
        self.CdA__m2 = CdA__m2
        self.valve_Cv_curve_fit = valve_Cv_curve_fit

    def set_CdA_from_valve_opening(self, valve_opening: float, isLiquid=True):
        # TODO need to add error handling for if valve_opening is not in range of curve fit or if curve fit not defined
        Cv = self.valve_Cv_curve_fit(valve_opening)

        self.CdA__m2 = CdA_from_Cv(Cv, isLiquid)

    def _check_area(self, State: FlowState):
        if State.area__m2 and self.CdA__m2:
            if self.CdA__m2 > State.area__m2:
                warnings.warn(
                    f"Orifice area ({self.CdA__m2:.2e} m^2) is larger than the \
                        defined state's flow area ({State.area__m2:.2e} m^2)."
                )
        elif not self.CdA__m2:
            raise ValueError(
                "Orifice CdA is not defined. Please set CdA__m2 or use set_CdA_from_valve_opening() to define it."
            )

    def _choked_flux(self, UpstreamState: FlowState, err_threshold=1e-5) -> float:
        """Calculate the choked mass flux through the orifice."""
        p1__Pa = UpstreamState.pressure__Pa
        h1__J_kg = UpstreamState.specific_enthalpy__J_kg

        # throat condition initial guess
        p_th__Pa = p1__Pa * critical_pressure_ratio(gamma=UpstreamState.gamma)

        # throat pressure physical limits
        p_th_abs_min__Pa = 0.0
        p_th_abs_max__Pa = p1__Pa
        # throat pressure realistic limits
        p_th_min_i__Pa = p1__Pa * critical_pressure_ratio(gamma=2.0)
        p_th_max_i__Pa = p1__Pa * critical_pressure_ratio(gamma=1 + 1e-5)

        p_th_min__Pa = p_th_min_i__Pa
        p_th_max__Pa = p_th_max_i__Pa

        i = 0
        rel_err = 1
        while rel_err > err_threshold and i < 50:
            # isentropic expansion to throat conditions
            ThroatState = UpstreamState.deepcopy()
            ThroatState.isentropic_property_update("P", p_th__Pa)
            sound_speed__m_s = ThroatState.sound_speed__m_s

            if ThroatState.sound_speed__m_s <= 0.0:
                # TODO consider multiphase and/or critical flow
                warnings.warn("Throat conditions are 2-phase. 2-phase flow hasn't been implemented yet.")
                sound_speed__m_s = np.nan

            h_th_min__J_kg = h1__J_kg - 0.5 * sound_speed__m_s * sound_speed__m_s
            if ThroatState.specific_enthalpy__J_kg < h_th_min__J_kg:
                # throat condition results in velocity that is larger than conservation of energy allows, raise pressure
                p_th_min__Pa = p_th__Pa
            else:
                p_th_max__Pa = p_th__Pa

            p_th__Pa = 0.5 * (p_th_min__Pa + p_th_max__Pa)
            rel_err = rel_error(p_th_min__Pa, p_th_max__Pa)

            if rel_err < 1e-3 or i > 20:
                # if, after 20 iterations, the pressure ratio is still not within 1e-3, widen the range
                if p_th_min__Pa == p_th_min_i__Pa:  # min bound hasn't updated, decrease min bound
                    p_th_min__Pa = 0.5 * (p_th_min__Pa + p_th_abs_min__Pa)
                    p_th_min_i__Pa = p_th_min__Pa
                if p_th_max__Pa == p_th_max_i__Pa:  # max bound hasn't updated, increase max bound
                    p_th_max__Pa = 0.5 * (p_th_max__Pa + p_th_abs_max__Pa)
                    p_th_max_i__Pa = p_th_max__Pa

            mass_flux__kg_m2s = ThroatState.density__kg_m3 * sound_speed__m_s
            i += 1

        self.ThroatState = ThroatState
        if rel_err < err_threshold:
            return mass_flux__kg_m2s
        else:
            raise ValueError(f"Failed to converge on choked mass flux. Residuals = {rel_err:.3e}")

    def calc_mdot(
        self, UpstreamState: FlowState, p2__Pa: float, err_threshold: float = 1e-5, max_iter: int = 50
    ) -> float:
        """Calculate the mass flowrate through the orifice provided an upstream state and downstream pressure.

        Args:
            UpstreamState (FlowState): upstream state. If diameter / area is defined, will treat it as upstream area and solve for upstream total properties.
            p2__Pa (float): downstream pressure [Pa]
            err_threshold (float, optional): allowable error. Defaults to 1e-5.
            max_iter (int, optional): maximum iterations in compressible while loop. Defaults to 50.

        Returns:
            float: mass flowrate [kg/s]
        """
        self._check_area(UpstreamState)
        assert p2__Pa < UpstreamState.pressure__Pa, "Downstream pressure must be less than upstream pressure."
        UStagState = UpstreamState.get_StagnationState(UpstreamState.velocity__m_s)
        ThroatStagState = UStagState.deepcopy()
        ThroatStagState.isentropic_property_update("P", p2__Pa)

        h1__J_kg = UStagState.specific_enthalpy__J_kg
        h2__J_kg = ThroatStagState.specific_enthalpy__J_kg
        if h2__J_kg < h1__J_kg:
            v2__m_s = (2 * (h1__J_kg - h2__J_kg)) ** 0.5

        if hasattr(self, "CdA__m2"):
            if not np.isinf(UpstreamState.area__m2):  # handle case where upstream area is specified
                # update stagnation properties and rerun mdot calc, accounting for non-zero upstream velocity
                i = 0
                rel_err = 1
                tempState = UpstreamState.deepcopy()
                tempState.diameter__m = np.inf
                mdot__kg_s = self.calc_mdot(tempState, p2__Pa)
                while rel_err > err_threshold and i < max_iter:
                    UpstreamGuessState = UpstreamState.deepcopy()
                    UpstreamGuessState.mdot__kg_s = mdot__kg_s
                    UpstreamStagnationState = ThermoState_to_FlowState(
                        UpstreamGuessState.get_StagnationState(UpstreamGuessState.velocity__m_s)
                    )
                    UpstreamStagnationState.diameter__m = np.inf
                    tempOrifice = Orifice(CdA__m2=self.CdA__m2)
                    mdot__kg_s = tempOrifice.calc_mdot(UpstreamStagnationState, p2__Pa)
                    rel_err = rel_error(mdot__kg_s, UpstreamGuessState.mdot__kg_s)
                    i += 1
                if rel_err > err_threshold:
                    raise ValueError(f"Failed to converge on inlet static conditions. Residuals = {rel_err:.3e}")

            elif UStagState.State.phase() in [1, 2, 5, 6]:  # standard gas flow
                if ThroatStagState.is2phase:
                    warnings.warn("Orifice throat state is 2-phase. Using Wood's formula to estimate speed of sound.")
                if h2__J_kg < h1__J_kg:
                    if v2__m_s < ThroatStagState.sound_speed__m_s:  # subsonic flow
                        mdot__kg_s = self.CdA__m2 * ThroatStagState.density__kg_m3 * v2__m_s
                    else:  # sonic flow
                        mdot__kg_s = self.CdA__m2 * self._choked_flux(UStagState, err_threshold)
                else:
                    raise ValueError(
                        f"Downstream enthalpy is greater than upstream. h1 = {h1__J_kg:.2f}, h2 = {h2__J_kg:.2f} [J/kg]"
                    )

            else:
                # UpstreamState.quality <= 0.01:  # handle liquid properties
                if ThroatStagState.isLiquid:  # liquid up and downstream
                    mdot__kg_s = self.CdA__m2 * ThroatStagState.density__kg_m3 * v2__m_s
                else:
                    # TODO handle cavitation
                    pass
        else:
            warnings.warn("CdA not specified. Defaulting to UpstreamState mdot (if defined).")
            mdot__kg_s = UpstreamState.mdot__kg_s
        return mdot__kg_s

    def calc_CdA(self, UpstreamState: FlowState, mdot__kg_s: float, p2__Pa: float):
        """Assuming that the DefinedState is the upstream state, calculate the CdA required to achieve the specified mass flowrate.

        Args:
            UpstreamState (FlowState): upstream state.
            mdot__kg_s (float): mass flowrate [kg/s]
            p2__Pa (float): downstream pressure [Pa]

        Returns:
            float: orifice CdA [m^2]
        """
        normalized_orifice = Orifice(CdA__m2=1.0)
        normalized_mdot__kg_s = normalized_orifice.calc_mdot(UpstreamState, p2__Pa)
        if normalized_mdot__kg_s == 0.0:
            warnings.warn("Could not find CdA. Returning 0. This could be due to multi-phase.")
            self.CdA__m2 = 0.0
        else:
            self.CdA__m2 = mdot__kg_s / normalized_mdot__kg_s
        return self.CdA__m2

    def D_from_CdA(self, Cd: float = 0.82):
        if hasattr(self, "CdA__m2"):
            return D_from_A(self.CdA__m2 / Cd)
        else:
            raise AttributeError("CdA not yet calculated.")

    def calc_upstream_pressure(self, DownstreamState: FlowState, mdot__kg_s: float, max_iter: int = 50):
        """Calculate the upstream pressure required to achieve the specified mass flowrate.

        Args:
            mdot__kg_s (float): mass flowrate [kg/s]
            max_iter (int, optional): maximum number of iterations in while loop. Defaults to 50.

        Returns:
            float: pressure [Pa]
        """
        self._check_area(DownstreamState)
        p_max__Pa = DownstreamState.pressure__Pa / critical_pressure_ratio(gamma=DownstreamState.gamma)
        p_min__Pa = DownstreamState.pressure__Pa
        guessUpstreamState = DownstreamState.deepcopy()
        i = 0
        rel_err = 1
        while rel_err > 1e-5 and i < max_iter:
            p__Pa = 0.5 * (p_min__Pa + p_max__Pa)
            guessUpstreamState.isenthalpic_property_update("P", p__Pa)
            mdot = self.calc_mdot(guessUpstreamState, DownstreamState.pressure__Pa)
            if mdot > mdot__kg_s:
                p_max__Pa = p__Pa
            else:
                p_min__Pa = p__Pa
            rel_err = rel_error(mdot, mdot__kg_s)
            i += 1
        return p__Pa

    def calc_downstream_pressure(self, UpstreamState: FlowState, mdot__kg_s: float, max_iter: int = 50):
        """Calculate the downstream pressure required to achieve the specified mass flowrate.

        Args:
            UpstreamState (FlowState): upstream state.
            mdot__kg_s (float): mass flowrate [kg/s]
            max_iter (int, optional): maximum number of iterations in while loop. Defaults to 50.

        Returns:
            float: pressure [Pa]
        """
        self._check_area(UpstreamState)
        choked_flow__kg_s = self.CdA__m2 * self._choked_flux(UpstreamState)
        if mdot__kg_s >= choked_flow__kg_s:
            crit_p = critical_pressure_ratio(gamma=UpstreamState.gamma) * UpstreamState.pressure__Pa
            raise ValueError(
                f"Specified mass flowrate ({mdot__kg_s:.2f} kg/s) is greater than or equal to the expected choked flow ({choked_flow__kg_s:.2f} kg/s). Pressure downstream of orifice will be {crit_p:.1f} Pa, or less. Use Orifice.calc_upstream_pressure() starting from known downstream pressure to check for unchoking, then solve for new, lower mass flowrate using Orifice.calc_mdot() (iterate to converge on mdot if unchoked)."
            )

        p_max__Pa = UpstreamState.pressure__Pa
        p_min__Pa = 0.0
        guessDownstreamState = UpstreamState.deepcopy()
        i = 0
        rel_err = 1
        while rel_err > 1e-5 and i < max_iter:
            p__Pa = 0.5 * (p_min__Pa + p_max__Pa)
            guessDownstreamState.isenthalpic_property_update("P", p__Pa)
            mdot = self.calc_mdot(UpstreamState, guessDownstreamState.pressure__Pa)
            if mdot > mdot__kg_s:
                p_min__Pa = p__Pa
            else:
                p_max__Pa = p__Pa
            rel_err = rel_error(mdot, mdot__kg_s)
            i += 1
        return p__Pa


def _SeriesOrificeEquivalent(UpstreamState: FlowState, CdA1: float, CdA2: float, p2__Pa: float = 101325) -> float:
    """Calculate the equivalent CdA and mdot for a series of orifices."""
    DownstreamState = UpstreamState.deepcopy()
    DownstreamState.isenthalpic_property_update("P", p2__Pa)
    orifice1 = Orifice(CdA__m2=CdA1)
    orifice2 = Orifice(CdA__m2=CdA2)
    mdot_max = orifice1.calc_mdot(UpstreamState, p2__Pa)
    p_mid_max = orifice2.calc_upstream_pressure(DownstreamState, mdot_max)
    p_mid_min = p2__Pa
    midState = UpstreamState.deepcopy()
    i = 0
    rel_err = 1
    while rel_err > 1e-5 and i < 50:
        p_mid = 0.5 * (p_mid_min + p_mid_max)
        midState.isenthalpic_property_update("P", p_mid)
        orifice2 = Orifice(CdA__m2=CdA2)
        mdot1 = orifice1.calc_mdot(UpstreamState, p_mid)
        mdot2 = orifice2.calc_mdot(midState, p2__Pa)
        if mdot1 < mdot2:
            p_mid_max = p_mid
        else:
            p_mid_min = p_mid
        rel_err = rel_error(mdot1, mdot2)
        i += 1
    if i == 50:
        warnings.warn("Failed to converge on equivalent CdA and mdot.")
    equiv_CdA = Orifice().calc_CdA(UpstreamState, mdot1, p2__Pa)
    return Orifice(CdA__m2=equiv_CdA)


def SeriesOrificeEquivalent(UpstreamState: FlowState, CdAs: List[float], p2__Pa: float = 101325) -> float:
    """Calculate the equivalent CdA and mdot for a series of orifices."""
    if len(CdAs) > 2:
        eOrifice_CdA = CdAs[0]
        for CdA in CdAs[1:]:
            EquivOrifice = _SeriesOrificeEquivalent(UpstreamState, eOrifice_CdA, CdA, p2__Pa)
            eOrifice_CdA = EquivOrifice.CdA__m2
    elif len(CdAs) == 2:
        EquivOrifice = _SeriesOrificeEquivalent(UpstreamState, CdAs[0], CdAs[1], p2__Pa)
    else:
        EquivOrifice = Orifice(CdA__m2=CdAs[0])
    return EquivOrifice


def CdA_from_Cv(Cv: float, isLiquid=True):
    Cv_factor = 38.0 if isLiquid else 27.66
    return convert(Cv / Cv_factor, "in**2", "m**2")


def critical_pressure_ratio(gamma: float) -> float:
    """Isentropic relationship for critical pressure ratio.

    Args:
        gamma (float): specific heat ratio

    Returns:
        float: pressure ratio
    """
    return (2 / (gamma + 1)) ** (gamma / (gamma - 1))


def calc_velocity(mdot__kg_s: float, rho__kg_m3: float, Dh__m: float):
    A__m2 = Circle(D=Dh__m).A
    return mdot__kg_s / rho__kg_m3 / A__m2


def Reynolds(D__m: float, mdot__kg_s: float, p__Pa: float, T__K: float, media: str):
    rho__kg_m3, mu__kg_ms = PropsSI(["D", "MU"], "P", p__Pa, "T", T__K, media)
    v__m_s = calc_velocity(mdot__kg_s, rho__kg_m3, D__m)
    return rho__kg_m3 * v__m_s * D__m / mu__kg_ms


def Dh_rectangular(h__m: float, w__m: float):
    rect = Rectangle(h__m, w__m)
    return 4 * rect.area / rect.perimeter


def scfm_to_kg_s(media: str, scfm: float):
    StdState = StandardState(media)
    if StdState.State.phase() == 0:
        rho_std__kg_m3 = StdState.molar_mass__kg_mol / molar_vol_STP__m3_mol
    else:
        rho_std__kg_m3 = StdState.density__kg_m3
    return convert(scfm, "ft**3/min", "m**3/s") * rho_std__kg_m3


def kg_s_to_scfm(media: str, kg_s: float):
    StdState = StandardState(media)
    if StdState.State.phase() == 0:
        rho_std__kg_m3 = StdState.molar_mass__kg_mol / molar_vol_STP__m3_mol
    else:
        rho_std__kg_m3 = StdState.density__kg_m3
    return convert(kg_s / rho_std__kg_m3, "m**3/s", "ft**3/min")


class MajorLoss:
    def __init__(self, diameter__m: float, abs_roughness__m: float):
        self.diameter__m = diameter__m
        self.abs_roughness__m = abs_roughness__m

    @property
    def rel_rough(self):
        return self.abs_roughness__m / self.diameter__m

    def major_loss_dp(self, k_factor: float, dynamic_pressure__Pa: float) -> float:
        """Calculate the major loss pressure drop."""
        return k_factor * dynamic_pressure__Pa


class ExpanderReducer(MajorLoss):
    """Class for conical expanders and reducers. Reference: Idel'chik, Handbook of Hydraulic Resistance, 4th Ed. Section 5"""

    def __init__(self, D1__m: float, D2__m: float, L__m: float, abs_rough__m: float):
        self.D2__m = D2__m
        self.L__m = L__m
        self.abs_rough__m = abs_rough__m
        super().__init__(D1__m, abs_rough__m)
        self.isConical = True

    @property
    def isReducer(self):
        return self.D2__m < self.diameter__m

    @property
    def AR(self):
        return (self.D2__m * self.D2__m) / (self.diameter__m * self.diameter__m)

    @property
    def alpha__rad(self):
        return 2 * np.arctan(0.5 * abs(self.diameter__m - self.D2__m) / self.L__m)

    def k_fric(self, ff_lambda: float):
        if self.isConical:
            N_ar = self.AR if self.isReducer else 1 / self.AR
            k_fr = ff_lambda / (8 * np.sin(0.5 * self.alpha__rad)) * (1 - N_ar * N_ar)
        else:
            raise ValueError("Only conical expanders/reducers are supported.")
        return k_fr

    def k_factor(self, Re: float):
        if self.isReducer:
            return self._reducer_k_factor(Re)
        else:
            return self._expander_k_factor(Re)

    def _reducer_k_factor(self, Re: float):
        alph = self.alpha__rad
        if Re < 1200 and alph < np.pi / 4:
            return 20.5 / self.AR**0.5 / np.tan(alph) ** 0.75 / Re
        else:
            ff_lambda = darcy_ff(Re, self.rel_rough)
            N_ar = self.AR
            ar_poly = -0.0125 * N_ar**4 + 0.0224 * N_ar**3 - 0.00723 * N_ar * N_ar + 0.00444 * N_ar - 0.00745
            alpha_poly = alph**3 - 2 * np.pi * alph * alph - 10 * alph
            return ar_poly * alpha_poly + self.k_fric(ff_lambda)

    def _expander_k_factor(self, Re: float):
        N_ar = self.AR
        alph = self.alpha__rad
        if Re < 1200 and alph < np.pi / 4:
            return 20 * N_ar**0.33 / np.tan(alph) ** 0.75 / Re
        else:
            ff_lambda = darcy_ff(Re, self.rel_rough)
            ar_term = (1 - 1 / N_ar) ** 2
            return 2.6 * (1 + 0.8 * ff_lambda) * ar_term * np.sin(alph / 2)

    def calc_dp(self, flowState: FlowState):
        """Calculate the pressure drop across the Expander or Reducer."""
        return self.major_loss_dp(self.k_factor(flowState.Reynolds), flowState.dynamic_pressure__Pa)


class Bend(MajorLoss):
    """Class for conical expanders and reducers. Reference: Idel'chik, Handbook of Hydraulic Resistance, 4th Ed. Section 6"""

    def __init__(self, angle__deg: float, bend_radius__m: float, diameter__m: float, abs_rough__m: float):
        self.angle_deg = angle__deg
        self.bend_radius = bend_radius__m
        super().__init__(diameter__m, abs_rough__m)

    @property
    def alpha__rad(self):
        return convert(self.angle_deg, "deg", "rad")

    @property
    def R_D(self):
        R_D = self.bend_radius / self.diameter__m
        assert R_D >= 0.5, "Bend radius must be at least 0.5 times the diameter."
        return R_D

    @property
    def k_factor(self):
        A = (
            0.9 * np.sin(self.alpha__rad)
            if self.angle_deg < 80
            else (1.0 if self.angle_deg < 100 else 0.7 + 0.35 * self.angle_deg / 90)
        )
        B = 0.21 * self.R_D ** (-2.5 if self.R_D < 1.0 else -0.5)
        C = 1.0  # assumes circular or square cross-section
        return A * B * C

    def k_fric(self, Re: float):
        ff_lambda = darcy_ff(Re, self.rel_rough)
        return ff_lambda * self.alpha__rad * self.R_D

    def calc_dp(self, flowState: FlowState):
        """Calculate the pressure drop across the bend."""
        return self.major_loss_dp(self.k_factor + self.k_fric(flowState.Reynolds), flowState.dynamic_pressure__Pa)


# TODO add TEE fittings


class MinorLoss:
    def __init__(self, diameter__m: float, length__m: float, abs_roughness__m: float = 1e-5) -> None:
        self.diameter__m = diameter__m
        self.length__m = length__m
        self.abs_roughness__m = abs_roughness__m
        self.relative_roughness = abs_roughness__m / diameter__m
        self.tube = Cylinder(H=length__m, D=diameter__m)

    def _fanno_1d_integration_step(self, tempUpstreamState: FlowState, dx__m: float, q__W_m2: float, dv__m_s: float):
        media = tempUpstreamState.media
        v1__m_s = tempUpstreamState.velocity__m_s
        surface_area__m2 = self.tube.surface_area
        rel_err = 1
        ix = 0
        while rel_err > 1e-4 and ix < 50:
            ff = darcy_ff(tempUpstreamState.Reynolds, self.relative_roughness)
            fl_d = ff * dx__m / self.diameter__m
            dP__Pa = tempUpstreamState.static_density__kg_m3 * v1__m_s * (0.5 * v1__m_s * fl_d + dv__m_s)
            p2__Pa = tempUpstreamState.static_pressure__Pa - dP__Pa
            v2__m_s = v1__m_s + dv__m_s
            h2__J_kg = (
                tempUpstreamState.static_specific_enthalpy__J_kg
                + 0.5 * v1__m_s * v1__m_s
                - 0.5 * v2__m_s * v2__m_s
                + q__W_m2 * surface_area__m2 / tempUpstreamState.mdot__kg_s
            )
            DownstreamState = FlowState(
                media=media,
                static_pressure__Pa=p2__Pa,
                static_specific_enthalpy__J_kg=h2__J_kg,
                mdot__kg_s=tempUpstreamState.mdot__kg_s,
                diameter__m=self.diameter__m,
            )
            rel_err = rel_error(DownstreamState.velocity__m_s, v2__m_s)
            dv__m_s = DownstreamState.velocity__m_s - v1__m_s
            ix += 1
        if ix == 50:
            warnings.warn("Fanno 1D integration failed to converge on downstream state.")
        return DownstreamState

    def get_equivalent_CdA(self, UpstreamState: ThermoState, mdot__kg_s: float, q__W_m2: float = 0.0) -> float:
        """Calculate the equivalent CdA for a minor loss duct.
        This is useful for speeding up simulations by simplifying the respresnation of flow restriction.
        Only valid for a narrow regime of flow conditions.

        Args:
            UpstreamState (ThermoState): thermodynamic state at the upstream end of the duct.
            mdot__kg_s (float): mass flowrate through the duct
            q__W_m2 (float, optional): heat flux [W/m^2]. Defaults to 0.0.

        Returns:
            float: CdA__m2
        """
        tempUpstreamState = ThermoState_to_FlowState(UpstreamState, mdot__kg_s=mdot__kg_s, diameter__m=self.diameter__m)
        DownstreamState = self.get_downstream_state(tempUpstreamState, mdot__kg_s, q__W_m2, set_state=False)

        tempUpstreamState.diameter__m = np.inf
        CdA__m2 = Orifice().calc_CdA(tempUpstreamState, mdot__kg_s, DownstreamState.pressure__Pa)
        return CdA__m2

    def get_downstream_state(
        self, UpstreamState: ThermoState, mdot__kg_s: float, q__W_m2: float = 0.0, set_state: bool = True
    ) -> FlowState:
        """Given the state upstream and mass flowrate through a duct, calculate the downstream state.

        Args:
            UpstreamState (ThermoState): thermodynamic state at the upstream end of the duct.
            mdot__kg_s (float): mass flowrate through the duct [kg/s]
            q__W_m2 (float, optional): heat flux [W/m^2]. Defaults to 0.0.
            set_state (bool, optional): optionally set UpstreamState property. Defaults to True.

        Returns:
            FlowState: DownstreamState
        """
        tempUpstreamState = ThermoState_to_FlowState(UpstreamState, mdot__kg_s=mdot__kg_s, diameter__m=self.diameter__m)

        dv__m_s = 0.0
        if not tempUpstreamState.isLiquid:  # treat as compressible, integrate over length
            dM_target = 1e-2  # target delta Mach number per integration step, this should capture property convergence
            x__m = 0.0  # intialize at one end of path
            # initial integration step size (very small at high Mach, 10D or L/100 at low Mach)
            dx__m = min(10 * self.diameter__m * (1 - tempUpstreamState.Mach) ** 8, self.length__m / 100)
            while x__m < self.length__m:
                try:
                    DownstreamState = self._fanno_1d_integration_step(tempUpstreamState, dx__m, q__W_m2, dv__m_s)
                    x__m += dx__m
                    dM = abs(DownstreamState.Mach - tempUpstreamState.Mach)
                    tempUpstreamState = DownstreamState
                    if dM > dM_target:
                        dx__m = min(
                            dx__m / 10, self.length__m - x__m
                        )  # integration step was too large, make it smaller
                    elif dM < dM_target / 10:
                        # integration step was too small, make it larger
                        dx__m = min(dx__m * (0.6 * dM_target / dM), self.length__m - x__m)
                except Exception as e:
                    DownstreamState = None
                    warnings.warn(
                        f"Compressible friction loss failed to converge on downstream state. This is usually due to choking. Error: {e}"
                    )
                    break
        else:  # treat as incompressible, calculate dp in single step
            try:
                DownstreamState = self._fanno_1d_integration_step(tempUpstreamState, self.length__m, q__W_m2, dv__m_s)
            except Exception as e:
                DownstreamState = None
                warnings.warn(f"Incompressible friction loss failed to converge on downstream state. Error: {e}")
        if set_state:
            self.DownstreamState = DownstreamState
        return DownstreamState

    def get_upstream_state(
        self,
        DownstreamState: ThermoState,
        mdot__kg_s: float,
        T1__K: float,
        q__W_m2: float = 0.0,
        set_state: bool = True,
        max_iter: int = 50,
    ) -> FlowState:
        """Given the state downstream and mass flowrate through a duct, calculate the upstream state.

        Args:
            DownstreamState (ThermoState): thermodynamic state at the downstream end of the duct.
            mdot__kg_s (float): mass flowrate through the duct [kg/s]
            T1__K (float): static temperature at the upstream end of the duct [K]
            q__W_m2 (float, optional): heat flux [W/m^2]. Defaults to 0.0.
            set_state (bool, optional): optionally set UpstreamState property. Defaults to True.
            max_iter (int, optional): number of iterations. Defaults to 50.

        Returns:
            FlowState: UpstreamState
        """
        # TODO, check for tube choking, increase upstream pressure if necessary
        media = DownstreamState.media
        tempDSState = ThermoState_to_FlowState(DownstreamState, mdot__kg_s=mdot__kg_s, diameter__m=self.diameter__m)

        if tempDSState.isLiquid:
            tempTube = MinorLoss(diameter__m=self.diameter__m, length__m=0.01, abs_roughness__m=self.abs_roughness__m)
            DSState = tempTube.get_downstream_state(tempDSState, mdot__kg_s, q__W_m2, set_state=False)
            dp_L__Pa_m = (tempDSState.pressure__Pa - DSState.pressure__Pa) / tempTube.length__m
            p__Pa = tempDSState.pressure__Pa + dp_L__Pa_m * self.length__m
            UpstreamState = FlowState(
                media=media,
                pressure__Pa=p__Pa,
                temperature__K=T1__K,
                mdot__kg_s=mdot__kg_s,
                diameter__m=self.diameter__m,
            )
        else:
            p_min__Pa = tempDSState.static_pressure__Pa
            p_sat__Pa = tempDSState.p_sat__Pa * (1 - 1e-6) if tempDSState.p_sat__Pa else 0.0
            p_max__Pa = max(10 * p_min__Pa, p_sat__Pa)  # TODO make this arbitrary maximum pressure guess smarter

            rel_err = 1
            i = 0
            while rel_err > 1e-4 and i < max_iter:
                p__Pa = 0.5 * (p_min__Pa + p_max__Pa)
                UpstreamState = FlowState(
                    media=media,
                    static_pressure__Pa=p__Pa,
                    static_temperature__K=T1__K,
                    mdot__kg_s=mdot__kg_s,
                    diameter__m=self.diameter__m,
                )
                DSState = self.get_downstream_state(UpstreamState, mdot__kg_s, q__W_m2, set_state=False)
                if DSState:
                    if DSState.pressure__Pa < tempDSState.pressure__Pa:
                        p_min__Pa = p__Pa
                    else:
                        p_max__Pa = p__Pa
                    rel_err = rel_error(DSState.pressure__Pa, tempDSState.pressure__Pa)
                else:
                    p_min__Pa = p__Pa
                i += 1
            if rel_err > 1e-4:
                warnings.warn("Failed to converge on upstream state.")

        if set_state:
            self.UpstreamState = UpstreamState
        return UpstreamState


def darcy_ff(Re: float, rel_roughness: float) -> float:
    """Darcy friction factor for any flow regime, Bellos, Nalbantis, Tsakiris.
    https://www.researchgate.net/publication/327931915_Friction_Modeling_of_Flood_Flow_Simulations

    Args:
        Re (float): Reynolds number, using hydraulic diameter
        rel_roughness (float): duct relative roughness (i.e. absolute roughness divided by diameter)

    Returns:
        float: Darcy Weisbach friction factor
    """
    A = 1 / (1 + (Re / 2712) ** 8.4)
    B = 1 / (1 + (Re * rel_roughness / 150) ** 1.8)
    ff = (
        (64 / Re) ** A
        * (0.75 * np.log(Re / 5.37)) ** (2 * (A - 1) * B)
        * (0.88 * np.log(3.41 / rel_roughness)) ** (2 * (A - 1) * (1 - B))
    )
    return ff


if __name__ == "__main__":
    x = FlowState("water", pressure__Pa=101325, temperature__K=400)
    # x = SuperHeatedFlow("water", dT_super__K=1, temperature__K=400)
    # y = SuperHeatedFlow("water", dT_super__K=1, temperature__K=400, Mach=0.2)
    # z = SuperHeatedFlow("water", dT_super__K=1, temperature__K=400, velocity__m_s=4)
