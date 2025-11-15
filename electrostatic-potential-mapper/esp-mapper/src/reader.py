"""Molecular input parser for electrostatic potential mapper.

Supported formats
-----------------
- Plain text: columns x y z q (Angstrom, e)
- CSV: columns x,y,z,q
- Minimal PDB with charges in REMARK CHARGE lines: `REMARK CHARGE idx q`

Returns
-------
np.ndarray of shape (N, 4) with columns (x, y, z, q).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

import numpy as np


@dataclass
class Atom:
    x: float
    y: float
    z: float
    q: float

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z, self.q], dtype=float)


def _parse_txt_or_csv(lines: Iterable[str], sep: str | None = None) -> List[Atom]:
    atoms: List[Atom] = []
    for lineno, line in enumerate(lines, start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if sep is None:
            parts = line.split()
        else:
            parts = [p for p in line.split(sep) if p]
        if len(parts) < 4:
            raise ValueError(f"Line {lineno}: expected at least 4 columns (x y z q), got {len(parts)}: {line!r}")
        try:
            x, y, z, q = map(float, parts[:4])
        except ValueError as exc:
            raise ValueError(f"Line {lineno}: could not parse floats from: {line!r}") from exc
        atoms.append(Atom(x, y, z, q))
    if not atoms:
        raise ValueError("No atoms parsed from input file.")
    return atoms


def _parse_pdb(lines: Iterable[str]) -> List[Atom]:
    """Parse a minimal PDB with charges.

    Assumes atomic coordinates from ATOM/HETATM records and charges from
    `REMARK CHARGE` lines of the form::

        REMARK CHARGE  <serial>  <q>

    The serial must match the atom serial in columns 7-11 of ATOM/HETATM.
    """

    coords: dict[int, Tuple[float, float, float]] = {}
    charges: dict[int, float] = {}

    for line in lines:
        record = line[:6].strip().upper()
        if record in {"ATOM", "HETATM"}:
            try:
                serial = int(line[6:11])
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
            except ValueError:
                continue
            coords[serial] = (x, y, z)
        elif line.startswith("REMARK CHARGE"):
            parts = line.split()
            if len(parts) >= 4:
                try:
                    serial = int(parts[2])
                    q = float(parts[3])
                except ValueError:
                    continue
                charges[serial] = q

    if not coords:
        raise ValueError("No ATOM/HETATM records found in PDB.")
    if not charges:
        raise ValueError("No REMARK CHARGE records found in PDB.")

    atoms: List[Atom] = []
    for serial, (x, y, z) in coords.items():
        if serial not in charges:
            raise ValueError(f"Missing charge for atom serial {serial} in PDB.")
        atoms.append(Atom(x, y, z, charges[serial]))

    return atoms


def load_atoms(path: str | Path) -> np.ndarray:
    """Load atoms from a text, CSV, or PDB file.

    Parameters
    ----------
    path:
        Path to input file.

    Returns
    -------
    atoms : np.ndarray, shape (N, 4)
        Columns: x, y, z, q.
    """

    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)

    suffix = path.suffix.lower()
    text = path.read_text().splitlines()

    if suffix in {".txt", ".dat", ""}:
        atoms = _parse_txt_or_csv(text)
    elif suffix == ".csv":
        atoms = _parse_txt_or_csv(text, sep=",")
    elif suffix in {".pdb", ".ent"}:
        atoms = _parse_pdb(text)
    else:
        raise ValueError(f"Unsupported file extension: {suffix}")

    arr = np.vstack([a.to_array() for a in atoms])

    # basic validation
    if not np.all(np.isfinite(arr)):
        raise ValueError("Non-finite coordinate or charge encountered.")

    return arr
