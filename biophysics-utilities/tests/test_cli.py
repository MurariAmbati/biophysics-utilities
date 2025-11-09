"""Tests for CLI commands."""

import pytest
from click.testing import CliRunner
from kinetics_playground.cli.main import main


class TestCLI:
    """Test suite for CLI."""
    
    def test_main_help(self):
        """Test main help command."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert 'Reaction Kinetics Playground' in result.output
    
    def test_presets_command(self):
        """Test presets listing."""
        runner = CliRunner()
        result = runner.invoke(main, ['presets'])
        assert result.exit_code == 0
        assert 'Available Reaction Network Presets' in result.output
    
    def test_parse_command(self):
        """Test parse command."""
        runner = CliRunner()
        result = runner.invoke(main, ['parse', 'A + B -> C ; 0.1'])
        assert result.exit_code == 0


if __name__ == '__main__':
    pytest.main([__file__])
