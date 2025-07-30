from CoolProp import CoolProp as CP


class Mixture:
    def __init__(self, **components) -> None:
        """Initialize a Mixture object with component names and their fractions.

        Args:
        **components: Arbitrary number of keyword arguments, where the key is the component name
        and the value is the molar fraction of that component in the mixture.
        """

        self.components = components
        self._check_valid_fraction()
        self._check_valid_fluids()

    @property
    def species_list(self):
        return list(self.components.keys())

    @property
    def mass_fraction_list(self):
        return list(self.components.values())

    @property
    def coolprop_string(self):  # TODO figure out why this isn't working with PropsSI()
        cp_str = ""
        for fluid, pct in self.components.items():
            if cp_str != "":
                cp_str += "&"
            cp_str += f"{fluid.capitalize()}[{pct:.5f}]"
        return cp_str

    @property
    def CP_AS_str(self):
        cp_str = ""
        for fluid in self.species_list:
            if cp_str != "":
                cp_str += "&"
            cp_str += f"{fluid.capitalize()}"
        return cp_str

    def CP_AbstractState(self, isGas: bool = True):
        CPState = CP.AbstractState("HEOS", self.CP_AS_str)
        CPState.set_mass_fractions(self.mass_fraction_list)
        if isGas:
            CPState.specify_phase(CP.iphase_gas)
        return CPState

    @staticmethod
    def _check_valid_fluid(fluid_name):
        try:
            CP.PropsSI("T", "P", 101325, "Q", 0, fluid_name)
            return True
        except ValueError:
            return False

    def _check_valid_fluids(self):
        for fluid_name in self.species_list:
            self._check_valid_fluid(fluid_name)

    def _check_valid_fraction(self):
        total_fraction = sum(self.mass_fraction_list)
        if not (0.99 <= total_fraction <= 1.01):
            raise ValueError(f"The sum of the fractional components ({total_fraction:.3f}) must be approximately 1.")

    def get_species_fraction(self, species_name: str) -> float:
        """Get the fraction of a specific species.

        Args:
            species_name (sr): The name of the species.

        Returns:
            float: The fraction of the species, or None if the species is not in the mixture.
        """
        return self.components.get(species_name, None)

    def _update_fractions(self, total_frac: float = 1.0):
        for species, pct in self.components.items():
            self.components[species] = pct * total_frac

    def add_component(self, species_name: str, fraction: float):
        """Add a species to the Mixture. The other components maintain the same relative molar ratios as before.

        Args:
            species_name (str): The name of the added species.
            fraction (float): The fraction of the species to add.
                e.g. 0.5 increases the molar fraction of the added species by 50%, so if starting with 50%, the end result would be 75%.

        Raises:
            ValueError if the total fraction exceeds 1.
        """
        # If adding an existing species, store the starting fraction.
        old_fraction = self.components[species_name] if species_name in self.species_list else 0.0
        # Update other species fractions
        self._update_fractions(1 - fraction)
        self.components[species_name] = fraction + old_fraction * (1 - fraction)

        self._check_valid_fraction()
        self._check_valid_fluid(species_name)

    def remove_component(self, species_name: str, fraction: float = 1.0):
        """Remove a species from the mixture.

        Args:
            species_name (str): The name of the removed species.
            fraction (float, optional): The fraction of the existing component to remove. Defaults to 1.0.
                e.g. 0.5 removes 50% of the existing species, 1.0 removes all.
        """
        if species_name in self.species_list:
            old_fraction = self.components[species_name]
            new_total = 1 - fraction * old_fraction
            self.components[species_name] = (1 - fraction) * old_fraction
            self._update_fractions(1 / new_total)
            self._check_valid_fraction()

            if self.components[species_name] == 0.0:
                del self.components[species_name]
        else:
            raise KeyError(f"Component '{species_name}' not found in the Mixture.")

    def __str__(self):
        return self.coolprop_string


if __name__ == "__main__":
    test_mixture = Mixture(helium=0.5, nitrogen=0.5)
    print(test_mixture.coolprop_string)
    test_mixture.add_component("helium", 0.99)
    print(test_mixture.coolprop_string)
    test_mixture.add_component("argon", 0.25)
    print(test_mixture.coolprop_string)
    test_mixture.remove_component("helium", 0.5)
    print(test_mixture.coolprop_string)
