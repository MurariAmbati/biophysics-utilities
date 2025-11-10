"""
Command-line interface for Force Field Evaluator.
"""

import argparse
import sys
from typing import List

from .constants import (
    DEFAULT_LJ,
    DEFAULT_MORSE,
    DEFAULT_COULOMB,
    DEFAULT_RANGE,
)
from .evaluator import ForceFieldEvaluator, create_distance_range


def parse_potential_list(potential_str: str) -> List[str]:
    """
    Parse comma-separated potential names.
    
    Parameters
    ----------
    potential_str : str
        Comma-separated potential names or 'all'
    
    Returns
    -------
    list of str
        List of potential names
    """
    if potential_str.lower() == 'all':
        return ['LJ', 'Morse', 'Coulomb']
    
    potentials = [p.strip() for p in potential_str.split(',')]
    
    # Normalize names
    normalized = []
    for p in potentials:
        if p.upper() == 'LJ' or p.lower() == 'lennard-jones':
            normalized.append('LJ')
        elif p.lower() == 'morse':
            normalized.append('Morse')
        elif p.lower() == 'coulomb':
            normalized.append('Coulomb')
        else:
            raise ValueError(f"Unknown potential: {p}")
    
    return normalized


def create_parser() -> argparse.ArgumentParser:
    """
    Create the argument parser for the CLI.
    
    Returns
    -------
    argparse.ArgumentParser
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        prog='forcefield-eval',
        description='Evaluate and compare classical potential energy functions for diatomic systems.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate Lennard-Jones potential
  forcefield-eval --potential LJ
  
  # Compare LJ and Morse potentials
  forcefield-eval --potential LJ,Morse --rmin 0.2 --rmax 0.8
  
  # Evaluate all potentials with custom parameters
  forcefield-eval --potential all --epsilon 0.3 --sigma 0.35
  
  # Generate plot
  forcefield-eval --potential LJ,Morse --output plot
  
  # Find equilibrium only
  forcefield-eval --potential Morse --find-min
        """
    )
    
    # Potential selection
    parser.add_argument(
        '--potential',
        type=str,
        default='all',
        help='Which potential(s) to evaluate: LJ, Morse, Coulomb, or all (comma-separated)'
    )
    
    # Distance range
    parser.add_argument(
        '--rmin',
        type=float,
        default=DEFAULT_RANGE['rmin'],
        help=f"Minimum distance [nm] (default: {DEFAULT_RANGE['rmin']})"
    )
    parser.add_argument(
        '--rmax',
        type=float,
        default=DEFAULT_RANGE['rmax'],
        help=f"Maximum distance [nm] (default: {DEFAULT_RANGE['rmax']})"
    )
    parser.add_argument(
        '--npoints',
        type=int,
        default=DEFAULT_RANGE['npoints'],
        help=f"Number of distance points (default: {DEFAULT_RANGE['npoints']})"
    )
    
    # Lennard-Jones parameters
    lj_group = parser.add_argument_group('Lennard-Jones parameters')
    lj_group.add_argument(
        '--epsilon',
        type=float,
        default=DEFAULT_LJ['epsilon'],
        help=f"LJ well depth [eV] (default: {DEFAULT_LJ['epsilon']})"
    )
    lj_group.add_argument(
        '--sigma',
        type=float,
        default=DEFAULT_LJ['sigma'],
        help=f"LJ zero-crossing distance [nm] (default: {DEFAULT_LJ['sigma']})"
    )
    
    # Morse parameters
    morse_group = parser.add_argument_group('Morse parameters')
    morse_group.add_argument(
        '--De',
        type=float,
        default=DEFAULT_MORSE['De'],
        help=f"Morse well depth [eV] (default: {DEFAULT_MORSE['De']})"
    )
    morse_group.add_argument(
        '--a',
        type=float,
        default=DEFAULT_MORSE['a'],
        help=f"Morse width parameter [1/nm] (default: {DEFAULT_MORSE['a']})"
    )
    morse_group.add_argument(
        '--re',
        type=float,
        default=DEFAULT_MORSE['re'],
        help=f"Morse equilibrium distance [nm] (default: {DEFAULT_MORSE['re']})"
    )
    
    # Coulomb parameters
    coulomb_group = parser.add_argument_group('Coulomb parameters')
    coulomb_group.add_argument(
        '--q1',
        type=float,
        default=DEFAULT_COULOMB['q1'],
        help=f"Charge of particle 1 [C] (default: {DEFAULT_COULOMB['q1']})"
    )
    coulomb_group.add_argument(
        '--q2',
        type=float,
        default=DEFAULT_COULOMB['q2'],
        help=f"Charge of particle 2 [C] (default: {DEFAULT_COULOMB['q2']})"
    )
    
    # Output options
    parser.add_argument(
        '--output',
        type=str,
        choices=['text', 'plot', 'data'],
        default='text',
        help='Output mode: text (summary), plot (matplotlib), or data (full arrays)'
    )
    parser.add_argument(
        '--find-min',
        action='store_true',
        help='Only find and report equilibrium distance and minimum energy'
    )
    parser.add_argument(
        '--force-curves',
        action='store_true',
        help='Include force curves in plot output'
    )
    parser.add_argument(
        '--save',
        type=str,
        default=None,
        help='Save plot to file (e.g., output.png)'
    )
    
    return parser


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Parse potential list
        potentials = parse_potential_list(args.potential)
        
        # Create distance range
        r_range = create_distance_range(args.rmin, args.rmax, args.npoints)
        
        # Prepare parameters
        params_dict = {
            'LJ': {'epsilon': args.epsilon, 'sigma': args.sigma},
            'Morse': {'De': args.De, 'a': args.a, 're': args.re},
            'Coulomb': {'q1': args.q1, 'q2': args.q2},
        }
        
        # Create evaluator
        evaluator = ForceFieldEvaluator()
        
        # Evaluate potentials
        if args.find_min:
            # Only find equilibrium
            print("\nEquilibrium Analysis:")
            print("=" * 50)
            for pot in potentials:
                result = evaluator.evaluate_potential(pot, params_dict[pot], r_range)
                print(f"\nPotential: {pot}")
                print(f"  r_eq = {result['r_eq']:.6f} nm")
                print(f"  U_min = {result['U_min']:.6f} eV")
        
        elif args.output == 'text':
            # Text summary
            print("\nForce Field Evaluation Results")
            print("=" * 50)
            for pot in potentials:
                result = evaluator.evaluate_potential(pot, params_dict[pot], r_range)
                print(f"\n{evaluator.get_summary(pot)}")
        
        elif args.output == 'data':
            # Full data output
            print("\nDistance [nm], Energy [eV], Force [eV/nm]")
            print("=" * 50)
            for pot in potentials:
                result = evaluator.evaluate_potential(pot, params_dict[pot], r_range)
                print(f"\n# Potential: {pot}")
                for i in range(len(result['r'])):
                    print(f"{result['r'][i]:.6f}, {result['U'][i]:.6f}, {result['F'][i]:.6f}")
        
        elif args.output == 'plot':
            # Import plotter here to avoid dependency if not needed
            try:
                from .plotter import plot_potentials, plot_forces
            except ImportError:
                print("Error: matplotlib is required for plotting. Install with: pip install matplotlib")
                sys.exit(1)
            
            # Evaluate all potentials
            results = []
            for pot in potentials:
                result = evaluator.evaluate_potential(pot, params_dict[pot], r_range)
                results.append(result)
            
            # Create plots
            if args.force_curves:
                plot_potentials(results, save_path=args.save, show_forces=True)
            else:
                plot_potentials(results, save_path=args.save, show_forces=False)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
