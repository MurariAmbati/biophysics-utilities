"""Command-line interface for the viscoelastic analyzer."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Sequence

from .models import SimulationConfig
from .plotting import plot_response
from .solver import compute_response


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="viscoelastic-analyzer",
        description="Compute analytical relaxation and creep responses for simple viscoelastic models.",
    )
    parser.add_argument("--model", choices=["maxwell", "kelvin_voigt"], required=True)
    parser.add_argument("--mode", choices=["relaxation", "creep"], required=True)
    parser.add_argument("--E", type=float, required=True, help="Elastic modulus (Pa)")
    parser.add_argument("--eta", type=float, required=True, help="Viscosity (Pa·s)")
    parser.add_argument("--strain0", type=float, help="Constant strain for relaxation experiments")
    parser.add_argument("--stress0", type=float, help="Constant stress for creep experiments")
    parser.add_argument("--t_max", type=float, required=True, help="Simulation horizon (s)")
    parser.add_argument("--dt", type=float, required=True, help="Time resolution (s)")
    parser.add_argument("--plot", action="store_true", help="Display the response curve with matplotlib")
    parser.add_argument("--plot-file", help="Save the response plot to the given file path")
    parser.add_argument("--json-out", help="Write response data as JSON")
    parser.add_argument("--csv-out", help="Write response data as CSV")
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console summary (still writes files/plots)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = SimulationConfig(
        model=args.model,
        mode=args.mode,
        E=args.E,
        eta=args.eta,
        strain0=args.strain0,
        stress0=args.stress0,
        t_max=args.t_max,
        dt=args.dt,
    )

    try:
        result = compute_response(config)
    except ValueError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    if not args.quiet:
        _print_summary(result, config)

    if args.json_out:
        _write_json(args.json_out, result)
    if args.csv_out:
        _write_csv(args.csv_out, result)

    if args.plot or args.plot_file:
        plot_response(result, show=args.plot, save_path=args.plot_file)

    return 0


def _print_summary(result, config: SimulationConfig) -> None:
    print(f"Model: {config.model} ({config.mode})")
    print(f"τ = {result.tau:.6g} s")
    print(
        "Time grid: {n} points between {start:.3g}s and {stop:.3g}s (dt={dt:.3g}s)".format(
            n=result.time.size,
            start=float(result.time[0]),
            stop=float(result.time[-1]),
            dt=config.dt,
        )
    )
    print(
        f"{result.quantity.title()} range: {result.response[0]:.6g} -> {result.response[-1]:.6g}"
    )


def _write_json(path_str: str, result) -> None:
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "time": result.time.tolist(),
        "response": result.response.tolist(),
        "quantity": result.quantity,
        "tau": float(result.tau),
        "label": result.label,
    }
    path.write_text(json.dumps(payload, indent=2))


def _write_csv(path_str: str, result) -> None:
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(["t", result.quantity])
        for t_val, resp in zip(result.time, result.response):
            writer.writerow([t_val, resp])


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
