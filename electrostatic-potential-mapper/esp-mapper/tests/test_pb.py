"""Tests for linearized PB potential solver."""

from __future__ import annotations

import numpy as np

from src import grid, pb_linear


def _single_charge_atoms() -> np.ndarray:
    return np.array([[0.0, 0.0, 0.0, 1.0]], dtype=float)


def test_screening_reduces_potential():
    atoms = _single_charge_atoms()
    center = (0.0, 0.0, 0.0)
    spec = grid.GridSpec(nx=5, ny=1, nz=1, spacing=1.0, center=center)
    mesh = grid.make_grid(spec)

    params_lowI = pb_linear.PBParams(ionic_strength=0.01)
    params_highI = pb_linear.PBParams(ionic_strength=0.5)

    phi_low = pb_linear.compute_potential(atoms, mesh, params_lowI)
    phi_high = pb_linear.compute_potential(atoms, mesh, params_highI)

    # At a distance from the center, stronger screening -> lower potential
    assert np.all(phi_high[0, :, :] < phi_low[0, :, :])
