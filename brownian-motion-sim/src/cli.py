#!/usr/bin/env python3
"""
Command-line interface for Brownian motion simulator.

Supports both interactive REPL mode and direct command-line execution.
"""

import argparse
import sys
from typing import Optional
import matplotlib.pyplot as plt

from .core import BrownianSimulator
from .viz import (
    visualize_trajectories,
    plot_msd_comparison,
    animate_trajectories,
    plot_displacement_histogram
)


class BrownianCLI:
    """Interactive command-line interface for Brownian simulation."""
    
    def __init__(self):
        self.sim = None
        self.D = 1.0
        self.dt = 0.01
        self.steps = 1000
        self.particles = 10
        self.dim = 2
        self.seed = None
        
    def print_header(self):
        """Print welcome header."""
        print("=" * 60)
        print("  Brownian Motion Simulator v1.0")
        print("  Stochastic particle diffusion in 2D/3D")
        print("=" * 60)
        print("\nAvailable commands:")
        print("  D = <value>         - Set diffusion coefficient (μm²/s)")
        print("  dt = <value>        - Set time step (s)")
        print("  steps = <value>     - Set number of steps")
        print("  particles = <value> - Set number of particles")
        print("  dim = <2|3>         - Set dimension (2D or 3D)")
        print("  seed = <value>      - Set random seed")
        print("  run()               - Run simulation")
        print("  plot()              - Plot trajectories")
        print("  msd()               - Plot MSD comparison")
        print("  animate()           - Animate trajectories")
        print("  histogram()         - Plot displacement histogram")
        print("  summary()           - Print simulation summary")
        print("  reset()             - Reset to defaults")
        print("  help                - Show this help")
        print("  exit/quit           - Exit program")
        print("\nCurrent parameters:")
        self.show_params()
        print()
    
    def show_params(self):
        """Display current parameters."""
        print(f"  D={self.D} μm²/s, dt={self.dt}s, steps={self.steps}, "
              f"particles={self.particles}, dim={self.dim}D")
    
    def parse_command(self, line: str) -> bool:
        """
        Parse and execute a command.
        
        Returns
        -------
        continue_running : bool
            False if should exit
        """
        line = line.strip()
        
        if not line:
            return True
        
        # Exit commands
        if line.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            return False
        
        # Help
        if line.lower() == 'help':
            self.print_header()
            return True
        
        # Parameter assignment
        if '=' in line and not line.startswith('run'):
            try:
                var, val = line.split('=', 1)
                var = var.strip()
                val = val.strip()
                
                if var == 'D':
                    self.D = float(val)
                    print(f"✓ Diffusion coefficient set to {self.D} μm²/s")
                elif var == 'dt':
                    self.dt = float(val)
                    print(f"✓ Time step set to {self.dt} s")
                elif var == 'steps':
                    self.steps = int(val)
                    print(f"✓ Steps set to {self.steps}")
                elif var == 'particles':
                    self.particles = int(val)
                    print(f"✓ Particles set to {self.particles}")
                elif var == 'dim':
                    dim_val = int(val)
                    if dim_val not in [2, 3]:
                        print("✗ Error: dim must be 2 or 3")
                    else:
                        self.dim = dim_val
                        print(f"✓ Dimension set to {self.dim}D")
                elif var == 'seed':
                    self.seed = int(val)
                    print(f"✓ Random seed set to {self.seed}")
                else:
                    print(f"✗ Unknown parameter: {var}")
                
            except ValueError as e:
                print(f"✗ Error: Invalid value - {e}")
            
            return True
        
        # Function calls
        if line.startswith('run'):
            self.run_simulation()
        elif line.startswith('plot'):
            self.plot_trajectories()
        elif line.startswith('msd'):
            self.plot_msd()
        elif line.startswith('animate'):
            self.animate()
        elif line.startswith('histogram'):
            self.plot_histogram()
        elif line.startswith('summary'):
            self.print_summary()
        elif line.startswith('reset'):
            self.reset()
        else:
            print(f"✗ Unknown command: {line}")
            print("  Type 'help' for available commands")
        
        return True
    
    def run_simulation(self):
        """Run the simulation."""
        print(f"\nSimulating {self.particles} particles in {self.dim}D "
              f"(D={self.D} μm²/s, Δt={self.dt}s)...")
        
        self.sim = BrownianSimulator(
            D=self.D,
            dt=self.dt,
            n_steps=self.steps,
            n_particles=self.particles,
            dim=self.dim,
            seed=self.seed
        )
        
        self.sim.simulate()
        
        # Calculate and display fit
        D_fit, r_squared = self.sim.fit_diffusion_coefficient()
        theoretical_coef = 2 * self.dim
        fitted_coef = 2 * self.dim * D_fit / self.D
        
        status = "✅" if abs(fitted_coef - theoretical_coef) < 0.5 else "⚠️"
        
        print(f"✓ Simulation complete!")
        print(f"  Mean-square displacement scaling: MSD ≈ {fitted_coef:.2f}Dt {status}")
        print(f"  (Expected: MSD ≈ {theoretical_coef}Dt)")
        print(f"  R² = {r_squared:.4f}")
        print("\nUse plot(), msd(), animate(), or histogram() to visualize results.")
    
    def plot_trajectories(self):
        """Plot trajectories."""
        if self.sim is None or self.sim.trajectories is None:
            print("✗ Error: No simulation data. Run simulation first with run()")
            return
        
        print("\nGenerating trajectory plot...")
        fig = visualize_trajectories(
            self.sim.trajectories,
            self.sim.time,
            dim=self.dim
        )
        plt.show()
        print("✓ Plot displayed")
    
    def plot_msd(self):
        """Plot MSD comparison."""
        if self.sim is None or self.sim.trajectories is None:
            print("✗ Error: No simulation data. Run simulation first with run()")
            return
        
        print("\nGenerating MSD comparison plot...")
        time, msd_sim = self.sim.compute_msd()
        msd_theory = self.sim.theoretical_msd()
        
        fig = plot_msd_comparison(
            time, msd_sim, msd_theory,
            self.D, self.dim
        )
        plt.show()
        print("✓ Plot displayed")
    
    def animate(self):
        """Create animation."""
        if self.sim is None or self.sim.trajectories is None:
            print("✗ Error: No simulation data. Run simulation first with run()")
            return
        
        print("\nGenerating animation...")
        print("  (Close the window to continue)")
        
        anim = animate_trajectories(
            self.sim.trajectories,
            self.sim.time,
            dim=self.dim,
            interval=50,
            trail_length=50
        )
        plt.show()
        print("✓ Animation displayed")
    
    def plot_histogram(self):
        """Plot displacement histogram."""
        if self.sim is None or self.sim.trajectories is None:
            print("✗ Error: No simulation data. Run simulation first with run()")
            return
        
        print("\nGenerating displacement histogram...")
        displacements = self.sim.get_displacement_distribution()
        
        fig = plot_displacement_histogram(
            displacements,
            self.D,
            self.sim.time[-1],
            self.dim
        )
        plt.show()
        print("✓ Plot displayed")
    
    def print_summary(self):
        """Print simulation summary."""
        if self.sim is None:
            print("✗ Error: No simulation data. Run simulation first with run()")
            return
        
        print("\n" + self.sim.get_summary())
    
    def reset(self):
        """Reset to default parameters."""
        self.D = 1.0
        self.dt = 0.01
        self.steps = 1000
        self.particles = 10
        self.dim = 2
        self.seed = None
        self.sim = None
        print("✓ Parameters reset to defaults:")
        self.show_params()
    
    def run_interactive(self):
        """Run interactive REPL."""
        self.print_header()
        
        while True:
            try:
                line = input(">>> ")
                if not self.parse_command(line):
                    break
            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'exit' to quit.")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"✗ Error: {e}")


def run_from_args(args):
    """Run simulation from command-line arguments."""
    print("=" * 60)
    print("  Brownian Motion Simulator v1.0")
    print("=" * 60)
    
    # Create simulator
    sim = BrownianSimulator(
        D=args.D,
        dt=args.dt,
        n_steps=args.steps,
        n_particles=args.particles,
        dim=args.dim,
        seed=args.seed
    )
    
    print(f"\nSimulating {args.particles} particles in {args.dim}D...")
    print(f"  D={args.D} μm²/s, Δt={args.dt}s, steps={args.steps}")
    
    # Run simulation
    sim.simulate()
    
    # Print summary
    print("\n" + sim.get_summary())
    
    # Generate plots if requested
    if args.plot:
        print("\nGenerating trajectory plot...")
        fig = visualize_trajectories(sim.trajectories, sim.time, dim=args.dim)
        if args.save:
            plt.savefig(f'brownian_trajectories_{args.dim}d.png', dpi=300, bbox_inches='tight')
            print(f"✓ Saved to brownian_trajectories_{args.dim}d.png")
        else:
            plt.show()
    
    if args.msd:
        print("\nGenerating MSD comparison plot...")
        time, msd_sim = sim.compute_msd()
        msd_theory = sim.theoretical_msd()
        fig = plot_msd_comparison(time, msd_sim, msd_theory, args.D, args.dim)
        if args.save:
            plt.savefig(f'brownian_msd_{args.dim}d.png', dpi=300, bbox_inches='tight')
            print(f"✓ Saved to brownian_msd_{args.dim}d.png")
        else:
            plt.show()
    
    if args.animate:
        print("\nGenerating animation...")
        anim = animate_trajectories(sim.trajectories, sim.time, dim=args.dim)
        if args.save:
            save_path = f'brownian_animation_{args.dim}d.mp4'
            print(f"Saving to {save_path}...")
            anim.save(save_path, writer='ffmpeg', fps=20, dpi=100)
            print(f"✓ Saved animation")
        else:
            plt.show()
    
    if args.histogram:
        print("\nGenerating displacement histogram...")
        displacements = sim.get_displacement_distribution()
        fig = plot_displacement_histogram(displacements, args.D, sim.time[-1], args.dim)
        if args.save:
            plt.savefig(f'brownian_histogram_{args.dim}d.png', dpi=300, bbox_inches='tight')
            print(f"✓ Saved to brownian_histogram_{args.dim}d.png")
        else:
            plt.show()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Brownian Motion Simulator - Stochastic particle diffusion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  brownian-sim
  
  # Direct simulation with custom parameters
  brownian-sim --dim 3 --particles 5 --D 2.5 --steps 2000 --plot --msd
  
  # Generate and save animation
  brownian-sim --dim 2 --particles 3 --animate --save
        """
    )
    
    parser.add_argument('--D', type=float, default=1.0,
                       help='Diffusion coefficient (μm²/s), default: 1.0')
    parser.add_argument('--dt', type=float, default=0.01,
                       help='Time step (s), default: 0.01')
    parser.add_argument('--steps', type=int, default=1000,
                       help='Number of simulation steps, default: 1000')
    parser.add_argument('--particles', type=int, default=10,
                       help='Number of particles, default: 10')
    parser.add_argument('--dim', type=int, choices=[2, 3], default=2,
                       help='Dimension (2 or 3), default: 2')
    parser.add_argument('--seed', type=int, default=None,
                       help='Random seed for reproducibility')
    
    parser.add_argument('--plot', action='store_true',
                       help='Generate trajectory plot')
    parser.add_argument('--msd', action='store_true',
                       help='Generate MSD comparison plot')
    parser.add_argument('--animate', action='store_true',
                       help='Generate animation')
    parser.add_argument('--histogram', action='store_true',
                       help='Generate displacement histogram')
    parser.add_argument('--save', action='store_true',
                       help='Save plots/animations instead of displaying')
    
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Start interactive REPL mode')
    
    args = parser.parse_args()
    
    # If no flags provided or interactive mode requested, start REPL
    if args.interactive or len(sys.argv) == 1:
        cli = BrownianCLI()
        cli.run_interactive()
    else:
        # Run from command-line arguments
        run_from_args(args)


if __name__ == '__main__':
    main()
