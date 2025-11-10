"""Unit tests for Lennard-Jones model calculations."""

import unittest
import numpy as np
from numpy.testing import assert_allclose, assert_array_almost_equal

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from model import (
    lj_potential,
    lj_force,
    lj_equilibrium,
    generate_lj_curve,
    morse_potential,
    reduced_lj_potential
)


class TestLJPotential(unittest.TestCase):
    """Test Lennard-Jones potential calculations."""
    
    def test_lj_potential_at_equilibrium(self):
        """Test that LJ potential equals -epsilon at equilibrium distance."""
        epsilon = 1.0
        sigma = 3.5
        r_eq, V_eq = lj_equilibrium(epsilon, sigma)
        
        V_at_eq = lj_potential(r_eq, epsilon, sigma)
        
        assert_allclose(V_at_eq, -epsilon, rtol=1e-10)
        assert_allclose(V_eq, -epsilon, rtol=1e-10)
    
    def test_lj_potential_at_sigma(self):
        """Test that LJ potential equals zero at r = sigma."""
        epsilon = 1.0
        sigma = 3.5
        
        V_at_sigma = lj_potential(sigma, epsilon, sigma)
        
        assert_allclose(V_at_sigma, 0.0, atol=1e-10)
    
    def test_lj_potential_infinity_at_zero(self):
        """Test that LJ potential is infinite at r = 0."""
        V_at_zero = lj_potential(0.0, epsilon=1.0, sigma=3.5)
        
        self.assertTrue(np.isinf(V_at_zero))
    
    def test_lj_potential_positive_at_short_distance(self):
        """Test that LJ potential is positive (repulsive) at short distances."""
        epsilon = 1.0
        sigma = 3.5
        r_short = 0.8 * sigma
        
        V_short = lj_potential(r_short, epsilon, sigma)
        
        self.assertGreater(V_short, 0.0)
    
    def test_lj_potential_approaches_zero_at_infinity(self):
        """Test that LJ potential approaches zero at large distances."""
        epsilon = 1.0
        sigma = 3.5
        r_large = 100 * sigma
        
        V_large = lj_potential(r_large, epsilon, sigma)
        
        assert_allclose(V_large, 0.0, atol=1e-6)
    
    def test_lj_potential_array_input(self):
        """Test that LJ potential works with array input."""
        epsilon = 1.0
        sigma = 3.5
        r = np.array([2.0, 3.0, 4.0, 5.0])
        
        V = lj_potential(r, epsilon, sigma)
        
        self.assertEqual(len(V), len(r))
        self.assertTrue(np.all(np.isfinite(V)))
    
    def test_lj_potential_scaling_with_epsilon(self):
        """Test that potential scales linearly with epsilon."""
        sigma = 3.5
        r = 4.0
        epsilon1 = 1.0
        epsilon2 = 2.0
        
        V1 = lj_potential(r, epsilon1, sigma)
        V2 = lj_potential(r, epsilon2, sigma)
        
        assert_allclose(V2, 2 * V1, rtol=1e-10)
    
    def test_lj_potential_invariance_with_reduced_units(self):
        """Test reduced potential form."""
        r_star = 1.5  # r/sigma
        V_star = reduced_lj_potential(r_star)
        
        # Should match V/epsilon for any epsilon, sigma
        epsilon = 2.5
        sigma = 3.0
        r = r_star * sigma
        V = lj_potential(r, epsilon, sigma)
        
        assert_allclose(V / epsilon, V_star, rtol=1e-10)


class TestLJForce(unittest.TestCase):
    """Test Lennard-Jones force calculations."""
    
    def test_force_zero_at_equilibrium(self):
        """Test that force is zero at equilibrium distance."""
        epsilon = 1.0
        sigma = 3.5
        r_eq, _ = lj_equilibrium(epsilon, sigma)
        
        F_at_eq = lj_force(r_eq, epsilon, sigma)
        
        assert_allclose(F_at_eq, 0.0, atol=1e-8)
    
    def test_force_repulsive_at_short_distance(self):
        """Test that force is repulsive (positive) at short distances."""
        epsilon = 1.0
        sigma = 3.5
        r_eq, _ = lj_equilibrium(epsilon, sigma)
        r_short = 0.9 * r_eq
        
        F_short = lj_force(r_short, epsilon, sigma)
        
        self.assertGreater(F_short, 0.0)
    
    def test_force_attractive_at_long_distance(self):
        """Test that force is attractive (negative) at long distances."""
        epsilon = 1.0
        sigma = 3.5
        r_eq, _ = lj_equilibrium(epsilon, sigma)
        r_long = 1.5 * r_eq
        
        F_long = lj_force(r_long, epsilon, sigma)
        
        self.assertLess(F_long, 0.0)
    
    def test_force_approaches_zero_at_infinity(self):
        """Test that force approaches zero at large distances."""
        epsilon = 1.0
        sigma = 3.5
        r_large = 100 * sigma
        
        F_large = lj_force(r_large, epsilon, sigma)
        
        assert_allclose(F_large, 0.0, atol=1e-6)
    
    def test_force_array_input(self):
        """Test that force calculation works with array input."""
        epsilon = 1.0
        sigma = 3.5
        r = np.linspace(2.0, 10.0, 50)
        
        F = lj_force(r, epsilon, sigma)
        
        self.assertEqual(len(F), len(r))
        self.assertTrue(np.all(np.isfinite(F)))
    
    def test_force_derivative_relationship(self):
        """Test that force is negative derivative of potential (numerically)."""
        epsilon = 1.0
        sigma = 3.5
        r = 4.0
        dr = 1e-6
        
        # Numerical derivative
        V_plus = lj_potential(r + dr, epsilon, sigma)
        V_minus = lj_potential(r - dr, epsilon, sigma)
        dV_dr_numerical = (V_plus - V_minus) / (2 * dr)
        
        # Analytical force
        F_analytical = lj_force(r, epsilon, sigma)
        
        # F = -dV/dr
        assert_allclose(-dV_dr_numerical, F_analytical, rtol=1e-4)


class TestLJEquilibrium(unittest.TestCase):
    """Test equilibrium calculations."""
    
    def test_equilibrium_distance_formula(self):
        """Test that r_min = 2^(1/6) * sigma."""
        sigma = 3.5
        r_eq, _ = lj_equilibrium(epsilon=1.0, sigma=sigma)
        
        expected = 2 ** (1/6) * sigma
        assert_allclose(r_eq, expected, rtol=1e-10)
    
    def test_equilibrium_energy(self):
        """Test that V_min = -epsilon."""
        epsilon = 2.5
        _, V_eq = lj_equilibrium(epsilon, sigma=3.5)
        
        assert_allclose(V_eq, -epsilon, rtol=1e-10)
    
    def test_equilibrium_scaling_with_sigma(self):
        """Test that r_min scales linearly with sigma."""
        epsilon = 1.0
        sigma1 = 3.0
        sigma2 = 4.5
        
        r_eq1, _ = lj_equilibrium(epsilon, sigma1)
        r_eq2, _ = lj_equilibrium(epsilon, sigma2)
        
        ratio = r_eq2 / r_eq1
        expected_ratio = sigma2 / sigma1
        
        assert_allclose(ratio, expected_ratio, rtol=1e-10)


class TestGenerateLJCurve(unittest.TestCase):
    """Test curve generation function."""
    
    def test_generate_curve_returns_correct_length(self):
        """Test that generated curve has correct number of points."""
        n_points = 100
        r, V = generate_lj_curve(n_points=n_points)
        
        self.assertEqual(len(r), n_points)
        self.assertEqual(len(V), n_points)
    
    def test_generate_curve_default_range(self):
        """Test that default range is 0.5*sigma to 3.0*sigma."""
        sigma = 3.5
        r, V = generate_lj_curve(epsilon=1.0, sigma=sigma)
        
        self.assertAlmostEqual(r[0], 0.5 * sigma, places=5)
        self.assertAlmostEqual(r[-1], 3.0 * sigma, places=5)
    
    def test_generate_curve_custom_range(self):
        """Test custom range specification."""
        r_min = 2.0
        r_max = 8.0
        r, V = generate_lj_curve(r_min=r_min, r_max=r_max)
        
        self.assertAlmostEqual(r[0], r_min, places=5)
        self.assertAlmostEqual(r[-1], r_max, places=5)
    
    def test_generate_curve_monotonic_r(self):
        """Test that r values are monotonically increasing."""
        r, V = generate_lj_curve()
        
        self.assertTrue(np.all(np.diff(r) > 0))


class TestMorsePotential(unittest.TestCase):
    """Test Morse potential for comparison."""
    
    def test_morse_minimum_at_equilibrium(self):
        """Test that Morse potential has minimum at r_e."""
        D_e = 1.0
        a = 1.5
        r_e = 3.5
        
        # Sample around r_e
        r = np.linspace(r_e - 0.5, r_e + 0.5, 100)
        V = morse_potential(r, D_e, a, r_e)
        
        min_idx = np.argmin(V)
        r_min = r[min_idx]
        
        assert_allclose(r_min, r_e, atol=0.01)
    
    def test_morse_minimum_energy(self):
        """Test that Morse potential minimum equals -D_e."""
        D_e = 1.5
        a = 1.5
        r_e = 3.5
        
        V_at_eq = morse_potential(r_e, D_e, a, r_e)
        
        assert_allclose(V_at_eq, -D_e, rtol=1e-10)
    
    def test_morse_approaches_zero_at_infinity(self):
        """Test that Morse potential approaches zero at large distances."""
        D_e = 1.0
        a = 1.5
        r_e = 3.5
        r_large = 100.0
        
        V_large = morse_potential(r_large, D_e, a, r_e)
        
        assert_allclose(V_large, 0.0, atol=1e-6)


class TestReducedLJPotential(unittest.TestCase):
    """Test reduced LJ potential."""
    
    def test_reduced_minimum(self):
        """Test that reduced LJ has minimum at r* = 2^(1/6)."""
        r_star = np.linspace(0.9, 1.5, 100)
        V_star = reduced_lj_potential(r_star)
        
        min_idx = np.argmin(V_star)
        r_star_min = r_star[min_idx]
        
        assert_allclose(r_star_min, 2 ** (1/6), atol=0.01)
    
    def test_reduced_minimum_value(self):
        """Test that reduced LJ minimum equals -1."""
        r_star_min = 2 ** (1/6)
        V_star_min = reduced_lj_potential(r_star_min)
        
        assert_allclose(V_star_min, -1.0, rtol=1e-10)
    
    def test_reduced_zero_at_unity(self):
        """Test that reduced LJ equals zero at r* = 1."""
        V_star = reduced_lj_potential(1.0)
        
        assert_allclose(V_star, 0.0, atol=1e-10)


def run_tests():
    """Run all unit tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
