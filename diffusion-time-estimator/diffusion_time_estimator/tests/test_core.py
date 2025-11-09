"""
Tests for core diffusion calculation functions.
"""
import pytest
import math
from diffusion_time_estimator.core import (
    diffusion_coefficient,
    diffusion_time,
    mean_square_displacement,
    format_time,
    format_coefficient
)
from diffusion_time_estimator.constants import k_B


class TestDiffusionCoefficient:
    """Tests for the Stokes-Einstein relation."""
    
    def test_basic_calculation(self):
        """Test basic diffusion coefficient calculation."""
        # Water-like conditions: r=1nm, η=1mPa·s, T=298K
        radius = 1e-9
        viscosity = 1e-3
        temperature = 298
        
        D = diffusion_coefficient(radius, viscosity, temperature)
        
        # Expected: k_B * T / (6 * π * η * r)
        expected = k_B * 298 / (6 * math.pi * 1e-3 * 1e-9)
        assert abs(D - expected) < 1e-15
        assert D > 0
    
    def test_temperature_dependence(self):
        """Test that D scales linearly with temperature."""
        radius = 1e-9
        viscosity = 1e-3
        
        D1 = diffusion_coefficient(radius, viscosity, 300)
        D2 = diffusion_coefficient(radius, viscosity, 600)
        
        # D should double when temperature doubles
        assert abs(D2 / D1 - 2.0) < 1e-10
    
    def test_radius_dependence(self):
        """Test that D scales as 1/r."""
        viscosity = 1e-3
        temperature = 298
        
        D1 = diffusion_coefficient(1e-9, viscosity, temperature)
        D2 = diffusion_coefficient(2e-9, viscosity, temperature)
        
        # D should halve when radius doubles
        assert abs(D1 / D2 - 2.0) < 1e-10
    
    def test_viscosity_dependence(self):
        """Test that D scales as 1/η."""
        radius = 1e-9
        temperature = 298
        
        D1 = diffusion_coefficient(radius, 1e-3, temperature)
        D2 = diffusion_coefficient(radius, 2e-3, temperature)
        
        # D should halve when viscosity doubles
        assert abs(D1 / D2 - 2.0) < 1e-10
    
    def test_invalid_inputs(self):
        """Test that invalid inputs raise appropriate errors."""
        with pytest.raises(ValueError, match="Radius must be positive"):
            diffusion_coefficient(-1e-9, 1e-3, 298)
        
        with pytest.raises(ValueError, match="Viscosity must be positive"):
            diffusion_coefficient(1e-9, -1e-3, 298)
        
        with pytest.raises(ValueError, match="Temperature must be positive"):
            diffusion_coefficient(1e-9, 1e-3, -298)


class TestDiffusionTime:
    """Tests for characteristic diffusion time calculation."""
    
    def test_basic_calculation(self):
        """Test basic diffusion time calculation."""
        distance = 1e-6  # 1 μm
        D = 1e-10  # m²/s
        dims = 3
        
        t = diffusion_time(distance, D, dims)
        
        # Expected: L² / (2 * n * D)
        expected = (1e-6)**2 / (2 * 3 * 1e-10)
        assert abs(t - expected) < 1e-15
        assert t > 0
    
    def test_distance_scaling(self):
        """Test that time scales as L²."""
        D = 1e-10
        dims = 3
        
        t1 = diffusion_time(1e-6, D, dims)
        t2 = diffusion_time(2e-6, D, dims)
        
        # Time should quadruple when distance doubles
        assert abs(t2 / t1 - 4.0) < 1e-10
    
    def test_dimension_dependence(self):
        """Test behavior across different dimensions."""
        distance = 1e-6
        D = 1e-10
        
        t1 = diffusion_time(distance, D, 1)
        t2 = diffusion_time(distance, D, 2)
        t3 = diffusion_time(distance, D, 3)
        
        # Higher dimensions should give shorter times
        assert t1 > t2 > t3
        assert abs(t1 / t2 - 2.0) < 1e-10
        assert abs(t1 / t3 - 3.0) < 1e-10
    
    def test_invalid_inputs(self):
        """Test that invalid inputs raise appropriate errors."""
        with pytest.raises(ValueError, match="Distance must be positive"):
            diffusion_time(-1e-6, 1e-10, 3)
        
        with pytest.raises(ValueError, match="Diffusion coefficient must be positive"):
            diffusion_time(1e-6, -1e-10, 3)
        
        with pytest.raises(ValueError, match="Dimensions must be 1, 2, or 3"):
            diffusion_time(1e-6, 1e-10, 4)


class TestMeanSquareDisplacement:
    """Tests for MSD calculation."""
    
    def test_basic_calculation(self):
        """Test basic MSD calculation."""
        D = 1e-10
        t = 1.0
        dims = 3
        
        msd = mean_square_displacement(D, t, dims)
        
        # Expected: 2 * n * D * t
        expected = 2 * 3 * 1e-10 * 1.0
        assert abs(msd - expected) < 1e-15
        assert msd > 0
    
    def test_time_scaling(self):
        """Test that MSD scales linearly with time."""
        D = 1e-10
        dims = 3
        
        msd1 = mean_square_displacement(D, 1.0, dims)
        msd2 = mean_square_displacement(D, 2.0, dims)
        
        # MSD should double when time doubles
        assert abs(msd2 / msd1 - 2.0) < 1e-10
    
    def test_dimension_dependence(self):
        """Test behavior across different dimensions."""
        D = 1e-10
        t = 1.0
        
        msd1 = mean_square_displacement(D, t, 1)
        msd2 = mean_square_displacement(D, t, 2)
        msd3 = mean_square_displacement(D, t, 3)
        
        # MSD should scale linearly with dimension
        assert abs(msd2 / msd1 - 2.0) < 1e-10
        assert abs(msd3 / msd1 - 3.0) < 1e-10
    
    def test_array_input(self):
        """Test that function works with array input."""
        import numpy as np
        
        D = 1e-10
        t = np.array([1.0, 2.0, 3.0])
        dims = 3
        
        msd = mean_square_displacement(D, t, dims)
        
        assert len(msd) == 3
        assert all(msd > 0)
        # Check linear scaling
        assert abs(msd[1] / msd[0] - 2.0) < 1e-10
        assert abs(msd[2] / msd[0] - 3.0) < 1e-10
    
    def test_invalid_inputs(self):
        """Test that invalid inputs raise appropriate errors."""
        with pytest.raises(ValueError, match="Diffusion coefficient must be positive"):
            mean_square_displacement(-1e-10, 1.0, 3)
        
        with pytest.raises(ValueError, match="Dimensions must be 1, 2, or 3"):
            mean_square_displacement(1e-10, 1.0, 0)


class TestFormattingFunctions:
    """Tests for output formatting functions."""
    
    def test_format_time_seconds(self):
        """Test time formatting in seconds."""
        assert "1" in format_time(1.5)
        assert "s" in format_time(1.5)
    
    def test_format_time_milliseconds(self):
        """Test time formatting in milliseconds."""
        result = format_time(0.005)
        assert "ms" in result
        assert "5" in result
    
    def test_format_time_microseconds(self):
        """Test time formatting in microseconds."""
        result = format_time(5e-6)
        assert "μs" in result
        assert "5" in result
    
    def test_format_time_nanoseconds(self):
        """Test time formatting in nanoseconds."""
        result = format_time(5e-9)
        assert "ns" in result
        assert "5" in result
    
    def test_format_coefficient(self):
        """Test diffusion coefficient formatting."""
        result = format_coefficient(2.18e-10)
        assert "2.18" in result or "2.2" in result
        assert "e-10" in result
        assert "m²/s" in result


class TestPhysicalRealism:
    """Tests that check physical realism of results."""
    
    def test_water_glucose(self):
        """Test diffusion of glucose in water at room temperature."""
        # Glucose: radius ~ 0.5 nm
        # Water: viscosity ~ 1 mPa·s, T = 298 K
        radius = 0.5e-9
        viscosity = 1e-3
        temperature = 298
        
        D = diffusion_coefficient(radius, viscosity, temperature)
        
        # Experimental D for glucose in water ~ 6e-10 m²/s
        # Our estimate should be within an order of magnitude
        assert 1e-10 < D < 1e-9
    
    def test_protein_cytoplasm(self):
        """Test diffusion of a small protein in cytoplasm."""
        # Small protein: radius ~ 2 nm
        # Cytoplasm: viscosity ~ 3 mPa·s, T = 310 K (body temp)
        radius = 2e-9
        viscosity = 3e-3
        temperature = 310
        
        D = diffusion_coefficient(radius, viscosity, temperature)
        
        # Should be slower than water but still reasonable
        assert 1e-11 < D < 1e-9
    
    def test_cell_crossing_time(self):
        """Test time to cross a typical cell."""
        # Small molecule in water crossing 10 μm
        radius = 1e-9
        viscosity = 1e-3
        D = diffusion_coefficient(radius, viscosity, 298)
        
        distance = 10e-6
        t = diffusion_time(distance, D, 3)
        
        # Should be on order of milliseconds to seconds
        assert 0.001 < t < 10
