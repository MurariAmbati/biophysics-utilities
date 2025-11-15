"""Linearized Poisson–Boltzmann electrostatic potential solver."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

EPS0 = 8.854187817e-12


@dataclass
class PBParams:
    dielectric: float = 80.0
    ionic_strength: float = 0.15  # mol/L
    temperature: float = 298.15  # K
    cutoff: float = 1e-3  # Angstrom
    prefactor_scale: float = 1.0

    def kappa(self) -> float:
        """Return Debye screening parameter kappa in 1/Angstrom.

        This uses an approximate relation between ionic strength and Debye
        length in water at room temperature. For simplicity and to avoid
        additional constants, we use a common biophysics approximation::

            lambda_D (nm) ~ 0.304 / sqrt(I / (mol/L))

        kappa = 1 / lambda_D.
        """

        I = max(self.ionic_strength, 1e-8)
        lambda_D_nm = 0.304 / np.sqrt(I)
        lambda_D_A = 10.0 * lambda_D_nm
        return 1.0 / lambda_D_A


def compute_potential(
    atoms: np.ndarray,
    grid: np.ndarray,
    params: Optional[PBParams] = None,
) -> np.ndarray:
    """Compute linearized PB potential on a grid using Yukawa Green's function.

    phi(r) = prefactor * sum_i q_i * exp(-kappa * d) / d
    """

    if params is None:
        params = PBParams()

    if atoms.ndim != 2 or atoms.shape[1] != 4:
        raise ValueError("atoms must have shape (N,4) with columns x,y,z,q")

    positions = atoms[:, :3]
    charges = atoms[:, 3]

    orig_shape = grid.shape[:-1]
    pts = grid.reshape(-1, 3)

    diff = pts[:, None, :] - positions[None, :, :]
    d = np.linalg.norm(diff, axis=-1)
    d = np.maximum(d, params.cutoff)

    kappa = params.kappa()
    prefactor = params.prefactor_scale / (4.0 * np.pi * EPS0 * params.dielectric)

    kernel = np.exp(-kappa * d) / d
    phi_flat = prefactor * np.sum(charges[None, :] * kernel, axis=1)
    phi = phi_flat.reshape(orig_shape)
    return phi
