"""Coulomb electrostatic potential solver."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

# Vacuum permittivity in SI units (C^2/(N m^2)).
EPS0 = 8.854187817e-12


@dataclass
class CoulombParams:
    dielectric: float = 80.0
    cutoff: float = 1e-3  # minimum distance in Angstrom to avoid singularities
    prefactor_scale: float = 1.0  # extra scaling if user wants non-SI units


def compute_potential(
    atoms: np.ndarray,
    grid: np.ndarray,
    params: Optional[CoulombParams] = None,
) -> np.ndarray:
    """Compute Coulomb potential on a grid.

    Parameters
    ----------
    atoms : np.ndarray, shape (N, 4)
        Columns x, y, z, q (Angstrom, e).
    grid : np.ndarray, shape (nx, ny, nz, 3)
        Cartesian coordinates of grid points.
    params : CoulombParams, optional
        Dielectric, cutoff, and scaling.

    Returns
    -------
    phi : np.ndarray, shape (nx, ny, nz)
        Electrostatic potential at each grid point (arbitrary units by default).

    Notes
    -----
    The formula implemented is::

        phi(r) = prefactor * sum_i q_i / |r - r_i|

    where ``prefactor = params.prefactor_scale / (4*pi*eps0*dielectric)``.

    Units: if coordinates are in Angstrom and charges in e, the absolute
    value is unit-dependent. The code is intended for relative comparisons
    and visualization rather than absolute physical units.
    """

    if params is None:
        params = CoulombParams()

    if atoms.ndim != 2 or atoms.shape[1] != 4:
        raise ValueError("atoms must have shape (N,4) with columns x,y,z,q")

    positions = atoms[:, :3]  # (N, 3)
    charges = atoms[:, 3]  # (N,)

    # Flatten grid for efficient broadcasting
    orig_shape = grid.shape[:-1]
    pts = grid.reshape(-1, 3)  # (M, 3)

    # Distances from all grid points to all atoms
    # pts[:, None, :] - positions[None, :, :] -> (M, N, 3)
    diff = pts[:, None, :] - positions[None, :, :]
    d = np.linalg.norm(diff, axis=-1)  # (M, N)

    # Apply cutoff to avoid division by zero
    d = np.maximum(d, params.cutoff)

    # Coulomb prefactor
    prefactor = params.prefactor_scale / (4.0 * np.pi * EPS0 * params.dielectric)

    phi_flat = prefactor * np.sum(charges[None, :] / d, axis=1)
    phi = phi_flat.reshape(orig_shape)
    return phi
