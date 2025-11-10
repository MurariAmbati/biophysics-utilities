"""
Analytic force derivatives for potential energy functions.

Force is the negative gradient: F(r) = -dU(r)/dr

All functions operate in nanometer/eV units, giving forces in eV/nm.
"""

import numpy as np
from .constants import K_E, NM_TO_M, EV_TO_J


def lj_force(r, epsilon, sigma):
    """
    Compute the force from Lennard-Jones potential.
    
    F(r) = -dU_LJ/dr = 24ε/r [(2(σ/r)^12 - (σ/r)^6)]
    
    Parameters
    ----------
    r : float or ndarray
        Interatomic distance [nm]
    epsilon : float
        Depth of potential well [eV]
    sigma : float
        Distance at which U=0 [nm]
    
    Returns
    -------
    float or ndarray
        Force [eV/nm], positive = repulsive, negative = attractive
    """
    r = np.asarray(r)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        sr = sigma / r
        sr6 = sr**6
        sr12 = sr6**2
        F = 24 * epsilon / r * (2 * sr12 - sr6)
    
    return F


def morse_force(r, De, a, re):
    """
    Compute the force from Morse potential.
    
    F(r) = -dU_M/dr = 2*De*a*e^(-a(r-re))*(1 - e^(-a(r-re)))
    
    Parameters
    ----------
    r : float or ndarray
        Interatomic distance [nm]
    De : float
        Well depth [eV]
    a : float
        Width parameter [1/nm]
    re : float
        Equilibrium bond length [nm]
    
    Returns
    -------
    float or ndarray
        Force [eV/nm], positive = repulsive, negative = attractive
    """
    r = np.asarray(r)
    
    exp_term = np.exp(-a * (r - re))
    F = 2 * De * a * exp_term * (1 - exp_term)
    
    return F


def coulomb_force(r, q1, q2):
    """
    Compute the force from Coulomb potential.
    
    F(r) = -dU_C/dr = k_e * q1 * q2 / r²
    
    Parameters
    ----------
    r : float or ndarray
        Interatomic distance [nm]
    q1 : float
        Charge of particle 1 [C]
    q2 : float
        Charge of particle 2 [C]
    
    Returns
    -------
    float or ndarray
        Force [eV/nm], positive = repulsive, negative = attractive
    """
    r = np.asarray(r)
    
    # Convert r from nm to m
    r_m = r * NM_TO_M
    
    with np.errstate(divide='ignore', invalid='ignore'):
        # Calculate in N (kg·m/s²)
        F_N = K_E * q1 * q2 / (r_m**2)
        # Convert to eV/nm: N = J/m, so N * m = J
        # F [eV/nm] = F [N] * (1 nm) / (1 eV/J)
        # = F [N] * NM_TO_M / EV_TO_J
        F_eV_nm = F_N * NM_TO_M / EV_TO_J
    
    return F_eV_nm


def combined_force(r, lj_params=None, morse_params=None, coulomb_params=None):
    """
    Compute combined force from multiple potential contributions.
    
    Parameters
    ----------
    r : float or ndarray
        Interatomic distance [nm]
    lj_params : dict, optional
        Dict with 'epsilon' and 'sigma' keys
    morse_params : dict, optional
        Dict with 'De', 'a', and 're' keys
    coulomb_params : dict, optional
        Dict with 'q1' and 'q2' keys
    
    Returns
    -------
    float or ndarray
        Total force [eV/nm]
    """
    F_total = np.zeros_like(r, dtype=float)
    
    if lj_params is not None:
        F_total += lj_force(r, **lj_params)
    
    if morse_params is not None:
        F_total += morse_force(r, **morse_params)
    
    if coulomb_params is not None:
        F_total += coulomb_force(r, **coulomb_params)
    
    return F_total


# Dictionary mapping potential names to force functions
FORCES = {
    "LJ": lj_force,
    "Morse": morse_force,
    "Coulomb": coulomb_force,
    "lennard_jones": lj_force,
    "morse": morse_force,
    "coulomb": coulomb_force,
}
