"""
Protein Shape Estimator Package

A minimal Python-based computational tool that estimates basic physical properties 
of a protein from sequence length and amino acid composition assumptions.
"""

__version__ = "0.1.0"

from .core import (
    molecular_weight,
    hydrodynamic_radius,
    net_charge,
    diffusion_coefficient,
)

__all__ = [
    "molecular_weight",
    "hydrodynamic_radius",
    "net_charge",
    "diffusion_coefficient",
]
