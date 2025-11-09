"""
Interactive REPL (Read-Eval-Print Loop) for biochemical calculations.
"""

import sys
import readline  # For command history and editing
from .constants import list_constants, get_constant, search_constants, CONSTANTS
from .units import convert, format_quantity, ureg
from .parser import evaluate, energy


class BioCalcREPL:
    """Interactive calculator REPL."""
    
    def __init__(self, precision=6):
        """
        Initialize REPL.
        
        Parameters
        ----------
        precision : int
            Default decimal precision for output
        """
        self.precision = precision
        self.history = []
        self.running = True
        
        # Built-in commands
        self.commands = {
            'help': self.cmd_help,
            'list': self.cmd_list_constants,
            'search': self.cmd_search,
            'convert': self.cmd_convert,
            'energy': self.cmd_energy,
            'precision': self.cmd_set_precision,
            'quit': self.cmd_quit,
            'exit': self.cmd_quit,
        }
    
    def cmd_help(self, args=None):
        """Display help message."""
        help_text = """
biocalc - Unit-Aware Biochemical Calculator

Available commands:
  help                    Show this help message
  list                    List all available constants
  search <query>          Search for constants matching query
  convert <expr> <unit>   Convert expression to target unit
  energy(<constant>)      Get energy value of constant
  precision <n>           Set decimal precision
  quit / exit             Exit calculator

Examples:
  >>> R * 300*K
  >>> avogadro * 1e-3 mol
  >>> convert(1 kcal/mol, J/mol)
  >>> energy(ATP_hydrolysis)
  >>> search(diffusion)
  
You can use any constant by name (type 'list' to see all).
Supports SI units and automatic conversions.
"""
        print(help_text)
    
    def cmd_list_constants(self, args=None):
        """List all available constants."""
        constants = list_constants()
        print("\nAvailable constants:")
        print("-" * 60)
        
        # Group by category
        categories = {
            'Fundamental': ['avogadro', 'N_A', 'boltzmann', 'k_B', 'R', 'gas_constant', 
                          'planck', 'h', 'speed_of_light', 'c', 'elementary_charge', 
                          'e', 'faraday', 'F'],
            'Biochemical Energy': ['ATP_hydrolysis', 'ATP_synthesis', 'GTP_hydrolysis', 
                                  'proton_motive_force'],
            'Diffusion': [k for k in constants if 'diffusion' in k],
            'Temperature & Pressure': ['standard_temperature', 'T_std', 'standard_pressure', 
                                      'P_std', 'body_temperature', 'T_body'],
            'Molecular Mass': [k for k in constants if 'mass_' in k],
            'Concentration': [k for k in constants if 'conc_' in k or 'pH' in k],
            'Membrane': [k for k in constants if 'membrane' in k],
            'Other': ['viscosity_water', 'gravitational_acceleration', 'g'],
        }
        
        for category, const_names in categories.items():
            if not const_names:
                continue
            print(f"\n{category}:")
            for name in const_names:
                if name in CONSTANTS:
                    value = CONSTANTS[name]
                    print(f"  {name:30s} = {format_quantity(value, self.precision)}")
    
    def cmd_search(self, args):
        """Search for constants."""
        if not args:
            print("Usage: search <query>")
            return
        
        query = ' '.join(args)
        results = search_constants(query)
        
        if not results:
            print(f"No constants found matching '{query}'")
            return
        
        print(f"\nConstants matching '{query}':")
        print("-" * 60)
        for name, value in results.items():
            print(f"  {name:30s} = {format_quantity(value, self.precision)}")
    
    def cmd_convert(self, args):
        """Convert units."""
        if len(args) < 2:
            print("Usage: convert <expression> <target_unit>")
            print("Example: convert 1 kcal/mol J/mol")
            return
        
        try:
            # Parse as "convert <value> <from_unit> <to_unit>" or "convert <value from_unit> <to_unit>"
            if len(args) == 3:
                expr = f"{args[0]} {args[1]}"
                target = args[2]
            else:
                expr = ' '.join(args[:-1])
                target = args[-1]
            
            result = convert(expr, target)
            print(format_quantity(result, self.precision))
        except Exception as e:
            print(f"Error: {e}")
    
    def cmd_energy(self, args):
        """Get energy value."""
        if not args:
            print("Usage: energy <constant_name>")
            print("Example: energy ATP_hydrolysis")
            return
        
        try:
            const_name = args[0]
            result = energy(const_name)
            print(format_quantity(result, self.precision))
        except Exception as e:
            print(f"Error: {e}")
    
    def cmd_set_precision(self, args):
        """Set output precision."""
        if not args:
            print(f"Current precision: {self.precision}")
            return
        
        try:
            self.precision = int(args[0])
            print(f"Precision set to {self.precision}")
        except ValueError:
            print("Error: Precision must be an integer")
    
    def cmd_quit(self, args=None):
        """Quit the REPL."""
        self.running = False
        print("Goodbye!")
    
    def process_command(self, line):
        """Process a command or expression."""
        line = line.strip()
        
        if not line:
            return
        
        # Check for built-in commands
        parts = line.split()
        cmd = parts[0].lower()
        
        if cmd in self.commands:
            self.commands[cmd](parts[1:] if len(parts) > 1 else None)
            return
        
        # Check for function-style commands
        if '(' in line:
            # Handle convert(...), energy(...), etc.
            if line.startswith('convert('):
                # Parse convert(expr, unit)
                try:
                    inner = line[8:-1]  # Remove 'convert(' and ')'
                    parts = [p.strip() for p in inner.split(',')]
                    if len(parts) == 2:
                        result = convert(parts[0], parts[1])
                        print(format_quantity(result, self.precision))
                        return
                except Exception as e:
                    print(f"Error: {e}")
                    return
            
            elif line.startswith('energy('):
                try:
                    const_name = line[7:-1].strip()
                    result = energy(const_name)
                    print(format_quantity(result, self.precision))
                    return
                except Exception as e:
                    print(f"Error: {e}")
                    return
            
            elif line.startswith('list_constants('):
                self.cmd_list_constants()
                return
        
        # Otherwise, try to evaluate as expression
        try:
            result = evaluate(line, return_units=True, precision=self.precision)
            
            # Format output
            if hasattr(result, 'units'):
                print(format_quantity(result, self.precision))
            else:
                print(f"{result:.{self.precision}f}")
            
            # Store in history
            self.history.append((line, result))
            
        except Exception as e:
            print(f"Error: {e}")
    
    def run(self):
        """Run the REPL."""
        print("biocalc - Unit-Aware Biochemical Calculator")
        print("Type 'help' for commands, 'quit' to exit\n")
        
        while self.running:
            try:
                line = input(">>> ")
                self.process_command(line)
            except KeyboardInterrupt:
                print("\nUse 'quit' or 'exit' to leave")
            except EOFError:
                self.cmd_quit()


def start_repl(precision=6):
    """
    Start the interactive REPL.
    
    Parameters
    ----------
    precision : int
        Decimal precision for output
    """
    repl = BioCalcREPL(precision=precision)
    repl.run()
