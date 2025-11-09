"""Tests for REPL module."""

import pytest
from io import StringIO
from biocalc.repl import BioCalcREPL


@pytest.fixture
def repl():
    """Create a REPL instance for testing."""
    return BioCalcREPL(precision=3)


def test_repl_creation(repl):
    """Test REPL initialization."""
    assert repl.precision == 3
    assert repl.running is True
    assert len(repl.commands) > 0


def test_cmd_help(repl, capsys):
    """Test help command."""
    repl.cmd_help()
    captured = capsys.readouterr()
    assert "biocalc" in captured.out.lower()
    assert "help" in captured.out.lower()


def test_cmd_list_constants(repl, capsys):
    """Test list constants command."""
    repl.cmd_list_constants()
    captured = capsys.readouterr()
    assert "avogadro" in captured.out.lower()
    assert "boltzmann" in captured.out.lower()


def test_cmd_search(repl, capsys):
    """Test search command."""
    repl.cmd_search(['diffusion'])
    captured = capsys.readouterr()
    assert "diffusion" in captured.out.lower()


def test_cmd_search_no_results(repl, capsys):
    """Test search with no results."""
    repl.cmd_search(['nonexistent_constant'])
    captured = capsys.readouterr()
    assert "no constants found" in captured.out.lower()


def test_cmd_set_precision(repl, capsys):
    """Test setting precision."""
    repl.cmd_set_precision(['5'])
    assert repl.precision == 5
    captured = capsys.readouterr()
    assert "5" in captured.out


def test_cmd_quit(repl):
    """Test quit command."""
    assert repl.running is True
    repl.cmd_quit()
    assert repl.running is False


def test_process_simple_expression(repl, capsys):
    """Test processing a simple expression."""
    repl.process_command("2 + 3")
    captured = capsys.readouterr()
    assert "5" in captured.out


def test_process_constant_expression(repl, capsys):
    """Test processing expression with constant."""
    repl.process_command("R")
    captured = capsys.readouterr()
    assert "8.31" in captured.out or "8.314" in captured.out


def test_process_function_style_energy(repl, capsys):
    """Test function-style energy command."""
    repl.process_command("energy(ATP_hydrolysis)")
    captured = capsys.readouterr()
    assert "50000" in captured.out or "50.0" in captured.out


def test_process_invalid_expression(repl, capsys):
    """Test processing invalid expression."""
    repl.process_command("invalid syntax here $%^")
    captured = capsys.readouterr()
    assert "error" in captured.out.lower()


def test_history_tracking(repl):
    """Test that history is tracked."""
    initial_len = len(repl.history)
    repl.process_command("2 + 3")
    assert len(repl.history) == initial_len + 1
