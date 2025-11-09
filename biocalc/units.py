"""
Unit parsing, conversion, and validation using Pint.
"""

from pint import UnitRegistry, DimensionalityError
from .constants import CONSTANTS

# Shared unit registry instance
ureg = UnitRegistry()

# Enable parsing of expressions with implicit multiplication
ureg.default_format = "~P"


def convert(value_expr, target_unit):
    """
    Convert a value expression to a target unit.
    
    Parameters
    ----------
    value_expr : str or pint.Quantity
        Expression like "1 kcal/mol" or a Quantity object
    target_unit : str
        Target unit like "J/mol"
        
    Returns
    -------
    pint.Quantity
        Converted value with units
        
    Examples
    --------
    >>> convert("1 kcal/mol", "J/mol")
    4184.0 J/mol
    
    >>> convert("50 kJ/mol", "kcal/mol")
    11.95 kcal/mol
    """
    # Parse the value if it's a string
    if isinstance(value_expr, str):
        value = ureg.parse_expression(value_expr)
    else:
        value = value_expr
    
    # Convert to target unit
    try:
        result = value.to(target_unit)
        return result
    except DimensionalityError as e:
        raise ValueError(
            f"Cannot convert {value.dimensionality} to {ureg(target_unit).dimensionality}"
        ) from e


def parse_quantity(expr):
    """
    Parse an expression into a quantity with units.
    
    Parameters
    ----------
    expr : str
        Expression like "50 kJ/mol" or "1.5e-9 m^2/s"
        
    Returns
    -------
    pint.Quantity
        Parsed quantity with units
        
    Examples
    --------
    >>> parse_quantity("50 kJ/mol")
    50.0 kJ/mol
    
    >>> parse_quantity("2.1e-9 m^2/s")
    2.1e-9 m^2/s
    """
    try:
        return ureg.parse_expression(expr)
    except Exception as e:
        raise ValueError(f"Cannot parse quantity '{expr}': {e}") from e


def check_dimensionality(quantity, expected_dimension):
    """
    Check if a quantity has the expected dimensionality.
    
    Parameters
    ----------
    quantity : pint.Quantity
        Quantity to check
    expected_dimension : str
        Expected dimension like "[energy]/[substance]"
        
    Returns
    -------
    bool
        True if dimensionality matches
        
    Examples
    --------
    >>> q = ureg.Quantity(50, "kJ/mol")
    >>> check_dimensionality(q, "[energy]/[substance]")
    True
    """
    expected = ureg.parse_expression(f"1 {expected_dimension}")
    return quantity.dimensionality == expected.dimensionality


def strip_units(quantity):
    """
    Extract the magnitude from a quantity.
    
    Parameters
    ----------
    quantity : pint.Quantity
        Quantity with units
        
    Returns
    -------
    float
        Magnitude without units
    """
    return quantity.magnitude


def add_units(value, unit_str):
    """
    Add units to a numeric value.
    
    Parameters
    ----------
    value : float
        Numeric value
    unit_str : str
        Unit string like "m/s" or "J/mol"
        
    Returns
    -------
    pint.Quantity
        Value with units attached
        
    Examples
    --------
    >>> add_units(50000, "J/mol")
    50000.0 J/mol
    """
    return ureg.Quantity(value, unit_str)


def get_base_units(quantity):
    """
    Convert quantity to base SI units.
    
    Parameters
    ----------
    quantity : pint.Quantity
        Quantity to convert
        
    Returns
    -------
    pint.Quantity
        Quantity in base SI units
        
    Examples
    --------
    >>> get_base_units(ureg.Quantity(1, "kcal/mol"))
    4184.0 J/mol
    """
    return quantity.to_base_units()


def format_quantity(quantity, precision=3):
    """
    Format a quantity for display.
    
    Parameters
    ----------
    quantity : pint.Quantity
        Quantity to format
    precision : int
        Number of decimal places
        
    Returns
    -------
    str
        Formatted string
        
    Examples
    --------
    >>> format_quantity(ureg.Quantity(4184.0, "J/mol"), precision=2)
    '4184.00 J/mol'
    """
    return f"{quantity.magnitude:.{precision}f} {quantity.units:~P}"


def compatible_units(unit_str):
    """
    Get a list of compatible units for a given unit.
    
    Parameters
    ----------
    unit_str : str
        Unit string like "J/mol"
        
    Returns
    -------
    list
        List of compatible unit strings
        
    Examples
    --------
    >>> compatible_units("J/mol")
    ['kJ/mol', 'kcal/mol', 'eV', ...]
    """
    try:
        unit = ureg(unit_str)
        dimensionality = unit.dimensionality
        
        # Get all units with matching dimensionality
        compatible = []
        for name in dir(ureg):
            if name.startswith('_'):
                continue
            try:
                u = getattr(ureg, name)
                if hasattr(u, 'dimensionality') and u.dimensionality == dimensionality:
                    compatible.append(name)
            except:
                pass
        
        return compatible
    except:
        return []
