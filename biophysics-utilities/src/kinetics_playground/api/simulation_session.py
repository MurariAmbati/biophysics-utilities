"""
Simulation session for managing multiple related simulations.

Useful for organizing parameter sweeps, sensitivity analysis, and comparative studies.
"""

from typing import List, Dict, Optional
import numpy as np
from kinetics_playground.api.reaction_network import ReactionNetwork
from kinetics_playground.core.integrator import IntegrationResult
from kinetics_playground.utils.logger import get_logger

logger = get_logger()


class SimulationSession:
    """
    Manages a collection of related simulations.
    
    Useful for parameter exploration, sensitivity analysis, and batch processing.
    """
    
    def __init__(self, network: ReactionNetwork, name: str = "session"):
        """
        Initialize simulation session.
        
        Args:
            network: ReactionNetwork to simulate
            name: Session name
        """
        self.network = network
        self.name = name
        self.results: List[IntegrationResult] = []
        self.metadata: List[Dict] = []
    
    def add_simulation(
        self,
        initial_conditions: Dict[str, float],
        metadata: Optional[Dict] = None,
        **kwargs
    ) -> IntegrationResult:
        """
        Run and store a simulation.
        
        Args:
            initial_conditions: Initial concentrations
            metadata: Optional metadata for this simulation
            **kwargs: Arguments passed to network.simulate()
            
        Returns:
            IntegrationResult
        """
        result = self.network.simulate(initial_conditions, **kwargs)
        
        self.results.append(result)
        self.metadata.append(metadata or {})
        
        return result
    
    def parameter_sweep(
        self,
        parameter: str,
        values: np.ndarray,
        initial_conditions: Dict[str, float],
        **kwargs
    ) -> List[IntegrationResult]:
        """
        Run parameter sweep and store results.
        
        Args:
            parameter: Parameter to sweep
            values: Parameter values
            initial_conditions: Base initial conditions
            **kwargs: Simulation arguments
            
        Returns:
            List of results
        """
        results = self.network.parameter_sweep(
            parameter, values, initial_conditions, **kwargs
        )
        
        # Store results with metadata
        for value, result in zip(values, results):
            self.results.append(result)
            self.metadata.append({
                'type': 'parameter_sweep',
                'parameter': parameter,
                'value': float(value)
            })
        
        logger.info(f"Parameter sweep stored: {len(results)} simulations")
        return results
    
    def sensitivity_analysis(
        self,
        base_initial_conditions: Dict[str, float],
        perturbation: float = 0.01,
        **kwargs
    ) -> Dict[str, IntegrationResult]:
        """
        Perform sensitivity analysis on initial conditions.
        
        Args:
            base_initial_conditions: Baseline initial conditions
            perturbation: Fractional perturbation
            **kwargs: Simulation arguments
            
        Returns:
            Dict mapping species to perturbed results
        """
        sensitivities = {}
        
        # Run baseline
        baseline = self.network.simulate(base_initial_conditions, **kwargs)
        self.results.append(baseline)
        self.metadata.append({'type': 'sensitivity_baseline'})
        
        # Perturb each species
        for species in base_initial_conditions.keys():
            perturbed_ic = base_initial_conditions.copy()
            perturbed_ic[species] *= (1.0 + perturbation)
            
            result = self.network.simulate(perturbed_ic, **kwargs)
            sensitivities[species] = result
            
            self.results.append(result)
            self.metadata.append({
                'type': 'sensitivity_analysis',
                'perturbed_species': species,
                'perturbation': perturbation
            })
        
        logger.info(f"Sensitivity analysis complete: {len(sensitivities)} perturbations")
        return sensitivities
    
    def get_results(self, filter_by: Optional[Dict] = None) -> List[IntegrationResult]:
        """
        Get results, optionally filtered by metadata.
        
        Args:
            filter_by: Dict of metadata key-value pairs to filter by
            
        Returns:
            List of matching results
        """
        if filter_by is None:
            return self.results
        
        filtered = []
        for result, meta in zip(self.results, self.metadata):
            if all(meta.get(k) == v for k, v in filter_by.items()):
                filtered.append(result)
        
        return filtered
    
    def clear(self):
        """Clear all stored results and metadata."""
        self.results.clear()
        self.metadata.clear()
        logger.info("Session cleared")
    
    def export_all(self, directory: str, prefix: str = "sim"):
        """
        Export all results to CSV files.
        
        Args:
            directory: Output directory
            prefix: Filename prefix
        """
        from pathlib import Path
        from kinetics_playground.utils.exporters import export_results_to_csv
        
        output_dir = Path(directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for idx, result in enumerate(self.results):
            filename = output_dir / f"{prefix}_{idx:04d}.csv"
            export_results_to_csv(result, str(filename))
        
        logger.info(f"Exported {len(self.results)} results to {directory}")
    
    def summary(self) -> str:
        """Generate session summary."""
        lines = [
            f"Simulation Session: {self.name}",
            f"  Network: {self.network.name}",
            f"  Total simulations: {len(self.results)}",
            ""
        ]
        
        # Count by type
        types = {}
        for meta in self.metadata:
            t = meta.get('type', 'unknown')
            types[t] = types.get(t, 0) + 1
        
        if types:
            lines.append("Simulation types:")
            for sim_type, count in types.items():
                lines.append(f"  {sim_type}: {count}")
        
        return "\n".join(lines)
    
    def __repr__(self):
        return f"SimulationSession(name='{self.name}', simulations={len(self.results)})"
