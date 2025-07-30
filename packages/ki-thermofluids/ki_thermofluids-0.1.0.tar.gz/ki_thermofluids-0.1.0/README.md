
# Karman Industries - Thermofluids

### Variable naming conventions
#### Variables
| Common Variables | Default Units | Discription                |
|------------------|---------------|----------------------------|
| P                | W             | Power                      |
| p                | Pa            | Pressure                   |
| T                | K             | Temperature                |
| h                | J/kg          | Specific Enthalpy          |
| s                | J/kgK         | Specific Entropy           |
| e                | J/kg          | Sp. Internal Energy        |
| H                | J             | Enthalpy                   |
| S                | J/K           | Entropy                    |
| E                | J             | (Internal) Energy          |
| eta              | -             | Efficiency                 |
| phi              | -             | Flow coefficient           |
| psi              | -             | Head coefficient           |
| omega            | rad/s         | Rotational speed           |
| mdot             | kg/s          | Mass flowrate              |
| vdot             | m3/s          | Volumetric flowrate        | 
| rho              | kg/m3         | Density                    | 
| pr               | -             | Pressure ratio             |  
| Q                | W             | Heat transferred           | 
| W                | W             | Work transferred           | 
| COP              | -             | Coefficient of Performance | 
| num              | int           | Number of                  | 
| dhp              | J/kg          | Polytropic head            |


#### Indicating units
It is encouraged to add units to variable names. This is done via the folling format `varname_subscript__unitNumerator_unitDenominator`:
- Use a double underscore to seperate the variable name and subscript from the unit.
- Use a single underscore to seperate the numerator from the denominator

Examples include:
```
h_isen__J_kg            # the isentropic specific enthalpy with units kJ/kg 
A_xsection__m2          # Cross-sectional area in m2
mdot_inlet__kg_s        # Flow rate in kg/s
```