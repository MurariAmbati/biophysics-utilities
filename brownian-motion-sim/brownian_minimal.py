#!/usr/bin/env python3
"""
Minimal single-file Brownian motion simulator (<150 lines).
For educational purposes and quick demonstrations.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class BrownianMotion:
    def __init__(self, D=1.0, dt=0.01, steps=1000, particles=10, dim=2):
        self.D, self.dt, self.steps, self.particles, self.dim = D, dt, steps, particles, dim
        self.traj = None
        self.time = np.arange(steps) * dt
        
    def run(self):
        """Simulate: x_{t+dt} = x_t + sqrt(2D*dt)*N(0,1)"""
        pos = np.zeros((self.particles, self.steps, self.dim))
        noise = np.random.randn(self.particles, self.steps-1, self.dim)
        pos[:, 1:, :] = np.cumsum(np.sqrt(2*self.D*self.dt) * noise, axis=1)
        self.traj = pos
        return pos
    
    def msd(self):
        """Calculate mean square displacement"""
        r2 = np.sum(self.traj**2, axis=2)
        return np.mean(r2, axis=0)
    
    def plot(self):
        """Plot trajectories"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Trajectories
        for i in range(self.particles):
            ax1.plot(self.traj[i,:,0], self.traj[i,:,1], alpha=0.6, lw=1.5)
        ax1.scatter(self.traj[:,0,0], self.traj[:,0,1], c='green', s=80, marker='o', label='Start')
        ax1.scatter(self.traj[:,-1,0], self.traj[:,-1,1], c='red', s=80, marker='s', label='End')
        ax1.set_xlabel('x (μm)'); ax1.set_ylabel('y (μm)')
        ax1.set_title(f'{self.particles} particles, D={self.D} μm²/s')
        ax1.legend(); ax1.grid(alpha=0.3); ax1.set_aspect('equal')
        
        # MSD
        msd_sim = self.msd()
        msd_theory = 2*self.dim*self.D*self.time
        ax2.plot(self.time, msd_sim, 'o-', label='Simulated', alpha=0.7)
        ax2.plot(self.time, msd_theory, '--', label=f'Theory: {2*self.dim}Dt', lw=2.5)
        ax2.set_xlabel('Time (s)'); ax2.set_ylabel('MSD (μm²)')
        ax2.set_title('Mean Square Displacement')
        ax2.legend(); ax2.grid(alpha=0.3)
        
        plt.tight_layout()
        return fig

# Quick demo
if __name__ == '__main__':
    print("Brownian Motion Quick Demo")
    print("="*40)
    
    # Run simulation
    sim = BrownianMotion(D=1.5, dt=0.01, steps=1000, particles=8, dim=2)
    print(f"Simulating {sim.particles} particles in {sim.dim}D...")
    sim.run()
    
    # Validate MSD scaling
    msd_sim = sim.msd()
    slope = np.polyfit(sim.time[10:], msd_sim[10:], 1)[0]
    D_fit = slope / (2*sim.dim)
    print(f"Expected D: {sim.D:.2f} μm²/s")
    print(f"Fitted D: {D_fit:.2f} μm²/s")
    print(f"MSD ~ {slope:.2f}t (expected: {2*sim.dim*sim.D:.2f}t)")
    print("="*40)
    
    # Plot
    sim.plot()
    plt.show()
