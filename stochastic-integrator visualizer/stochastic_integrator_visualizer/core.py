"""
Core stochastic integration methods for solving SDEs.

Implements:
- Euler–Maruyama method
- Milstein method
- Deterministic solver (b=0)
- Ensemble simulations
"""

import numpy as np
from typing import Callable, Optional, Tuple, List
from .constants import DEFAULT_X0, DEFAULT_DT, DEFAULT_STEPS, DEFAULT_SEED


def euler_maruyama(
    a: Callable[[float, float], float],
    b: Callable[[float, float], float],
    x0: float = DEFAULT_X0,
    dt: float = DEFAULT_DT,
    steps: int = DEFAULT_STEPS,
    seed: Optional[int] = DEFAULT_SEED,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Euler–Maruyama method for solving SDEs.
    
    Solves: dx_t = a(x_t, t) dt + b(x_t, t) dW_t
    
    Update rule:
    x_{t+Δt} = x_t + a(x_t, t)Δt + b(x_t, t)√Δt ξ_t
    where ξ_t ~ N(0,1)
    
    Parameters
    ----------
    a : callable
        Drift function a(x, t)
    b : callable
        Diffusion function b(x, t)
    x0 : float
        Initial condition
    dt : float
        Time step
    steps : int
        Number of steps
    seed : int, optional
        Random seed for reproducibility
        
    Returns
    -------
    t : np.ndarray
        Time array
    x : np.ndarray
        Solution trajectory
    """
    rng = np.random.default_rng(seed)
    
    # Initialize arrays
    x = np.zeros(steps)
    t = np.arange(steps) * dt
    x[0] = x0
    
    # Integration loop
    for i in range(steps - 1):
        # Wiener process increment: dW = √dt * ξ where ξ ~ N(0,1)
        dw = np.sqrt(dt) * rng.normal()
        
        # Euler–Maruyama update
        drift = a(x[i], t[i]) * dt
        diffusion = b(x[i], t[i]) * dw
        x[i + 1] = x[i] + drift + diffusion
    
    return t, x


def milstein(
    a: Callable[[float, float], float],
    b: Callable[[float, float], float],
    b_prime: Callable[[float, float], float],
    x0: float = DEFAULT_X0,
    dt: float = DEFAULT_DT,
    steps: int = DEFAULT_STEPS,
    seed: Optional[int] = DEFAULT_SEED,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Milstein method for solving SDEs with higher-order accuracy.
    
    Solves: dx_t = a(x_t, t) dt + b(x_t, t) dW_t
    
    Update rule:
    x_{t+Δt} = x_t + a(x_t, t)Δt + b(x_t, t)ΔW_t + 0.5 * b(x_t, t) * b'(x_t, t) * (ΔW_t^2 - Δt)
    
    Parameters
    ----------
    a : callable
        Drift function a(x, t)
    b : callable
        Diffusion function b(x, t)
    b_prime : callable
        Derivative of diffusion function with respect to x: ∂b/∂x
    x0 : float
        Initial condition
    dt : float
        Time step
    steps : int
        Number of steps
    seed : int, optional
        Random seed for reproducibility
        
    Returns
    -------
    t : np.ndarray
        Time array
    x : np.ndarray
        Solution trajectory
    """
    rng = np.random.default_rng(seed)
    
    # Initialize arrays
    x = np.zeros(steps)
    t = np.arange(steps) * dt
    x[0] = x0
    
    # Integration loop
    for i in range(steps - 1):
        # Wiener process increment
        dw = np.sqrt(dt) * rng.normal()
        
        # Current values
        drift = a(x[i], t[i])
        diffusion = b(x[i], t[i])
        diffusion_deriv = b_prime(x[i], t[i])
        
        # Milstein correction term
        correction = 0.5 * diffusion * diffusion_deriv * (dw**2 - dt)
        
        # Milstein update
        x[i + 1] = x[i] + drift * dt + diffusion * dw + correction
    
    return t, x


def deterministic_solver(
    a: Callable[[float, float], float],
    x0: float = DEFAULT_X0,
    dt: float = DEFAULT_DT,
    steps: int = DEFAULT_STEPS,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Deterministic ODE solver (b=0).
    
    Solves: dx_t = a(x_t, t) dt
    
    Parameters
    ----------
    a : callable
        Drift function a(x, t)
    x0 : float
        Initial condition
    dt : float
        Time step
    steps : int
        Number of steps
        
    Returns
    -------
    t : np.ndarray
        Time array
    x : np.ndarray
        Solution trajectory
    """
    # Initialize arrays
    x = np.zeros(steps)
    t = np.arange(steps) * dt
    x[0] = x0
    
    # Simple Euler method for deterministic case
    for i in range(steps - 1):
        x[i + 1] = x[i] + a(x[i], t[i]) * dt
    
    return t, x


def run_ensemble(
    method: str,
    a: Callable[[float, float], float],
    b: Callable[[float, float], float],
    x0: float = DEFAULT_X0,
    dt: float = DEFAULT_DT,
    steps: int = DEFAULT_STEPS,
    num_trajectories: int = 100,
    base_seed: Optional[int] = DEFAULT_SEED,
    b_prime: Optional[Callable[[float, float], float]] = None,
) -> Tuple[np.ndarray, List[np.ndarray], np.ndarray]:
    """
    Run multiple trajectories to visualize stochastic variance.
    
    Parameters
    ----------
    method : str
        Integration method: "euler-maruyama", "milstein", or "deterministic"
    a : callable
        Drift function a(x, t)
    b : callable
        Diffusion function b(x, t)
    x0 : float
        Initial condition
    dt : float
        Time step
    steps : int
        Number of steps
    num_trajectories : int
        Number of trajectories to simulate
    base_seed : int, optional
        Base random seed (each trajectory gets base_seed + i)
    b_prime : callable, optional
        Derivative of b for Milstein method
        
    Returns
    -------
    t : np.ndarray
        Time array (shared across all trajectories)
    trajectories : list of np.ndarray
        List of solution trajectories
    final_values : np.ndarray
        Array of final values from each trajectory
    """
    trajectories = []
    final_values = np.zeros(num_trajectories)
    t = None
    
    for i in range(num_trajectories):
        seed = None if base_seed is None else base_seed + i
        
        if method == "euler-maruyama":
            t, x = euler_maruyama(a, b, x0, dt, steps, seed)
        elif method == "milstein":
            if b_prime is None:
                raise ValueError("Milstein method requires b_prime (derivative of diffusion)")
            t, x = milstein(a, b, b_prime, x0, dt, steps, seed)
        elif method == "deterministic":
            t, x = deterministic_solver(a, x0, dt, steps)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        trajectories.append(x)
        final_values[i] = x[-1]
    
    return t, trajectories, final_values


# Common drift and diffusion functions for testing

def linear_drift(x: float, t: float, a: float = 1.0) -> float:
    """Linear drift: a(x,t) = a * x"""
    return a * x


def constant_drift(x: float, t: float, a: float = 1.0) -> float:
    """Constant drift: a(x,t) = a"""
    return a


def linear_diffusion(x: float, t: float, b: float = 0.3) -> float:
    """Linear diffusion: b(x,t) = b * x"""
    return b * x


def constant_diffusion(x: float, t: float, b: float = 0.3) -> float:
    """Constant diffusion: b(x,t) = b"""
    return b


def linear_diffusion_derivative(x: float, t: float, b: float = 0.3) -> float:
    """Derivative of linear diffusion: ∂b/∂x = b"""
    return b


def constant_diffusion_derivative(x: float, t: float, b: float = 0.3) -> float:
    """Derivative of constant diffusion: ∂b/∂x = 0"""
    return 0.0


# Factory functions for creating drift/diffusion with parameters

def make_constant_drift(a: float) -> Callable[[float, float], float]:
    """Create a constant drift function with coefficient a."""
    return lambda x, t: a


def make_linear_drift(a: float) -> Callable[[float, float], float]:
    """Create a linear drift function with coefficient a."""
    return lambda x, t: a * x


def make_constant_diffusion(b: float) -> Callable[[float, float], float]:
    """Create a constant diffusion function with coefficient b."""
    return lambda x, t: b


def make_linear_diffusion(b: float) -> Callable[[float, float], float]:
    """Create a linear diffusion function with coefficient b."""
    return lambda x, t: b * x


def make_constant_diffusion_derivative(b: float) -> Callable[[float, float], float]:
    """Create derivative for constant diffusion (always 0)."""
    return lambda x, t: 0.0


def make_linear_diffusion_derivative(b: float) -> Callable[[float, float], float]:
    """Create derivative for linear diffusion."""
    return lambda x, t: b
