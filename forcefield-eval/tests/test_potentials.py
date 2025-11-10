"""
Unit tests for potential energy functions.
"""

import unittest
import numpy as np
from numpy.testing import assert_allclose

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.potentials import lennard_jones, morse, coulomb
from src.derivatives import lj_force, morse_force, coulomb_force
from src.evaluator import ForceFieldEvaluator, create_distance_range


class TestLennardJones(unittest.TestCase):
    """Test Lennard-Jones potential."""
    
    def test_lj_at_sigma(self):
        """U(σ) should be 0."""
        sigma = 0.34
        epsilon = 0.2
        U = lennard_jones(sigma, epsilon, sigma)
        self.assertAlmostEqual(U, 0.0, places=10)
    
    def test_lj_minimum(self):
        """Minimum should occur at r = 2^(1/6) * σ with U = -ε."""
        sigma = 0.34
        epsilon = 0.2
        r_min = 2**(1/6) * sigma
        U_min = lennard_jones(r_min, epsilon, sigma)
        self.assertAlmostEqual(U_min, -epsilon, places=10)
    
    def test_lj_force_at_minimum(self):
        """Force should be zero at minimum."""
        sigma = 0.34
        epsilon = 0.2
        r_min = 2**(1/6) * sigma
        F = lj_force(r_min, epsilon, sigma)
        self.assertAlmostEqual(F, 0.0, places=8)
    
    def test_lj_repulsive_at_short_range(self):
        """Force should be positive (repulsive) at short range."""
        sigma = 0.34
        epsilon = 0.2
        r = 0.2 * sigma
        F = lj_force(r, epsilon, sigma)
        self.assertGreater(F, 0)
    
    def test_lj_attractive_at_long_range(self):
        """Force should be negative (attractive) at intermediate range."""
        sigma = 0.34
        epsilon = 0.2
        r = 1.5 * sigma
        F = lj_force(r, epsilon, sigma)
        self.assertLess(F, 0)


class TestMorse(unittest.TestCase):
    """Test Morse potential."""
    
    def test_morse_at_equilibrium(self):
        """U(re) should be -De."""
        De = 0.4
        a = 1.5
        re = 0.3
        U = morse(re, De, a, re)
        self.assertAlmostEqual(U, -De, places=10)
    
    def test_morse_force_at_equilibrium(self):
        """Force should be zero at equilibrium."""
        De = 0.4
        a = 1.5
        re = 0.3
        F = morse_force(re, De, a, re)
        self.assertAlmostEqual(F, 0.0, places=10)
    
    def test_morse_dissociation(self):
        """U(r → ∞) should approach 0."""
        De = 0.4
        a = 1.5
        re = 0.3
        r_large = 10.0
        U = morse(r_large, De, a, re)
        self.assertAlmostEqual(U, 0.0, places=6)
    
    def test_morse_repulsive_at_short_range(self):
        """Force should be positive at r < re."""
        De = 0.4
        a = 1.5
        re = 0.3
        r = 0.2
        F = morse_force(r, De, a, re)
        self.assertGreater(F, 0)


class TestCoulomb(unittest.TestCase):
    """Test Coulomb potential."""
    
    def test_coulomb_opposite_charges(self):
        """Opposite charges should have negative (attractive) potential."""
        q1 = 1e-19
        q2 = -1e-19
        r = 0.5
        U = coulomb(r, q1, q2)
        self.assertLess(U, 0)
    
    def test_coulomb_like_charges(self):
        """Like charges should have positive (repulsive) potential."""
        q1 = 1e-19
        q2 = 1e-19
        r = 0.5
        U = coulomb(r, q1, q2)
        self.assertGreater(U, 0)
    
    def test_coulomb_inverse_r(self):
        """Energy should scale as 1/r."""
        q1 = 1e-19
        q2 = -1e-19
        r1 = 0.5
        r2 = 1.0
        U1 = coulomb(r1, q1, q2)
        U2 = coulomb(r2, q1, q2)
        # U1/U2 should equal r2/r1
        self.assertAlmostEqual(U1/U2, r2/r1, places=8)
    
    def test_coulomb_force_opposite_charges(self):
        """Force between opposite charges should be negative (attractive)."""
        q1 = 1e-19
        q2 = -1e-19
        r = 0.5
        F = coulomb_force(r, q1, q2)
        self.assertLess(F, 0)


class TestForceDerivatives(unittest.TestCase):
    """Test that forces are consistent with numerical derivatives."""
    
    def test_lj_numerical_derivative(self):
        """Verify LJ force matches numerical derivative."""
        epsilon = 0.2
        sigma = 0.34
        r = 0.4
        dr = 1e-8
        
        # Numerical derivative
        U_plus = lennard_jones(r + dr, epsilon, sigma)
        U_minus = lennard_jones(r - dr, epsilon, sigma)
        F_numerical = -(U_plus - U_minus) / (2 * dr)
        
        # Analytic force
        F_analytic = lj_force(r, epsilon, sigma)
        
        self.assertAlmostEqual(F_analytic, F_numerical, places=5)
    
    def test_morse_numerical_derivative(self):
        """Verify Morse force matches numerical derivative."""
        De = 0.4
        a = 1.5
        re = 0.3
        r = 0.35
        dr = 1e-8
        
        # Numerical derivative
        U_plus = morse(r + dr, De, a, re)
        U_minus = morse(r - dr, De, a, re)
        F_numerical = -(U_plus - U_minus) / (2 * dr)
        
        # Analytic force
        F_analytic = morse_force(r, De, a, re)
        
        self.assertAlmostEqual(F_analytic, F_numerical, places=5)
    
    def test_coulomb_numerical_derivative(self):
        """Verify Coulomb force matches numerical derivative."""
        q1 = 1e-19
        q2 = -1e-19
        r = 0.5
        dr = 1e-8
        
        # Numerical derivative
        U_plus = coulomb(r + dr, q1, q2)
        U_minus = coulomb(r - dr, q1, q2)
        F_numerical = -(U_plus - U_minus) / (2 * dr)
        
        # Analytic force
        F_analytic = coulomb_force(r, q1, q2)
        
        self.assertAlmostEqual(F_analytic, F_numerical, places=5)


class TestEvaluator(unittest.TestCase):
    """Test ForceFieldEvaluator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.evaluator = ForceFieldEvaluator()
        self.r_range = create_distance_range(0.2, 1.0, 50)
    
    def test_evaluate_lj(self):
        """Test evaluation of LJ potential."""
        params = {'epsilon': 0.2, 'sigma': 0.34}
        result = self.evaluator.evaluate_potential('LJ', params, self.r_range)
        
        self.assertIn('r', result)
        self.assertIn('U', result)
        self.assertIn('F', result)
        self.assertIn('r_eq', result)
        self.assertIn('U_min', result)
        
        # Check equilibrium is close to expected
        r_eq_expected = 2**(1/6) * params['sigma']
        self.assertAlmostEqual(result['r_eq'], r_eq_expected, places=2)
    
    def test_evaluate_morse(self):
        """Test evaluation of Morse potential."""
        params = {'De': 0.4, 'a': 1.5, 're': 0.3}
        result = self.evaluator.evaluate_potential('Morse', params, self.r_range)
        
        # Equilibrium should be at re
        self.assertAlmostEqual(result['r_eq'], params['re'], places=2)
        # Minimum energy should be -De
        self.assertAlmostEqual(result['U_min'], -params['De'], places=2)
    
    def test_compare_potentials(self):
        """Test comparison of multiple potentials."""
        params_dict = {
            'LJ': {'epsilon': 0.2, 'sigma': 0.34},
            'Morse': {'De': 0.4, 'a': 1.5, 're': 0.3},
        }
        
        comparison = self.evaluator.compare_potentials(
            ['LJ', 'Morse'], params_dict, self.r_range
        )
        
        self.assertEqual(len(comparison['potentials']), 2)
        self.assertIn('lowest_minimum', comparison)


class TestDistanceRange(unittest.TestCase):
    """Test distance range creation."""
    
    def test_linear_range(self):
        """Test linear distance range creation."""
        r = create_distance_range(0.1, 1.0, 10)
        self.assertEqual(len(r), 10)
        self.assertAlmostEqual(r[0], 0.1)
        self.assertAlmostEqual(r[-1], 1.0)


if __name__ == '__main__':
    unittest.main()
