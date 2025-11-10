"""
Utility functions for unit conversions and input validation.
"""

from typing import Tuple
from .constants import ANGSTROM_TO_METER, NM2_TO_M2


def angstrom_to_meter(angstrom: float) -> float:
    """
    Convert Angstroms to meters.
    
    Parameters
    ----------
    angstrom : float
        Distance in Angstroms
    
    Returns
    -------
    float
        Distance in meters
    """
    return angstrom * ANGSTROM_TO_METER


def meter_to_angstrom(meter: float) -> float:
    """
    Convert meters to Angstroms.
    
    Parameters
    ----------
    meter : float
        Distance in meters
    
    Returns
    -------
    float
        Distance in Angstroms
    """
    return meter / ANGSTROM_TO_METER


def nm2_to_m2(nm2: float) -> float:
    """
    Convert square nanometers to square meters.
    
    Parameters
    ----------
    nm2 : float
        Area in nm²
    
    Returns
    -------
    float
        Area in m²
    """
    return nm2 * NM2_TO_M2


def m2_to_nm2(m2: float) -> float:
    """
    Convert square meters to square nanometers.
    
    Parameters
    ----------
    m2 : float
        Area in m²
    
    Returns
    -------
    float
        Area in nm²
    """
    return m2 / NM2_TO_M2


def validate_surface_area(area: float) -> Tuple[bool, str]:
    """
    Validate surface area input.
    
    Parameters
    ----------
    area : float
        Surface area in m²
    
    Returns
    -------
    tuple
        (is_valid, error_message)
    """
    if area <= 0:
        return False, "Surface area must be positive"
    
    # Typical protein surface areas range from ~1e-18 to ~1e-15 m²
    if area < 1e-20 or area > 1e-13:
        return False, "Surface area seems unrealistic (expected range: 1e-20 to 1e-13 m²)"
    
    return True, ""


def validate_hydrophilicity_index(index: float) -> Tuple[bool, str]:
    """
    Validate hydrophilicity index.
    
    Parameters
    ----------
    index : float
        Hydrophilicity index (0 to 1)
    
    Returns
    -------
    tuple
        (is_valid, error_message)
    """
    if not 0 <= index <= 1:
        return False, "Hydrophilicity index must be between 0 and 1"
    
    return True, ""


def validate_shell_thickness(thickness: float) -> Tuple[bool, str]:
    """
    Validate shell thickness.
    
    Parameters
    ----------
    thickness : float
        Shell thickness in Angstroms
    
    Returns
    -------
    tuple
        (is_valid, error_message)
    """
    if thickness <= 0:
        return False, "Shell thickness must be positive"
    
    # Typical hydration shells are 2.5-5.0 Å
    if thickness < 1.0 or thickness > 10.0:
        return False, "Shell thickness seems unrealistic (expected range: 1.0 to 10.0 Å)"
    
    return True, ""


def validate_all_inputs(
    surface_area: float,
    hydrophilicity_index: float,
    shell_thickness: float
) -> Tuple[bool, str]:
    """
    Validate all input parameters.
    
    Parameters
    ----------
    surface_area : float
        Surface area in m²
    hydrophilicity_index : float
        Hydrophilicity index (0 to 1)
    shell_thickness : float
        Shell thickness in Angstroms
    
    Returns
    -------
    tuple
        (is_valid, error_message)
    """
    validators = [
        validate_surface_area(surface_area),
        validate_hydrophilicity_index(hydrophilicity_index),
        validate_shell_thickness(shell_thickness),
    ]
    
    for is_valid, message in validators:
        if not is_valid:
            return False, message
    
    return True, ""


def format_scientific(value: float, sig_figs: int = 3) -> str:
    """
    Format a number in scientific notation with specified significant figures.
    
    Parameters
    ----------
    value : float
        Number to format
    sig_figs : int, optional
        Number of significant figures, default 3
    
    Returns
    -------
    str
        Formatted string in scientific notation
    """
    return f"{value:.{sig_figs-1}e}"
