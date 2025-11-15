"""Grid generation utilities for electrostatic potential mapping."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass
class GridSpec:
    nx: int
    ny: int
    nz: int
    spacing: float  # Angstrom per grid step
    center: Tuple[float, float, float]


def infer_center(atoms: np.ndarray) -> Tuple[float, float, float]:
    """Return geometric center of atoms.

    Parameters
    ----------
    atoms : np.ndarray, shape (N, 4)
        Columns x, y, z, q.
    """

    if atoms.size == 0:
        raise ValueError("Empty atoms array.")
    center = atoms[:, :3].mean(axis=0)
    return tuple(center.tolist())  # type: ignore[return-value]


def make_grid(spec: GridSpec) -> np.ndarray:
    """Create a 3D mesh grid.

    Returns
    -------
    grid : np.ndarray, shape (nx, ny, nz, 3)
        Cartesian coordinates of each grid point.
    """

    nx, ny, nz = spec.nx, spec.ny, spec.nz
    spacing = spec.spacing
    cx, cy, cz = spec.center

    # Build axes so that the center coincides with the middle of the grid
    xs = (np.arange(nx) - (nx - 1) / 2.0) * spacing + cx
    ys = (np.arange(ny) - (ny - 1) / 2.0) * spacing + cy
    zs = (np.arange(nz) - (nz - 1) / 2.0) * spacing + cz

    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    grid = np.stack((X, Y, Z), axis=-1)
    return grid
