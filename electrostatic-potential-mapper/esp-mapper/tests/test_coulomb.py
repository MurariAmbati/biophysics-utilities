"""Tests for Coulomb potential solver."""

from __future__ import annotations

import numpy as np

from src import coulomb, grid


def _single_charge_atoms() -> np.ndarray:
    # Single +1e charge at origin
    return np.array([[0.0, 0.0, 0.0, 1.0]], dtype=float)


def test_radial_symmetry():
    atoms = _single_charge_atoms()
    center = (0.0, 0.0, 0.0)
    spec = grid.GridSpec(nx=5, ny=5, nz=5, spacing=1.0, center=center)
    mesh = grid.make_grid(spec)

    phi = coulomb.compute_potential(atoms, mesh)

    # Opposite points along x-axis should have same potential
    mid = spec.nx // 2
    left = phi[0, mid, mid]
    right = phi[-1, mid, mid]
    assert np.isclose(left, right)


def test_decay_with_distance():
    atoms = _single_charge_atoms()
    center = (0.0, 0.0, 0.0)
    spec = grid.GridSpec(nx=5, ny=1, nz=1, spacing=1.0, center=center)
    mesh = grid.make_grid(spec)
    phi = coulomb.compute_potential(atoms, mesh)

    # Potential magnitude should decrease as distance increases
    assert phi[2, 0, 0] > phi[0, 0, 0]
