"""
ODE integration engine using SciPy's solve_ivp.

Provides adaptive time-stepping, multiple integration methods, and
event detection for chemical reaction networks.
"""

import numpy as np
from scipy.integrate import solve_ivp
from typing import Callable, Optional, Tuple, Dict, List, Any
from dataclasses import dataclass, field
import warnings


@dataclass
class IntegrationResult:
    """Container for integration results."""
    t: np.ndarray  # Time points
    y: np.ndarray  # Species concentrations (shape: num_species x num_timepoints)
    success: bool
    message: str
    nfev: int = 0  # Number of function evaluations
    njev: int = 0  # Number of Jacobian evaluations
    nlu: int = 0   # Number of LU decompositions
    species_names: List[str] = field(default_factory=list)
    
    def get_species(self, name: str) -> np.ndarray:
        """
        Get time series for a specific species.
        
        Args:
            name: Species name
            
        Returns:
            Array of concentrations over time
        """
        if name not in self.species_names:
            raise ValueError(f"Species '{name}' not found in results")
        
        idx = self.species_names.index(name)
        return self.y[idx, :]
    
    def to_dict(self) -> Dict[str, np.ndarray]:
        """
        Convert results to dictionary format.
        
        Returns:
            Dictionary with 't' and species names as keys
        """
        result_dict = {'t': self.t}
        for name in self.species_names:
            result_dict[name] = self.get_species(name)
        return result_dict
    
    def final_state(self) -> Dict[str, float]:
        """Get final concentrations as dictionary."""
        return {
            name: float(self.y[i, -1])
            for i, name in enumerate(self.species_names)
        }


class ODEIntegrator:
    """
    Numerical ODE integrator for reaction kinetics.
    
    Wraps SciPy's solve_ivp with convenient defaults and options
    suitable for chemical reaction networks.
    """
    
    AVAILABLE_METHODS = ['RK45', 'RK23', 'DOP853', 'Radau', 'BDF', 'LSODA']
    
    def __init__(
        self,
        dydt: Callable[[float, np.ndarray], np.ndarray],
        species_names: List[str],
        method: str = 'LSODA',
        rtol: float = 1e-6,
        atol: float = 1e-9,
        max_step: float = np.inf,
        dense_output: bool = False
    ):
        """
        Initialize ODE integrator.
        
        Args:
            dydt: Function computing derivatives with signature f(t, y) -> dy/dt
            species_names: List of species names corresponding to y components
            method: Integration method ('RK45', 'LSODA', 'BDF', etc.)
            rtol: Relative tolerance
            atol: Absolute tolerance
            max_step: Maximum allowed step size
            dense_output: Whether to compute continuous solution
        """
        self.dydt = dydt
        self.species_names = species_names
        self.method = method
        self.rtol = rtol
        self.atol = atol
        self.max_step = max_step
        self.dense_output = dense_output
        
        # Validate method
        if method not in self.AVAILABLE_METHODS:
            raise ValueError(
                f"Unknown method '{method}'. "
                f"Available: {', '.join(self.AVAILABLE_METHODS)}"
            )
    
    def integrate(
        self,
        y0: np.ndarray,
        t_span: Tuple[float, float],
        t_eval: Optional[np.ndarray] = None,
        events: Optional[List[Callable]] = None,
        args: Optional[Tuple] = None
    ) -> IntegrationResult:
        """
        Perform time integration.
        
        Args:
            y0: Initial conditions (array of length num_species)
            t_span: Time interval (t_start, t_end)
            t_eval: Specific time points to evaluate solution
            events: Event functions for detection
            args: Additional arguments to pass to dydt
            
        Returns:
            IntegrationResult object
        """
        # Validate initial conditions
        if len(y0) != len(self.species_names):
            raise ValueError(
                f"Initial conditions size ({len(y0)}) doesn't match "
                f"number of species ({len(self.species_names)})"
            )
        
        # Check for negative concentrations
        if np.any(y0 < 0):
            warnings.warn(
                "Negative initial concentrations detected. "
                "This may cause integration issues."
            )
        
        # Perform integration
        sol = solve_ivp(
            self.dydt,
            t_span,
            y0,
            method=self.method,
            t_eval=t_eval,
            dense_output=self.dense_output,
            events=events,
            rtol=self.rtol,
            atol=self.atol,
            max_step=self.max_step,
            args=args or ()
        )
        
        # Package results
        result = IntegrationResult(
            t=sol.t,
            y=sol.y,
            success=sol.success,
            message=sol.message,
            nfev=sol.nfev,
            njev=sol.njev,
            nlu=sol.nlu,
            species_names=self.species_names.copy()
        )
        
        return result
    
    def integrate_to_steady_state(
        self,
        y0: np.ndarray,
        max_time: float = 1e6,
        steady_state_tol: float = 1e-6,
        check_interval: float = 100.0
    ) -> IntegrationResult:
        """
        Integrate until steady state is reached.
        
        Args:
            y0: Initial conditions
            max_time: Maximum simulation time
            steady_state_tol: Tolerance for steady state detection
            check_interval: Time between steady state checks
            
        Returns:
            IntegrationResult at steady state
        """
        # Define event to detect steady state
        def steady_state_event(t, y):
            """Event function: returns 0 when steady state reached."""
            dydt_val = self.dydt(t, y)
            return np.max(np.abs(dydt_val)) - steady_state_tol
        
        steady_state_event.terminal = True
        steady_state_event.direction = -1
        
        result = self.integrate(
            y0,
            t_span=(0, max_time),
            events=[steady_state_event]
        )
        
        if not result.success:
            warnings.warn(
                f"Integration did not reach steady state within {max_time} time units"
            )
        
        return result
    
    def sensitivity_analysis(
        self,
        y0: np.ndarray,
        t_span: Tuple[float, float],
        parameter_indices: List[int],
        perturbation: float = 0.01
    ) -> Dict[int, IntegrationResult]:
        """
        Perform simple sensitivity analysis by perturbing parameters.
        
        Args:
            y0: Initial conditions
            t_span: Time interval
            parameter_indices: Which parameters (species) to perturb
            perturbation: Fractional perturbation amount
            
        Returns:
            Dictionary mapping parameter index to perturbed result
        """
        results = {}
        
        for idx in parameter_indices:
            y0_perturbed = y0.copy()
            y0_perturbed[idx] *= (1.0 + perturbation)
            
            result = self.integrate(y0_perturbed, t_span)
            results[idx] = result
        
        return results


def create_time_points(t_start: float, t_end: float, num_points: int = 1000,
                      log_scale: bool = False) -> np.ndarray:
    """
    Create array of time points for evaluation.
    
    Args:
        t_start: Start time
        t_end: End time
        num_points: Number of points
        log_scale: Use logarithmic spacing
        
    Returns:
        Array of time points
    """
    if log_scale and t_start > 0:
        return np.logspace(np.log10(t_start), np.log10(t_end), num_points)
    else:
        return np.linspace(t_start, t_end, num_points)


def check_stiffness(dydt: Callable, y0: np.ndarray, t: float = 0.0) -> Dict[str, Any]:
    """
    Heuristic check for stiffness of ODE system.
    
    Estimates the Jacobian and computes its eigenvalues to assess stiffness.
    
    Args:
        dydt: ODE function
        y0: State vector
        t: Time point
        
    Returns:
        Dictionary with stiffness metrics
    """
    n = len(y0)
    eps = 1e-8
    
    # Estimate Jacobian by finite differences
    J = np.zeros((n, n))
    f0 = dydt(t, y0)
    
    for i in range(n):
        y_pert = y0.copy()
        y_pert[i] += eps
        f_pert = dydt(t, y_pert)
        J[:, i] = (f_pert - f0) / eps
    
    # Compute eigenvalues
    eigenvalues = np.linalg.eigvals(J)
    
    # Stiffness ratio: |max eigenvalue| / |min eigenvalue|
    abs_eigs = np.abs(eigenvalues)
    stiffness_ratio = np.max(abs_eigs) / np.min(abs_eigs[abs_eigs > 1e-10])
    
    # System is considered stiff if ratio > 1000
    is_stiff = stiffness_ratio > 1000
    
    return {
        'is_stiff': is_stiff,
        'stiffness_ratio': stiffness_ratio,
        'max_eigenvalue': np.max(abs_eigs),
        'min_eigenvalue': np.min(abs_eigs[abs_eigs > 1e-10]) if np.any(abs_eigs > 1e-10) else 0,
        'eigenvalues': eigenvalues,
        'recommended_method': 'BDF' if is_stiff else 'RK45'
    }
