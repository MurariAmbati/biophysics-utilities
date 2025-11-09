"""
Tests for the command-line interface.
"""
import pytest
import sys
from io import StringIO
from diffusion_time_estimator.__main__ import main


class TestCLI:
    """Tests for command-line interface."""
    
    def test_basic_usage(self, monkeypatch, capsys):
        """Test basic CLI usage with required argument."""
        test_args = ['diffusion-time', '--radius', '1e-9']
        monkeypatch.setattr(sys, 'argv', test_args)
        
        result = main()
        
        assert result == 0
        captured = capsys.readouterr()
        assert "diffusion coefficient" in captured.out.lower()
        assert "diffusion time" in captured.out.lower()
    
    def test_all_arguments(self, monkeypatch, capsys):
        """Test CLI with all arguments specified."""
        test_args = [
            'diffusion-time',
            '--radius', '1e-9',
            '--viscosity', '1e-3',
            '--temperature', '298',
            '--distance', '1e-6',
            '--dims', '3'
        ]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        result = main()
        
        assert result == 0
        captured = capsys.readouterr()
        assert "2.1" in captured.out and "e-10" in captured.out
    
    def test_verbose_output(self, monkeypatch, capsys):
        """Test verbose output mode."""
        test_args = [
            'diffusion-time',
            '--radius', '1e-9',
            '--verbose'
        ]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        result = main()
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Input Parameters" in captured.out
        assert "Results" in captured.out
        assert "Molecule radius" in captured.out
    
    def test_missing_required_argument(self, monkeypatch, capsys):
        """Test that missing required argument causes error."""
        test_args = ['diffusion-time']
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code != 0
    
    def test_invalid_radius(self):
        """Test that invalid radius value is caught by validation."""
        # Test directly with the core function since argparse can't handle negative scientific notation easily
        from diffusion_time_estimator.core import diffusion_coefficient
        with pytest.raises(ValueError, match="Radius must be positive"):
            diffusion_coefficient(-1e-9, 1e-3, 298)
    
    def test_dimension_choices(self, monkeypatch, capsys):
        """Test different dimension choices."""
        for dims in [1, 2, 3]:
            test_args = [
                'diffusion-time',
                '--radius', '1e-9',
                '--dims', str(dims)
            ]
            monkeypatch.setattr(sys, 'argv', test_args)
            
            result = main()
            assert result == 0
    
    def test_invalid_dimension(self, monkeypatch, capsys):
        """Test that invalid dimension is rejected."""
        test_args = [
            'diffusion-time',
            '--radius', '1e-9',
            '--dims', '4'
        ]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code != 0
    
    def test_short_flags(self, monkeypatch, capsys):
        """Test that short flags work."""
        test_args = [
            'diffusion-time',
            '-r', '1e-9',
            '-v', '2e-3',
            '-T', '310',
            '-L', '1e-5',
            '-n', '2'
        ]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        result = main()
        
        assert result == 0
    
    def test_help_message(self, monkeypatch):
        """Test that help message is displayed."""
        test_args = ['diffusion-time', '--help']
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        # Help should exit with code 0
        assert exc_info.value.code == 0
    
    def test_example_from_docs(self, monkeypatch, capsys):
        """Test the example from the documentation."""
        test_args = [
            'diffusion-time',
            '--radius', '1e-9',
            '--viscosity', '1e-3',
            '--distance', '1e-6'
        ]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        result = main()
        
        assert result == 0
        captured = capsys.readouterr()
        # Should show coefficient around 2.18e-10 m²/s
        assert "2.1" in captured.out and "e-10" in captured.out
        # Should show time in μs range
        assert "μs" in captured.out or "us" in captured.out
