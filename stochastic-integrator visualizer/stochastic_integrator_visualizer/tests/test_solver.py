"""
Tests for the core SDE solvers.

Tests:
- Euler-Maruyama accuracy
- Milstein accuracy
- Deterministic solver accuracy
- Reproducibility with fixed seeds
- Ensemble statistics
"""

import pytest
import numpy as np
from stochastic_integrator_visualizer.core import (
    euler_maruyama,
    milstein,
    deterministic_solver,
    run_ensemble,
    make_constant_drift,
    make_linear_drift,
    make_constant_diffusion,
    make_linear_diffusion,
    make_constant_diffusion_derivative,
    make_linear_diffusion_derivative,
)


class TestEulerMaruyama:
    """Tests for Euler-Maruyama method."""
    
    def test_basic_integration(self):
        """Test that Euler-Maruyama produces output of correct shape."""
        drift = make_constant_drift(1.0)
        diffusion = make_constant_diffusion(0.3)
        
        t, x = euler_maruyama(drift, diffusion, x0=0.0, dt=0.01, steps=100, seed=42)
        
        assert len(t) == 100
        assert len(x) == 100
        assert x[0] == 0.0
    
    def test_deterministic_case(self):
        """Test Euler-Maruyama with zero diffusion matches deterministic."""
        drift = make_constant_drift(1.0)
        diffusion = make_constant_diffusion(0.0)
        
        t1, x1 = euler_maruyama(drift, diffusion, x0=0.0, dt=0.01, steps=100, seed=42)
        t2, x2 = deterministic_solver(drift, x0=0.0, dt=0.01, steps=100)
        
        np.testing.assert_allclose(x1, x2, rtol=1e-10)
    
    def test_reproducibility(self):
        """Test that same seed produces same results."""
        drift = make_constant_drift(1.0)
        diffusion = make_constant_diffusion(0.3)
        
        t1, x1 = euler_maruyama(drift, diffusion, x0=0.0, dt=0.01, steps=100, seed=42)
        t2, x2 = euler_maruyama(drift, diffusion, x0=0.0, dt=0.01, steps=100, seed=42)
        
        np.testing.assert_array_equal(x1, x2)
    
    def test_different_seeds(self):
        """Test that different seeds produce different results."""
        drift = make_constant_drift(1.0)
        diffusion = make_constant_diffusion(0.3)
        
        t1, x1 = euler_maruyama(drift, diffusion, x0=0.0, dt=0.01, steps=100, seed=42)
        t2, x2 = euler_maruyama(drift, diffusion, x0=0.0, dt=0.01, steps=100, seed=43)
        
        assert not np.array_equal(x1, x2)
    
    def test_constant_drift_growth(self):
        """Test that constant positive drift leads to growth."""
        drift = make_constant_drift(1.0)
        diffusion = make_constant_diffusion(0.0)
        
        t, x = euler_maruyama(drift, diffusion, x0=0.0, dt=0.01, steps=100, seed=42)
        
        # With constant drift of 1.0 and no noise, trajectory should grow
        assert x[-1] > x[0]
        # Approximate analytical solution: x(t) = x0 + a*t
        expected_final = 0.0 + 1.0 * (100 * 0.01)
        assert abs(x[-1] - expected_final) < 0.01
    
    def test_linear_drift_exponential(self):
        """Test linear drift with no noise approximates exponential growth."""
        drift = make_linear_drift(1.0)
        diffusion = make_constant_diffusion(0.0)
        
        t, x = euler_maruyama(drift, diffusion, x0=1.0, dt=0.01, steps=100, seed=42)
        
        # With linear drift a*x and no noise, should approximate exp(a*t)
        # x(t) ≈ x0 * exp(a*t)
        T = 100 * 0.01
        expected_final = 1.0 * np.exp(1.0 * T)
        # Allow 5% error due to discretization
        assert abs(x[-1] - expected_final) / expected_final < 0.05


class TestMilstein:
    """Tests for Milstein method."""
    
    def test_basic_integration(self):
        """Test that Milstein produces output of correct shape."""
        drift = make_constant_drift(1.0)
        diffusion = make_constant_diffusion(0.3)
        diffusion_deriv = make_constant_diffusion_derivative(0.3)
        
        t, x = milstein(drift, diffusion, diffusion_deriv, 
                       x0=0.0, dt=0.01, steps=100, seed=42)
        
        assert len(t) == 100
        assert len(x) == 100
        assert x[0] == 0.0
    
    def test_constant_diffusion_matches_euler(self):
        """Test Milstein with constant diffusion matches Euler-Maruyama."""
        drift = make_constant_drift(1.0)
        diffusion = make_constant_diffusion(0.3)
        diffusion_deriv = make_constant_diffusion_derivative(0.3)
        
        t1, x1 = euler_maruyama(drift, diffusion, x0=0.0, dt=0.01, steps=100, seed=42)
        t2, x2 = milstein(drift, diffusion, diffusion_deriv,
                         x0=0.0, dt=0.01, steps=100, seed=42)
        
        # For constant diffusion, derivative is 0, so correction term vanishes
        np.testing.assert_allclose(x1, x2, rtol=1e-10)
    
    def test_reproducibility(self):
        """Test that same seed produces same results."""
        drift = make_linear_drift(1.0)
        diffusion = make_linear_diffusion(0.3)
        diffusion_deriv = make_linear_diffusion_derivative(0.3)
        
        t1, x1 = milstein(drift, diffusion, diffusion_deriv,
                         x0=1.0, dt=0.01, steps=100, seed=42)
        t2, x2 = milstein(drift, diffusion, diffusion_deriv,
                         x0=1.0, dt=0.01, steps=100, seed=42)
        
        np.testing.assert_array_equal(x1, x2)


class TestDeterministicSolver:
    """Tests for deterministic ODE solver."""
    
    def test_basic_integration(self):
        """Test that deterministic solver produces correct output."""
        drift = make_constant_drift(1.0)
        
        t, x = deterministic_solver(drift, x0=0.0, dt=0.01, steps=100)
        
        assert len(t) == 100
        assert len(x) == 100
        assert x[0] == 0.0
    
    def test_constant_drift(self):
        """Test constant drift gives linear growth."""
        drift = make_constant_drift(2.0)
        
        t, x = deterministic_solver(drift, x0=0.0, dt=0.01, steps=100)
        
        # x(t) = x0 + a*t
        T = 100 * 0.01
        expected_final = 0.0 + 2.0 * T
        np.testing.assert_allclose(x[-1], expected_final, rtol=1e-10)
    
    def test_linear_drift_exponential(self):
        """Test linear drift approximates exponential."""
        drift = make_linear_drift(1.0)
        
        t, x = deterministic_solver(drift, x0=1.0, dt=0.01, steps=100)
        
        # x(t) = x0 * exp(a*t)
        T = 100 * 0.01
        expected_final = 1.0 * np.exp(1.0 * T)
        # Allow small error due to Euler discretization
        assert abs(x[-1] - expected_final) / expected_final < 0.01


class TestEnsemble:
    """Tests for ensemble simulations."""
    
    def test_ensemble_shape(self):
        """Test that ensemble produces correct number of trajectories."""
        drift = make_constant_drift(1.0)
        diffusion = make_constant_diffusion(0.3)
        
        t, trajectories, final_values = run_ensemble(
            method="euler-maruyama",
            a=drift,
            b=diffusion,
            x0=0.0,
            dt=0.01,
            steps=100,
            num_trajectories=50,
            base_seed=42
        )
        
        assert len(trajectories) == 50
        assert len(final_values) == 50
        assert all(len(traj) == 100 for traj in trajectories)
    
    def test_ensemble_statistics(self):
        """Test that ensemble statistics are reasonable."""
        drift = make_constant_drift(0.0)  # No drift
        diffusion = make_constant_diffusion(0.3)
        
        t, trajectories, final_values = run_ensemble(
            method="euler-maruyama",
            a=drift,
            b=diffusion,
            x0=0.0,
            dt=0.01,
            steps=1000,
            num_trajectories=500,
            base_seed=42
        )
        
        # With no drift, mean should be close to initial value
        mean_final = np.mean(final_values)
        assert abs(mean_final - 0.0) < 0.2  # Allow some variance
        
        # Standard deviation should be roughly sqrt(b^2 * T) for Brownian motion
        T = 1000 * 0.01
        expected_std = np.sqrt(0.3**2 * T)
        actual_std = np.std(final_values)
        # Allow 20% error
        assert abs(actual_std - expected_std) / expected_std < 0.2
    
    def test_ensemble_reproducibility(self):
        """Test that ensemble with same base seed is reproducible."""
        drift = make_constant_drift(1.0)
        diffusion = make_constant_diffusion(0.3)
        
        t1, traj1, final1 = run_ensemble(
            method="euler-maruyama",
            a=drift,
            b=diffusion,
            x0=0.0,
            dt=0.01,
            steps=100,
            num_trajectories=10,
            base_seed=42
        )
        
        t2, traj2, final2 = run_ensemble(
            method="euler-maruyama",
            a=drift,
            b=diffusion,
            x0=0.0,
            dt=0.01,
            steps=100,
            num_trajectories=10,
            base_seed=42
        )
        
        np.testing.assert_array_equal(final1, final2)
        for tr1, tr2 in zip(traj1, traj2):
            np.testing.assert_array_equal(tr1, tr2)


class TestFactoryFunctions:
    """Tests for drift and diffusion factory functions."""
    
    def test_constant_drift_factory(self):
        """Test constant drift factory."""
        drift = make_constant_drift(2.5)
        assert drift(0.0, 0.0) == 2.5
        assert drift(10.0, 5.0) == 2.5
    
    def test_linear_drift_factory(self):
        """Test linear drift factory."""
        drift = make_linear_drift(2.0)
        assert drift(0.0, 0.0) == 0.0
        assert drift(5.0, 0.0) == 10.0
    
    def test_constant_diffusion_factory(self):
        """Test constant diffusion factory."""
        diffusion = make_constant_diffusion(0.3)
        assert diffusion(0.0, 0.0) == 0.3
        assert diffusion(10.0, 5.0) == 0.3
    
    def test_linear_diffusion_factory(self):
        """Test linear diffusion factory."""
        diffusion = make_linear_diffusion(0.5)
        assert diffusion(0.0, 0.0) == 0.0
        assert diffusion(4.0, 0.0) == 2.0
    
    def test_constant_diffusion_derivative(self):
        """Test constant diffusion derivative."""
        deriv = make_constant_diffusion_derivative(0.3)
        assert deriv(0.0, 0.0) == 0.0
        assert deriv(10.0, 5.0) == 0.0
    
    def test_linear_diffusion_derivative(self):
        """Test linear diffusion derivative."""
        deriv = make_linear_diffusion_derivative(0.5)
        assert deriv(0.0, 0.0) == 0.5
        assert deriv(10.0, 5.0) == 0.5
