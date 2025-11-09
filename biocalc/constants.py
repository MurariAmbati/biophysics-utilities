"""
Physical and biological constants with units.
"""

from pint import UnitRegistry

# Initialize unit registry
ureg = UnitRegistry()

# Define biochemical and physical constants
CONSTANTS = {
    # Fundamental constants
    "avogadro": 6.02214076e23 * ureg("1/mol"),
    "N_A": 6.02214076e23 * ureg("1/mol"),
    "boltzmann": 1.380649e-23 * ureg("J/K"),
    "k_B": 1.380649e-23 * ureg("J/K"),
    "R": 8.314462618 * ureg("J/(mol*K)"),
    "gas_constant": 8.314462618 * ureg("J/(mol*K)"),
    "planck": 6.62607015e-34 * ureg("J*s"),
    "h": 6.62607015e-34 * ureg("J*s"),
    "speed_of_light": 299792458 * ureg("m/s"),
    "c": 299792458 * ureg("m/s"),
    "elementary_charge": 1.602176634e-19 * ureg("C"),
    "e": 1.602176634e-19 * ureg("C"),
    "faraday": 96485.33212 * ureg("C/mol"),
    "F": 96485.33212 * ureg("C/mol"),
    
    # Biochemical energies
    "ATP_hydrolysis": 50e3 * ureg("J/mol"),
    "ATP_synthesis": -50e3 * ureg("J/mol"),
    "GTP_hydrolysis": 50e3 * ureg("J/mol"),
    "proton_motive_force": 200e-3 * ureg("V"),
    
    # Diffusion coefficients (in water at 25°C)
    "diffusion_O2_water": 2.1e-9 * ureg("m^2/s"),
    "diffusion_glucose_water": 0.67e-9 * ureg("m^2/s"),
    "diffusion_protein_water": 0.1e-9 * ureg("m^2/s"),
    "diffusion_ion_water": 2.0e-9 * ureg("m^2/s"),
    
    # Standard conditions
    "standard_temperature": 298.15 * ureg("K"),
    "T_std": 298.15 * ureg("K"),
    "standard_pressure": 101325 * ureg("Pa"),
    "P_std": 101325 * ureg("Pa"),
    "body_temperature": 310.15 * ureg("K"),
    "T_body": 310.15 * ureg("K"),
    
    # Molecular masses (g/mol)
    "mass_ATP": 507.18 * ureg("g/mol"),
    "mass_glucose": 180.16 * ureg("g/mol"),
    "mass_water": 18.015 * ureg("g/mol"),
    "mass_O2": 32.0 * ureg("g/mol"),
    "mass_CO2": 44.01 * ureg("g/mol"),
    
    # Biological concentrations (typical)
    "conc_ATP_cell": 5e-3 * ureg("mol/L"),
    "conc_glucose_blood": 5e-3 * ureg("mol/L"),
    "pH_blood": 7.4 * ureg(""),
    "pH_cytoplasm": 7.2 * ureg(""),
    
    # Membrane properties
    "membrane_potential": -70e-3 * ureg("V"),
    "membrane_capacitance": 1e-2 * ureg("F/m^2"),
    
    # Viscosity
    "viscosity_water": 0.001 * ureg("Pa*s"),
    
    # Other useful constants
    "gravitational_acceleration": 9.80665 * ureg("m/s^2"),
    "g": 9.80665 * ureg("m/s^2"),
}


def list_constants():
    """Return a list of all available constant names."""
    return sorted(CONSTANTS.keys())


def get_constant(name):
    """
    Get a constant by name.
    
    Parameters
    ----------
    name : str
        Name of the constant
        
    Returns
    -------
    pint.Quantity
        The constant with units
        
    Raises
    ------
    KeyError
        If constant not found
    """
    if name not in CONSTANTS:
        available = ", ".join(list_constants())
        raise KeyError(
            f"Unknown constant '{name}'. Available constants: {available}"
        )
    return CONSTANTS[name]


def search_constants(query):
    """
    Search for constants matching a query string.
    
    Parameters
    ----------
    query : str
        Search term (case-insensitive)
        
    Returns
    -------
    dict
        Dictionary of matching constants
    """
    query_lower = query.lower()
    return {
        name: value
        for name, value in CONSTANTS.items()
        if query_lower in name.lower()
    }
