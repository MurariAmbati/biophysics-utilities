#!/usr/bin/env python3
"""
Command-line interface for the Protein Hydration Shell Estimator.

Provides an interactive REPL for computing hydration shell properties.
"""

import sys
from typing import Optional
from .model import HydrationShellEstimator
from .constants import (
    DEFAULT_SHELL_THICKNESS,
    DEFAULT_HYDROPHILICITY_INDEX,
)
from .utils import (
    validate_all_inputs,
    nm2_to_m2,
    format_scientific,
)


class HydrationREPL:
    """Interactive REPL for hydration shell estimation."""
    
    def __init__(self):
        self.surface_area: Optional[float] = None
        self.hydrophilicity: Optional[float] = None
        self.thickness: Optional[float] = None
        self.estimator: Optional[HydrationShellEstimator] = None
    
    def print_banner(self):
        """Print welcome banner."""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║   Protein Hydration Shell Estimator                      ║
║   Theoretical estimation of water molecules in            ║
║   protein hydration shells                                ║
╚═══════════════════════════════════════════════════════════╝

Commands:
  surface_area = <value>      Set surface area (m²)
  hydrophilicity = <value>    Set hydrophilicity index (0-1)
  thickness = <value>         Set shell thickness (Å)
  compute()                   Calculate hydration shell properties
  reset()                     Clear all parameters
  help()                      Show this help message
  exit()                      Exit the program

Tips:
  - Surface area in m² (e.g., 1.5e-17 for typical protein)
  - Or use nm² with conversion: surface_area = nm2(150)
  - Hydrophilicity: 0 = hydrophobic, 1 = hydrophilic
  - Default thickness: 3.0 Å

Example session:
  >>> surface_area = 1.5e-17
  >>> hydrophilicity = 0.65
  >>> thickness = 3.0
  >>> compute()
"""
        print(banner)
    
    def nm2(self, area_nm2: float) -> float:
        """Convert nm² to m² for convenience."""
        return nm2_to_m2(area_nm2)
    
    def parse_command(self, line: str) -> bool:
        """
        Parse and execute a command.
        
        Returns
        -------
        bool
            True to continue REPL, False to exit
        """
        line = line.strip()
        
        if not line or line.startswith('#'):
            return True
        
        # Exit commands
        if line.lower() in ['exit()', 'quit()', 'exit', 'quit', 'q']:
            print("Goodbye!")
            return False
        
        # Help command
        if line.lower() in ['help()', 'help', '?']:
            self.print_banner()
            return True
        
        # Reset command
        if line.lower() in ['reset()', 'reset']:
            self.surface_area = None
            self.hydrophilicity = None
            self.thickness = None
            self.estimator = None
            print("Parameters reset.")
            return True
        
        # Compute command
        if line.lower() in ['compute()', 'compute', 'calc()', 'calc']:
            self.compute()
            return True
        
        # Parameter assignment
        if '=' in line:
            self.parse_assignment(line)
            return True
        
        # Try to evaluate as Python expression
        try:
            result = eval(line, {"nm2": self.nm2}, {})
            print(f"  → {result}")
        except Exception as e:
            print(f"Error: {e}")
            print("Type 'help()' for usage information.")
        
        return True
    
    def parse_assignment(self, line: str):
        """Parse variable assignment."""
        try:
            var_name, value_expr = line.split('=', 1)
            var_name = var_name.strip().lower()
            
            # Evaluate the value expression
            value = eval(value_expr.strip(), {"nm2": self.nm2}, {})
            
            if var_name in ['surface_area', 'area', 'a']:
                self.surface_area = float(value)
                print(f"Surface area set to {format_scientific(self.surface_area)} m²")
            
            elif var_name in ['hydrophilicity', 'hydro', 'h']:
                self.hydrophilicity = float(value)
                print(f"Hydrophilicity index set to {self.hydrophilicity:.2f}")
            
            elif var_name in ['thickness', 'thick', 't']:
                self.thickness = float(value)
                print(f"Shell thickness set to {self.thickness:.1f} Å")
            
            else:
                print(f"Unknown parameter: {var_name}")
                print("Valid parameters: surface_area, hydrophilicity, thickness")
        
        except Exception as e:
            print(f"Error parsing assignment: {e}")
    
    def compute(self):
        """Compute and display hydration shell properties."""
        # Use defaults if not set
        surface_area = self.surface_area
        hydrophilicity = self.hydrophilicity if self.hydrophilicity is not None else DEFAULT_HYDROPHILICITY_INDEX
        thickness = self.thickness if self.thickness is not None else DEFAULT_SHELL_THICKNESS
        
        if surface_area is None:
            print("Error: surface_area not set. Please set it first.")
            print("Example: surface_area = 1.5e-17")
            return
        
        # Validate inputs
        is_valid, error_msg = validate_all_inputs(surface_area, hydrophilicity, thickness)
        if not is_valid:
            print(f"Validation error: {error_msg}")
            return
        
        # Create estimator and compute
        self.estimator = HydrationShellEstimator(
            surface_area=surface_area,
            hydrophilicity_index=hydrophilicity,
            shell_thickness=thickness,
        )
        
        results = self.estimator.compute()
        
        # Display results
        print("\n" + "="*60)
        print(f"V_shell  = {format_scientific(results['V_shell'])} m³")
        print(f"ρ_shell  = {format_scientific(results['rho_shell'])} molecules/m³")
        print(f"N_H2O    = {format_scientific(results['N_H2O'])}")
        print(f"\n≈ {results['N_H2O']:.0f} water molecules in hydration shell")
        print("="*60 + "\n")
    
    def run(self):
        """Run the interactive REPL."""
        self.print_banner()
        
        while True:
            try:
                line = input(">>> ")
                if not self.parse_command(line):
                    break
            except EOFError:
                print("\nGoodbye!")
                break
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'exit()' to quit.")
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")


def main():
    """Main entry point for CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Protein Hydration Shell Estimator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hydration-estimator
    Start interactive REPL
  
  hydration-estimator --surface-area 1.5e-17 --hydrophilicity 0.65
    Compute with specified parameters
"""
    )
    
    parser.add_argument(
        '-a', '--surface-area',
        type=float,
        help='Surface area in m² (e.g., 1.5e-17)'
    )
    
    parser.add_argument(
        '-i', '--hydrophilicity',
        type=float,
        default=DEFAULT_HYDROPHILICITY_INDEX,
        help=f'Hydrophilicity index 0-1 (default: {DEFAULT_HYDROPHILICITY_INDEX})'
    )
    
    parser.add_argument(
        '-t', '--thickness',
        type=float,
        default=DEFAULT_SHELL_THICKNESS,
        help=f'Shell thickness in Å (default: {DEFAULT_SHELL_THICKNESS})'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Force interactive mode even with parameters'
    )
    
    args = parser.parse_args()
    
    # If surface area provided and not interactive, compute directly
    if args.surface_area is not None and not args.interactive:
        is_valid, error_msg = validate_all_inputs(
            args.surface_area,
            args.hydrophilicity,
            args.thickness
        )
        
        if not is_valid:
            print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)
        
        estimator = HydrationShellEstimator(
            surface_area=args.surface_area,
            hydrophilicity_index=args.hydrophilicity,
            shell_thickness=args.thickness,
        )
        
        print(estimator.get_summary())
    else:
        # Start interactive REPL
        repl = HydrationREPL()
        
        # Pre-populate if arguments provided
        if args.surface_area is not None:
            repl.surface_area = args.surface_area
        if args.hydrophilicity != DEFAULT_HYDROPHILICITY_INDEX:
            repl.hydrophilicity = args.hydrophilicity
        if args.thickness != DEFAULT_SHELL_THICKNESS:
            repl.thickness = args.thickness
        
        repl.run()


if __name__ == '__main__':
    main()
