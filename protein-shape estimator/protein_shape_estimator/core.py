"""
Core computational functions for protein shape estimation.
All calculations are based on theoretical models and empirical relationships.
"""

import math
from .constants import (
    K_B,
    AVG_MW_PER_RESIDUE,
    RH_COEFFICIENT,
    RH_EXPONENT,
    DEFAULT_TEMP,
    DEFAULT_VISCOSITY,
    DEFAULT_POS_FRAC,
    DEFAULT_NEG_FRAC,
)


def molecular_weight(n_residues):
    """
    Calculate the approximate molecular weight of a protein.
    
    Args:
        n_residues (int): Number of amino acid residues
        
    Returns:
        float: Molecular weight in Daltons (Da)
    """
    return AVG_MW_PER_RESIDUE * n_residues


def hydrodynamic_radius(n_residues):
    """
    Estimate the hydrodynamic radius of a protein using empirical scaling.
    
    Uses the relationship: Rh ≈ 0.066 × MW^0.37 (in nm)
    
    Args:
        n_residues (int): Number of amino acid residues
        
    Returns:
        float: Hydrodynamic radius in meters
    """
    mw = molecular_weight(n_residues)
    # Calculate radius in nm, then convert to meters
    r_h_nm = RH_COEFFICIENT * (mw ** RH_EXPONENT)
    return r_h_nm * 1e-9


def net_charge(n_residues, f_pos=DEFAULT_POS_FRAC, f_neg=DEFAULT_NEG_FRAC):
    """
    Estimate the net charge of a protein at pH 7.
    
    Based on average amino acid composition:
    Z = N_res × (f_pos - f_neg)
    
    Args:
        n_residues (int): Number of amino acid residues
        f_pos (float): Fraction of positively charged residues (Lys + Arg)
        f_neg (float): Fraction of negatively charged residues (Asp + Glu)
        
    Returns:
        float: Net charge in elementary charge units (e)
    """
    return n_residues * (f_pos - f_neg)


def diffusion_coefficient(R_h, temp=DEFAULT_TEMP, viscosity=DEFAULT_VISCOSITY):
    """
    Calculate the diffusion coefficient using the Stokes-Einstein relation.
    
    D = k_B × T / (6 × π × η × R_h)
    
    Args:
        R_h (float): Hydrodynamic radius in meters
        temp (float): Temperature in Kelvin
        viscosity (float): Solvent viscosity in Pa·s
        
    Returns:
        float: Diffusion coefficient in m²/s
    """
    return K_B * temp / (6 * math.pi * viscosity * R_h)
