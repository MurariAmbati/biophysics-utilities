"""Core Lennard-Jones potential model and calculations."""

import numpy as np
from typing import Tuple, Optional


def lj_potential(r: np.ndarray, epsilon: float = 1.0, sigma: float = 3.5) -> np.ndarray:
    """
    Calculate the Lennard-Jones 12-6 potential.
    
    V(r) = 4ε[(σ/r)^12 - (σ/r)^6]
    
    Parameters
    ----------
    r : np.ndarray
        Interparticle distance(s) in Ångströms
    epsilon : float, optional
        Depth of potential well in kJ/mol (default: 1.0)
    sigma : float, optional
        Collision diameter in Ångströms (default: 3.5)
        
    Returns
    -------
    np.ndarray
        Potential energy V(r) in kJ/mol
        
    Notes
    -----
    Returns np.inf for r = 0 to avoid division by zero.
    """
    r = np.asarray(r, dtype=np.float64)
    
    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        sigma_over_r = sigma / r
        sigma_over_r_6 = sigma_over_r ** 6
        sigma_over_r_12 = sigma_over_r_6 ** 2
        
        V = 4 * epsilon * (sigma_over_r_12 - sigma_over_r_6)
    
    # Set infinite potential at r=0
    V = np.where(r == 0, np.inf, V)
    
    return V


def lj_force(r: np.ndarray, epsilon: float = 1.0, sigma: float = 3.5) -> np.ndarray:
    """
    Calculate the force from the Lennard-Jones potential.
    
    F(r) = -dV/dr = 24ε/r [(σ/r)^6 - 2(σ/r)^12]
    
    Positive force = repulsive, Negative force = attractive
    
    Parameters
    ----------
    r : np.ndarray
        Interparticle distance(s) in Ångströms
    epsilon : float, optional
        Depth of potential well in kJ/mol (default: 1.0)
    sigma : float, optional
        Collision diameter in Ångströms (default: 3.5)
        
    Returns
    -------
    np.ndarray
        Force F(r) in kJ/mol/Å
    """
    r = np.asarray(r, dtype=np.float64)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        sigma_over_r = sigma / r
        sigma_over_r_6 = sigma_over_r ** 6
        sigma_over_r_12 = sigma_over_r_6 ** 2
        
        F = 24 * epsilon / r * (sigma_over_r_6 - 2 * sigma_over_r_12)
    
    # Set force to zero at r=0 (though physically undefined)
    F = np.where(r == 0, 0, F)
    
    return F


def lj_equilibrium(epsilon: float = 1.0, sigma: float = 3.5) -> Tuple[float, float]:
    """
    Calculate the equilibrium distance and minimum energy.
    
    At minimum: r_min = 2^(1/6) * σ ≈ 1.122σ
                V_min = -ε
    
    Parameters
    ----------
    epsilon : float, optional
        Depth of potential well in kJ/mol (default: 1.0)
    sigma : float, optional
        Collision diameter in Ångströms (default: 3.5)
        
    Returns
    -------
    r_min : float
        Equilibrium distance in Ångströms
    V_min : float
        Minimum potential energy in kJ/mol
    """
    r_min = 2 ** (1/6) * sigma
    V_min = -epsilon
    
    return r_min, V_min


def generate_lj_curve(
    epsilon: float = 1.0,
    sigma: float = 3.5,
    r_min: Optional[float] = None,
    r_max: Optional[float] = None,
    n_points: int = 500
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a Lennard-Jones potential curve over a distance range.
    
    Parameters
    ----------
    epsilon : float, optional
        Depth of potential well in kJ/mol (default: 1.0)
    sigma : float, optional
        Collision diameter in Ångströms (default: 3.5)
    r_min : float, optional
        Minimum distance in Ångströms (default: 0.5*sigma)
    r_max : float, optional
        Maximum distance in Ångströms (default: 3.0*sigma)
    n_points : int, optional
        Number of points to compute (default: 500)
        
    Returns
    -------
    r : np.ndarray
        Distance array in Ångströms
    V : np.ndarray
        Potential energy array in kJ/mol
    """
    if r_min is None:
        r_min = 0.5 * sigma
    if r_max is None:
        r_max = 3.0 * sigma
    
    r = np.linspace(r_min, r_max, n_points)
    V = lj_potential(r, epsilon, sigma)
    
    return r, V


def morse_potential(
    r: np.ndarray,
    D_e: float = 1.0,
    a: float = 1.0,
    r_e: float = 3.5
) -> np.ndarray:
    """
    Calculate the Morse potential for comparison.
    
    V(r) = D_e [1 - exp(-a(r - r_e))]^2 - D_e
    
    Parameters
    ----------
    r : np.ndarray
        Interparticle distance(s) in Ångströms
    D_e : float, optional
        Well depth in kJ/mol (default: 1.0)
    a : float, optional
        Width parameter in 1/Å (default: 1.0)
    r_e : float, optional
        Equilibrium distance in Ångströms (default: 3.5)
        
    Returns
    -------
    np.ndarray
        Morse potential energy in kJ/mol
    """
    r = np.asarray(r, dtype=np.float64)
    exp_term = np.exp(-a * (r - r_e))
    V = D_e * (1 - exp_term) ** 2 - D_e
    
    return V


def reduced_lj_potential(r_star: np.ndarray) -> np.ndarray:
    """
    Calculate the reduced Lennard-Jones potential.
    
    V*(r*) = 4[(1/r*)^12 - (1/r*)^6]
    
    where r* = r/σ and V* = V/ε
    
    Parameters
    ----------
    r_star : np.ndarray
        Reduced distance r/σ (dimensionless)
        
    Returns
    -------
    np.ndarray
        Reduced potential V/ε (dimensionless)
    """
    r_star = np.asarray(r_star, dtype=np.float64)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        r_inv = 1.0 / r_star
        r_inv_6 = r_inv ** 6
        r_inv_12 = r_inv_6 ** 2
        
        V_star = 4 * (r_inv_12 - r_inv_6)
    
    V_star = np.where(r_star == 0, np.inf, V_star)
    
    return V_star
