"""
High-level ReactionNetwork API for easy model construction and simulation.

This is the main user-facing interface for the kinetics playground.
"""

import numpy as np
from typing import List, Dict, Optional, Union, Tuple
from kinetics_playground.core.parser import ReactionParser, ParsedReaction
from kinetics_playground.core.model import ReactionModel
from kinetics_playground.core.kinetics import KineticSystem, KineticLaw
from kinetics_playground.core.integrator import ODEIntegrator, IntegrationResult
from kinetics_playground.core.validator import ReactionValidator
from kinetics_playground.core.stoichiometry import StoichiometricMatrix
from kinetics_playground.visualization.plotter import Plotter
from kinetics_playground.utils.logger import get_logger

logger = get_logger()


class ReactionNetwork:
    """
    High-level interface for reaction network construction and simulation.
    
    Examples:
        >>> # Create from reaction strings
        >>> reactions = [
        ...     "A + B -> C ; 0.1",
        ...     "C -> A + B ; 0.05"
        ... ]
        >>> network = ReactionNetwork(reactions)
        >>> 
        >>> # Simulate
        >>> result = network.simulate(
        ...     initial_conditions={"A": 1.0, "B": 1.0, "C": 0.0},
        ...     time_span=(0, 100)
        ... )
        >>> 
        >>> # Visualize
        >>> result.plot()
    """
    
    def __init__(
        self,
        reactions: Optional[Union[str, List[str], dict]] = None,
        name: str = "reaction_network"
    ):
        """
        Initialize reaction network.
        
        Args:
            reactions: Reactions in various formats:
                - Single string: "A + B -> C ; 0.1"
                - List of strings: ["A -> B ; 0.1", "B -> C ; 0.2"]
                - Dict/YAML/JSON format
                - None: Create empty network
            name: Network name
        """
        self.name = name
        self.model = ReactionModel()
        self.kinetic_system = None
        self.stoichiometric_matrix = None
        self.parser = ReactionParser()
        
        if reactions is not None:
            self.add_reactions(reactions)
    
    def add_reactions(self, reactions: Union[str, List[str], dict]):
        """
        Add reactions to the network.
        
        Args:
            reactions: Reactions to add
        """
        # Parse reactions
        if isinstance(reactions, str):
            if '\n' in reactions:
                parsed = self.parser.parse_multiple(reactions.strip().split('\n'))
            else:
                parsed = [self.parser.parse_single(reactions)]
        elif isinstance(reactions, list):
            parsed = self.parser.parse_multiple(reactions)
        else:
            raise TypeError(f"Unsupported reaction format: {type(reactions)}")
        
        # Add to model
        for parsed_rxn in parsed:
            self.model.add_reaction(
                reactants=parsed_rxn.reactants,
                products=parsed_rxn.products,
                rate_constant=parsed_rxn.rate_constant,
                reversible=parsed_rxn.reversible,
                kinetic_law=parsed_rxn.kinetic_law,
                parameters=parsed_rxn.parameters
            )
        
        # Rebuild kinetic system
        self._rebuild_kinetic_system()
        
        logger.info(f"Added {len(parsed)} reaction(s) to network")
    
    def set_initial_conditions(self, initial_conditions: Dict[str, float]):
        """
        Set initial concentrations for species.
        
        Args:
            initial_conditions: Dict mapping species names to concentrations
        """
        for species_name, concentration in initial_conditions.items():
            self.model.set_initial_concentration(species_name, concentration)
    
    def set_kinetic_law(self, reaction_index: int, kinetic_law: KineticLaw):
        """
        Set custom kinetic law for a reaction.
        
        Args:
            reaction_index: Index of reaction
            kinetic_law: KineticLaw object
        """
        if self.kinetic_system is None:
            self._rebuild_kinetic_system()
        
        self.kinetic_system.set_kinetic_law(reaction_index, kinetic_law)
    
    def simulate(
        self,
        initial_conditions: Optional[Dict[str, float]] = None,
        time_span: Tuple[float, float] = (0, 100),
        num_points: int = 1000,
        method: str = 'LSODA',
        **kwargs
    ) -> IntegrationResult:
        """
        Run simulation.
        
        Args:
            initial_conditions: Initial concentrations (uses model defaults if None)
            time_span: (t_start, t_end) tuple
            num_points: Number of time points to evaluate
            method: Integration method ('RK45', 'LSODA', 'BDF', etc.)
            **kwargs: Additional arguments for integrator
            
        Returns:
            IntegrationResult object
        """
        # Set initial conditions
        if initial_conditions is not None:
            self.set_initial_conditions(initial_conditions)
        
        # Get initial state
        y0 = self.model.get_initial_concentrations()
        
        # Build kinetic system if needed
        if self.kinetic_system is None:
            self._rebuild_kinetic_system()
        
        # Create numerical function
        dydt = self.kinetic_system.to_numerical_function()
        
        # Create integrator
        integrator = ODEIntegrator(
            dydt=dydt,
            species_names=self.model.get_species_names(),
            method=method,
            **kwargs
        )
        
        # Time points
        t_eval = np.linspace(time_span[0], time_span[1], num_points)
        
        # Integrate
        logger.info(f"Starting simulation: t={time_span[0]} to {time_span[1]}")
        result = integrator.integrate(y0, time_span, t_eval=t_eval)
        
        if result.success:
            logger.info("Simulation completed successfully")
        else:
            logger.warning(f"Simulation issue: {result.message}")
        
        return result
    
    def parameter_sweep(
        self,
        parameter: str,
        values: np.ndarray,
        initial_conditions: Dict[str, float],
        **kwargs
    ) -> List[IntegrationResult]:
        """
        Perform parameter sweep.
        
        Args:
            parameter: Parameter name (e.g., rate constant "k_0")
            values: Array of parameter values to sweep
            initial_conditions: Initial conditions for all runs
            **kwargs: Additional arguments for simulate()
            
        Returns:
            List of IntegrationResult objects
        """
        results = []
        original_value = None
        
        # Determine what parameter to sweep
        if parameter.startswith('k_'):
            # Rate constant
            rxn_idx = int(parameter.split('_')[1])
            original_value = self.model.reactions[rxn_idx].rate_constant
            
            for value in values:
                # Temporarily change rate constant
                self.model.reactions[rxn_idx].rate_constant = value
                self._rebuild_kinetic_system()
                
                result = self.simulate(initial_conditions, **kwargs)
                results.append(result)
            
            # Restore original
            self.model.reactions[rxn_idx].rate_constant = original_value
            self._rebuild_kinetic_system()
        
        elif parameter in self.model._species_map:
            # Initial concentration sweep
            for value in values:
                ic = initial_conditions.copy()
                ic[parameter] = value
                result = self.simulate(ic, **kwargs)
                results.append(result)
        
        else:
            raise ValueError(f"Unknown parameter: {parameter}")
        
        logger.info(f"Parameter sweep complete: {len(values)} simulations")
        return results
    
    def validate(self, raise_on_error: bool = False) -> List:
        """
        Validate the network model.
        
        Args:
            raise_on_error: If True, raise exception on errors
            
        Returns:
            List of validation issues
        """
        validator = ReactionValidator(self.model)
        issues = validator.validate_all()
        
        if issues:
            print(validator.report())
        else:
            logger.info("✓ All validation checks passed")
        
        if raise_on_error and validator.has_errors():
            raise ValueError("Validation failed - see report above")
        
        return issues
    
    def get_species_names(self) -> List[str]:
        """Get list of species names."""
        return self.model.get_species_names()
    
    def get_reaction_names(self) -> List[str]:
        """Get list of reaction names."""
        return self.model.get_reaction_names()
    
    def get_stoichiometric_matrix(self) -> StoichiometricMatrix:
        """Get stoichiometric matrix."""
        if self.stoichiometric_matrix is None:
            self.stoichiometric_matrix = StoichiometricMatrix(self.model)
        return self.stoichiometric_matrix
    
    def get_ode_system(self) -> Dict:
        """Get symbolic ODE system."""
        if self.kinetic_system is None:
            self._rebuild_kinetic_system()
        return self.kinetic_system.get_ode_system()
    
    def export(self, filename: str, format: str = 'auto'):
        """
        Export model to file.
        
        Args:
            filename: Output filename
            format: Format ('sbml', 'latex', 'json', 'matlab', or 'auto' to infer from extension)
        """
        from kinetics_playground.utils.exporters import (
            export_to_sbml, export_to_latex, export_to_json, export_to_matlab
        )
        
        if format == 'auto':
            if filename.endswith('.xml') or filename.endswith('.sbml'):
                format = 'sbml'
            elif filename.endswith('.tex'):
                format = 'latex'
            elif filename.endswith('.json'):
                format = 'json'
            elif filename.endswith('.m'):
                format = 'matlab'
            else:
                raise ValueError(f"Cannot infer format from filename: {filename}")
        
        if format == 'sbml':
            export_to_sbml(self.model, filename, self.name)
        elif format == 'latex':
            export_to_latex(self.model, filename)
        elif format == 'json':
            export_to_json(self.model, filename)
        elif format == 'matlab':
            export_to_matlab(self.model, filename)
        else:
            raise ValueError(f"Unknown format: {format}")
        
        logger.info(f"Exported to {filename} ({format} format)")
    
    def summary(self) -> str:
        """Get network summary."""
        return self.model.summary()
    
    def plot(self, result: IntegrationResult, **kwargs):
        """
        Quick plot of simulation results.
        
        Args:
            result: IntegrationResult from simulate()
            **kwargs: Additional plotting arguments
        """
        plotter = Plotter()
        plotter.plot_time_course(result, **kwargs)
        plotter.show()
    
    def _rebuild_kinetic_system(self):
        """Rebuild kinetic system after model changes."""
        self.kinetic_system = KineticSystem(self.model)
        self.stoichiometric_matrix = None  # Invalidate cache
    
    def __repr__(self):
        return f"ReactionNetwork(species={self.model.num_species()}, reactions={self.model.num_reactions()})"


# Convenience function
def from_reactions(reactions: Union[str, List[str]]) -> ReactionNetwork:
    """
    Create ReactionNetwork from reaction strings.
    
    Args:
        reactions: Reaction string(s)
        
    Returns:
        ReactionNetwork instance
    """
    return ReactionNetwork(reactions)
