"""
Diffusion Time Estimator - A tool for estimating diffusion timescales from first principles.
"""
from .core import (
    diffusion_coefficient,
    diffusion_time,
    mean_square_displacement,
    format_time,
    format_coefficient
)
from .constants import k_B, WATER_VISCOSITY, ROOM_TEMPERATURE

__version__ = "0.1.0"
__all__ = [
    "diffusion_coefficient",
    "diffusion_time",
    "mean_square_displacement",
    "format_time",
    "format_coefficient",
    "k_B",
    "WATER_VISCOSITY",
    "ROOM_TEMPERATURE"
]
