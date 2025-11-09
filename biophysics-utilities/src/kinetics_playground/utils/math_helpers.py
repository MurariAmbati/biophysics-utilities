"""
Mathematical helper functions for analysis and computation.

Includes Jacobian computation, sensitivity analysis, and stability analysis.
"""

import numpy as np
from typing import Callable, Dict, List, Tuple, Optional
from scipy.linalg import eig


def jacobian(
    func: Callable[[np.ndarray], np.ndarray],
    x: np.ndarray,
    eps: float = 1e-8
) -> np.ndarray:
    """
    Compute Jacobian matrix using finite differences.
    
    Args:
        func: Function f: R^n -> R^m
        x: Point at which to evaluate Jacobian
        eps: Step size for finite differences
        
    Returns:
        Jacobian matrix J[i,j] = ∂f_i/∂x_j
    """
    n = len(x)
    f0 = func(x)
    m = len(f0)
    
    J = np.zeros((m, n))
    
    for j in range(n):
        x_pert = x.copy()
        x_pert[j] += eps
        f_pert = func(x_pert)
        J[:, j] = (f_pert - f0) / eps
    
    return J


def hessian(
    func: Callable[[np.ndarray], float],
    x: np.ndarray,
    eps: float = 1e-5
) -> np.ndarray:
    """
    Compute Hessian matrix using finite differences.
    
    Args:
        func: Scalar function f: R^n -> R
        x: Point at which to evaluate Hessian
        eps: Step size for finite differences
        
    Returns:
        Hessian matrix H[i,j] = ∂²f/∂x_i∂x_j
    """
    n = len(x)
    H = np.zeros((n, n))
    f0 = func(x)
    
    for i in range(n):
        for j in range(i, n):
            # Compute second derivative using central differences
            x_pp = x.copy()
            x_pp[i] += eps
            x_pp[j] += eps
            
            x_pm = x.copy()
            x_pm[i] += eps
            x_pm[j] -= eps
            
            x_mp = x.copy()
            x_mp[i] -= eps
            x_mp[j] += eps
            
            x_mm = x.copy()
            x_mm[i] -= eps
            x_mm[j] -= eps
            
            H[i, j] = (func(x_pp) - func(x_pm) - func(x_mp) + func(x_mm)) / (4 * eps * eps)
            
            if i != j:
                H[j, i] = H[i, j]  # Symmetry
    
    return H


def sensitivity_matrix(
    dydt: Callable[[float, np.ndarray], np.ndarray],
    t: float,
    y: np.ndarray,
    parameter_indices: Optional[List[int]] = None
) -> np.ndarray:
    """
    Compute sensitivity matrix ∂(dy/dt)/∂y.
    
    This is the Jacobian of the ODE right-hand side with respect to state variables.
    
    Args:
        dydt: ODE function
        t: Time point
        y: State vector
        parameter_indices: Optional list of state indices to compute sensitivity for
        
    Returns:
        Sensitivity matrix
    """
    if parameter_indices is None:
        parameter_indices = list(range(len(y)))
    
    return jacobian(lambda y_var: dydt(t, y_var), y)


def find_steady_states(
    dydt: Callable[[float, np.ndarray], np.ndarray],
    initial_guesses: List[np.ndarray],
    tol: float = 1e-6
) -> List[np.ndarray]:
    """
    Find steady states by solving dy/dt = 0.
    
    Args:
        dydt: ODE function
        initial_guesses: List of initial guesses for root finding
        tol: Tolerance for steady state
        
    Returns:
        List of steady state vectors
    """
    from scipy.optimize import fsolve
    
    steady_states = []
    
    for guess in initial_guesses:
        # Solve dy/dt = 0
        def residual(y):
            return dydt(0, y)  # Time doesn't matter for autonomous systems
        
        solution = fsolve(residual, guess, full_output=True)
        y_ss = solution[0]
        info = solution[1]
        
        # Check if it converged to a steady state
        residual_norm = np.linalg.norm(residual(y_ss))
        
        if residual_norm < tol:
            # Check if this is a new steady state
            is_new = True
            for existing_ss in steady_states:
                if np.linalg.norm(y_ss - existing_ss) < tol:
                    is_new = False
                    break
            
            if is_new:
                steady_states.append(y_ss)
    
    return steady_states


def analyze_stability(
    dydt: Callable[[float, np.ndarray], np.ndarray],
    steady_state: np.ndarray
) -> Dict[str, any]:
    """
    Analyze stability of a steady state using linearization.
    
    Computes eigenvalues of the Jacobian at the steady state.
    
    Args:
        dydt: ODE function
        steady_state: Steady state point to analyze
        
    Returns:
        Dictionary with stability information
    """
    # Compute Jacobian at steady state
    J = jacobian(lambda y: dydt(0, y), steady_state)
    
    # Compute eigenvalues
    eigenvalues, eigenvectors = eig(J)
    
    # Determine stability
    real_parts = np.real(eigenvalues)
    max_real = np.max(real_parts)
    
    if max_real < -1e-10:
        stability = 'stable'
    elif max_real > 1e-10:
        stability = 'unstable'
    else:
        stability = 'marginal'
    
    # Check for oscillations (complex eigenvalues with non-zero imaginary part)
    has_oscillations = np.any(np.abs(np.imag(eigenvalues)) > 1e-10)
    
    return {
        'stability': stability,
        'eigenvalues': eigenvalues,
        'eigenvectors': eigenvectors,
        'max_real_eigenvalue': max_real,
        'has_oscillations': has_oscillations,
        'jacobian': J
    }


def lyapunov_exponent(
    trajectory: np.ndarray,
    dt: float,
    dimension: Optional[int] = None
) -> float:
    """
    Estimate maximum Lyapunov exponent from trajectory.
    
    Positive exponent indicates chaos.
    
    Args:
        trajectory: Time series data (shape: time x dimension)
        dt: Time step
        dimension: Embedding dimension (default: auto-detect)
        
    Returns:
        Maximum Lyapunov exponent
    """
    # Simplified implementation - for demonstration
    # Real implementation would use method of Wolf et al. or Rosenstein et al.
    
    if dimension is None:
        dimension = trajectory.shape[1] if trajectory.ndim > 1 else 1
    
    # Compute neighboring trajectories
    # This is a placeholder - proper implementation requires more sophisticated algorithm
    return 0.0  # Placeholder


def compute_divergence(
    dydt: Callable[[float, np.ndarray], np.ndarray],
    t: float,
    y: np.ndarray
) -> float:
    """
    Compute divergence of the vector field: ∇·f = Σ ∂f_i/∂y_i
    
    Args:
        dydt: ODE function
        t: Time
        y: State vector
        
    Returns:
        Divergence value
    """
    J = jacobian(lambda y_var: dydt(t, y_var), y)
    return np.trace(J)


def parameter_sensitivity(
    simulate: Callable[[Dict[str, float]], np.ndarray],
    parameters: Dict[str, float],
    observable: Callable[[np.ndarray], float],
    perturbation: float = 0.01
) -> Dict[str, float]:
    """
    Compute sensitivity of an observable to parameter changes.
    
    Args:
        simulate: Function that takes parameters and returns trajectory
        parameters: Dictionary of parameter values
        observable: Function that computes observable from trajectory
        perturbation: Fractional parameter perturbation
        
    Returns:
        Dictionary of sensitivities for each parameter
    """
    # Baseline simulation
    baseline_trajectory = simulate(parameters)
    baseline_value = observable(baseline_trajectory)
    
    sensitivities = {}
    
    for param_name, param_value in parameters.items():
        # Perturb parameter
        perturbed_params = parameters.copy()
        perturbed_params[param_name] = param_value * (1 + perturbation)
        
        # Simulate with perturbed parameter
        perturbed_trajectory = simulate(perturbed_params)
        perturbed_value = observable(perturbed_trajectory)
        
        # Compute normalized sensitivity
        sensitivity = (perturbed_value - baseline_value) / (perturbation * baseline_value)
        sensitivities[param_name] = sensitivity
    
    return sensitivities


def moving_average(data: np.ndarray, window_size: int) -> np.ndarray:
    """
    Compute moving average for smoothing time series.
    
    Args:
        data: 1D array of data
        window_size: Size of moving average window
        
    Returns:
        Smoothed data
    """
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')


def autocorrelation(data: np.ndarray, max_lag: Optional[int] = None) -> np.ndarray:
    """
    Compute autocorrelation function.
    
    Args:
        data: 1D time series data
        max_lag: Maximum lag to compute (default: len(data)//2)
        
    Returns:
        Autocorrelation values
    """
    if max_lag is None:
        max_lag = len(data) // 2
    
    # Normalize data
    data_normalized = data - np.mean(data)
    
    # Compute autocorrelation
    autocorr = np.correlate(data_normalized, data_normalized, mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    autocorr = autocorr / autocorr[0]  # Normalize
    
    return autocorr[:max_lag]
