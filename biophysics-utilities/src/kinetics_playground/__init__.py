"""Kinetics Playground: A modular framework for chemical reaction network simulation."""

__version__ = "0.1.0"
__author__ = "Murari"

from kinetics_playground.api.reaction_network import ReactionNetwork
from kinetics_playground.api.simulation_session import SimulationSession

__all__ = ["ReactionNetwork", "SimulationSession"]
