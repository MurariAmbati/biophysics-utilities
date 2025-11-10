#!/usr/bin/env python3
"""
Quick demo of the Lennard-Jones Playground
Run this to see a basic example!
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import numpy as np
import matplotlib.pyplot as plt
from model import generate_lj_curve, lj_equilibrium, lj_force

def main():
    print("=" * 60)
    print("  Lennard-Jones Potential Playground - Demo")
    print("=" * 60)
    print()
    
    # Parameters
    epsilon = 1.0  # kJ/mol
    sigma = 3.5    # Angstrom
    
    print(f"Parameters:")
    print(f"  ε (epsilon) = {epsilon} kJ/mol")
    print(f"  σ (sigma)   = {sigma} Å")
    print()
    
    # Calculate equilibrium
    r_eq, V_eq = lj_equilibrium(epsilon, sigma)
    print(f"Equilibrium Properties:")
    print(f"  r_min = {r_eq:.3f} Å")
    print(f"  V_min = {V_eq:.3f} kJ/mol")
    print(f"  r_min/σ = {r_eq/sigma:.4f} (theoretical: {2**(1/6):.4f})")
    print()
    
    # Generate curves
    print("Generating potential and force curves...")
    r, V = generate_lj_curve(epsilon, sigma)
    F = lj_force(r, epsilon, sigma)
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Potential
    ax1.plot(r, V, 'b-', linewidth=2.5, label='LJ Potential')
    ax1.axhline(y=0, color='k', linestyle='--', linewidth=1, alpha=0.5)
    ax1.plot(r_eq, V_eq, 'ro', markersize=12, 
            label=f'Minimum: r={r_eq:.2f} Å, V={V_eq:.2f} kJ/mol')
    
    # Highlight regions
    ax1.axvspan(r[0], r_eq, alpha=0.1, color='red', label='Repulsive region')
    ax1.axvspan(r_eq, r[-1], alpha=0.1, color='blue', label='Attractive region')
    
    ax1.set_xlabel('Distance r (Å)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Potential V(r) (kJ/mol)', fontsize=12, fontweight='bold')
    ax1.set_title(f'Lennard-Jones Potential (ε={epsilon} kJ/mol, σ={sigma} Å)', 
                 fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(fontsize=10, loc='upper right')
    ax1.set_ylim(-1.5, 2)
    
    # Plot 2: Force
    ax2.plot(r, F, 'r-', linewidth=2.5, label='LJ Force')
    ax2.axhline(y=0, color='k', linestyle='--', linewidth=1, alpha=0.5)
    ax2.axvline(x=r_eq, color='gray', linestyle=':', linewidth=1.5, alpha=0.7,
               label=f'Equilibrium (r={r_eq:.2f} Å)')
    
    # Annotate force regions
    ax2.text(r_eq - 0.5, 5, 'Repulsive\nF > 0', ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='red', alpha=0.3))
    ax2.text(r_eq + 1.5, -1, 'Attractive\nF < 0', ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='blue', alpha=0.3))
    
    ax2.set_xlabel('Distance r (Å)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Force F(r) (kJ/mol/Å)', fontsize=12, fontweight='bold')
    ax2.set_title('Lennard-Jones Force: F(r) = -dV/dr', 
                 fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(fontsize=10, loc='upper right')
    
    plt.tight_layout()
    
    print("✓ Plot generated!")
    print()
    print("Close the plot window to continue...")
    plt.show()
    
    print()
    print("=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Try the CLI:  python -m src.cli")
    print("2. Open notebook: jupyter notebook examples/lj_interactive_demo.ipynb")
    print("3. Read QUICKSTART.md for more examples")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have installed dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
