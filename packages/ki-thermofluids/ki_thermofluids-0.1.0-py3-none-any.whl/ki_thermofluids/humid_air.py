import warnings
from math import isclose

import numpy as np
from CoolProp.CoolProp import PropsSI
from CoolProp.HumidAirProp import HAPropsSI
from ki_util.geometry import Circle, D_from_A
from ki_util.helpers import rel_error, transpose_dict
from ki_util.units import convert_units as convert
from scipy.optimize import brentq

from ki_thermofluids.flow import FlowState, ThermoState

HA_INTENSIVE_PROPS = {
    "P": "pressure__Pa",
    "Tdb": "temperature_dry_bulb__K",
    "Vha": "specific_volume__m3_kg",
    "Hha": "specific_enthalpy__J_kg",
    "Hda": "specific_enthalpy_dry_air__J_kg",
    "cp": "cp_dry_air__J_kgK",
    "cp_ha": "cp__J_kgK",
    "CV": "cv_dry_air__J_kgK",
    "cv_ha": "cv__J_kgK",
    "k": "thermal_conductivity__W_mK",
    "mu": "viscosity__kg_ms",
    "Sda": "specific_entropy_dry_air__J_kgK",
    "Sha": "specific_entropy__J_kgK",
}
HA_MIXTURE_PROPS = {
    "HumRat": "humidity_ratio",
    "RH": "relative_humidity",
    "P_w": "partial_pressure_water__Pa",
    "Twb": "temperature_wet_bulb__K",
    "Tdp": "temperature_dew_point__K",
}
FLOW_PROPS = ["mdot__kg_s", "vdot__m3_s", "diameter__m", "area__m2"]


class HumidAirState:
    MW_ratio = 18.0153 / 28.96

    def __init__(self, **props: float) -> None:
        f"""Humid air thermodynamic state. 
        Valid inputs: {HA_INTENSIVE_PROPS.values()} and {HA_MIXTURE_PROPS.values()}.
        """
        # separate inputs into intensive properties and mixture properties
        intensive_props = {k: v for k, v in props.items() if k in HA_INTENSIVE_PROPS.values() and v is not None}
        mixture_props = {k: v for k, v in props.items() if k in HA_MIXTURE_PROPS.values() and v is not None}

        if len(intensive_props.keys()) != 2:
            raise KeyError("Thermodynamic state is poorly defined. Must specify exactly 2 intensive properties.")
        if len(mixture_props.keys()) != 1:
            raise KeyError("Thermodynamic state is poorly defined. Must specify 1 mixture property.")
        self.properties = props

        self.CP_PROPS = transpose_dict({**HA_INTENSIVE_PROPS, **HA_MIXTURE_PROPS})
        for key, val in self.CP_PROPS.items():
            # initialize all intensive properties as attributes
            setattr(self, key, None)

        in_props = {}
        for key, val in self.properties.items():
            setattr(self, key, val)
            if key in self.CP_PROPS.keys():
                # track which intensive properties were input
                in_props[self.CP_PROPS[key]] = val

        prop1 = list(in_props.items())[0]
        prop2 = list(in_props.items())[1]
        prop3 = list(in_props.items())[2]

        self.update_properties(prop1[0], prop1[1], prop2[0], prop2[1], prop3[0], prop3[1])

    @property
    def density__kg_m3(self):
        return 1 / self.specific_volume__m3_kg

    @property
    def p_sat__Pa(self):
        return self.partial_pressure_water__Pa / self.relative_humidity

    @property
    def dT_sat_margin__K(self):
        return self.temperature_dry_bulb__K - self.temperature_dew_point__K

    @property
    def molar_ratio(self):
        return self.humidity_ratio / (self.MW_ratio + self.humidity_ratio)

    def update_properties(self, prop1_type, prop1, prop2_type, prop2, prop3_type, prop3):
        for key, cp_key in self.CP_PROPS.items():
            val = HAPropsSI(cp_key, prop1_type, prop1, prop2_type, prop2, prop3_type, prop3)
            setattr(self, key, val)
        self.specific_enthalpy_dew_point__J_kg = HAPropsSI(
            "Hha", "Tdb", self.temperature_dew_point__K, "P", self.pressure__Pa, "RH", 1.0
        )
        try:
            self.humidity_ratio_max = HAPropsSI(
                "HumRat", "Tdb", self.temperature_dry_bulb__K, "P", self.pressure__Pa, "RH", 1.0
            )
        except ValueError:
            warnings.warn("Humidity ratio exceeds 10 [kg/kg]. Consider treating this as steam.")
            self.humidity_ratio_max = None

    def heat_transfer(self, prop_type: str, prop: float, dp__Pa: float = 0.0):
        """Target a dry bulb temperature or specific enthalpy by adding or removing heat from humid air.
        If target is above dew point, no condensation occurs. Otherwise, first cool to 100% relative humidity,
        then dehumidify to target temperature with 100% relative humidity.

        Args:
            prop_type (str): Input property type ('Tdb' or 'Hha')
            prop (float): Input property value [K or J/kg]
            dp__Pa (float, optional): Pressure drop. Defaults to 0.0.
        """
        # TODO check which is more conservative, dP in dry or wet portion
        if prop_type == "Tdb":
            T_dew__K = self.temperature_dew_point__K
            if prop < T_dew__K or isclose(prop, T_dew__K, rel_tol=1e-5):
                self.wet_heat_transfer(prop_type, prop, dp__Pa)
            else:
                self.dry_heat_transfer(prop_type, prop, dp__Pa)
        elif prop_type == "Hha":
            h_dew__J_kg = self.specific_enthalpy_dew_point__J_kg
            if prop < h_dew__J_kg or isclose(prop, h_dew__J_kg, rel_tol=1e-5):
                self.wet_heat_transfer(prop_type, prop, dp__Pa)
            else:
                self.dry_heat_transfer(prop_type, prop, dp__Pa)
        else:
            raise ValueError("Invalid property type. Must be 'Tdb' or 'Hha'")

    def wet_heat_transfer(self, prop_type: str, prop: float, dp__Pa: float = 0.0):
        """Target a dry bulb temperature or specific enthalpy by adding or removing heat from humid air, maintaining constant relative humidity (with condensation).

        Args:
            prop_type (str): Input property type ('Tdb' or 'Hha')
            prop (float): Input property value [K or J/kg]
            dp__Pa (float, optional): Pressure drop. Defaults to 0.0.
        """
        assert prop_type in ["Tdb", "Hha"], "Invalid property type. Must be 'Tdb' or 'Hha'."

        if prop_type == "Tdb":
            if prop > self.temperature_dew_point__K:
                warnings.warn("Target temperature is above the dew point. Asserting RH=1.0.")
            self._wet_heat_transfer_to_temperature(prop, dp__Pa)
        elif prop_type == "Hha":
            if prop > self.specific_enthalpy_dew_point__J_kg:
                warnings.warn("Target specific enthalpy is above the dew point. Asserting RH=1.0.")
            self._wet_heat_transfer_to_enthalpy(prop, dp__Pa)
        else:
            raise ValueError("Invalid property type. Must be 'Tdb' or 'Hha'")

    def dry_heat_transfer(self, prop_type: str, prop: float, dp__Pa: float = 0.0):
        """Target a dry bulb temperature or enthalpy by adding or removing heat from humid air, maintaining constant absolute humidity (no condensation).

        Args:
            prop_type (str): Input property type ('Tdb' or 'Hha')
            prop (float): Input property value [K or J/kg]
            dp__Pa (float, optional): Pressure drop. Defaults to 0.0.
        """
        assert prop_type in ["Tdb", "Hha"], "Invalid property type. Must be 'Tdb' or 'Hha'."

        if prop_type == "Tdb":
            T_dew__K = self.temperature_dew_point__K
            if prop <= T_dew__K:
                warnings.warn("Target temperature is below dew point. Asserting RH=1.0.")
            self._dry_heat_transfer_to_temperature(max(prop, T_dew__K + 1e-6), dp__Pa)
        elif prop_type == "Hha":
            h_dew__J_kg = self.specific_enthalpy_dew_point__J_kg
            if prop <= h_dew__J_kg:
                warnings.warn("Target specific enthalpy is below dew point. Asserting RH=1.0.")
            self._dry_heat_transfer_to_enthalpy(max(prop, h_dew__J_kg + 1e-6), dp__Pa)
        else:
            raise ValueError("Invalid property type. Must be 'Tdb' or 'Hha'")

    def _wet_heat_transfer_to_enthalpy(self, specific_enthalpy__J_kg: float, dp__Pa: float = 0.0):
        """Maintaining constant relative humidity (with condensation), update state to new specific enthalpy."""
        p2__Pa = self.pressure__Pa - dp__Pa
        self.update_properties("Hha", specific_enthalpy__J_kg, "P", p2__Pa, "RH", 1.0)

    def _wet_heat_transfer_to_temperature(self, temperature__K: float, dp__Pa: float = 0.0):
        """Maintaining constant relative humidity (with condensation), update state to new temperature."""
        p2__Pa = self.pressure__Pa - dp__Pa
        self.update_properties("Tdb", temperature__K, "P", p2__Pa, "RH", 1.0)

    def _dry_heat_transfer_to_enthalpy(self, specific_enthalpy__J_kg: float, dp__Pa: float = 0.0):
        """Maintaining constant absolute humidity (no condensation), update state to new specific enthalpy."""
        p2__Pa = self.pressure__Pa - dp__Pa
        self.update_properties("Hha", specific_enthalpy__J_kg, "P", p2__Pa, "HumRat", self.humidity_ratio)

    def _dry_heat_transfer_to_temperature(self, temperature__K: float, dp__Pa: float = 0.0):
        """Maintaining constant absolute humidity (no condensation), update state to new temperature."""
        p2__Pa = self.pressure__Pa - dp__Pa
        self.update_properties("Tdb", temperature__K, "P", p2__Pa, "HumRat", self.humidity_ratio)

    def humidify(self, prop_type: str, prop: float, dp__Pa: float = 0.0, withSteam: bool = True):
        """Update state to new relative or absolute humidity by adding saturated steam or water.

        If humidifying with steam, the process is isothermal. Enthalpy increases because the steam will have a higher enthalpy than the humid air.
        If humidifying with water, the process is isenthalpic because the water enthalpy and mdot is negligible relative to the humid air and energy is conserved.

        Args:
            prop_type (str): input property type ('RH' or 'HumRat')
            prop (float): property value
            dp__Pa (float, optional): pressure change. Defaults to 0.0.
            withSteam (bool, optional): add steam or water. Defaults to True (steam).
        """

        if prop_type == "RH":
            self._humidify_to_relative_humidity(prop, dp__Pa, withSteam)
        elif prop_type == "HumRat":
            self._humidify_to_humidity_ratio(prop, dp__Pa, withSteam)
        elif prop_type == "Tdb":
            if dp__Pa != 0:
                warnings.warn(
                    "You're specifying a change in pressure and a drybulb temperature. \
                        The assumption that temprature will decrease may not be true. Results may be INVALID."
                )
            self._humidify_to_temperature(prop, dp__Pa, withSteam)
        else:
            raise ValueError("Invalid property type. Must be 'RH' or 'HumRat'")

    def _humidify_to_relative_humidity(self, relative_humidity: float, dp__Pa: float, withSteam: bool):
        """Update state to new relative humidity."""
        assert relative_humidity >= self.relative_humidity, "This function does not dehumidify humid air."
        assert relative_humidity <= 1.0, "Relative humidity must be between 0 and 1."
        prop_type = "Tdb" if withSteam else "Hha"
        prop = self.temperature_dry_bulb__K if withSteam else self.specific_enthalpy__J_kg
        p2__Pa = self.pressure__Pa - dp__Pa
        self.update_properties("RH", relative_humidity, "P", p2__Pa, prop_type, prop)

    def _humidify_to_humidity_ratio(self, humidity_ratio: float, dp__Pa: float, withSteam: bool):
        """Update state to new humidity raio."""
        assert humidity_ratio >= self.humidity_ratio, "This function does not dehumidify humid air."
        p2__Pa = self.pressure__Pa - dp__Pa
        hum_rat_max = HAPropsSI("HumRat", "RH", 1.0, "Tdb", self.temperature_dry_bulb__K, "P", p2__Pa)
        if humidity_ratio > hum_rat_max:
            warnings.warn(f"HumRat exceeds maximum value ({hum_rat_max:.2f}) for given T and P. Asserting RH=1.0.")
            humidity_ratio = hum_rat_max * (1 - 1e-6)
        prop_type = "Tdb" if withSteam else "Hha"
        prop = self.temperature_dry_bulb__K if withSteam else self.specific_enthalpy__J_kg
        self.update_properties("HumRat", humidity_ratio, "P", p2__Pa, prop_type, prop)

    def _humidify_to_temperature(self, temperature__K: float, dp__Pa: float, withSteam: bool, max_iter: int = 50):
        """Update state to new temperature by adding humidity."""
        p2__Pa = self.pressure__Pa - dp__Pa
        if temperature__K >= self.temperature_dry_bulb__K:
            warnings.warn("Post-humidification temperature must be less than current temperature. Doing nothing.")
        elif temperature__K < self.temperature_dew_point__K:
            warnings.warn(
                f"Target humidification temperature is below dew point {self.temperature_dew_point__K:.2f}. Asserting RH=1.0."
            )
            self.update_properties("Tdb", self.temperature_dew_point__K, "RH", 1.0, "P", p2__Pa)
        else:
            relhum_max = 1.0
            relhum_min = self.humidity_ratio
            iter = 0
            while relhum_max - relhum_min > 1e-5 and iter < max_iter:
                relhum = (relhum_max + relhum_min) / 2
                self._humidify_to_relative_humidity(relhum, dp__Pa, withSteam)
                if self.temperature_dry_bulb__K < temperature__K:
                    relhum_max = relhum
                else:
                    relhum_min = relhum
                iter += 1
            if iter == max_iter:
                warnings.warn("Max iteration reached. Humidification may not have converged.")

    def deepcopy(self):
        return HumidAirState(
            temperature_dry_bulb__K=self.temperature_dry_bulb__K,
            pressure__Pa=self.pressure__Pa,
            relative_humidity=self.relative_humidity,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(P: {self.pressure__Pa:.0f} Pa, T_db: {self.temperature_dry_bulb__K:.2f} K, T_wb: {self.temperature_wet_bulb__K:.2f} K, HumRat: {self.humidity_ratio:.2f}, RH: {self.relative_humidity:.2f}, Hha: {self.specific_enthalpy__J_kg:.0f} J/kg)"


class IdealHumidAirState:
    MW_ratio = 18.0153 / 28.96

    def __init__(self, temperature_dry_bulb__K: float, pressure__Pa: float, humidity_ratio: float) -> None:
        """Humid air properties at a given temperature, pressure, and humidity ratio.
        Useful for calculating properties outside of the range of validity of CoolProp (e.g. elevated temperature, high humidity)."""
        self.pressure__Pa = pressure__Pa
        self._T__K = temperature_dry_bulb__K
        self._hum_rat = humidity_ratio

    def air_lookup(self, property_name: str):
        return PropsSI(property_name, "T|gas", self.temperature_dry_bulb__K, "P", self.partial_pressure_air__Pa, "air")

    def vapor_lookup(self, property_name: str):
        return PropsSI(
            property_name, "T|gas", self.temperature_dry_bulb__K, "P", self.partial_pressure_water__Pa, "water"
        )

    @property
    def temperature_dry_bulb__K(self):
        return self._T__K

    @temperature_dry_bulb__K.setter
    def temperature_dry_bulb__K(self, new_T):
        self._T__K = new_T

    @property
    def humidity_ratio(self):
        return self._T__K

    @humidity_ratio.setter
    def humidity_ratio(self, new_hum_rat):
        self._hum_rat = new_hum_rat

    @property
    def molar_ratio(self):
        return self.humidity_ratio / (self.MW_ratio + self.humidity_ratio)

    @property
    def partial_pressure_water__Pa(self):
        return self.pressure__Pa * self.molar_ratio

    @property
    def partial_pressure_air__Pa(self):
        return self.pressure__Pa - self.partial_pressure_water__Pa

    @property
    def mole_fraction_water(self):
        return self.partial_pressure_water__Pa / self.pressure__Pa

    @property
    def relative_humidity(self):
        return self.partial_pressure_water__Pa / self.p_sat__Pa

    @property
    def p_sat__Pa(self):  # only valid at ambient pressure
        Tp_pairs__degC_Pa = [
            [-50, 4.0],
            [-20, 104],
            [-10, 260],
            [0, 610],
            [5, 868],
            [10, 1190],
            [15, 1690],
            [20, 2330],
            [25, 3170],
            [30, 4240],
            [37, 6310],
            [40, 7340],
            [50, 12300],
            [60, 19900],
            [70, 31200],
            [80, 47300],
            [90, 70100],
            [95, 85900],
            [100, 101000],
            [120, 199000],
            [150, 476000],
            [200, 1.55e6],
            [220, 2.32e6],
        ]
        temp__degC, p_vap__Pa = zip(*Tp_pairs__degC_Pa)
        return np.interp(self.temperature_dry_bulb__K, convert(temp__degC, "degC", "K"), p_vap__Pa)

    @property
    def vaporState(self):
        return ThermoState("water", temperature__K=self._T__K, pressure__Pa=self.partial_pressure_water__Pa)

    @property
    def airState(self):
        return ThermoState("air", temperature__K=self._T__K, pressure__Pa=self.partial_pressure_air__Pa)

    @property
    def pct_air(self):
        return 1 / (1 + self.humidity_ratio)

    @property
    def pct_vapor(self):
        return self.humidity_ratio / (1 + self.humidity_ratio)

    @property
    def specific_enthalpy__J_kg(self):
        return self.pct_air * self.air_lookup("H") + self.pct_vapor * self.vapor_lookup("H")

    @property
    def cp__J_kgK(self):
        return self.pct_air * self.air_lookup("C") + self.pct_vapor * self.vapor_lookup("C")

    @property
    def density__kg_m3(self):
        return self.pct_air * self.air_lookup("D") + self.pct_vapor * self.vapor_lookup("D")


class HumidAirFlowState(HumidAirState):
    def __init__(self, **props: float) -> None:
        self._mdot = props.get("mdot__kg_s", None)
        _vdot = props.get("vdot__m3_s", None)
        self._D__m = props.get("diameter__m", None)
        _area = props.get("area__m2", None)

        _ = [props.pop(key) for key in FLOW_PROPS if key in props.keys()]
        super().__init__(**props)

        if self._mdot is not None and _vdot is not None:
            raise ValueError("Cannot specify both mass flow rate and volumetric flow rate.")

        if self._D__m is not None and _area is not None:
            raise ValueError("Cannot specify both diameter and area.")

        if _vdot is not None:
            self._mdot = _vdot * self.density__kg_m3
        elif self._mdot is None:
            self._mdot = 0.0

        if _area is not None:
            self._D__m = D_from_A(_area)
        elif self._D__m is None:
            self._D__m = np.inf

        self.mdot_condensed__kg_s = 0
        self.mdot_air__kg_s = self._mdot / (1 + self.humidity_ratio)
        self.isCondensing = self.temperature_dry_bulb__K < self.temperature_dew_point__K

    @property
    def mdot__kg_s(self):
        return self._mdot

    @mdot__kg_s.setter
    def mdot__kg_s(self, new_mdot):
        self._mdot = new_mdot
        self.mdot_air__kg_s = self._mdot / (1 + self.humidity_ratio)

    @property
    def diameter__m(self):
        return self._D__m

    @diameter__m.setter
    def diameter__m(self, new_D):
        self._D__m = new_D

    @property
    def area__m2(self):
        return Circle(D=self.diameter__m).area

    @property
    def vdot__m3_s(self):
        return self.mdot__kg_s / self.density__kg_m3

    @property
    def velocity__m_s(self):
        return self.vdot__m3_s / self.area__m2

    @property
    def enthalpy_flowrate__J_s(self):
        return self.mdot__kg_s * self.specific_enthalpy__J_kg

    @property
    def mdot_water__kg_s(self):
        return self.mdot__kg_s - self.mdot_air__kg_s

    @mdot_water__kg_s.setter
    def mdot_water__kg_s(self, new_mdot_water):
        self._mdot = new_mdot_water + self.mdot_air__kg_s

    @property
    def airState(self):
        return FlowState(
            media="air",
            pressure__Pa=self.partial_pressure_air__Pa,
            temperature__K=self.temperature_dry_bulb__K,
            mdot__kg_s=self.mdot_air__kg_s,
        )

    @property
    def waterState(self):
        return FlowState(
            media="water",
            pressure__Pa=self.partial_pressure_water__Pa,
            temperature__K=self.temperature_dry_bulb__K,
            mdot__kg_s=self.mdot_water__kg_s,
        )

    @property
    def condensateState(self):
        return FlowState(
            media="water",
            pressure__Pa=self.pressure__Pa,
            temperature__K=self.temperature_dry_bulb__K,
            mdot__kg_s=self.mdot_condensed__kg_s,
        )

    def update_condensate(self, T2__K: float):
        """If the humid air is condensing, update the condensate and humid air flowrates."""
        hum_rat2 = HAPropsSI("HumRat", "Tdb", T2__K, "P", self.pressure__Pa, "RH", 1.0)
        mdot_W_final__kg_s = self.mdot_air__kg_s * hum_rat2
        dm_condensed__kg_s = self.mdot_water__kg_s - mdot_W_final__kg_s
        self.mdot_condensed__kg_s += dm_condensed__kg_s
        self.mdot_water__kg_s = mdot_W_final__kg_s

    def available_heat(self, T2__K: float):
        """Cool at constant pressure down to final temperature. Return amount of heat removed in the process."""
        # TODO maybe try the real humid air state, using dew point temperature
        if T2__K < self.temperature_dew_point__K:
            dQ_sensible__J_s = self.available_heat(self.temperature_dew_point__K)
            T1__K = self.temperature_dew_point__K
            hum_rat2 = HAPropsSI("HumRat", "Tdb", T2__K, "P", self.pressure__Pa, "RH", 1.0)
            pp1_h2o__Pa = HAPropsSI("P_w", "Tdb", T1__K, "P", self.pressure__Pa, "RH", 1.0)
            pp2_h2o__Pa = HAPropsSI("P_w", "Tdb", T2__K, "P", self.pressure__Pa, "RH", 1.0)
        else:
            dQ_sensible__J_s = 0
            T1__K = self.temperature_dry_bulb__K
            hum_rat2 = self.humidity_ratio
            pp1_h2o__Pa = self.partial_pressure_water__Pa
            pp2_h2o__Pa = HAPropsSI("P_w", "Tdb", T2__K, "P", self.pressure__Pa, "HumRat", hum_rat2)

        mdot_W_final__kg_s = self.mdot_air__kg_s * hum_rat2
        dm_condensed__kg_s = self.mdot_water__kg_s - mdot_W_final__kg_s

        pp1_air__Pa = self.pressure__Pa - pp1_h2o__Pa
        pp2_air__Pa = self.pressure__Pa - pp2_h2o__Pa

        # air sensible heat
        h1_air__J_kg = PropsSI("H", "T|gas", T1__K, "P", pp1_air__Pa, "air")
        h2_air__J_kg = PropsSI("H", "T|gas", T2__K, "P", pp2_air__Pa, "air")
        dQ_A__J_s = self.mdot_air__kg_s * (h1_air__J_kg - h2_air__J_kg)

        # water sensible heat
        h1_water__J_kg = PropsSI("H", "T|gas", T1__K, "P", pp1_h2o__Pa, "water")
        h2_water__J_kg = PropsSI("H", "T|gas", T2__K, "P", pp2_h2o__Pa, "water")
        dQ_W__J_s = mdot_W_final__kg_s * (h1_water__J_kg - h2_water__J_kg)

        # liquid water sensible heat
        h1_cond__J_kg = PropsSI("H", "T|liquid", T1__K, "P", self.pressure__Pa, "water")
        h2_cond__J_kg = PropsSI("H", "T|liquid", T2__K, "P", self.pressure__Pa, "water")
        dQ_Wliq__J_s = self.mdot_condensed__kg_s * (h1_cond__J_kg - h2_cond__J_kg)

        # water latent heat of condensation
        dQ_condensed__J_s = dm_condensed__kg_s * (h1_water__J_kg - h2_cond__J_kg)

        return dQ_sensible__J_s + dQ_W__J_s + dQ_A__J_s + dQ_Wliq__J_s + dQ_condensed__J_s

    def remove_heat_cp(self, dQ__W: float):
        """Remove heat from humid air at constant pressure.
        This method tries to root solve final temperature matching the change in enthalpy to the heat removed.
        """
        if dQ__W <= 0:
            raise ValueError("dQ__W should be a positive number indicating heat removed.")

        # we need to figure out a workaround for condensed mass, because humidity ratio at high temperature breaks in CoolProp
        # dm_max = dQ__W / self.condensateState.hvap__J_kg
        # dm_min = 0.0
        # dm_guess = (dm_max + dm_min) / 2
        # hum_rat_guess = (self.mdot_water__kg_s - dm_guess) / self.mdot_air__kg_s

        def dH__W(T_guess__K: float):
            return self.available_heat(T_guess__K) - dQ__W

        T_min_guess__K = self.temperature_dew_point__K - dQ__W / self.available_heat(self.temperature_dry_bulb__K - 1)

        T_final__K = brentq(dH__W, T_min_guess__K, self.temperature_dry_bulb__K + 1, rtol=1e-4)

        if not self.isCondensing and T_final__K < self.temperature_dew_point__K:
            # toggle once
            self.isCondensing = True

        self.heat_transfer("Tdb", T_final__K, dp__Pa=0)

        if self.isCondensing:
            self.update_condensate(T_final__K)

    def _remove_heat_constP(self, dQ__W: float):
        """Remove heat from humid air.
        This method tries to use conservation of energy to find the final specific enthalpy of the humid air.
        Energy conservation apparently fails though"""
        raise NotImplementedError(
            "This method is not implemented. Use remove_heat_cp() instead for constant pressure heat removal."
        )
        if dQ__W <= 0:
            raise ValueError("dQ__W should be a positive number indicating heat removed.")

        starting_mdot__kg_s = self.mdot__kg_s + self.mdot_condensed__kg_s

        starting_enthalpy_flow__J_s = self.enthalpy_flowrate__J_s

        final_enthalpy_flow__J_s = starting_enthalpy_flow__J_s - dQ__W
        new_specific_enthalpy__J_kg = final_enthalpy_flow__J_s / (self.mdot__kg_s + self.mdot_condensed__kg_s)

        if not self.isCondensing and (new_specific_enthalpy__J_kg < self.specific_enthalpy_dew_point__J_kg):
            # cool to dew point (only happens once in the cycle)
            self._dry_heat_transfer_to_enthalpy(self.specific_enthalpy_dew_point__J_kg, dp__Pa=0.0)
            # calculate how much heat still needs to be removed
            assert self.mdot_condensed__kg_s == 0, "Condensation should not have occurred yet."
            dQ_to_dew__W = starting_total_enthalpy_flow__J_s - self.enthalpy_flowrate__J_s
            dQ__W = dQ__W - dQ_to_dew__W
            # now we are at dew point, so we can condense
            self.isCondensing = True

        if self.isCondensing:
            # dehumidify to target enthalpy
            new_enthalpy_flow__J_s = self.enthalpy_flowrate__J_s - dQ__W
            specific_enthalpy_max__J_kg = self.specific_enthalpy__J_kg
            specific_enthalpy_min__J_kg = new_enthalpy_flow__J_s / self.mdot__kg_s

            r_err = 1
            ix = 0
            while r_err > 1e-7 and ix < 50:
                h_guess__J_kg = (specific_enthalpy_max__J_kg + specific_enthalpy_min__J_kg) / 2

                humidity_ratio = HAPropsSI("HumRat", "Hha", h_guess__J_kg, "P", self.pressure__Pa, "RH", 1.0)
                T_db__K = HAPropsSI("Tdb", "Hha", h_guess__J_kg, "P", self.pressure__Pa, "RH", 1.0)
                # new condensate
                dm_condensed__kg_s = self.mdot_water__kg_s - (self.mdot_air__kg_s * humidity_ratio)
                # humid air enthalpy flow
                h_flow_ha__J_s = h_guess__J_kg * (self.mdot__kg_s - dm_condensed__kg_s)
                # condensate enthalpy flow
                h_c__J_kg = PropsSI("H", "T", T_db__K, "P", self.pressure__Pa, "water")
                h_cflow__J_s = h_c__J_kg * (self.mdot_condensed__kg_s + dm_condensed__kg_s)

                dH_condensed__J_s = dm_condensed__kg_s * self.condensateState.hvap__J_kg

                enthalpy_flow__J_s = h_flow_ha__J_s + h_cflow__J_s  # - dH_condensed__J_s

                if enthalpy_flow__J_s < new_enthalpy_flow__J_s:
                    specific_enthalpy_min__J_kg = h_guess__J_kg
                else:
                    specific_enthalpy_max__J_kg = h_guess__J_kg

                r_err = rel_error(enthalpy_flow__J_s, new_enthalpy_flow__J_s)
                ix += 1

            self.update_properties("Hha", h_guess__J_kg, "P", self.pressure__Pa, "RH", 1.0)
            self.mdot_condensed__kg_s += dm_condensed__kg_s
            self.mdot_water__kg_s -= dm_condensed__kg_s
            final_mdot__kg_s = self.mdot_water__kg_s + self.mdot_air__kg_s + self.mdot_condensed__kg_s
            total_enthalpy_flow__J_s = self.enthalpy_flowrate__J_s + self.condensateState.enthalpy_flowrate__J_s
            assert isclose(
                final_mdot__kg_s,
                starting_mdot__kg_s,
                rel_tol=1e-7,
            ), "Mass balance error"
            assert isclose(
                self.enthalpy_flowrate__J_s,
                final_enthalpy_flow__J_s,
                rel_tol=1e-7,
            ), "Energy balance error"
        else:
            # cool to target enthalpy
            self._dry_heat_transfer_to_enthalpy(new_specific_enthalpy__J_kg, dp__Pa=0.0)

    def deepcopy(self):
        return HumidAirFlowState(
            temperature_dry_bulb__K=self.temperature_dry_bulb__K,
            pressure__Pa=self.pressure__Pa,
            relative_humidity=self.relative_humidity,
            mdot__kg_s=self._mdot,
            diameter__m=self._D__m,
        )

    def __repr__(self) -> str:
        hflow_str = f", {self.enthalpy_flowrate__J_s:.0f} J/s" if self.enthalpy_flowrate__J_s else ", nan J/s"
        mdot_str = f", {self.mdot__kg_s:.2f} kg/s" if self.mdot__kg_s else ", nan kg/s"
        diam_str = f", {self.diameter__m:.2f} m" if self.diameter__m else ", inf m"
        return super().__repr__()[:-1] + hflow_str + mdot_str + diam_str + ")"


if __name__ == "__main__":
    pass
