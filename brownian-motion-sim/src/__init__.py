"""
Brownian Motion Simulator
A tool for simulating and visualizing stochastic particle motion.
"""

__version__ = "1.0.0"
__author__ = "Biophysics Utilities"

from .core import BrownianSimulator
from .viz import visualize_trajectories, plot_msd_comparison

__all__ = ["BrownianSimulator", "visualize_trajectories", "plot_msd_comparison"]
