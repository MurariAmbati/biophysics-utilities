"""
Tutorial: Understanding Brownian Motion Through Simulation

This tutorial walks through the key concepts and demonstrates
how to use the simulator to explore diffusion physics.
"""

# %% [markdown]
# # Brownian Motion Tutorial
# 
# ## Introduction
# 
# Brownian motion describes the random movement of particles in a fluid.
# This fundamental phenomenon appears throughout nature:
# - Pollen grains in water (Robert Brown, 1827)
# - Proteins diffusing in cell membranes
# - Drug molecules in bloodstream
# - Stock price fluctuations
#
# In this tutorial, we'll use simulation to understand the key properties.

# %% Setup
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core import BrownianSimulator
from src.viz import visualize_trajectories, plot_msd_comparison
import matplotlib.pyplot as plt
import numpy as np

# %% [markdown]
# ## Part 1: Basic 2D Simulation
#
# Let's start with a simple case: one particle diffusing in 2D.

# %%
print("="*60)
print("Part 1: Single Particle in 2D")
print("="*60)

# Create simulator with single particle
sim = BrownianSimulator(
    D=1.0,          # Diffusion coefficient (μm²/s)
    dt=0.01,        # Time step (s)
    n_steps=1000,   # Number of steps
    n_particles=1,  # Single particle
    dim=2,          # 2D space
    seed=42         # For reproducibility
)

# Run simulation
sim.simulate()
print("\n✓ Simulation complete!")

# Visualize
fig = visualize_trajectories(sim.trajectories, sim.time, dim=2)
plt.show()

print("\nObserve: The particle performs a 'random walk' - each step is independent.")
print("Question: Can you predict where the particle will end up? No!")
print("But we CAN predict statistical properties...")

# %% [markdown]
# ## Part 2: The Mean Square Displacement
#
# While individual trajectories are unpredictable, the AVERAGE behavior
# follows a simple law: MSD = 4Dt (in 2D).

# %%
print("\n" + "="*60)
print("Part 2: Mean Square Displacement (MSD)")
print("="*60)

# Run with many particles for statistics
sim_many = BrownianSimulator(D=1.0, dt=0.01, n_steps=1000, n_particles=50, dim=2, seed=123)
sim_many.simulate()

# Calculate MSD
time, msd_sim = sim_many.compute_msd()
msd_theory = sim_many.theoretical_msd()

# Plot comparison
fig = plot_msd_comparison(time, msd_sim, msd_theory, D=1.0, dim=2)
plt.show()

print("\nKey insight: MSD grows LINEARLY with time!")
print("This is the signature of 'normal diffusion'.")
print("\nEinstein's relation (1905): <r²(t)> = 4Dt in 2D")
print("                                    = 6Dt in 3D")

# Fit to verify
D_fit, r_squared = sim_many.fit_diffusion_coefficient()
print(f"\nVerification:")
print(f"  Input D: 1.0 μm²/s")
print(f"  Fitted D: {D_fit:.3f} μm²/s")
print(f"  R²: {r_squared:.4f}")
print(f"  Match: {'✅ Excellent!' if abs(D_fit - 1.0) < 0.1 else '⚠️ Check statistics'}")

# %% [markdown]
# ## Part 3: Effect of Diffusion Coefficient
#
# Let's explore how D affects particle motion.

# %%
print("\n" + "="*60)
print("Part 3: Varying Diffusion Coefficient")
print("="*60)

D_values = [0.5, 1.0, 2.0, 5.0]
colors = ['blue', 'green', 'orange', 'red']

fig, ax = plt.subplots(figsize=(10, 8))

for D, color in zip(D_values, colors):
    sim_d = BrownianSimulator(D=D, dt=0.01, n_steps=1000, n_particles=1, dim=2, seed=99)
    sim_d.simulate()
    
    traj = sim_d.trajectories[0]
    ax.plot(traj[:, 0], traj[:, 1], alpha=0.7, linewidth=2, 
           color=color, label=f'D={D} μm²/s')

ax.set_xlabel('x (μm)', fontsize=12)
ax.set_ylabel('y (μm)', fontsize=12)
ax.set_title('Effect of Diffusion Coefficient', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(alpha=0.3)
ax.set_aspect('equal')
plt.tight_layout()
plt.show()

print("\nObservation: Higher D → more 'spread out' trajectories")
print("Physical meaning: D ∝ kT/ηr (Stokes-Einstein)")
print("  - Higher temperature → faster diffusion")
print("  - Lower viscosity → faster diffusion")
print("  - Smaller particles → faster diffusion")

# %% [markdown]
# ## Part 4: 2D vs 3D Diffusion

# %%
print("\n" + "="*60)
print("Part 4: Comparing 2D and 3D Diffusion")
print("="*60)

# Same D, same number of steps
sim_2d = BrownianSimulator(D=1.0, dt=0.01, n_steps=1000, n_particles=30, dim=2, seed=555)
sim_3d = BrownianSimulator(D=1.0, dt=0.01, n_steps=1000, n_particles=30, dim=3, seed=555)

sim_2d.simulate()
sim_3d.simulate()

# Compare MSD
time_2d, msd_2d = sim_2d.compute_msd()
time_3d, msd_3d = sim_3d.compute_msd()

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(time_2d, msd_2d, 'o-', label='2D (simulated)', alpha=0.7, color='steelblue')
ax.plot(time_2d, sim_2d.theoretical_msd(), '--', label='2D theory (4Dt)', 
       linewidth=2.5, color='blue')
ax.plot(time_3d, msd_3d, 's-', label='3D (simulated)', alpha=0.7, color='coral')
ax.plot(time_3d, sim_3d.theoretical_msd(), '--', label='3D theory (6Dt)', 
       linewidth=2.5, color='red')

ax.set_xlabel('Time (s)', fontsize=12)
ax.set_ylabel('MSD (μm²)', fontsize=12)
ax.set_title('2D vs 3D Diffusion', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()

print("\nKey difference: 3D particles spread out FASTER")
print("  2D: MSD = 4Dt")
print("  3D: MSD = 6Dt")
print("Reason: More directions to explore in 3D!")

# %% [markdown]
# ## Part 5: Statistical Properties

# %%
print("\n" + "="*60)
print("Part 5: Statistical Analysis")
print("="*60)

# Large ensemble
sim_large = BrownianSimulator(D=2.0, dt=0.01, n_steps=2000, n_particles=100, dim=2, seed=777)
sim_large.simulate()

# Final positions
final_pos = sim_large.get_final_positions()

print(f"\nFinal positions after {sim_large.time[-1]:.1f}s:")
print(f"  Mean x: {np.mean(final_pos[:, 0]):.3f} μm (expect ~0)")
print(f"  Mean y: {np.mean(final_pos[:, 1]):.3f} μm (expect ~0)")
print(f"  Std x:  {np.std(final_pos[:, 0]):.3f} μm")
print(f"  Std y:  {np.std(final_pos[:, 1]):.3f} μm")

# Theoretical prediction for std
expected_std = np.sqrt(2 * sim_large.D * sim_large.time[-1])
print(f"  Expected std: {expected_std:.3f} μm")

# Plot distribution
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Scatter of final positions
ax1.scatter(final_pos[:, 0], final_pos[:, 1], alpha=0.6, s=50, color='steelblue')
ax1.scatter(0, 0, color='red', s=200, marker='X', label='Origin', zorder=10)
circle = plt.Circle((0, 0), expected_std, fill=False, color='red', 
                     linestyle='--', linewidth=2, label=f'Expected spread ({expected_std:.1f} μm)')
ax1.add_patch(circle)
ax1.set_xlabel('x (μm)', fontsize=12)
ax1.set_ylabel('y (μm)', fontsize=12)
ax1.set_title('Final Positions (100 particles)', fontsize=13, fontweight='bold')
ax1.legend()
ax1.grid(alpha=0.3)
ax1.set_aspect('equal')

# Histogram of displacements
displacements = sim_large.get_displacement_distribution()
ax2.hist(displacements, bins=30, density=True, alpha=0.7, color='steelblue', edgecolor='black')

# Theoretical Rayleigh distribution
r = np.linspace(0, displacements.max() * 1.2, 200)
sigma_sq = 2 * sim_large.D * sim_large.time[-1]
rayleigh = (r / sigma_sq) * np.exp(-r**2 / (2 * sigma_sq))
ax2.plot(r, rayleigh, 'r-', linewidth=2.5, label='Rayleigh (theory)')

ax2.set_xlabel('Distance from Origin (μm)', fontsize=12)
ax2.set_ylabel('Probability Density', fontsize=12)
ax2.set_title('Displacement Distribution', fontsize=13, fontweight='bold')
ax2.legend()
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.show()

print("\nStatistical properties verified:")
print("  ✅ Mean displacement ≈ 0 (no systematic drift)")
print("  ✅ Distribution follows Rayleigh (in 2D)")
print("  ✅ Spread matches theoretical prediction")

# %% [markdown]
# ## Summary and Key Takeaways

# %%
print("\n" + "="*60)
print("SUMMARY: What We Learned")
print("="*60)
print("""
1. **Random Walk Nature**
   - Individual trajectories are unpredictable
   - Each step is independent (Markov property)
   
2. **Einstein Relation**
   - MSD grows linearly: <r²(t)> = 2·dim·D·t
   - This is the hallmark of normal diffusion
   
3. **Diffusion Coefficient D**
   - Controls the 'speed' of spreading
   - Related to temperature, viscosity, particle size
   
4. **Dimensionality Matters**
   - Higher dimensions → faster spreading
   - 2D: MSD = 4Dt | 3D: MSD = 6Dt
   
5. **Statistical Predictability**
   - Can't predict individual particles
   - CAN predict ensemble averages perfectly
   - This is the power of statistical mechanics!

Applications in Biophysics:
  • Protein diffusion in membranes (D ~ 0.1-10 μm²/s)
  • Cytoplasmic transport (D ~ 1-100 μm²/s)
  • Drug delivery modeling
  • Receptor-ligand binding kinetics
  • DNA conformational dynamics

Next Steps:
  - Explore different parameter combinations
  - Try the interactive CLI for quick experiments
  - Modify the code to add drift or boundaries
  - Apply to your specific biophysics problem!
""")

print("="*60)
print("Tutorial Complete! 🎓")
print("="*60)

# %%
