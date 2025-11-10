"""
Stochastic Integrator Visualizer

A lightweight, interactive simulator and visualizer for stochastic differential equations (SDEs),
demonstrating how noise and drift affect trajectories.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .core import euler_maruyama, milstein, run_ensemble
from .visualize import plot_trajectory, plot_histogram, plot_phase_space, plot_multiple_trajectories

__all__ = [
    "euler_maruyama",
    "milstein",
    "run_ensemble",
    "plot_trajectory",
    "plot_histogram",
    "plot_phase_space",
    "plot_multiple_trajectories",
]
