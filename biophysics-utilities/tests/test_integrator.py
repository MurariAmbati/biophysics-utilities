"""Tests for ODE integrator."""

import pytest
import numpy as np
from kinetics_playground.core.integrator import ODEIntegrator


class TestODEIntegrator:
    """Test suite for ODE integrator."""
    
    def test_simple_decay(self):
        """Test simple exponential decay."""
        # dy/dt = -k*y
        k = 0.1
        def dydt(t, y):
            return np.array([-k * y[0]])
        
        integrator = ODEIntegrator(
            dydt=dydt,
            species_names=['A'],
            method='RK45'
        )
        
        y0 = np.array([1.0])
        result = integrator.integrate(y0, t_span=(0, 10))
        
        assert result.success
        assert len(result.t) > 0
        assert result.y[0, -1] < y0[0]  # Should decay
    
    def test_integration_methods(self):
        """Test different integration methods."""
        def dydt(t, y):
            return np.array([-0.1 * y[0]])
        
        y0 = np.array([1.0])
        
        for method in ['RK45', 'LSODA', 'BDF']:
            integrator = ODEIntegrator(
                dydt=dydt,
                species_names=['A'],
                method=method
            )
            result = integrator.integrate(y0, t_span=(0, 10))
            assert result.success


if __name__ == '__main__':
    pytest.main([__file__])
