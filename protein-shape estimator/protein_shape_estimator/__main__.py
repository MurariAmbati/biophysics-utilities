"""
Command-line interface for protein shape estimation.
"""

import argparse
import sys
from .core import hydrodynamic_radius, net_charge, diffusion_coefficient
from .constants import DEFAULT_TEMP, DEFAULT_VISCOSITY, DEFAULT_POS_FRAC, DEFAULT_NEG_FRAC


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Estimate basic physical properties of a protein from sequence length.",
        prog="protein-shape"
    )
    
    parser.add_argument(
        "--length",
        type=int,
        required=True,
        help="Sequence length (number of residues)"
    )
    
    parser.add_argument(
        "--temp",
        type=float,
        default=DEFAULT_TEMP,
        help=f"Temperature in Kelvin (default: {DEFAULT_TEMP})"
    )
    
    parser.add_argument(
        "--viscosity",
        type=float,
        default=DEFAULT_VISCOSITY,
        help=f"Solvent viscosity in Pa·s (default: {DEFAULT_VISCOSITY})"
    )
    
    parser.add_argument(
        "--pos-frac",
        type=float,
        default=DEFAULT_POS_FRAC,
        help=f"Fraction of basic residues (default: {DEFAULT_POS_FRAC})"
    )
    
    parser.add_argument(
        "--neg-frac",
        type=float,
        default=DEFAULT_NEG_FRAC,
        help=f"Fraction of acidic residues (default: {DEFAULT_NEG_FRAC})"
    )
    
    args = parser.parse_args()
    
    # Validate input
    if args.length <= 0:
        print("Error: Sequence length must be positive.", file=sys.stderr)
        sys.exit(1)
    
    if args.temp <= 0:
        print("Error: Temperature must be positive.", file=sys.stderr)
        sys.exit(1)
    
    if args.viscosity <= 0:
        print("Error: Viscosity must be positive.", file=sys.stderr)
        sys.exit(1)
    
    # Calculate properties
    R_h = hydrodynamic_radius(args.length)
    R_h_nm = R_h * 1e9  # Convert to nm for display
    
    Z = net_charge(args.length, args.pos_frac, args.neg_frac)
    
    D = diffusion_coefficient(R_h, args.temp, args.viscosity)
    
    # Output results
    print(f"Hydrodynamic radius: {R_h_nm:.2f} nm")
    print(f"Net charge (approx.): {Z:+.1f} e")
    print(f"Diffusion coefficient: {D:.1e} m²/s")


if __name__ == "__main__":
    main()
