"""Command-line interface for Lennard-Jones playground."""

import argparse
import sys
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional

from .model import (
    lj_potential, 
    lj_force, 
    lj_equilibrium, 
    generate_lj_curve,
    morse_potential,
    reduced_lj_potential
)
from .utils import format_energy, format_distance, save_potential_table


class LJPlayground:
    """Interactive REPL for exploring Lennard-Jones potentials."""
    
    def __init__(self):
        self.epsilon = 1.0  # kJ/mol
        self.sigma = 3.5    # Angstrom
        self.r_min = None   # Will default to 0.5*sigma
        self.r_max = None   # Will default to 3.0*sigma
        self.show_force = False
        self.show_morse = False
        self.show_reduced = False
        
    def set_epsilon(self, value: float):
        """Set epsilon parameter."""
        if value <= 0:
            print("Error: epsilon must be positive")
            return
        self.epsilon = value
        print(f"ε = {value} kJ/mol")
        
    def set_sigma(self, value: float):
        """Set sigma parameter."""
        if value <= 0:
            print("Error: sigma must be positive")
            return
        self.sigma = value
        print(f"σ = {value} Å")
        
    def set_range(self, r_min: Optional[float] = None, r_max: Optional[float] = None):
        """Set plotting range."""
        if r_min is not None:
            if r_min <= 0:
                print("Error: r_min must be positive")
                return
            self.r_min = r_min
        if r_max is not None:
            if r_max <= 0 or (r_min is not None and r_max <= r_min):
                print("Error: r_max must be positive and greater than r_min")
                return
            self.r_max = r_max
        
        r_min_str = f"{self.r_min:.2f}" if self.r_min else f"0.5σ"
        r_max_str = f"{self.r_max:.2f}" if self.r_max else f"3.0σ"
        print(f"Range: [{r_min_str}, {r_max_str}] Å")
        
    def toggle_force(self):
        """Toggle force curve display."""
        self.show_force = not self.show_force
        print(f"Force curve: {'ON' if self.show_force else 'OFF'}")
        
    def toggle_morse(self):
        """Toggle Morse potential comparison."""
        self.show_morse = not self.show_morse
        print(f"Morse potential: {'ON' if self.show_morse else 'OFF'}")
        
    def toggle_reduced(self):
        """Toggle reduced LJ potential."""
        self.show_reduced = not self.show_reduced
        print(f"Reduced LJ: {'ON' if self.show_reduced else 'OFF'}")
        
    def info(self):
        """Display current parameters and equilibrium info."""
        print("\n" + "="*50)
        print("Current Parameters:")
        print(f"  ε (epsilon) = {self.epsilon} kJ/mol")
        print(f"  σ (sigma)   = {self.sigma} Å")
        
        r_min_str = f"{self.r_min} Å" if self.r_min else f"{0.5*self.sigma:.2f} Å (0.5σ)"
        r_max_str = f"{self.r_max} Å" if self.r_max else f"{3.0*self.sigma:.2f} Å (3.0σ)"
        print(f"  Range       = [{r_min_str}, {r_max_str}]")
        
        print("\nEquilibrium Properties:")
        r_eq, V_eq = lj_equilibrium(self.epsilon, self.sigma)
        print(f"  r_min = {format_distance(r_eq)}")
        print(f"  V_min = {format_energy(V_eq)}")
        
        print("\nDisplay Options:")
        print(f"  Force curve:      {'ON' if self.show_force else 'OFF'}")
        print(f"  Morse potential:  {'ON' if self.show_morse else 'OFF'}")
        print(f"  Reduced LJ:       {'ON' if self.show_reduced else 'OFF'}")
        print("="*50 + "\n")
        
    def plot(self, save_file: Optional[str] = None):
        """Generate and display the LJ potential plot."""
        # Generate curve
        r, V = generate_lj_curve(
            self.epsilon, 
            self.sigma, 
            self.r_min, 
            self.r_max
        )
        
        # Create figure
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        # Plot potential
        ax1.plot(r, V, 'b-', linewidth=2, label='LJ Potential')
        ax1.axhline(y=0, color='k', linestyle='--', linewidth=0.8, alpha=0.5)
        ax1.set_xlabel('Distance r (Å)', fontsize=12)
        ax1.set_ylabel('Potential V(r) (kJ/mol)', fontsize=12, color='b')
        ax1.tick_params(axis='y', labelcolor='b')
        ax1.grid(True, alpha=0.3)
        
        # Mark equilibrium
        r_eq, V_eq = lj_equilibrium(self.epsilon, self.sigma)
        ax1.plot(r_eq, V_eq, 'ro', markersize=8, label=f'Min: ({r_eq:.2f} Å, {V_eq:.2f} kJ/mol)')
        
        # Add Morse potential if requested
        if self.show_morse:
            # Match Morse parameters to LJ
            D_e = self.epsilon
            r_e = r_eq
            a = np.sqrt(36 * self.epsilon / (self.sigma ** 2)) / 2  # Approximate matching
            V_morse = morse_potential(r, D_e, a, r_e)
            ax1.plot(r, V_morse, 'g--', linewidth=2, label='Morse Potential', alpha=0.7)
        
        # Plot force on secondary axis if requested
        if self.show_force:
            ax2 = ax1.twinx()
            F = lj_force(r, self.epsilon, self.sigma)
            ax2.plot(r, F, 'r-', linewidth=1.5, alpha=0.7, label='LJ Force')
            ax2.axhline(y=0, color='r', linestyle=':', linewidth=0.8, alpha=0.3)
            ax2.set_ylabel('Force F(r) (kJ/mol/Å)', fontsize=12, color='r')
            ax2.tick_params(axis='y', labelcolor='r')
            
            # Combine legends
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        else:
            ax1.legend(loc='upper right')
        
        plt.title(f'Lennard-Jones Potential (ε={self.epsilon} kJ/mol, σ={self.sigma} Å)', 
                  fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_file:
            plt.savefig(save_file, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_file}")
        else:
            plt.show()
            
        # Print equilibrium info
        print(f"\nMin at r = {format_distance(r_eq)}, V = {format_energy(V_eq)}")
        
    def export(self, filename: str = "lj_potential.csv"):
        """Export potential data to CSV."""
        r, V = generate_lj_curve(self.epsilon, self.sigma, self.r_min, self.r_max)
        
        if self.show_force:
            F = lj_force(r, self.epsilon, self.sigma)
            save_potential_table(r, V, filename, include_force=True, F=F)
        else:
            save_potential_table(r, V, filename, include_force=False)
    
    def help(self):
        """Display help message."""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║         Lennard-Jones Playground - Command Reference          ║
╚══════════════════════════════════════════════════════════════╝

PARAMETERS:
  epsilon = <value>     Set ε (well depth) in kJ/mol
  sigma = <value>       Set σ (collision diameter) in Å
  range <min> <max>     Set plotting range in Å

ACTIONS:
  plot()                Generate and display LJ potential plot
  plot('filename.png')  Save plot to file
  info()                Show current parameters and equilibrium
  export()              Export data to CSV (default: lj_potential.csv)
  export('file.csv')    Export data to specified file

TOGGLES:
  force                 Toggle force curve display
  morse                 Toggle Morse potential comparison
  reduced               Toggle reduced LJ potential

OTHER:
  help                  Show this help message
  quit / exit           Exit the program

EXAMPLES:
  >>> epsilon = 0.8
  >>> sigma = 3.2
  >>> plot()
  >>> force
  >>> plot()
  >>> export('my_data.csv')

"""
        print(help_text)


def repl():
    """Run the interactive REPL."""
    playground = LJPlayground()
    
    print("\n" + "="*60)
    print("  Lennard-Jones Potential Playground")
    print("  Type 'help' for commands, 'quit' to exit")
    print("="*60 + "\n")
    
    playground.info()
    
    while True:
        try:
            user_input = input(">>> ").strip()
            
            if not user_input:
                continue
                
            # Handle exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
                
            # Handle help
            if user_input.lower() == 'help':
                playground.help()
                continue
                
            # Handle info
            if user_input.lower() == 'info':
                playground.info()
                continue
                
            # Handle toggles
            if user_input.lower() == 'force':
                playground.toggle_force()
                continue
            if user_input.lower() == 'morse':
                playground.toggle_morse()
                continue
            if user_input.lower() == 'reduced':
                playground.toggle_reduced()
                continue
                
            # Handle parameter assignments
            if '=' in user_input:
                parts = user_input.split('=')
                if len(parts) == 2:
                    var = parts[0].strip().lower()
                    try:
                        value = float(parts[1].strip())
                        if var == 'epsilon':
                            playground.set_epsilon(value)
                        elif var == 'sigma':
                            playground.set_sigma(value)
                        else:
                            print(f"Unknown parameter: {var}")
                    except ValueError:
                        print("Error: Invalid number")
                continue
                
            # Handle range command
            if user_input.lower().startswith('range'):
                parts = user_input.split()[1:]
                if len(parts) == 2:
                    try:
                        r_min = float(parts[0])
                        r_max = float(parts[1])
                        playground.set_range(r_min, r_max)
                    except ValueError:
                        print("Error: Invalid range values")
                else:
                    print("Usage: range <min> <max>")
                continue
                
            # Handle plot command
            if user_input.lower().startswith('plot'):
                if 'plot()' in user_input:
                    playground.plot()
                elif "plot('" in user_input or 'plot("' in user_input:
                    # Extract filename
                    start = user_input.find("'") if "'" in user_input else user_input.find('"')
                    end = user_input.rfind("'") if "'" in user_input else user_input.rfind('"')
                    if start != -1 and end != -1 and start < end:
                        filename = user_input[start+1:end]
                        playground.plot(save_file=filename)
                    else:
                        playground.plot()
                else:
                    playground.plot()
                continue
                
            # Handle export command
            if user_input.lower().startswith('export'):
                if 'export()' in user_input:
                    playground.export()
                elif "export('" in user_input or 'export("' in user_input:
                    # Extract filename
                    start = user_input.find("'") if "'" in user_input else user_input.find('"')
                    end = user_input.rfind("'") if "'" in user_input else user_input.rfind('"')
                    if start != -1 and end != -1 and start < end:
                        filename = user_input[start+1:end]
                        playground.export(filename)
                    else:
                        playground.export()
                else:
                    playground.export()
                continue
                
            print("Unknown command. Type 'help' for available commands.")
            
        except KeyboardInterrupt:
            print("\nUse 'quit' to exit")
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Lennard-Jones Potential Playground',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--epsilon', '-e',
        type=float,
        default=1.0,
        help='Well depth ε in kJ/mol (default: 1.0)'
    )
    
    parser.add_argument(
        '--sigma', '-s',
        type=float,
        default=3.5,
        help='Collision diameter σ in Å (default: 3.5)'
    )
    
    parser.add_argument(
        '--plot', '-p',
        action='store_true',
        help='Generate plot and exit (non-interactive)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Save plot to file (requires --plot)'
    )
    
    parser.add_argument(
        '--export', '-x',
        type=str,
        help='Export data to CSV file'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Include force curve in plot'
    )
    
    args = parser.parse_args()
    
    # Non-interactive mode
    if args.plot or args.export:
        playground = LJPlayground()
        playground.epsilon = args.epsilon
        playground.sigma = args.sigma
        playground.show_force = args.force
        
        if args.plot:
            playground.plot(save_file=args.output)
            
        if args.export:
            playground.export(args.export)
    else:
        # Interactive REPL mode
        repl()


if __name__ == '__main__':
    main()
