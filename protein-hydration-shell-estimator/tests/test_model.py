"""
Unit tests for the Protein Hydration Shell Estimator.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model import HydrationShellEstimator
from src.constants import RHO_BULK_WATER, AVOGADRO_NUMBER, ANGSTROM_TO_METER
from src.utils import (
    angstrom_to_meter,
    meter_to_angstrom,
    nm2_to_m2,
    m2_to_nm2,
    validate_surface_area,
    validate_hydrophilicity_index,
    validate_shell_thickness,
    validate_all_inputs,
)


class TestConstants(unittest.TestCase):
    """Test physical constants."""
    
    def test_bulk_water_density(self):
        """Test bulk water density value."""
        self.assertAlmostEqual(RHO_BULK_WATER, 3.34e28, places=2)
    
    def test_avogadro_number(self):
        """Test Avogadro's number."""
        self.assertAlmostEqual(AVOGADRO_NUMBER, 6.022e23, places=2)
    
    def test_angstrom_conversion(self):
        """Test Angstrom to meter conversion."""
        self.assertEqual(ANGSTROM_TO_METER, 1e-10)


class TestUnitConversions(unittest.TestCase):
    """Test unit conversion functions."""
    
    def test_angstrom_to_meter(self):
        """Test Angstrom to meter conversion."""
        self.assertEqual(angstrom_to_meter(10), 1e-9)
        self.assertEqual(angstrom_to_meter(3.0), 3e-10)
    
    def test_meter_to_angstrom(self):
        """Test meter to Angstrom conversion."""
        self.assertEqual(meter_to_angstrom(1e-9), 10)
        self.assertEqual(meter_to_angstrom(3e-10), 3.0)
    
    def test_nm2_to_m2(self):
        """Test nm² to m² conversion."""
        self.assertEqual(nm2_to_m2(1), 1e-18)
        self.assertAlmostEqual(nm2_to_m2(100), 1e-16, places=25)
    
    def test_m2_to_nm2(self):
        """Test m² to nm² conversion."""
        self.assertEqual(m2_to_nm2(1e-18), 1)
        self.assertAlmostEqual(m2_to_nm2(1e-16), 100, places=10)


class TestValidation(unittest.TestCase):
    """Test input validation functions."""
    
    def test_validate_surface_area_positive(self):
        """Test that positive surface areas are valid."""
        is_valid, _ = validate_surface_area(1e-17)
        self.assertTrue(is_valid)
    
    def test_validate_surface_area_negative(self):
        """Test that negative surface areas are invalid."""
        is_valid, msg = validate_surface_area(-1e-17)
        self.assertFalse(is_valid)
        self.assertIn("positive", msg.lower())
    
    def test_validate_surface_area_unrealistic(self):
        """Test that unrealistic surface areas are flagged."""
        is_valid, msg = validate_surface_area(1e-25)
        self.assertFalse(is_valid)
        self.assertIn("unrealistic", msg.lower())
    
    def test_validate_hydrophilicity_valid_range(self):
        """Test valid hydrophilicity indices."""
        for value in [0, 0.5, 1.0]:
            is_valid, _ = validate_hydrophilicity_index(value)
            self.assertTrue(is_valid)
    
    def test_validate_hydrophilicity_out_of_range(self):
        """Test invalid hydrophilicity indices."""
        for value in [-0.1, 1.1, 2.0]:
            is_valid, msg = validate_hydrophilicity_index(value)
            self.assertFalse(is_valid)
            self.assertIn("between 0 and 1", msg)
    
    def test_validate_thickness_positive(self):
        """Test that positive thicknesses are valid."""
        is_valid, _ = validate_shell_thickness(3.0)
        self.assertTrue(is_valid)
    
    def test_validate_thickness_negative(self):
        """Test that negative thicknesses are invalid."""
        is_valid, msg = validate_shell_thickness(-1.0)
        self.assertFalse(is_valid)
        self.assertIn("positive", msg.lower())
    
    def test_validate_all_inputs_valid(self):
        """Test validation with all valid inputs."""
        is_valid, _ = validate_all_inputs(1e-17, 0.6, 3.0)
        self.assertTrue(is_valid)
    
    def test_validate_all_inputs_invalid(self):
        """Test validation catches any invalid input."""
        is_valid, _ = validate_all_inputs(-1e-17, 0.6, 3.0)
        self.assertFalse(is_valid)


class TestHydrationShellEstimator(unittest.TestCase):
    """Test the HydrationShellEstimator model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.surface_area = 1.5e-17  # m²
        self.hydrophilicity = 0.65
        self.thickness = 3.0  # Å
        
        self.estimator = HydrationShellEstimator(
            surface_area=self.surface_area,
            hydrophilicity_index=self.hydrophilicity,
            shell_thickness=self.thickness,
        )
    
    def test_initialization(self):
        """Test estimator initialization."""
        self.assertEqual(self.estimator.surface_area, self.surface_area)
        self.assertEqual(self.estimator.hydrophilicity_index, self.hydrophilicity)
        self.assertEqual(self.estimator.shell_thickness, self.thickness)
    
    def test_calculate_shell_density(self):
        """Test shell density calculation."""
        density = self.estimator.calculate_shell_density()
        
        # Expected: f_hydrophilic = 0.8 + 0.4 * 0.65 = 1.06
        # ρ_shell = 3.34e28 * 1.06 = 3.54e28
        expected_f = 0.8 + 0.4 * self.hydrophilicity
        expected_density = RHO_BULK_WATER * expected_f
        
        self.assertAlmostEqual(density, expected_density, places=25)
    
    def test_calculate_shell_volume(self):
        """Test shell volume calculation."""
        volume = self.estimator.calculate_shell_volume()
        
        # Expected: V = A * t = 1.5e-17 * 3e-10 = 4.5e-27 m³
        thickness_m = self.thickness * ANGSTROM_TO_METER
        expected_volume = self.surface_area * thickness_m
        
        self.assertAlmostEqual(volume, expected_volume, places=35)
    
    def test_calculate_water_count(self):
        """Test water molecule count calculation."""
        count = self.estimator.calculate_water_count()
        
        # Should be positive
        self.assertGreater(count, 0)
        
        # Verify it's computed as density * volume
        density = self.estimator.calculate_shell_density()
        volume = self.estimator.calculate_shell_volume()
        expected_count = density * volume
        
        self.assertAlmostEqual(count, expected_count, places=10)
    
    def test_calculate_water_moles(self):
        """Test water moles calculation."""
        moles = self.estimator.calculate_water_moles()
        
        # Should be positive but small
        self.assertGreater(moles, 0)
        self.assertLess(moles, 1e-10)  # Should be tiny amount
        
        # Verify relationship with count
        count = self.estimator.calculate_water_count()
        expected_moles = count / AVOGADRO_NUMBER
        
        self.assertAlmostEqual(moles, expected_moles, places=30)
    
    def test_compute_returns_dict(self):
        """Test that compute returns a dictionary with all keys."""
        results = self.estimator.compute()
        
        self.assertIsInstance(results, dict)
        self.assertIn('V_shell', results)
        self.assertIn('rho_shell', results)
        self.assertIn('N_H2O', results)
        self.assertIn('n_H2O', results)
    
    def test_compute_values_reasonable(self):
        """Test that computed values are in reasonable ranges."""
        results = self.estimator.compute()
        
        # All values should be positive
        for key, value in results.items():
            self.assertGreater(value, 0, f"{key} should be positive")
        
        # Water count should be in reasonable range (tens to thousands)
        self.assertGreater(results['N_H2O'], 10)
        self.assertLess(results['N_H2O'], 1e6)
    
    def test_get_summary(self):
        """Test that summary generation works."""
        summary = self.estimator.get_summary()
        
        self.assertIsInstance(summary, str)
        self.assertIn('Hydration Shell', summary)
        self.assertIn('V_shell', summary)
        self.assertIn('N_H2O', summary)
    
    def test_hydrophilicity_effect(self):
        """Test that higher hydrophilicity increases water density."""
        estimator_low = HydrationShellEstimator(
            surface_area=self.surface_area,
            hydrophilicity_index=0.2,
            shell_thickness=self.thickness,
        )
        
        estimator_high = HydrationShellEstimator(
            surface_area=self.surface_area,
            hydrophilicity_index=0.9,
            shell_thickness=self.thickness,
        )
        
        density_low = estimator_low.calculate_shell_density()
        density_high = estimator_high.calculate_shell_density()
        
        self.assertGreater(density_high, density_low)
    
    def test_surface_area_effect(self):
        """Test that larger surface area increases water count."""
        estimator_small = HydrationShellEstimator(
            surface_area=1e-17,
            hydrophilicity_index=self.hydrophilicity,
            shell_thickness=self.thickness,
        )
        
        estimator_large = HydrationShellEstimator(
            surface_area=5e-17,
            hydrophilicity_index=self.hydrophilicity,
            shell_thickness=self.thickness,
        )
        
        count_small = estimator_small.calculate_water_count()
        count_large = estimator_large.calculate_water_count()
        
        self.assertGreater(count_large, count_small)
    
    def test_thickness_effect(self):
        """Test that thicker shell increases water count."""
        estimator_thin = HydrationShellEstimator(
            surface_area=self.surface_area,
            hydrophilicity_index=self.hydrophilicity,
            shell_thickness=2.5,
        )
        
        estimator_thick = HydrationShellEstimator(
            surface_area=self.surface_area,
            hydrophilicity_index=self.hydrophilicity,
            shell_thickness=4.0,
        )
        
        count_thin = estimator_thin.calculate_water_count()
        count_thick = estimator_thick.calculate_water_count()
        
        self.assertGreater(count_thick, count_thin)
    
    def test_example_from_spec(self):
        """Test the example from the specification."""
        # From spec: surface_area = 1.5e-17, hydrophilicity = 0.65, thickness = 3.0
        # Expected: V_shell = 4.5e-27 m³, N_H2O ≈ 190
        
        results = self.estimator.compute()
        
        # Check volume (should be exact)
        self.assertAlmostEqual(results['V_shell'], 4.5e-27, places=35)
        
        # Check water count (approximate)
        self.assertGreater(results['N_H2O'], 150)
        self.assertLess(results['N_H2O'], 250)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def test_minimum_hydrophilicity(self):
        """Test with minimum hydrophilicity (fully hydrophobic)."""
        estimator = HydrationShellEstimator(
            surface_area=1e-17,
            hydrophilicity_index=0.0,
            shell_thickness=3.0,
        )
        
        results = estimator.compute()
        
        # Should still have water, but density reduced
        self.assertGreater(results['N_H2O'], 0)
        
        # Density should be 0.8 * bulk
        expected_density = RHO_BULK_WATER * 0.8
        self.assertAlmostEqual(results['rho_shell'], expected_density, places=25)
    
    def test_maximum_hydrophilicity(self):
        """Test with maximum hydrophilicity (fully hydrophilic)."""
        estimator = HydrationShellEstimator(
            surface_area=1e-17,
            hydrophilicity_index=1.0,
            shell_thickness=3.0,
        )
        
        results = estimator.compute()
        
        # Density should be 1.2 * bulk (allowing for floating point precision)
        expected_density = RHO_BULK_WATER * 1.2
        # Use relative tolerance for large numbers
        self.assertAlmostEqual(results['rho_shell'] / expected_density, 1.0, places=10)
    
    def test_small_surface_area(self):
        """Test with very small surface area."""
        estimator = HydrationShellEstimator(
            surface_area=1e-19,
            hydrophilicity_index=0.6,
            shell_thickness=3.0,
        )
        
        results = estimator.compute()
        
        # Should have fewer water molecules
        self.assertGreater(results['N_H2O'], 0)
        self.assertLess(results['N_H2O'], 10)
    
    def test_large_thickness(self):
        """Test with larger shell thickness."""
        estimator = HydrationShellEstimator(
            surface_area=1e-17,
            hydrophilicity_index=0.6,
            shell_thickness=5.0,
        )
        
        results = estimator.compute()
        
        # Should have proportionally more water
        self.assertGreater(results['N_H2O'], 100)


def run_tests():
    """Run all tests and display results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConstants))
    suite.addTests(loader.loadTestsFromTestCase(TestUnitConversions))
    suite.addTests(loader.loadTestsFromTestCase(TestValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestHydrationShellEstimator))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
