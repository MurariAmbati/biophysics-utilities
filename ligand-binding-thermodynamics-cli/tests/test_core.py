"""
Unit tests for core thermodynamic calculations.
"""

import unittest
import math
from src.core import (
    calculate_ka,
    calculate_kd,
    calculate_delta_g,
    calculate_entropy,
    calculate_enthalpy,
    van_t_hoff_ka,
    hill_fractional_occupancy,
    compute_all,
)
from src.constants import GAS_CONSTANT_R


class TestBindingConstants(unittest.TestCase):
    """Test calculation of Ka and Kd."""
    
    def test_calculate_ka_basic(self):
        """Test basic Ka calculation."""
        # [P] = 1e-6 M, [L] = 1e-6 M, [PL] = 5e-7 M
        # Ka = 5e-7 / (1e-6 * 1e-6) = 5e-7 / 1e-12 = 5e5 M^-1
        ka = calculate_ka(1e-6, 1e-6, 5e-7)
        self.assertAlmostEqual(ka, 5e5, places=0)
    
    def test_calculate_ka_different_values(self):
        """Test Ka with different concentration values."""
        # [P] = 2e-6 M, [L] = 3e-6 M, [PL] = 1.2e-6 M
        # Ka = 1.2e-6 / (2e-6 * 3e-6) = 1.2e-6 / 6e-12 = 2e5 M^-1
        ka = calculate_ka(2e-6, 3e-6, 1.2e-6)
        self.assertAlmostEqual(ka, 2e5, places=0)
    
    def test_calculate_ka_zero_pl(self):
        """Test Ka when [PL] = 0."""
        ka = calculate_ka(1e-6, 1e-6, 0)
        self.assertEqual(ka, 0)
    
    def test_calculate_ka_invalid_concentrations(self):
        """Test Ka with invalid concentrations."""
        with self.assertRaises(ValueError):
            calculate_ka(0, 1e-6, 5e-7)  # [P] = 0
        
        with self.assertRaises(ValueError):
            calculate_ka(1e-6, 0, 5e-7)  # [L] = 0
        
        with self.assertRaises(ValueError):
            calculate_ka(1e-6, 1e-6, -1e-7)  # [PL] < 0
    
    def test_calculate_kd_basic(self):
        """Test basic Kd calculation."""
        ka = 5e5  # M^-1
        kd = calculate_kd(ka)
        self.assertAlmostEqual(kd, 2e-6, places=9)
    
    def test_calculate_kd_reciprocal(self):
        """Test that Kd = 1/Ka."""
        ka = 1e6
        kd = calculate_kd(ka)
        self.assertAlmostEqual(ka * kd, 1.0, places=10)
    
    def test_calculate_kd_invalid(self):
        """Test Kd with invalid Ka."""
        with self.assertRaises(ValueError):
            calculate_kd(0)
        
        with self.assertRaises(ValueError):
            calculate_kd(-1e5)


class TestFreeEnergy(unittest.TestCase):
    """Test ΔG calculations."""
    
    def test_calculate_delta_g_basic(self):
        """Test basic ΔG calculation."""
        # Ka = 5e5 M^-1, T = 298 K
        # ΔG = -RT ln(Ka) = -8.314 * 298 * ln(5e5)
        # ln(5e5) ≈ 13.122
        # ΔG ≈ -8.314 * 298 * 13.122 ≈ -32.51 kJ/mol
        ka = 5e5
        temp = 298
        delta_g = calculate_delta_g(ka, temp)
        expected = -GAS_CONSTANT_R * temp * math.log(ka) * 0.001
        self.assertAlmostEqual(delta_g, expected, places=2)
    
    def test_calculate_delta_g_high_ka(self):
        """Test ΔG with high Ka (strong binding)."""
        ka = 1e9  # Very strong binding
        temp = 298
        delta_g = calculate_delta_g(ka, temp)
        # Should be very negative
        self.assertLess(delta_g, -50)
    
    def test_calculate_delta_g_low_ka(self):
        """Test ΔG with low Ka (weak binding)."""
        ka = 1e2  # Weak binding
        temp = 298
        delta_g = calculate_delta_g(ka, temp)
        # Should be less negative
        self.assertGreater(delta_g, -20)
    
    def test_calculate_delta_g_temperature_dependence(self):
        """Test that ΔG changes with temperature."""
        ka = 1e5
        temp1 = 273
        temp2 = 323
        
        delta_g1 = calculate_delta_g(ka, temp1)
        delta_g2 = calculate_delta_g(ka, temp2)
        
        # At higher temperature, ΔG should be more negative
        self.assertLess(delta_g2, delta_g1)
    
    def test_calculate_delta_g_invalid(self):
        """Test ΔG with invalid inputs."""
        with self.assertRaises(ValueError):
            calculate_delta_g(0, 298)  # Ka = 0
        
        with self.assertRaises(ValueError):
            calculate_delta_g(1e5, 0)  # T = 0


class TestEntropyEnthalpy(unittest.TestCase):
    """Test entropy and enthalpy calculations."""
    
    def test_calculate_entropy_basic(self):
        """Test basic entropy calculation."""
        # ΔG = -30 kJ/mol, ΔH = -50 kJ/mol, T = 298 K
        # ΔS = (ΔH - ΔG) / T = (-50 - (-30)) / 298 = -20 / 298
        # ΔS = -20000 / 298 ≈ -67.1 J/(mol·K)
        delta_g = -30
        delta_h = -50
        temp = 298
        
        delta_s = calculate_entropy(delta_g, delta_h, temp)
        expected = (-50000 - (-30000)) / 298
        self.assertAlmostEqual(delta_s, expected, places=1)
    
    def test_calculate_entropy_endothermic(self):
        """Test entropy with endothermic binding (positive ΔH)."""
        delta_g = -10
        delta_h = 20  # Endothermic
        temp = 298
        
        delta_s = calculate_entropy(delta_g, delta_h, temp)
        # Should be positive (entropy-driven)
        self.assertGreater(delta_s, 0)
    
    def test_calculate_enthalpy_basic(self):
        """Test basic enthalpy calculation."""
        # ΔG = -30 kJ/mol, ΔS = -67.1 J/(mol·K), T = 298 K
        # ΔH = ΔG + TΔS
        delta_g = -30
        delta_s = -67.1
        temp = 298
        
        delta_h = calculate_enthalpy(delta_g, delta_s, temp)
        expected = -30 + (298 * -67.1 * 0.001)
        self.assertAlmostEqual(delta_h, expected, places=1)
    
    def test_thermodynamic_consistency(self):
        """Test that ΔG = ΔH - TΔS is consistent."""
        delta_h = -40
        delta_s = -50
        temp = 300
        
        # Calculate ΔG from ΔH and ΔS
        delta_g_calculated = delta_h - (temp * delta_s * 0.001)
        
        # Calculate ΔS from ΔG and ΔH
        delta_s_back = calculate_entropy(delta_g_calculated, delta_h, temp)
        
        self.assertAlmostEqual(delta_s, delta_s_back, places=1)


class TestVanTHoff(unittest.TestCase):
    """Test van't Hoff equation."""
    
    def test_van_t_hoff_basic(self):
        """Test van't Hoff Ka calculation."""
        # ΔH = -40 kJ/mol, ΔS = -50 J/(mol·K), T = 298 K
        delta_h = -40
        delta_s = -50
        temp = 298
        
        ka = van_t_hoff_ka(delta_h, delta_s, temp)
        
        # Verify using ΔG = -RT ln(Ka)
        delta_g = calculate_delta_g(ka, temp)
        delta_g_expected = delta_h - temp * delta_s * 0.001
        
        self.assertAlmostEqual(delta_g, delta_g_expected, places=1)
    
    def test_van_t_hoff_temperature_series(self):
        """Test van't Hoff at multiple temperatures."""
        delta_h = -50
        delta_s = -80
        
        temps = [273, 298, 323]
        kas = [van_t_hoff_ka(delta_h, delta_s, t) for t in temps]
        
        # Ka should decrease with increasing temperature (for ΔH < 0)
        self.assertGreater(kas[0], kas[1])
        self.assertGreater(kas[1], kas[2])


class TestHillEquation(unittest.TestCase):
    """Test Hill equation for cooperative binding."""
    
    def test_hill_fractional_occupancy_basic(self):
        """Test basic Hill equation."""
        # At [L] = Kd, θ = 0.5 for n = 1
        ligand = 1e-6
        kd = 1e-6
        n = 1.0
        
        theta = hill_fractional_occupancy(ligand, kd, n)
        self.assertAlmostEqual(theta, 0.5, places=5)
    
    def test_hill_cooperativity(self):
        """Test cooperative binding (n > 1)."""
        ligand = 1e-6
        kd = 1e-6
        
        # Compare n = 1 (non-cooperative) vs n = 2 (cooperative)
        theta_1 = hill_fractional_occupancy(ligand, kd, 1.0)
        theta_2 = hill_fractional_occupancy(ligand, kd, 2.0)
        
        # For n = 1, θ = 0.5 at [L] = Kd
        self.assertAlmostEqual(theta_1, 0.5, places=5)
        
        # For n > 1, θ at [L] = Kd depends on n
        # θ = [L]^n / (Kd + [L]^n) = Kd^n / (Kd + Kd^n)
        # When [L] = Kd: θ = Kd / (Kd + Kd) = 0.5 only for the numerator
        # Actually: θ = [L]^n / (Kd + [L]^n), not (Kd^n + [L]^n)
        # So when [L] = Kd = 1e-6: θ = (1e-6)^2 / (1e-6 + (1e-6)^2) ≈ 1e-6
        self.assertLess(theta_2, theta_1)  # Steeper curve for n > 1
    
    def test_hill_limits(self):
        """Test Hill equation at extreme concentrations."""
        kd = 1e-6
        n = 1.0
        
        # [L] >> Kd: θ → 1
        theta_high = hill_fractional_occupancy(1e-3, kd, n)
        self.assertGreater(theta_high, 0.999)
        
        # [L] << Kd: θ → 0
        theta_low = hill_fractional_occupancy(1e-9, kd, n)
        self.assertLess(theta_low, 0.001)


class TestComputeAll(unittest.TestCase):
    """Test the comprehensive compute_all function."""
    
    def test_compute_all_basic(self):
        """Test compute_all with basic inputs."""
        results = compute_all(1e-6, 1e-6, 5e-7, 298)
        
        # Check all required keys
        self.assertIn('Ka', results)
        self.assertIn('Kd', results)
        self.assertIn('ΔG', results)
        
        # Verify values
        self.assertAlmostEqual(results['Ka'], 5e5, places=0)
        self.assertAlmostEqual(results['Kd'], 2e-6, places=9)
        self.assertLess(results['ΔG'], 0)  # Should be negative
    
    def test_compute_all_with_enthalpy(self):
        """Test compute_all with enthalpy included."""
        results = compute_all(1e-6, 1e-6, 5e-7, 298, delta_h=-50)
        
        # Check entropy is calculated
        self.assertIn('ΔS', results)
        self.assertIn('ΔH', results)
        
        # Verify thermodynamic consistency
        delta_g = results['ΔG']
        delta_h = results['ΔH']
        delta_s = results['ΔS']
        temp = 298
        
        delta_g_check = delta_h - temp * delta_s * 0.001
        self.assertAlmostEqual(delta_g, delta_g_check, places=1)


if __name__ == '__main__':
    unittest.main()
