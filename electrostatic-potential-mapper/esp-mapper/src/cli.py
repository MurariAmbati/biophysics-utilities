"""Command-line interface for the electrostatic potential mapper."""

from __future__ import annotations

import argparse
import cmd
from pathlib import Path
from typing import Optional

import numpy as np

from . import coulomb, grid, pb_linear, reader, visualize


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="esp-map", description="Electrostatic potential mapper")
    p.add_argument("--input", "-i", type=str, help="Input atoms file (txt/csv/pdb)")
    p.add_argument("--mode", "-m", choices=["coulomb", "pb"], default="coulomb")
    p.add_argument("--dielectric", "-e", type=float, default=80.0)
    p.add_argument("--grid", "-g", type=int, default=80, help="Grid size per axis (Nx=Ny=Nz)")
    p.add_argument("--spacing", "-s", type=float, default=0.5, help="Grid spacing in Angstrom")
    p.add_argument("--ionic-strength", "-I", type=float, default=0.15, help="Ionic strength in mol/L (for PB)")
    p.add_argument("--out", "-o", type=str, help="Output .npy file for potential")
    p.add_argument("--slice", type=str, help="Optional slice description, e.g. z=0")
    return p


def run_single_shot(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.input:
        parser.error("--input is required in single-shot mode")

    atoms = reader.load_atoms(args.input)
    center = grid.infer_center(atoms)
    spec = grid.GridSpec(nx=args.grid, ny=args.grid, nz=args.grid, spacing=args.spacing, center=center)
    mesh = grid.make_grid(spec)

    if args.mode == "coulomb":
        params = coulomb.CoulombParams(dielectric=args.dielectric)
        phi = coulomb.compute_potential(atoms, mesh, params)
    else:
        params = pb_linear.PBParams(dielectric=args.dielectric, ionic_strength=args.ionic_strength)
        phi = pb_linear.compute_potential(atoms, mesh, params)

    if args.out:
        visualize.save_npy(args.out, phi)

    if args.slice:
        try:
            axis, idx_str = args.slice.split("=")
            idx = int(idx_str)
        except Exception:
            parser.error("Invalid --slice format, expected like 'z=0'")
        visualize.show_slice(phi, visualize.SliceSpec(axis=axis, index=idx), atoms=atoms)

    return 0


class ESPRepl(cmd.Cmd):
    intro = "Electrostatic potential mapper REPL. Type help or ? to list commands."
    prompt = "esp-map> "

    def __init__(self) -> None:
        super().__init__()
        self.atoms: Optional[np.ndarray] = None
        self.mode: str = "coulomb"
        self.dielectric: float = 80.0
        self.grid_size: int = 80
        self.spacing: float = 0.5
        self.ionic_strength: float = 0.15
        self.phi: Optional[np.ndarray] = None

    # basic helpers
    def _require_atoms(self) -> None:
        if self.atoms is None:
            print("No atoms loaded. Use 'load <path>'.")
            raise cmd.Cmd

    def _require_phi(self) -> None:
        if self.phi is None:
            print("No potential computed. Use 'compute'.")
            raise cmd.Cmd

    def do_load(self, arg: str) -> None:
        """load <path>

        Load atomic coordinates and charges from file.
        """

        path = arg.strip()
        if not path:
            print("Usage: load <path>")
            return
        try:
            self.atoms = reader.load_atoms(path)
        except Exception as exc:
            print(f"Error loading atoms: {exc}")
            return
        print(f"Loaded {self.atoms.shape[0]} atoms from {path}.")

    def do_mode(self, arg: str) -> None:
        """mode <coulomb|pb>

        Set computation mode.
        """

        mode = arg.strip().lower()
        if mode not in {"coulomb", "pb"}:
            print("Mode must be 'coulomb' or 'pb'.")
            return
        self.mode = mode
        print(f"Mode set to {self.mode}.")

    def do_dielectric(self, arg: str) -> None:
        """dielectric <value>

        Set dielectric constant.
        """

        try:
            self.dielectric = float(arg.strip())
        except ValueError:
            print("Usage: dielectric <float>")
            return
        print(f"Dielectric set to {self.dielectric}.")

    def do_grid(self, arg: str) -> None:
        """grid <nx> [ny nz]

        Set grid size. If ny and nz are omitted, uses cubic grid.
        """

        parts = arg.split()
        if not parts:
            print("Usage: grid <nx> [ny nz]")
            return
        try:
            n = list(map(int, parts))
        except ValueError:
            print("Grid sizes must be integers.")
            return
        if len(n) == 1:
            self.grid_size = n[0]
        else:
            # For simplicity, only store one size; different dimensions could be added later
            if len(set(n)) != 1:
                print("Non-cubic grids not yet supported; using nx for all dimensions.")
            self.grid_size = n[0]
        print(f"Grid size set to {self.grid_size}^3.")

    def do_spacing(self, arg: str) -> None:
        """spacing <value>

        Set grid spacing in Angstrom.
        """

        try:
            self.spacing = float(arg.strip())
        except ValueError:
            print("Usage: spacing <float>")
            return
        print(f"Grid spacing set to {self.spacing} Å.")

    def do_ionic_strength(self, arg: str) -> None:
        """ionic_strength <value>

        Set ionic strength in mol/L (for PB mode).
        """

        try:
            self.ionic_strength = float(arg.strip())
        except ValueError:
            print("Usage: ionic_strength <float>")
            return
        print(f"Ionic strength set to {self.ionic_strength} mol/L.")

    def do_compute(self, arg: str) -> None:  # noqa: ARG002
        """compute

        Compute electrostatic potential on the current grid.
        """

        if self.atoms is None:
            print("No atoms loaded.")
            return

        center = grid.infer_center(self.atoms)
        spec = grid.GridSpec(
            nx=self.grid_size,
            ny=self.grid_size,
            nz=self.grid_size,
            spacing=self.spacing,
            center=center,
        )
        mesh = grid.make_grid(spec)

        print("Computing electrostatic potential...")
        if self.mode == "coulomb":
            params = coulomb.CoulombParams(dielectric=self.dielectric)
            self.phi = coulomb.compute_potential(self.atoms, mesh, params)
        else:
            params = pb_linear.PBParams(dielectric=self.dielectric, ionic_strength=self.ionic_strength)
            self.phi = pb_linear.compute_potential(self.atoms, mesh, params)
        print("done.")

    def do_export(self, arg: str) -> None:
        """export <path>

        Export potential grid to .npy file.
        """

        if self.phi is None:
            print("No potential computed.")
            return
        path = arg.strip()
        if not path:
            print("Usage: export <path>")
            return
        visualize.save_npy(path, self.phi)
        print(f"Saved potential to {path}.")

    def do_visualize(self, arg: str) -> None:
        """visualize slice <axis>=<index>

        Example: visualize slice z=0
        """

        parts = arg.split()
        if len(parts) != 2 or parts[0] != "slice":
            print("Usage: visualize slice <axis>=<index>")
            return
        if self.phi is None:
            print("No potential computed.")
            return
        try:
            axis, idx_str = parts[1].split("=")
            idx = int(idx_str)
        except Exception:
            print("Invalid slice specification; expected like z=0")
            return
        visualize.show_slice(self.phi, visualize.SliceSpec(axis=axis, index=idx), atoms=self.atoms)

    def do_exit(self, arg: str) -> bool:  # noqa: ARG002
        """Exit the REPL."""

        print("Exiting.")
        return True

    def do_quit(self, arg: str) -> bool:  # noqa: ARG002
        """Alias for exit."""

        return self.do_exit(arg)


def main(argv: Optional[list[str]] = None) -> int:
    if argv:
        return run_single_shot(argv)
    repl = ESPRepl()
    repl.cmdloop()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
