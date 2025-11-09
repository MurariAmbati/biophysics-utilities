"""Tests for parser module."""

import pytest
from biocalc.parser import (
    evaluate,
    parse_expression,
    extract_units_from_expression,
    substitute_and_eval,
    energy,
)


def test_evaluate_simple():
    """Test simple expression evaluation."""
    result = evaluate("2 + 3", return_units=False)
    assert result == 5.0


def test_evaluate_with_constant():
    """Test evaluation with constant."""
    result = evaluate("R * 300", return_units=False)
    assert result == pytest.approx(2494.34, rel=1e-4)


def test_evaluate_with_units():
    """Test evaluation with units."""
    result = evaluate("50 kJ/mol")
    assert hasattr(result, 'magnitude')
    assert result.magnitude == 50.0


def test_evaluate_avogadro():
    """Test Avogadro's number calculation."""
    result = evaluate("avogadro * 1e-3", return_units=False)
    assert result == pytest.approx(6.022e20, rel=1e-3)


def test_parse_expression():
    """Test expression parsing."""
    expr = parse_expression("R * T")
    assert 'R' in str(expr)
    assert 'T' in str(expr)


def test_extract_units():
    """Test unit extraction."""
    expr, unit = extract_units_from_expression("50 kJ/mol")
    assert expr == "50"
    assert unit == "kJ/mol"


def test_extract_units_no_units():
    """Test extraction when no units present."""
    expr, unit = extract_units_from_expression("R * 300")
    assert "R * 300" in expr
    assert unit is None


def test_substitute_and_eval():
    """Test substitution and evaluation."""
    result = substitute_and_eval("R * T", {"T": 300})
    assert result == pytest.approx(2494.34, rel=1e-4)


def test_energy_function():
    """Test energy function."""
    result = energy("ATP_hydrolysis")
    assert hasattr(result, 'magnitude')
    assert result.magnitude == 50000.0


def test_energy_unknown_constant():
    """Test energy with unknown constant."""
    with pytest.raises(ValueError):
        energy("unknown_constant")


def test_evaluate_with_precision():
    """Test evaluation with precision."""
    result = evaluate("22/7", return_units=False, precision=3)
    assert result == pytest.approx(3.143, abs=0.001)


def test_math_functions():
    """Test math functions in expressions."""
    import math
    result = evaluate("exp(1)", return_units=False)
    assert result == pytest.approx(math.e, rel=1e-6)
