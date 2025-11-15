"""High-level orchestration for viscoelastic simulations."""

from __future__ import annotations

from typing import Callable

import numpy as np

from .models import (
    Response,
    SimulationConfig,
    kelvin_voigt_creep,
    maxwell_creep,
    maxwell_relaxation,
)

ComputeFn = Callable[[np.ndarray, float, float, float], tuple[np.ndarray, float, str, str]]


def compute_response(config: SimulationConfig) -> Response:
    """Validate configuration and compute the requested response."""

    _validate_config(config)
    time = _build_time_vector(config.t_max, config.dt)

    if config.model == "maxwell" and config.mode == "relaxation":
        response, tau, quantity, label = maxwell_relaxation(time, config.E, config.eta, config.strain0 or 0.0)
    elif config.model == "maxwell" and config.mode == "creep":
        response, tau, quantity, label = maxwell_creep(time, config.E, config.eta, config.stress0 or 0.0)
    elif config.model == "kelvin_voigt" and config.mode == "creep":
        response, tau, quantity, label = kelvin_voigt_creep(time, config.E, config.eta, config.stress0 or 0.0)
    else:
        raise ValueError("Kelvin–Voigt relaxation is not supported; strain relaxes only under unloading.")

    return Response(time=time, response=response, quantity=quantity, tau=tau, label=label)


def _validate_config(config: SimulationConfig) -> None:
    for field_name in ("E", "eta", "t_max", "dt"):
        value = getattr(config, field_name)
        if value is None or value <= 0:
            raise ValueError(f"{field_name} must be positive; received {value!r}")

    if config.dt > config.t_max:
        raise ValueError("dt must be smaller than t_max to form a useful time grid")

    if config.mode == "relaxation":
        if config.strain0 is None:
            raise ValueError("relaxation mode requires --strain0 (constant strain)")
    elif config.mode == "creep":
        if config.stress0 is None:
            raise ValueError("creep mode requires --stress0 (constant stress)")
    else:
        raise ValueError(f"Unknown experiment mode: {config.mode}")

    if config.model not in {"maxwell", "kelvin_voigt"}:
        raise ValueError(f"Unknown model: {config.model}")

    if config.model == "kelvin_voigt" and config.mode == "relaxation":
        raise ValueError("Kelvin–Voigt relaxation is not well-defined for the imposed-load scenario")


def _build_time_vector(t_max: float, dt: float) -> np.ndarray:
    # include final point by padding half-step
    return np.arange(0.0, t_max + 0.5 * dt, dt, dtype=float)
