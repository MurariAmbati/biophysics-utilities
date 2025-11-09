"""Tests for visualization components."""

import pytest
import numpy as np
from kinetics_playground.core.integrator import IntegrationResult
from kinetics_playground.visualization.plotter import Plotter


class TestPlotter:
    """Test suite for plotter."""
    
    def test_plotter_creation(self):
        """Test plotter initialization."""
        plotter = Plotter()
        assert plotter is not None
    
    def test_time_course_plot(self):
        """Test time course plotting."""
        # Create mock result
        t = np.linspace(0, 10, 100)
        y = np.array([np.exp(-0.1 * t), 1 - np.exp(-0.1 * t)])
        
        result = IntegrationResult(
            t=t,
            y=y,
            success=True,
            message="Test",
            species_names=['A', 'B']
        )
        
        plotter = Plotter()
        ax = plotter.plot_time_course(result)
        
        assert ax is not None


if __name__ == '__main__':
    pytest.main([__file__])
