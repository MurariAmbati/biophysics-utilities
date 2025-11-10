"""
Core thermodynamic calculation functions for ligand binding.

Equations:
    Ka = [PL] / ([P][L])  (M⁻¹)
    Kd = 1 / Ka  (M)
    ΔG = -RT ln(Ka)  (kJ/mol)
    ΔG = ΔH - TΔS  (kJ/mol)
"""

import math
from typing import Optional, Tuple

from .constants import GAS_CONSTANT_R, J_TO_KJ, KJ_TO_J


def calculate_ka(p_conc: float, l_conc: float, pl_conc: float) -> float:
    """
    Calculate the association constant Ka.
    
    Ka = [PL] / ([P][L])
    
    Args:
        p_conc: Protein concentration [P] in M
        l_conc: Ligand concentration [L] in M
        pl_conc: Complex concentration [PL] in M
    
    Returns:
        Association constant Ka in M⁻¹
    
    Raises:
        ValueError: If concentrations are invalid or result in division by zero
    """
    if p_conc <= 0 or l_conc <= 0:
        raise ValueError("Protein and ligand concentrations must be positive")
    
    if pl_conc < 0:
        raise ValueError("Complex concentration cannot be negative")
    
    denominator = p_conc * l_conc
    if denominator == 0:
        raise ValueError("Product [P][L] cannot be zero")
    
    ka = pl_conc / denominator
    return ka


def calculate_kd(ka: float) -> float:
    """
    Calculate the dissociation constant Kd from Ka.
    
    Kd = 1 / Ka
    
    Args:
        ka: Association constant in M⁻¹
    
    Returns:
        Dissociation constant Kd in M
    
    Raises:
        ValueError: If Ka is zero or negative
    """
    if ka <= 0:
        raise ValueError("Association constant Ka must be positive")
    
    kd = 1.0 / ka
    return kd


def calculate_delta_g(ka: float, temperature: float) -> float:
    """
    Calculate the standard free energy of binding ΔG.
    
    ΔG = -RT ln(Ka)
    
    Args:
        ka: Association constant in M⁻¹
        temperature: Temperature in K
    
    Returns:
        Free energy ΔG in kJ/mol
    
    Raises:
        ValueError: If Ka is non-positive or temperature is invalid
    """
    if ka <= 0:
        raise ValueError("Association constant Ka must be positive")
    
    if temperature <= 0:
        raise ValueError("Temperature must be positive (in Kelvin)")
    
    # ΔG = -RT ln(Ka)
    # Result in J/mol, convert to kJ/mol
    delta_g_j = -GAS_CONSTANT_R * temperature * math.log(ka)
    delta_g_kj = delta_g_j * J_TO_KJ
    
    return delta_g_kj


def calculate_entropy(delta_g: float, delta_h: float, temperature: float) -> float:
    """
    Calculate the entropy of binding ΔS from ΔG and ΔH.
    
    ΔG = ΔH - TΔS  =>  ΔS = (ΔH - ΔG) / T
    
    Args:
        delta_g: Free energy in kJ/mol
        delta_h: Enthalpy in kJ/mol
        temperature: Temperature in K
    
    Returns:
        Entropy ΔS in J/(mol·K)
    
    Raises:
        ValueError: If temperature is invalid
    """
    if temperature <= 0:
        raise ValueError("Temperature must be positive (in Kelvin)")
    
    # Convert ΔG and ΔH from kJ/mol to J/mol for consistency
    delta_g_j = delta_g * KJ_TO_J
    delta_h_j = delta_h * KJ_TO_J
    
    # ΔS = (ΔH - ΔG) / T
    delta_s = (delta_h_j - delta_g_j) / temperature
    
    return delta_s


def calculate_enthalpy(delta_g: float, delta_s: float, temperature: float) -> float:
    """
    Calculate the enthalpy of binding ΔH from ΔG and ΔS.
    
    ΔG = ΔH - TΔS  =>  ΔH = ΔG + TΔS
    
    Args:
        delta_g: Free energy in kJ/mol
        delta_s: Entropy in J/(mol·K)
        temperature: Temperature in K
    
    Returns:
        Enthalpy ΔH in kJ/mol
    
    Raises:
        ValueError: If temperature is invalid
    """
    if temperature <= 0:
        raise ValueError("Temperature must be positive (in Kelvin)")
    
    # Convert ΔG from kJ/mol to J/mol
    delta_g_j = delta_g * KJ_TO_J
    
    # ΔH = ΔG + TΔS (in J/mol)
    delta_h_j = delta_g_j + temperature * delta_s
    
    # Convert back to kJ/mol
    delta_h_kj = delta_h_j * J_TO_KJ
    
    return delta_h_kj


def van_t_hoff_ka(delta_h: float, delta_s: float, temperature: float) -> float:
    """
    Calculate Ka from van't Hoff equation.
    
    ln(Ka) = -ΔH/R · (1/T) + ΔS/R
    
    Args:
        delta_h: Enthalpy in kJ/mol
        delta_s: Entropy in J/(mol·K)
        temperature: Temperature in K
    
    Returns:
        Association constant Ka in M⁻¹
    
    Raises:
        ValueError: If temperature is invalid
    """
    if temperature <= 0:
        raise ValueError("Temperature must be positive (in Kelvin)")
    
    # Convert ΔH from kJ/mol to J/mol
    delta_h_j = delta_h * KJ_TO_J
    
    # ln(Ka) = -ΔH/R · (1/T) + ΔS/R
    ln_ka = (-delta_h_j / GAS_CONSTANT_R) * (1.0 / temperature) + (delta_s / GAS_CONSTANT_R)
    
    ka = math.exp(ln_ka)
    return ka


def hill_fractional_occupancy(ligand_conc: float, kd: float, hill_coefficient: float) -> float:
    """
    Calculate fractional occupancy using the Hill equation.
    
    θ = [L]ⁿ / (Kd + [L]ⁿ)
    
    Args:
        ligand_conc: Ligand concentration [L] in M
        kd: Dissociation constant in M
        hill_coefficient: Hill coefficient n (cooperativity)
    
    Returns:
        Fractional occupancy θ (0 to 1)
    
    Raises:
        ValueError: If concentrations are invalid
    """
    if ligand_conc < 0:
        raise ValueError("Ligand concentration cannot be negative")
    
    if kd <= 0:
        raise ValueError("Dissociation constant Kd must be positive")
    
    if hill_coefficient <= 0:
        raise ValueError("Hill coefficient must be positive")
    
    # θ = [L]ⁿ / (Kd + [L]ⁿ)
    l_n = math.pow(ligand_conc, hill_coefficient)
    theta = l_n / (kd + l_n)
    
    return theta


def compute_all(
    p_conc: float,
    l_conc: float,
    pl_conc: float,
    temperature: float,
    delta_h: Optional[float] = None
) -> dict:
    """
    Compute all thermodynamic parameters from equilibrium concentrations.
    
    Args:
        p_conc: Protein concentration [P] in M
        l_conc: Ligand concentration [L] in M
        pl_conc: Complex concentration [PL] in M
        temperature: Temperature in K
        delta_h: Optional enthalpy in kJ/mol
    
    Returns:
        Dictionary containing Ka, Kd, ΔG, and optionally ΔS
    """
    results = {}
    
    # Calculate Ka
    ka = calculate_ka(p_conc, l_conc, pl_conc)
    results['Ka'] = ka
    results['Ka_unit'] = 'M^-1'
    
    # Calculate Kd
    kd = calculate_kd(ka)
    results['Kd'] = kd
    results['Kd_unit'] = 'M'
    
    # Calculate ΔG
    delta_g = calculate_delta_g(ka, temperature)
    results['ΔG'] = delta_g
    results['ΔG_unit'] = 'kJ/mol'
    
    # If ΔH provided, calculate ΔS
    if delta_h is not None:
        delta_s = calculate_entropy(delta_g, delta_h, temperature)
        results['ΔH'] = delta_h
        results['ΔH_unit'] = 'kJ/mol'
        results['ΔS'] = delta_s
        results['ΔS_unit'] = 'J/(mol·K)'
    
    return results
