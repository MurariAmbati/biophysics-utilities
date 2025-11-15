"""Core data structures and analytical responses for viscoelastic models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

ModelName = Literal["maxwell", "kelvin_voigt"]
ModeName = Literal["relaxation", "creep"]
QuantityName = Literal["stress", "strain"]


@dataclass(frozen=True)
class SimulationConfig:
    """Normalized configuration for a viscoelastic experiment."""

    model: ModelName
    mode: ModeName
    E: float
    eta: float
    strain0: float | None
    stress0: float | None
    t_max: float
    dt: float


@dataclass(frozen=True)
class Response:
    """Result of a viscoelastic simulation."""

    time: np.ndarray
    response: np.ndarray
    quantity: QuantityName
    tau: float
    label: str


def maxwell_relaxation(time: np.ndarray, E: float, eta: float, strain0: float) -> tuple[np.ndarray, float, QuantityName, str]:
    tau = eta / E
    sigma0 = E * strain0
    response = sigma0 * np.exp(-time / tau)
    return response, tau, "stress", r"$\sigma(t)$"


def maxwell_creep(time: np.ndarray, E: float, eta: float, stress0: float) -> tuple[np.ndarray, float, QuantityName, str]:
    tau = eta / E
    response = (stress0 / E) + (stress0 / eta) * time
    return response, tau, "strain", r"$\varepsilon(t)$"


def kelvin_voigt_creep(time: np.ndarray, E: float, eta: float, stress0: float) -> tuple[np.ndarray, float, QuantityName, str]:
    tau = eta / E
    response = (stress0 / E) * (1.0 - np.exp(-time / tau))
    return response, tau, "strain", r"$\varepsilon(t)$"
