"""
Unit tests for Brownian motion simulator core functionality.
"""

import sys
import os
import unittest
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core import BrownianSimulator


class TestBrownianSimulator(unittest.TestCase):
    """Test cases for BrownianSimulator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sim_2d = BrownianSimulator(D=1.0, dt=0.01, n_steps=100, 
                                        n_particles=10, dim=2, seed=42)
        self.sim_3d = BrownianSimulator(D=1.0, dt=0.01, n_steps=100, 
                                        n_particles=10, dim=3, seed=42)
    
    def test_initialization(self):
        """Test simulator initialization."""
        self.assertEqual(self.sim_2d.D, 1.0)
        self.assertEqual(self.sim_2d.dt, 0.01)
        self.assertEqual(self.sim_2d.n_steps, 100)
        self.assertEqual(self.sim_2d.n_particles, 10)
        self.assertEqual(self.sim_2d.dim, 2)
        self.assertIsNone(self.sim_2d.trajectories)
    
    def test_invalid_dimension(self):
        """Test that invalid dimension raises error."""
        with self.assertRaises(ValueError):
            BrownianSimulator(dim=1)
        with self.assertRaises(ValueError):
            BrownianSimulator(dim=4)
    
    def test_simulate_2d(self):
        """Test 2D simulation."""
        trajectories = self.sim_2d.simulate()
        
        # Check shape
        self.assertEqual(trajectories.shape, (10, 100, 2))
        
        # Check that trajectories start at origin
        np.testing.assert_array_almost_equal(
            trajectories[:, 0, :],
            np.zeros((10, 2))
        )
        
        # Check that positions change over time
        self.assertTrue(np.any(trajectories[:, -1, :] != 0))
    
    def test_simulate_3d(self):
        """Test 3D simulation."""
        trajectories = self.sim_3d.simulate()
        
        # Check shape
        self.assertEqual(trajectories.shape, (10, 100, 3))
        
        # Check that trajectories start at origin
        np.testing.assert_array_almost_equal(
            trajectories[:, 0, :],
            np.zeros((10, 3))
        )
    
    def test_compute_msd(self):
        """Test MSD computation."""
        self.sim_2d.simulate()
        time, msd = self.sim_2d.compute_msd()
        
        # Check shapes
        self.assertEqual(len(time), 100)
        self.assertEqual(len(msd), 100)
        
        # Check that MSD starts at 0
        self.assertAlmostEqual(msd[0], 0.0)
        
        # Check that MSD increases over time
        self.assertTrue(np.all(np.diff(msd) >= 0))
    
    def test_theoretical_msd(self):
        """Test theoretical MSD calculation."""
        self.sim_2d.simulate()
        msd_theory = self.sim_2d.theoretical_msd()
        
        # Check shape
        self.assertEqual(len(msd_theory), 100)
        
        # Check formula: MSD = 2*dim*D*t
        expected = 2 * 2 * 1.0 * self.sim_2d.time
        np.testing.assert_array_almost_equal(msd_theory, expected)
        
        # Test 3D
        self.sim_3d.simulate()
        msd_theory_3d = self.sim_3d.theoretical_msd()
        expected_3d = 2 * 3 * 1.0 * self.sim_3d.time
        np.testing.assert_array_almost_equal(msd_theory_3d, expected_3d)
    
    def test_fit_diffusion_coefficient(self):
        """Test diffusion coefficient fitting."""
        # Use large number of particles for better statistics
        sim = BrownianSimulator(D=2.5, dt=0.01, n_steps=1000, 
                               n_particles=100, dim=2, seed=123)
        sim.simulate()
        
        D_fit, r_squared = sim.fit_diffusion_coefficient()
        
        # Fitted D should be close to true D (within 20% for stochastic process)
        self.assertAlmostEqual(D_fit, 2.5, delta=0.5)
        
        # R² should be high (good fit)
        self.assertGreater(r_squared, 0.95)
    
    def test_get_final_positions(self):
        """Test getting final positions."""
        self.sim_2d.simulate()
        final_pos = self.sim_2d.get_final_positions()
        
        # Check shape
        self.assertEqual(final_pos.shape, (10, 2))
        
        # Check that it matches last step
        np.testing.assert_array_equal(
            final_pos,
            self.sim_2d.trajectories[:, -1, :]
        )
    
    def test_get_displacement_distribution(self):
        """Test displacement distribution."""
        self.sim_2d.simulate()
        displacements = self.sim_2d.get_displacement_distribution()
        
        # Check shape
        self.assertEqual(displacements.shape, (10,))
        
        # All displacements should be non-negative
        self.assertTrue(np.all(displacements >= 0))
    
    def test_reproducibility(self):
        """Test that same seed produces same results."""
        sim1 = BrownianSimulator(D=1.0, dt=0.01, n_steps=100, 
                                n_particles=5, dim=2, seed=999)
        sim2 = BrownianSimulator(D=1.0, dt=0.01, n_steps=100, 
                                n_particles=5, dim=2, seed=999)
        
        traj1 = sim1.simulate()
        traj2 = sim2.simulate()
        
        # Should produce identical trajectories
        np.testing.assert_array_almost_equal(traj1, traj2)
    
    def test_msd_scaling(self):
        """Test that MSD scales linearly with time."""
        sim = BrownianSimulator(D=1.0, dt=0.01, n_steps=500, 
                               n_particles=50, dim=2, seed=456)
        sim.simulate()
        
        time, msd = sim.compute_msd()
        
        # Skip first few points and fit linear relationship
        # MSD should be proportional to time
        t_fit = time[10:]
        msd_fit = msd[10:]
        
        # Linear regression
        slope = np.sum(t_fit * msd_fit) / np.sum(t_fit**2)
        
        # Slope should be close to 2*dim*D = 4
        self.assertAlmostEqual(slope, 4.0, delta=0.5)
    
    def test_error_before_simulation(self):
        """Test that methods fail appropriately before simulation."""
        sim = BrownianSimulator()
        
        with self.assertRaises(RuntimeError):
            sim.compute_msd()
        
        with self.assertRaises(RuntimeError):
            sim.get_final_positions()
        
        with self.assertRaises(RuntimeError):
            sim.get_displacement_distribution()


class TestStatisticalProperties(unittest.TestCase):
    """Test statistical properties of Brownian motion."""
    
    def test_zero_mean_displacement(self):
        """Test that mean displacement is approximately zero."""
        sim = BrownianSimulator(D=1.0, dt=0.01, n_steps=1000, 
                               n_particles=100, dim=2, seed=789)
        sim.simulate()
        
        final_pos = sim.get_final_positions()
        mean_displacement = np.mean(final_pos, axis=0)
        
        # Mean displacement should be close to zero (within statistical fluctuations)
        self.assertAlmostEqual(mean_displacement[0], 0.0, delta=0.5)
        self.assertAlmostEqual(mean_displacement[1], 0.0, delta=0.5)
    
    def test_variance_growth(self):
        """Test that variance grows linearly with time."""
        sim = BrownianSimulator(D=1.0, dt=0.01, n_steps=500, 
                               n_particles=100, dim=2, seed=321)
        sim.simulate()
        
        # Calculate variance at different times
        times_to_check = [100, 200, 300, 400]
        variances = []
        
        for t_idx in times_to_check:
            positions = sim.trajectories[:, t_idx, :]
            var = np.var(positions)
            variances.append(var)
        
        # Variance should increase roughly linearly
        # Check that later variance is larger
        self.assertGreater(variances[-1], variances[0])


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
