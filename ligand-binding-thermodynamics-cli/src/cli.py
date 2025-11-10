#!/usr/bin/env python3
"""
Interactive command-line interface for ligand binding thermodynamics calculations.

Usage:
    $ python -m src.cli
    or
    $ bind-thermo (if installed via setup.py)
"""

import sys
from typing import Dict, Optional

from .core import (
    calculate_ka,
    calculate_kd,
    calculate_delta_g,
    calculate_entropy,
    compute_all,
)
from .parser import (
    parse_assignment,
    parse_command,
    validate_state_for_computation,
    normalize_variable_name,
    format_scientific,
    ValidationError,
)
from .constants import GAS_CONSTANT_R


class BindingThermoREPL:
    """Interactive REPL for binding thermodynamics calculations."""
    
    def __init__(self):
        self.state: Dict[str, float] = {}
        self.last_results: Optional[dict] = None
        self.running = True
    
    def print_banner(self):
        """Print welcome banner."""
        print("=" * 60)
        print("  Ligand Binding Thermodynamics CLI")
        print("  Version 1.0.0")
        print("=" * 60)
        print("\nCommands:")
        print("  T = <value>         Set temperature (K)")
        print("  P = <value>         Set protein concentration (M)")
        print("  L = <value>         Set ligand concentration (M)")
        print("  PL = <value>        Set complex concentration (M)")
        print("  ΔH = <value>        Set enthalpy (kJ/mol)")
        print("  compute()           Calculate Ka, Kd, ΔG")
        print("  compute_entropy()   Calculate ΔS (requires ΔH)")
        print("  show()              Show current state")
        print("  clear()             Clear all variables")
        print("  help()              Show this help")
        print("  quit()              Exit")
        print("\nExample:")
        print("  >>> T = 298")
        print("  >>> P = 1e-6")
        print("  >>> L = 1e-6")
        print("  >>> PL = 5e-7")
        print("  >>> compute()")
        print()
    
    def handle_assignment(self, line: str) -> bool:
        """
        Handle variable assignment.
        
        Returns:
            True if assignment was successful
        """
        try:
            result = parse_assignment(line)
            if result is None:
                return False
            
            var_name, value = result
            var_name = normalize_variable_name(var_name)
            
            self.state[var_name] = value
            print(f"{var_name} = {format_scientific(value)}")
            return True
            
        except ValidationError as e:
            print(f"Error: {e}")
            return False
    
    def handle_command(self, line: str) -> bool:
        """
        Handle command execution.
        
        Returns:
            True if command was recognized
        """
        command, args = parse_command(line)
        
        if not command:
            return False
        
        command_lower = command.lower()
        
        if command_lower == 'quit' or command_lower == 'exit':
            self.running = False
            print("Goodbye!")
            return True
        
        elif command_lower == 'help':
            self.print_banner()
            return True
        
        elif command_lower == 'show':
            self.show_state()
            return True
        
        elif command_lower == 'clear':
            self.state.clear()
            self.last_results = None
            print("All variables cleared.")
            return True
        
        elif command_lower == 'compute':
            self.compute()
            return True
        
        elif command_lower == 'compute_entropy':
            self.compute_entropy()
            return True
        
        else:
            print(f"Unknown command: {command}")
            print("Type 'help()' for available commands.")
            return True
    
    def show_state(self):
        """Display current variable state."""
        if not self.state:
            print("No variables defined.")
            return
        
        print("\nCurrent state:")
        print("-" * 40)
        for var_name in sorted(self.state.keys()):
            value = self.state[var_name]
            print(f"  {var_name:4s} = {format_scientific(value, 3)}")
        print("-" * 40)
    
    def compute(self):
        """Perform main computation: Ka, Kd, ΔG."""
        try:
            # Validate required parameters
            temp, p_conc, l_conc, pl_conc = validate_state_for_computation(self.state)
            
            # Get optional ΔH
            delta_h = self.state.get('ΔH')
            
            # Compute all parameters
            results = compute_all(p_conc, l_conc, pl_conc, temp, delta_h)
            self.last_results = results
            
            # Display results
            print("\n" + "=" * 50)
            print("  RESULTS")
            print("=" * 50)
            
            # Show the equations used
            print("\nEquations:")
            print(f"  Ka = [PL] / ([P][L])")
            print(f"     = {format_scientific(pl_conc, 2)} / ({format_scientific(p_conc, 2)} × {format_scientific(l_conc, 2)})")
            
            ka = results['Ka']
            print(f"\n  Ka = {format_scientific(ka, 2)} M^-1")
            
            kd = results['Kd']
            print(f"\n  Kd = 1 / Ka")
            print(f"     = {format_scientific(kd, 2)} M")
            
            # ΔG calculation
            print(f"\n  ΔG = -RT ln(Ka)")
            print(f"     = -({GAS_CONSTANT_R:.6f} J/(mol·K)) × {temp} K × ln({format_scientific(ka, 2)})")
            
            delta_g = results['ΔG']
            print(f"     = {delta_g:.2f} kJ/mol")
            
            # If ΔH provided, show ΔS
            if delta_h is not None:
                delta_s = results['ΔS']
                print(f"\n  ΔS = (ΔH - ΔG) / T")
                print(f"     = ({delta_h} - {delta_g:.2f}) / {temp}")
                print(f"     = {delta_s:.1f} J/(mol·K)")
            
            print("=" * 50)
            
        except ValidationError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Calculation error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    
    def compute_entropy(self):
        """Compute entropy from ΔG and ΔH."""
        try:
            # Check if we have results from previous computation
            if self.last_results is None or 'ΔG' not in self.last_results:
                print("Error: Run compute() first to calculate ΔG")
                return
            
            # Check if ΔH is defined
            if 'ΔH' not in self.state:
                print("Error: ΔH (enthalpy) must be defined")
                print("Example: ΔH = -50")
                return
            
            delta_h = self.state['ΔH']
            delta_g = self.last_results['ΔG']
            temp = self.state['T']
            
            # Calculate entropy
            delta_s = calculate_entropy(delta_g, delta_h, temp)
            
            # Display result
            print("\n" + "=" * 50)
            print("  ENTROPY CALCULATION")
            print("=" * 50)
            print(f"\n  ΔG = ΔH - TΔS")
            print(f"  ΔS = (ΔH - ΔG) / T")
            print(f"\n  Given:")
            print(f"    ΔH = {delta_h} kJ/mol")
            print(f"    ΔG = {delta_g:.2f} kJ/mol")
            print(f"    T  = {temp} K")
            print(f"\n  ΔS = {delta_s:.1f} J/(mol·K)")
            print("=" * 50)
            
            # Store in state
            self.state['ΔS'] = delta_s
            
        except ValidationError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Calculation error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    
    def run(self):
        """Main REPL loop."""
        self.print_banner()
        
        while self.running:
            try:
                line = input(">>> ").strip()
                
                if not line:
                    continue
                
                # Try to handle as assignment
                if self.handle_assignment(line):
                    continue
                
                # Try to handle as command
                if self.handle_command(line):
                    continue
                
                # Unknown input
                print("Invalid input. Type 'help()' for available commands.")
                
            except EOFError:
                print("\nGoodbye!")
                break
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'quit()' to exit.")
                continue
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Entry point for CLI."""
    repl = BindingThermoREPL()
    repl.run()


if __name__ == "__main__":
    main()
