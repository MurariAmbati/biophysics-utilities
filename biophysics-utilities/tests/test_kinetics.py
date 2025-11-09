"""Tests for kinetic system."""

import pytest
import numpy as np
from kinetics_playground.core.model import ReactionModel
from kinetics_playground.core.kinetics import KineticSystem, MassActionKinetics


class TestKineticSystem:
    """Test suite for kinetic system."""
    
    def test_mass_action_rate(self):
        """Test mass action kinetics."""
        model = ReactionModel()
        model.add_species('A', initial_concentration=1.0)
        model.add_species('B', initial_concentration=2.0)
        model.add_species('C', initial_concentration=0.0)
        model.add_reaction({'A': 1, 'B': 1}, {'C': 1}, rate_constant=0.1)
        
        system = KineticSystem(model)
        rate_exprs = system.get_rate_expressions()
        
        assert len(rate_exprs) == 1
    
    def test_ode_system_generation(self):
        """Test ODE system generation."""
        model = ReactionModel()
        model.add_species('A', initial_concentration=1.0)
        model.add_species('B', initial_concentration=0.0)
        model.add_reaction({'A': 1}, {'B': 1}, rate_constant=1.0)
        
        system = KineticSystem(model)
        ode_system = system.get_ode_system()
        
        assert len(ode_system) == 2
    
    def test_numerical_function(self):
        """Test numerical function generation."""
        model = ReactionModel()
        model.add_species('A', initial_concentration=1.0)
        model.add_species('B', initial_concentration=0.0)
        model.add_reaction({'A': 1}, {'B': 1}, rate_constant=1.0)
        
        system = KineticSystem(model)
        dydt = system.to_numerical_function()
        
        # Test function call
        y = np.array([1.0, 0.0])
        result = dydt(0, y)
        
        assert len(result) == 2
        assert result[0] < 0  # A should decrease
        assert result[1] > 0  # B should increase


if __name__ == '__main__':
    pytest.main([__file__])
