"""
Expression parsing and evaluation with symbolic and numeric support.
"""

import re
from sympy import sympify, symbols, lambdify
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)
from .constants import CONSTANTS, get_constant
from .units import ureg, parse_quantity, add_units


# Unit pattern regex (e.g., "K", "mol", "J/mol")
UNIT_PATTERN = re.compile(r'\b([A-Za-z]+(?:/[A-Za-z]+)?)\b')


def create_namespace():
    """
    Create a namespace with all constants for expression evaluation.
    
    Returns
    -------
    dict
        Namespace with constant names mapped to their magnitudes
    """
    namespace = {}
    
    # Add all constants (strip units for symbolic evaluation)
    for name, value in CONSTANTS.items():
        namespace[name] = value.magnitude if hasattr(value, 'magnitude') else value
    
    # Add common math functions
    import math
    for func_name in ['sin', 'cos', 'tan', 'exp', 'log', 'log10', 'sqrt']:
        namespace[func_name] = getattr(math, func_name)
    
    return namespace


def parse_expression(expr_str):
    """
    Parse a string expression into a SymPy expression.
    
    Parameters
    ----------
    expr_str : str
        Expression string like "R * 300*K" or "avogadro * 1e-3 mol"
        
    Returns
    -------
    sympy.Expr
        Parsed symbolic expression
        
    Examples
    --------
    >>> parse_expression("R * 300")
    R*300
    
    >>> parse_expression("avogadro / 1000")
    avogadro/1000
    """
    try:
        # Use transformations for implicit multiplication
        transformations = (
            standard_transformations + (implicit_multiplication_application,)
        )
        
        # Parse with sympy
        expr = parse_expr(
            expr_str,
            transformations=transformations,
            local_dict=create_namespace()
        )
        
        return expr
    except Exception as e:
        raise ValueError(f"Cannot parse expression '{expr_str}': {e}") from e


def extract_units_from_expression(expr_str):
    """
    Extract unit strings from an expression.
    
    Parameters
    ----------
    expr_str : str
        Expression that may contain units
        
    Returns
    -------
    tuple
        (expression_without_units, unit_string or None)
        
    Examples
    --------
    >>> extract_units_from_expression("50 kJ/mol")
    ('50', 'kJ/mol')
    
    >>> extract_units_from_expression("R * 300*K")
    ('R * 300', 'K')
    """
    # Try to detect if expression has explicit units like "50 kJ/mol"
    parts = expr_str.split()
    
    if len(parts) >= 2:
        # Check if last part(s) look like units
        potential_unit = parts[-1]
        try:
            ureg(potential_unit)
            # It's a valid unit
            expr_part = ' '.join(parts[:-1])
            return expr_part, potential_unit
        except:
            pass
    
    # Check for units after * or other operators
    match = re.search(r'\*\s*([A-Za-z_][A-Za-z0-9_/^*]*)\s*$', expr_str)
    if match:
        unit_part = match.group(1)
        try:
            ureg(unit_part)
            expr_part = expr_str[:match.start()].strip().rstrip('*').strip()
            return expr_part, unit_part
        except:
            pass
    
    return expr_str, None


def evaluate(expr_str, return_units=True, precision=None):
    """
    Evaluate an expression with constants and units.
    
    Parameters
    ----------
    expr_str : str
        Expression to evaluate
    return_units : bool
        Whether to return result with units
    precision : int, optional
        Number of decimal places for rounding
        
    Returns
    -------
    float or pint.Quantity
        Evaluated result
        
    Examples
    --------
    >>> evaluate("R * 300")
    2494.3387854 J/mol
    
    >>> evaluate("avogadro * 1e-3")
    6.02214076e20
    """
    # Extract units if present
    expr_part, unit_str = extract_units_from_expression(expr_str)
    
    # Try to evaluate as a unit quantity first
    if unit_str is None:
        try:
            result = parse_quantity(expr_str)
            if precision is not None:
                result = round(result.magnitude, precision) * result.units
            return result
        except:
            pass
    
    # Create namespace with constants
    namespace = create_namespace()
    
    try:
        # Parse and evaluate the expression
        expr = parse_expression(expr_part)
        
        # Substitute constants and evaluate
        result = float(expr.evalf(subs=namespace))
        
        # Apply precision if specified
        if precision is not None:
            result = round(result, precision)
        
        # Attach units if detected
        if return_units and unit_str:
            result = add_units(result, unit_str)
        
        return result
        
    except Exception as e:
        # Fall back to direct eval with namespace (less safe but more flexible)
        try:
            result = eval(expr_part, {"__builtins__": {}}, namespace)
            
            if precision is not None:
                result = round(result, precision)
            
            if return_units and unit_str:
                result = add_units(result, unit_str)
            
            return result
        except Exception as e2:
            raise ValueError(
                f"Cannot evaluate expression '{expr_str}': {e2}"
            ) from e2


def symbolic_eval(expr_str):
    """
    Evaluate expression symbolically (without substituting constants).
    
    Parameters
    ----------
    expr_str : str
        Expression to evaluate
        
    Returns
    -------
    sympy.Expr
        Symbolic result
        
    Examples
    --------
    >>> symbolic_eval("R * T")
    R*T
    
    >>> symbolic_eval("avogadro / N")
    avogadro/N
    """
    return parse_expression(expr_str)


def substitute_and_eval(expr_str, substitutions):
    """
    Evaluate expression with custom substitutions.
    
    Parameters
    ----------
    expr_str : str
        Expression to evaluate
    substitutions : dict
        Dictionary of symbol -> value substitutions
        
    Returns
    -------
    float
        Evaluated result
        
    Examples
    --------
    >>> substitute_and_eval("R * T", {"T": 300})
    2494.3387854
    """
    namespace = create_namespace()
    namespace.update(substitutions)
    
    expr = parse_expression(expr_str)
    result = float(expr.evalf(subs=namespace))
    
    return result


def energy(constant_name):
    """
    Get the energy value for a named constant.
    
    Parameters
    ----------
    constant_name : str
        Name of energy constant (e.g., "ATP_hydrolysis")
        
    Returns
    -------
    pint.Quantity
        Energy value with units
        
    Examples
    --------
    >>> energy("ATP_hydrolysis")
    50000.0 J/mol
    """
    if constant_name in CONSTANTS:
        value = CONSTANTS[constant_name]
        # Check if it's an energy-related constant
        if hasattr(value, 'dimensionality'):
            dim_str = str(value.dimensionality)
            if 'energy' in dim_str.lower() or '[mass]' in dim_str:
                return value
        return value
    else:
        raise ValueError(f"Unknown constant: {constant_name}")
