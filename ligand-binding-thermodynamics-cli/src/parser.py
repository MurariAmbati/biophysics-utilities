"""
Input parsing and validation for CLI commands.
"""

import re
from typing import Optional, Tuple, Any

from .constants import (
    MIN_TEMPERATURE,
    MAX_TEMPERATURE,
    MIN_CONCENTRATION,
    MAX_CONCENTRATION,
)


class ValidationError(Exception):
    """Custom exception for input validation errors."""
    pass


def parse_scientific_notation(value_str: str) -> float:
    """
    Parse a string that may contain scientific notation (e.g., '1e-6', '5.0e+05').
    
    Args:
        value_str: String representation of a number
    
    Returns:
        Parsed float value
    
    Raises:
        ValidationError: If parsing fails
    """
    try:
        value = float(value_str)
        return value
    except ValueError:
        raise ValidationError(f"Invalid number format: '{value_str}'")


def parse_assignment(line: str) -> Optional[Tuple[str, float]]:
    """
    Parse an assignment line (e.g., 'T = 298', 'P = 1e-6').
    
    Args:
        line: Input line from user
    
    Returns:
        Tuple of (variable_name, value) or None if not an assignment
    
    Raises:
        ValidationError: If assignment format is invalid
    """
    # Match pattern: variable = value
    match = re.match(r'^\s*([A-Za-z_Δ][A-Za-z0-9_Δ]*)\s*=\s*([+-]?[0-9]*\.?[0-9]+(?:[eE][+-]?[0-9]+)?)\s*$', line)
    
    if not match:
        return None
    
    var_name = match.group(1)
    value_str = match.group(2)
    
    value = parse_scientific_notation(value_str)
    
    return (var_name, value)


def validate_temperature(temp: float) -> None:
    """
    Validate temperature value.
    
    Args:
        temp: Temperature in K
    
    Raises:
        ValidationError: If temperature is out of valid range
    """
    if temp <= MIN_TEMPERATURE:
        raise ValidationError(
            f"Temperature must be greater than {MIN_TEMPERATURE} K (absolute zero)"
        )
    
    if temp > MAX_TEMPERATURE:
        raise ValidationError(
            f"Temperature {temp} K exceeds reasonable limit of {MAX_TEMPERATURE} K"
        )


def validate_concentration(conc: float, var_name: str = "Concentration") -> None:
    """
    Validate concentration value.
    
    Args:
        conc: Concentration in M
        var_name: Name of the variable for error messages
    
    Raises:
        ValidationError: If concentration is out of valid range
    """
    if conc < MIN_CONCENTRATION:
        raise ValidationError(f"{var_name} cannot be negative")
    
    if conc > MAX_CONCENTRATION:
        raise ValidationError(
            f"{var_name} {conc} M exceeds reasonable limit of {MAX_CONCENTRATION} M"
        )


def validate_state_for_computation(state: dict) -> Tuple[float, float, float, float]:
    """
    Validate that all required parameters are present for computation.
    
    Args:
        state: Dictionary containing user-defined variables
    
    Returns:
        Tuple of (T, P, L, PL) values
    
    Raises:
        ValidationError: If any required parameter is missing
    """
    required = ['T', 'P', 'L', 'PL']
    missing = [var for var in required if var not in state]
    
    if missing:
        raise ValidationError(
            f"Missing required parameters: {', '.join(missing)}. "
            f"Required: T (temperature), P (protein), L (ligand), PL (complex)"
        )
    
    temp = state['T']
    p_conc = state['P']
    l_conc = state['L']
    pl_conc = state['PL']
    
    # Validate each parameter
    validate_temperature(temp)
    validate_concentration(p_conc, "[P]")
    validate_concentration(l_conc, "[L]")
    validate_concentration(pl_conc, "[PL]")
    
    return temp, p_conc, l_conc, pl_conc


def parse_command(line: str) -> Tuple[str, list]:
    """
    Parse a command line (e.g., 'compute()', 'compute_entropy()').
    
    Args:
        line: Input line from user
    
    Returns:
        Tuple of (command_name, arguments_list)
        Returns ('', []) if not a command
    """
    # Match pattern: command() or command(arg1, arg2, ...)
    match = re.match(r'^\s*([a-z_][a-z0-9_]*)\s*\(\s*(.*?)\s*\)\s*$', line, re.IGNORECASE)
    
    if not match:
        return ('', [])
    
    command = match.group(1)
    args_str = match.group(2)
    
    # Parse arguments if present
    args = []
    if args_str:
        # Simple comma-separated parsing
        args = [arg.strip() for arg in args_str.split(',')]
    
    return (command, args)


def normalize_variable_name(var_name: str) -> str:
    """
    Normalize variable names for consistency.
    Supports Greek letters like ΔH, ΔS, ΔG.
    
    Args:
        var_name: Variable name as entered by user
    
    Returns:
        Normalized variable name
    """
    # Map common alternatives
    mappings = {
        'temp': 'T',
        'temperature': 'T',
        'protein': 'P',
        'ligand': 'L',
        'complex': 'PL',
        'pl': 'PL',
        'dg': 'ΔG',
        'dh': 'ΔH',
        'ds': 'ΔS',
        'DG': 'ΔG',
        'DH': 'ΔH',
        'DS': 'ΔS',
    }
    
    return mappings.get(var_name.lower(), var_name)


def format_scientific(value: float, precision: int = 2) -> str:
    """
    Format a number in scientific notation with specified precision.
    
    Args:
        value: Number to format
        precision: Number of decimal places
    
    Returns:
        Formatted string
    """
    if abs(value) < 1e-3 or abs(value) >= 1e6:
        return f"{value:.{precision}e}"
    else:
        return f"{value:.{precision}f}"
