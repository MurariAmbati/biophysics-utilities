"""
Core physics and computation functions for diffusion time estimation.
"""
import math
from .constants import k_B


def diffusion_coefficient(radius, viscosity, temperature=298):
    """
    Calculate diffusion coefficient using the Stokes-Einstein relation.
    
    D = k_B * T / (6 * π * η * r)
    
    Parameters
    ----------
    radius : float
        Hydrodynamic radius of the molecule (m)
    viscosity : float
        Dynamic viscosity of the medium (Pa·s)
    temperature : float, optional
        Temperature (K), default is 298 K
        
    Returns
    -------
    float
        Diffusion coefficient (m²/s)
    """
    if radius <= 0:
        raise ValueError("Radius must be positive")
    if viscosity <= 0:
        raise ValueError("Viscosity must be positive")
    if temperature <= 0:
        raise ValueError("Temperature must be positive")
    
    return k_B * temperature / (6 * math.pi * viscosity * radius)


def diffusion_time(distance, D, dims=3):
    """
    Estimate characteristic diffusion time.
    
    t_diff ≈ L² / (2 * n * D)
    
    Parameters
    ----------
    distance : float
        Characteristic distance to diffuse (m)
    D : float
        Diffusion coefficient (m²/s)
    dims : int, optional
        Number of spatial dimensions (1, 2, or 3), default is 3
        
    Returns
    -------
    float
        Characteristic diffusion time (s)
    """
    if distance <= 0:
        raise ValueError("Distance must be positive")
    if D <= 0:
        raise ValueError("Diffusion coefficient must be positive")
    if dims not in [1, 2, 3]:
        raise ValueError("Dimensions must be 1, 2, or 3")
    
    return (distance ** 2) / (2 * dims * D)


def mean_square_displacement(D, t, dims=3):
    """
    Calculate mean-square displacement as a function of time.
    
    ⟨x²(t)⟩ = 2 * n * D * t
    
    Parameters
    ----------
    D : float
        Diffusion coefficient (m²/s)
    t : float or array-like
        Time or array of times (s)
    dims : int, optional
        Number of spatial dimensions (1, 2, or 3), default is 3
        
    Returns
    -------
    float or array-like
        Mean-square displacement (m²)
    """
    if D <= 0:
        raise ValueError("Diffusion coefficient must be positive")
    if dims not in [1, 2, 3]:
        raise ValueError("Dimensions must be 1, 2, or 3")
    
    return 2 * dims * D * t


def format_time(seconds):
    """
    Format time in appropriate units (s, ms, μs, ns).
    
    Parameters
    ----------
    seconds : float
        Time in seconds
        
    Returns
    -------
    str
        Formatted time string with appropriate unit
    """
    if seconds >= 1:
        return f"{seconds:.3g} s"
    elif seconds >= 1e-3:
        return f"{seconds * 1e3:.3g} ms"
    elif seconds >= 1e-6:
        return f"{seconds * 1e6:.3g} μs"
    else:
        return f"{seconds * 1e9:.3g} ns"


def format_coefficient(D):
    """
    Format diffusion coefficient in scientific notation.
    
    Parameters
    ----------
    D : float
        Diffusion coefficient (m²/s)
        
    Returns
    -------
    str
        Formatted string with scientific notation
    """
    return f"{D:.3e} m²/s"
