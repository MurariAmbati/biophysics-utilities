"""
Unit tests for core computation functions.
"""

import pytest
import math
from protein_shape_estimator.core import (
    molecular_weight,
    hydrodynamic_radius,
    net_charge,
    diffusion_coefficient,
)
from protein_shape_estimator.constants import (
    AVG_MW_PER_RESIDUE,
    K_B,
    DEFAULT_TEMP,
    DEFAULT_VISCOSITY,
)


class TestMolecularWeight:
    """Tests for molecular weight calculation."""
    
    def test_basic_calculation(self):
        """Test basic molecular weight calculation."""
        assert molecular_weight(100) == 11000
        assert molecular_weight(300) == 33000
        assert molecular_weight(500) == 55000
    
    def test_single_residue(self):
        """Test single residue."""
        assert molecular_weight(1) == AVG_MW_PER_RESIDUE


class TestHydrodynamicRadius:
    """Tests for hydrodynamic radius calculation."""
    
    def test_positive_values(self):
        """Test that hydrodynamic radius is positive."""
        assert hydrodynamic_radius(100) > 0
        assert hydrodynamic_radius(300) > 0
        assert hydrodynamic_radius(500) > 0
    
    def test_scaling(self):
        """Test that radius increases with sequence length."""
        r1 = hydrodynamic_radius(100)
        r2 = hydrodynamic_radius(200)
        r3 = hydrodynamic_radius(400)
        assert r2 > r1
        assert r3 > r2
    
    def test_expected_magnitude(self):
        """Test that radius is in expected range (nanometers when converted)."""
        # For 300 residues, should be around 2-3 nm
        r_h = hydrodynamic_radius(300)
        r_h_nm = r_h * 1e9
        assert 2.0 < r_h_nm < 4.0


class TestNetCharge:
    """Tests for net charge calculation."""
    
    def test_default_composition(self):
        """Test net charge with default composition."""
        # With f_pos=0.08 and f_neg=0.07, net charge should be positive
        z = net_charge(100)
        assert z == 1.0  # 100 * (0.08 - 0.07) = 1.0
    
    def test_custom_composition(self):
        """Test net charge with custom composition."""
        # More positive residues
        z_pos = net_charge(100, f_pos=0.15, f_neg=0.05)
        assert z_pos == 10.0
        
        # More negative residues
        z_neg = net_charge(100, f_pos=0.05, f_neg=0.15)
        assert z_neg == -10.0
    
    def test_neutral_protein(self):
        """Test neutral protein."""
        z = net_charge(100, f_pos=0.1, f_neg=0.1)
        assert z == 0.0


class TestDiffusionCoefficient:
    """Tests for diffusion coefficient calculation."""
    
    def test_stokes_einstein(self):
        """Test Stokes-Einstein relation."""
        # For a 1 nm radius particle at 298 K in water
        R_h = 1e-9  # 1 nm in meters
        D = diffusion_coefficient(R_h)
        
        # Expected value: k_B * T / (6 * pi * eta * R_h)
        expected = K_B * DEFAULT_TEMP / (6 * math.pi * DEFAULT_VISCOSITY * R_h)
        assert abs(D - expected) < 1e-20
    
    def test_temperature_dependence(self):
        """Test that diffusion coefficient increases with temperature."""
        R_h = 2e-9
        D_298 = diffusion_coefficient(R_h, temp=298)
        D_310 = diffusion_coefficient(R_h, temp=310)
        assert D_310 > D_298
    
    def test_viscosity_dependence(self):
        """Test that diffusion coefficient decreases with viscosity."""
        R_h = 2e-9
        D_low = diffusion_coefficient(R_h, viscosity=1e-3)
        D_high = diffusion_coefficient(R_h, viscosity=2e-3)
        assert D_low > D_high
    
    def test_size_dependence(self):
        """Test that smaller particles diffuse faster."""
        D_small = diffusion_coefficient(1e-9)  # 1 nm
        D_large = diffusion_coefficient(3e-9)  # 3 nm
        assert D_small > D_large


class TestIntegration:
    """Integration tests combining multiple functions."""
    
    def test_typical_protein(self):
        """Test a typical medium-sized protein."""
        n_res = 300
        
        # Calculate all properties
        R_h = hydrodynamic_radius(n_res)
        Z = net_charge(n_res)
        D = diffusion_coefficient(R_h)
        
        # Sanity checks
        assert 2e-9 < R_h < 4e-9  # 2-4 nm
        assert 0 < Z < 10  # Small positive charge
        assert 5e-11 < D < 1e-10  # Reasonable diffusion coefficient
