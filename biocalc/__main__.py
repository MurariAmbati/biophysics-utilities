"""
CLI entrypoint for biocalc.

Usage:
    bio-calc                        # Start interactive REPL
    bio-calc "R * 300*K"            # Evaluate expression
    bio-calc --list                 # List constants
    bio-calc --convert "1 kcal/mol" "J/mol"
"""

import sys
import argparse
from .repl import start_repl
from .constants import list_constants, get_constant, search_constants
from .units import convert, format_quantity
from .parser import evaluate, energy


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog='bio-calc',
        description='Unit-Aware Biochemical Calculator',
        epilog='Examples:\n'
               '  bio-calc\n'
               '  bio-calc "R * 300*K"\n'
               '  bio-calc --list\n'
               '  bio-calc --convert "1 kcal/mol" "J/mol"',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Positional argument for expression
    parser.add_argument(
        'expression',
        nargs='?',
        help='Expression to evaluate (if omitted, starts REPL)'
    )
    
    # Optional flags
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available constants'
    )
    
    parser.add_argument(
        '--search',
        metavar='QUERY',
        help='Search for constants matching query'
    )
    
    parser.add_argument(
        '--convert',
        nargs=2,
        metavar=('VALUE', 'UNIT'),
        help='Convert value to target unit (e.g., --convert "1 kcal/mol" "J/mol")'
    )
    
    parser.add_argument(
        '--energy',
        metavar='CONSTANT',
        help='Get energy value of constant (e.g., --energy ATP_hydrolysis)'
    )
    
    parser.add_argument(
        '--precision',
        type=int,
        default=6,
        metavar='N',
        help='Decimal precision for output (default: 6)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='biocalc 0.1.0'
    )
    
    args = parser.parse_args()
    
    # Handle --list
    if args.list:
        constants = list_constants()
        print("\nAvailable constants:")
        print("-" * 60)
        for name in constants:
            try:
                value = get_constant(name)
                print(f"  {name:30s} = {format_quantity(value, args.precision)}")
            except:
                pass
        return 0
    
    # Handle --search
    if args.search:
        results = search_constants(args.search)
        if not results:
            print(f"No constants found matching '{args.search}'")
            return 1
        
        print(f"\nConstants matching '{args.search}':")
        print("-" * 60)
        for name, value in results.items():
            print(f"  {name:30s} = {format_quantity(value, args.precision)}")
        return 0
    
    # Handle --convert
    if args.convert:
        try:
            value_expr, target_unit = args.convert
            result = convert(value_expr, target_unit)
            print(format_quantity(result, args.precision))
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    
    # Handle --energy
    if args.energy:
        try:
            result = energy(args.energy)
            print(format_quantity(result, args.precision))
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    
    # Handle expression evaluation
    if args.expression:
        try:
            result = evaluate(args.expression, return_units=True, precision=args.precision)
            
            if hasattr(result, 'units'):
                print(format_quantity(result, args.precision))
            else:
                print(f"{result:.{args.precision}f}")
            
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    
    # No arguments - start REPL
    start_repl(precision=args.precision)
    return 0


if __name__ == '__main__':
    sys.exit(main())
