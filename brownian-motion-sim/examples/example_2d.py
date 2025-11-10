"""
Example: 2D Brownian Motion Simulation

This script demonstrates a basic 2D Brownian motion simulation
with visualization and MSD analysis.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core import BrownianSimulator
from src.viz import visualize_trajectories, plot_msd_comparison
import matplotlib.pyplot as plt


def main():
    """Run a simple 2D Brownian motion example."""
    
    print("=" * 60)
    print("  2D Brownian Motion Example")
    print("=" * 60)
    
    # Simulation parameters
    D = 2.0          # Diffusion coefficient (μm²/s)
    dt = 0.01        # Time step (s)
    n_steps = 1000   # Number of steps
    n_particles = 5  # Number of particles
    
    print(f"\nParameters:")
    print(f"  Diffusion coefficient: {D} μm²/s")
    print(f"  Time step: {dt} s")
    print(f"  Total steps: {n_steps}")
    print(f"  Particles: {n_particles}")
    print(f"  Dimension: 2D")
    
    # Create simulator
    sim = BrownianSimulator(
        D=D,
        dt=dt,
        n_steps=n_steps,
        n_particles=n_particles,
        dim=2,
        seed=42  # For reproducibility
    )
    
    # Run simulation
    print("\nRunning simulation...")
    trajectories = sim.simulate()
    print("✓ Simulation complete!")
    
    # Calculate MSD
    time, msd_sim = sim.compute_msd()
    msd_theory = sim.theoretical_msd()
    
    # Fit diffusion coefficient
    D_fit, r_squared = sim.fit_diffusion_coefficient()
    
    print(f"\nResults:")
    print(f"  Fitted D: {D_fit:.3f} μm²/s (expected: {D:.3f})")
    print(f"  R²: {r_squared:.4f}")
    print(f"  MSD scaling: {2*2*D_fit/D:.2f}Dt (expected: 4Dt)")
    
    # Print summary
    print("\n" + "=" * 60)
    print(sim.get_summary())
    print("=" * 60)
    
    # Visualize trajectories
    print("\nGenerating trajectory plot...")
    fig1 = visualize_trajectories(
        trajectories,
        time,
        dim=2,
        title="2D Brownian Motion Example"
    )
    
    # Plot MSD comparison
    print("Generating MSD comparison...")
    fig2 = plot_msd_comparison(
        time, msd_sim, msd_theory,
        D, dim=2
    )
    
    # Show all plots
    print("\nDisplaying plots... (close windows to continue)")
    plt.show()
    
    print("\n✓ Example complete!")


if __name__ == '__main__':
    main()
