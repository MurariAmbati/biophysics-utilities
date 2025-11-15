"""Visualization utilities for electrostatic potential grids."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

import numpy as np
import matplotlib.pyplot as plt


@dataclass
class SliceSpec:
    axis: str = "z"  # "x", "y", or "z"
    index: int | None = None  # if None, use central slice


def _slice_along_axis(phi: np.ndarray, spec: SliceSpec) -> Tuple[np.ndarray, int]:
    axis = spec.axis.lower()
    if axis not in {"x", "y", "z"}:
        raise ValueError("axis must be 'x', 'y', or 'z'")

    nx, ny, nz = phi.shape
    if axis == "x":
        n = nx
    elif axis == "y":
        n = ny
    else:
        n = nz

    idx = spec.index if spec.index is not None else n // 2
    if not (0 <= idx < n):
        raise IndexError(f"slice index {idx} out of range for axis size {n}")

    if axis == "x":
        return phi[idx, :, :], idx
    elif axis == "y":
        return phi[:, idx, :], idx
    else:
        return phi[:, :, idx], idx


def show_slice(
    phi: np.ndarray,
    spec: SliceSpec | None = None,
    atoms: np.ndarray | None = None,
    cmap: str = "bwr",
    vmin: float | None = None,
    vmax: float | None = None,
) -> None:
    """Display a 2D slice of the potential.

    Parameters
    ----------
    phi : np.ndarray, shape (nx, ny, nz)
        Potential grid.
    spec : SliceSpec, optional
        Axis and index for the slice. If None, uses central z-slice.
    atoms : np.ndarray, shape (N, 4), optional
        If provided, overlays atom positions projected onto the slice plane.
    """

    if phi.ndim != 3:
        raise ValueError("phi must be 3D array")
    if spec is None:
        spec = SliceSpec()

    slice2d, idx = _slice_along_axis(phi, spec)

    plt.figure()
    im = plt.imshow(
        slice2d.T,
        origin="lower",
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
    )
    plt.colorbar(im, label="Potential (arb. units)")
    plt.title(f"Potential slice {spec.axis} = {idx}")

    if atoms is not None and atoms.size > 0:
        coords = atoms[:, :3]
        if spec.axis == "x":
            x = coords[:, 1]
            y = coords[:, 2]
        elif spec.axis == "y":
            x = coords[:, 0]
            y = coords[:, 2]
        else:
            x = coords[:, 0]
            y = coords[:, 1]
        plt.scatter(x, y, c="k", s=10, alpha=0.7)

    plt.tight_layout()
    plt.show()


def save_npy(path: str, phi: np.ndarray) -> None:
    np.save(path, phi)


def save_csv_slice(path: str, phi: np.ndarray, axis: str = "z", index: int | None = None) -> None:
    """Save a 2D slice to CSV file."""

    slice2d, _ = _slice_along_axis(phi, SliceSpec(axis=axis, index=index))
    np.savetxt(path, slice2d, delimiter=",")
