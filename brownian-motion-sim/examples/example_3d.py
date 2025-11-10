"""
Example: 3D Brownian Motion with Animation

Demonstrates 3D trajectory simulation and animated visualization.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core import BrownianSimulator
from src.viz import visualize_trajectories, animate_trajectories
import matplotlib.pyplot as plt


def main():
    """Run 3D Brownian motion with animation."""
    
    print("=" * 60)
    print("  3D Brownian Motion with Animation")
    print("=" * 60)
    
    # Parameters for 3D simulation
    sim = BrownianSimulator(
        D=1.5,
        dt=0.01,
        n_steps=500,
        n_particles=3,
        dim=3,
        seed=123
    )
    
    print("\nSimulating 3 particles in 3D...")
    sim.simulate()
    
    print("✓ Simulation complete!")
    print("\n" + sim.get_summary())
    
    # Static 3D plot
    print("\nGenerating 3D trajectory plot...")
    fig = visualize_trajectories(
        sim.trajectories,
        sim.time,
        dim=3,
        title="3D Brownian Motion"
    )
    plt.show()
    
    # Animated visualization
    print("\nGenerating animation...")
    print("(Close window when done)")
    anim = animate_trajectories(
        sim.trajectories,
        sim.time,
        dim=3,
        interval=30,
        trail_length=30
    )
    plt.show()
    
    print("\n✓ Example complete!")


if __name__ == '__main__':
    main()
