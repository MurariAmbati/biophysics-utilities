"""
Protein Hydration Shell Estimator

A theoretical tool for estimating the number, density, and thickness of water
molecules in the hydration shell of a protein based on surface area and 
hydrophilicity index.
"""

__version__ = "1.0.0"
__author__ = "Biophysics Utilities"

from .model import HydrationShellEstimator
from .constants import (
    RHO_BULK_WATER,
    AVOGADRO_NUMBER,
    DEFAULT_SHELL_THICKNESS,
    DEFAULT_HYDROPHILICITY_INDEX,
)

__all__ = [
    "HydrationShellEstimator",
    "RHO_BULK_WATER",
    "AVOGADRO_NUMBER",
    "DEFAULT_SHELL_THICKNESS",
    "DEFAULT_HYDROPHILICITY_INDEX",
]
