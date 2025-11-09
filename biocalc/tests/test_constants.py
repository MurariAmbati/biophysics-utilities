"""Tests for constants module."""

import pytest
from biocalc.constants import (
    CONSTANTS,
    list_constants,
    get_constant,
    search_constants,
)


def test_constants_exist():
    """Test that key constants are defined."""
    required = ['avogadro', 'boltzmann', 'R', 'ATP_hydrolysis']
    for name in required:
        assert name in CONSTANTS


def test_list_constants():
    """Test listing constants."""
    constants = list_constants()
    assert isinstance(constants, list)
    assert len(constants) > 0
    assert 'avogadro' in constants


def test_get_constant():
    """Test getting a constant."""
    avogadro = get_constant('avogadro')
    assert avogadro.magnitude == pytest.approx(6.022e23, rel=1e-3)
    assert str(avogadro.units) == '1 / mole'


def test_get_constant_unknown():
    """Test getting unknown constant raises error."""
    with pytest.raises(KeyError):
        get_constant('unknown_constant')


def test_search_constants():
    """Test searching for constants."""
    results = search_constants('diffusion')
    assert len(results) > 0
    assert 'diffusion_O2_water' in results


def test_constant_units():
    """Test that constants have correct units."""
    # Energy constant
    atp = CONSTANTS['ATP_hydrolysis']
    assert 'joule' in str(atp.units).lower()
    assert 'mole' in str(atp.units).lower()
    
    # Temperature constant
    temp = CONSTANTS['standard_temperature']
    assert 'kelvin' in str(temp.units).lower()


def test_constant_values():
    """Test specific constant values."""
    assert CONSTANTS['R'].magnitude == pytest.approx(8.314, rel=1e-3)
    assert CONSTANTS['c'].magnitude == pytest.approx(299792458, rel=1e-6)
    assert CONSTANTS['body_temperature'].magnitude == pytest.approx(310.15, rel=1e-4)
