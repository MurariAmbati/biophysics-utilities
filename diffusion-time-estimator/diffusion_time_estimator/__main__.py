"""
Command-line interface for the diffusion time estimator.
"""
import argparse
import sys
from .core import (
    diffusion_coefficient,
    diffusion_time,
    format_time,
    format_coefficient
)
from .constants import WATER_VISCOSITY, ROOM_TEMPERATURE


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Estimate diffusion timescales for molecules in various media.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --radius 1e-9 --viscosity 1e-3 --distance 1e-6
  %(prog)s --radius 5e-9 --temperature 310 --plot
  %(prog)s --radius 1e-9 --dims 2 --distance 1e-5
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--radius', '-r',
        type=float,
        required=True,
        help='Molecule hydrodynamic radius (m), e.g., 1e-9 for 1 nm'
    )
    
    # Optional arguments
    parser.add_argument(
        '--viscosity', '-v',
        type=float,
        default=WATER_VISCOSITY,
        help=f'Medium viscosity (Pa·s), default: {WATER_VISCOSITY} (water at ~20°C)'
    )
    
    parser.add_argument(
        '--temperature', '-T',
        type=float,
        default=ROOM_TEMPERATURE,
        help=f'Temperature (K), default: {ROOM_TEMPERATURE}'
    )
    
    parser.add_argument(
        '--distance', '-L',
        type=float,
        default=1e-6,
        help='Diffusion distance (m), default: 1e-6 (1 μm)'
    )
    
    parser.add_argument(
        '--dims', '-n',
        type=int,
        choices=[1, 2, 3],
        default=3,
        help='Spatial dimensions (1, 2, or 3), default: 3'
    )
    
    parser.add_argument(
        '--plot', '-p',
        action='store_true',
        help='Plot MSD vs. time (requires matplotlib)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output with all parameters'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    try:
        # Calculate diffusion coefficient
        D = diffusion_coefficient(args.radius, args.viscosity, args.temperature)
        
        # Calculate characteristic diffusion time
        t_diff = diffusion_time(args.distance, D, args.dims)
        
        # Display results
        if args.verbose:
            print("=" * 60)
            print("DIFFUSION TIME ESTIMATOR")
            print("=" * 60)
            print("\nInput Parameters:")
            print(f"  Molecule radius:       {args.radius:.3e} m")
            print(f"  Medium viscosity:      {args.viscosity:.3e} Pa·s")
            print(f"  Temperature:           {args.temperature:.1f} K")
            print(f"  Diffusion distance:    {args.distance:.3e} m")
            print(f"  Spatial dimensions:    {args.dims}D")
            print("\nResults:")
            print(f"  Diffusion coefficient: {format_coefficient(D)}")
            print(f"  Diffusion time:        {format_time(t_diff)}")
            print("=" * 60)
        else:
            print(f"Estimated diffusion coefficient: {format_coefficient(D)}")
            print(f"Characteristic diffusion time: {format_time(t_diff)}")
        
        # Optional plotting
        if args.plot:
            try:
                from .plot import plot_msd
                plot_msd(D, dims=args.dims)
            except ImportError:
                print("\nWarning: matplotlib not available. Install it to enable plotting:", 
                      file=sys.stderr)
                print("  pip install matplotlib", file=sys.stderr)
                sys.exit(1)
        
        return 0
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
