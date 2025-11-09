"""Tests for units module."""

import pytest
from biocalc.units import (
    ureg,
    convert,
    parse_quantity,
    check_dimensionality,
    strip_units,
    add_units,
    format_quantity,
)


def test_convert_energy():
    """Test energy unit conversion."""
    result = convert("1 kcal/mol", "J/mol")
    assert result.magnitude == pytest.approx(4184.0, rel=1e-3)


def test_convert_quantity_object():
    """Test conversion with Quantity object."""
    value = ureg.Quantity(50, "kJ/mol")
    result = convert(value, "kcal/mol")
    assert result.magnitude == pytest.approx(11.95, rel=1e-2)


def test_convert_incompatible_units():
    """Test that incompatible unit conversion raises error."""
    with pytest.raises(ValueError):
        convert("1 meter", "second")


def test_parse_quantity():
    """Test parsing quantity strings."""
    q = parse_quantity("50 kJ/mol")
    assert q.magnitude == 50.0
    assert 'kilojoule' in str(q.units).lower()


def test_parse_quantity_scientific():
    """Test parsing scientific notation."""
    q = parse_quantity("2.1e-9 m^2/s")
    assert q.magnitude == pytest.approx(2.1e-9)


def test_check_dimensionality():
    """Test dimensionality checking."""
    q = ureg.Quantity(50, "kJ/mol")
    assert check_dimensionality(q, "[energy]/[substance]")


def test_strip_units():
    """Test stripping units."""
    q = ureg.Quantity(42.0, "m/s")
    mag = strip_units(q)
    assert mag == 42.0
    assert isinstance(mag, (int, float))


def test_add_units():
    """Test adding units."""
    q = add_units(50000, "J/mol")
    assert q.magnitude == 50000
    assert 'joule' in str(q.units).lower()


def test_format_quantity():
    """Test formatting quantities."""
    q = ureg.Quantity(4184.0, "J/mol")
    formatted = format_quantity(q, precision=2)
    assert "4184.00" in formatted
    assert "J/mol" in formatted or "joule" in formatted.lower()


def test_temperature_conversion():
    """Test temperature conversion."""
    result = convert("298.15 K", "celsius")
    assert result.magnitude == pytest.approx(25.0, rel=1e-2)


def test_concentration_units():
    """Test concentration units."""
    q = parse_quantity("5 mmol/L")
    result = convert(q, "mol/L")
    assert result.magnitude == pytest.approx(0.005, rel=1e-6)
