"""
Unit tests for CLI functionality.
"""

import subprocess
import sys
import pytest


class TestCLI:
    """Tests for command-line interface."""
    
    def test_basic_usage(self):
        """Test basic CLI usage with --length flag."""
        result = subprocess.run(
            [sys.executable, "-m", "protein_shape_estimator", "--length", "300"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Hydrodynamic radius:" in result.stdout
        assert "Net charge" in result.stdout
        assert "Diffusion coefficient:" in result.stdout
    
    def test_custom_temperature(self):
        """Test with custom temperature."""
        result = subprocess.run(
            [sys.executable, "-m", "protein_shape_estimator", 
             "--length", "500", "--temp", "310"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "m²/s" in result.stdout
    
    def test_custom_fractions(self):
        """Test with custom charge fractions."""
        result = subprocess.run(
            [sys.executable, "-m", "protein_shape_estimator",
             "--length", "200", "--pos-frac", "0.1", "--neg-frac", "0.05"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Net charge" in result.stdout
    
    def test_missing_required_argument(self):
        """Test that missing --length argument causes error."""
        result = subprocess.run(
            [sys.executable, "-m", "protein_shape_estimator"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "required" in result.stderr.lower() or "required" in result.stdout.lower()
    
    def test_negative_length(self):
        """Test that negative length causes error."""
        result = subprocess.run(
            [sys.executable, "-m", "protein_shape_estimator", "--length", "-100"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "Error:" in result.stderr
    
    def test_zero_length(self):
        """Test that zero length causes error."""
        result = subprocess.run(
            [sys.executable, "-m", "protein_shape_estimator", "--length", "0"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
    
    def test_help_message(self):
        """Test that --help flag works."""
        result = subprocess.run(
            [sys.executable, "-m", "protein_shape_estimator", "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "--length" in result.stdout
        assert "--temp" in result.stdout
        assert "--viscosity" in result.stdout


class TestOutputFormat:
    """Tests for output formatting."""
    
    def test_output_format_300_residues(self):
        """Test output format for 300 residue protein."""
        result = subprocess.run(
            [sys.executable, "-m", "protein_shape_estimator", "--length", "300"],
            capture_output=True,
            text=True
        )
        
        lines = result.stdout.strip().split('\n')
        assert len(lines) == 3
        
        # Check that values are formatted correctly
        assert "nm" in lines[0]
        assert "e" in lines[1]
        assert "m²/s" in lines[2]
        
        # Check for sign in charge (+ or -)
        assert "+" in lines[1] or "-" in lines[1]
