"""
Force field evaluation and comparison logic.

Evaluates potential energy and forces over distance ranges,
finds equilibrium positions, and compares potentials.
"""

import numpy as np
from scipy.optimize import minimize_scalar, brentq
from typing import Dict, List, Tuple, Optional

from .potentials import POTENTIALS
from .derivatives import FORCES


class ForceFieldEvaluator:
    """
    Evaluates and compares classical potential energy functions.
    """
    
    def __init__(self):
        """Initialize the evaluator."""
        self.results = {}
    
    def evaluate_potential(
        self,
        potential_name: str,
        params: Dict,
        r_range: np.ndarray
    ) -> Dict:
        """
        Evaluate a single potential over a distance range.
        
        Parameters
        ----------
        potential_name : str
            Name of potential: 'LJ', 'Morse', or 'Coulomb'
        params : dict
            Parameters for the potential
        r_range : ndarray
            Array of distances [nm]
        
        Returns
        -------
        dict
            Results containing r, U(r), F(r), r_eq, U_min
        """
        # Get potential and force functions
        potential_func = POTENTIALS[potential_name]
        force_func = FORCES[potential_name]
        
        # Compute energy and force over range
        U = potential_func(r_range, **params)
        F = force_func(r_range, **params)
        
        # Find equilibrium distance and minimum energy
        r_eq, U_min = self._find_equilibrium(potential_func, params, r_range)
        
        result = {
            "potential": potential_name,
            "params": params,
            "r": r_range,
            "U": U,
            "F": F,
            "r_eq": r_eq,
            "U_min": U_min,
        }
        
        # Store in results
        self.results[potential_name] = result
        
        return result
    
    def _find_equilibrium(
        self,
        potential_func,
        params: Dict,
        r_range: np.ndarray
    ) -> Tuple[float, float]:
        """
        Find equilibrium distance where F=0 and minimum energy.
        
        Parameters
        ----------
        potential_func : callable
            Potential energy function
        params : dict
            Parameters for the potential
        r_range : ndarray
            Array of distances [nm]
        
        Returns
        -------
        r_eq : float
            Equilibrium distance [nm]
        U_min : float
            Minimum potential energy [eV]
        """
        # Use scipy optimization to find minimum
        bounds = (r_range[0], r_range[-1])
        
        # Define objective function
        def objective(r):
            return potential_func(r, **params)
        
        try:
            result = minimize_scalar(objective, bounds=bounds, method='bounded')
            r_eq = result.x
            U_min = result.fun
        except Exception:
            # Fallback: find minimum from discrete values
            U = potential_func(r_range, **params)
            min_idx = np.argmin(U)
            r_eq = r_range[min_idx]
            U_min = U[min_idx]
        
        return r_eq, U_min
    
    def compare_potentials(
        self,
        potential_names: List[str],
        params_dict: Dict[str, Dict],
        r_range: np.ndarray
    ) -> Dict:
        """
        Compare multiple potentials.
        
        Parameters
        ----------
        potential_names : list of str
            Names of potentials to compare
        params_dict : dict
            Dictionary mapping potential names to parameter dicts
        r_range : ndarray
            Array of distances [nm]
        
        Returns
        -------
        dict
            Comparison results
        """
        comparison = {
            "potentials": [],
            "r_range": r_range,
        }
        
        for name in potential_names:
            if name not in params_dict:
                raise ValueError(f"No parameters provided for potential '{name}'")
            
            result = self.evaluate_potential(name, params_dict[name], r_range)
            comparison["potentials"].append(result)
        
        # Find which has lowest minimum
        min_energies = [(p["potential"], p["U_min"]) for p in comparison["potentials"]]
        min_energies.sort(key=lambda x: x[1])
        comparison["lowest_minimum"] = min_energies[0]
        
        return comparison
    
    def find_crossing_points(
        self,
        potential1_name: str,
        params1: Dict,
        potential2_name: str,
        params2: Dict,
        r_range: np.ndarray
    ) -> List[float]:
        """
        Find distances where two potentials cross (equal energy).
        
        Parameters
        ----------
        potential1_name : str
            Name of first potential
        params1 : dict
            Parameters for first potential
        potential2_name : str
            Name of second potential
        params2 : dict
            Parameters for second potential
        r_range : ndarray
            Array of distances to search
        
        Returns
        -------
        list of float
            Crossing distances [nm]
        """
        func1 = POTENTIALS[potential1_name]
        func2 = POTENTIALS[potential2_name]
        
        # Define difference function
        def difference(r):
            return func1(r, **params1) - func2(r, **params2)
        
        # Evaluate over range
        U_diff = difference(r_range)
        
        # Find sign changes (crossings)
        crossings = []
        for i in range(len(r_range) - 1):
            if U_diff[i] * U_diff[i + 1] < 0:
                # Sign change detected, refine with root finding
                try:
                    r_cross = brentq(difference, r_range[i], r_range[i + 1])
                    crossings.append(r_cross)
                except Exception:
                    pass
        
        return crossings
    
    def evaluate_at_distance(
        self,
        potential_name: str,
        params: Dict,
        r: float
    ) -> Tuple[float, float]:
        """
        Evaluate potential and force at a specific distance.
        
        Parameters
        ----------
        potential_name : str
            Name of potential
        params : dict
            Parameters for the potential
        r : float
            Distance [nm]
        
        Returns
        -------
        U : float
            Potential energy [eV]
        F : float
            Force [eV/nm]
        """
        potential_func = POTENTIALS[potential_name]
        force_func = FORCES[potential_name]
        
        U = potential_func(r, **params)
        F = force_func(r, **params)
        
        return U, F
    
    def get_summary(self, potential_name: str) -> str:
        """
        Get a text summary of evaluation results.
        
        Parameters
        ----------
        potential_name : str
            Name of potential
        
        Returns
        -------
        str
            Summary text
        """
        if potential_name not in self.results:
            return f"No results for potential '{potential_name}'"
        
        result = self.results[potential_name]
        
        summary = f"Potential: {result['potential']}\n"
        summary += f"Parameters: {result['params']}\n"
        summary += f"r_eq = {result['r_eq']:.4f} nm\n"
        summary += f"U_min = {result['U_min']:.6f} eV\n"
        
        return summary


def create_distance_range(rmin: float, rmax: float, npoints: int) -> np.ndarray:
    """
    Create a linear distance range for evaluation.
    
    Parameters
    ----------
    rmin : float
        Minimum distance [nm]
    rmax : float
        Maximum distance [nm]
    npoints : int
        Number of points
    
    Returns
    -------
    ndarray
        Distance array [nm]
    """
    return np.linspace(rmin, rmax, npoints)


def create_log_distance_range(rmin: float, rmax: float, npoints: int) -> np.ndarray:
    """
    Create a logarithmic distance range for evaluation.
    Useful for capturing steep repulsive regions.
    
    Parameters
    ----------
    rmin : float
        Minimum distance [nm]
    rmax : float
        Maximum distance [nm]
    npoints : int
        Number of points
    
    Returns
    -------
    ndarray
        Distance array [nm]
    """
    return np.logspace(np.log10(rmin), np.log10(rmax), npoints)
