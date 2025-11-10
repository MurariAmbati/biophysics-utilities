"""
Classical potential energy functions for diatomic systems.

All functions operate in nanometer/eV units by default.
"""

import numpy as np
from .constants import K_E, NM_TO_M, EV_TO_J


def lennard_jones(r, epsilon, sigma):
    """
    Compute the Lennard-Jones 12-6 potential.
    
    U_LJ(r) = 4ε[(σ/r)^12 - (σ/r)^6]
    
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
        Potential energy [eV]
    
    Notes
    -----
    The potential has a minimum at r = 2^(1/6) * σ ≈ 1.122σ
    where U_min = -ε
    """
    r = np.asarray(r)
    
    # Handle division by zero for very small r
    with np.errstate(divide='ignore', invalid='ignore'):
        sr = sigma / r
        sr6 = sr**6
        sr12 = sr6**2
        U = 4 * epsilon * (sr12 - sr6)
    
    return U


def morse(r, De, a, re):
    """
    Compute the Morse potential.
    
    U_M(r) = De[(1 - e^(-a(r-re)))^2 - 1]
    
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
        Potential energy [eV]
    
    Notes
    -----
    The potential has a minimum at r = re where U_min = -De.
    More realistic than LJ for covalent bonds as it allows dissociation.
    """
    r = np.asarray(r)
    
    exp_term = np.exp(-a * (r - re))
    U = De * ((1 - exp_term)**2 - 1)
    
    return U


def coulomb(r, q1, q2):
    """
    Compute the Coulomb electrostatic potential.
    
    U_C(r) = k_e * q1 * q2 / r
    
    where k_e = 1/(4πε₀) = 8.987551787e9 N·m²/C²
    
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
        Potential energy [eV]
    
    Notes
    -----
    Returns positive values for like charges (repulsion)
    and negative values for opposite charges (attraction).
    Result is converted from Joules to eV.
    """
    r = np.asarray(r)
    
    # Convert r from nm to m
    r_m = r * NM_TO_M
    
    # Handle division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        # Calculate in Joules
        U_J = K_E * q1 * q2 / r_m
        # Convert to eV
        U_eV = U_J / EV_TO_J
    
    return U_eV


def combined_potential(r, lj_params=None, morse_params=None, coulomb_params=None):
    """
    Compute a combined potential from multiple contributions.
    
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
        Total potential energy [eV]
    """
    U_total = np.zeros_like(r, dtype=float)
    
    if lj_params is not None:
        U_total += lennard_jones(r, **lj_params)
    
    if morse_params is not None:
        U_total += morse(r, **morse_params)
    
    if coulomb_params is not None:
        U_total += coulomb(r, **coulomb_params)
    
    return U_total


# Dictionary mapping potential names to functions
POTENTIALS = {
    "LJ": lennard_jones,
    "Morse": morse,
    "Coulomb": coulomb,
    "lennard_jones": lennard_jones,
    "morse": morse,
    "coulomb": coulomb,
}
