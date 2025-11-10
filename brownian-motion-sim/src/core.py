"""
Core Brownian motion simulation engine.

Implements stochastic differential equation:
    dx_t = sqrt(2D) * dW_t
    
Discrete approximation:
    x_{t+Δt} = x_t + sqrt(2D*Δt) * N(0,1)
"""

import numpy as np
from typing import Tuple, Optional


class BrownianSimulator:
    """
    Simulate Brownian motion in 2D or 3D.
    
    Parameters
    ----------
    D : float
        Diffusion coefficient (μm²/s)
    dt : float
        Time step (s)
    n_steps : int
        Number of simulation steps
    n_particles : int
        Number of particles to simulate
    dim : int
        Dimensionality (2 or 3)
    seed : Optional[int]
        Random seed for reproducibility
    """
    
    def __init__(
        self,
        D: float = 1.0,
        dt: float = 0.01,
        n_steps: int = 1000,
        n_particles: int = 10,
        dim: int = 2,
        seed: Optional[int] = None
    ):
        self.D = D
        self.dt = dt
        self.n_steps = n_steps
        self.n_particles = n_particles
        self.dim = dim
        
        if dim not in [2, 3]:
            raise ValueError("Dimension must be 2 or 3")
        
        self.rng = np.random.default_rng(seed)
        self.trajectories = None
        self.time = None
        
    def simulate(self) -> np.ndarray:
        """
        Run the Brownian motion simulation.
        
        Returns
        -------
        trajectories : np.ndarray
            Shape (n_particles, n_steps, dim) containing particle positions
        """
        # Initialize positions at origin
        positions = np.zeros((self.n_particles, self.n_steps, self.dim))
        
        # Generate random increments
        # Shape: (n_particles, n_steps-1, dim)
        noise = self.rng.standard_normal((self.n_particles, self.n_steps - 1, self.dim))
        
        # Calculate displacements: dx = sqrt(2D*dt) * N(0,1)
        displacements = np.sqrt(2 * self.D * self.dt) * noise
        
        # Compute cumulative sum to get trajectories
        positions[:, 1:, :] = np.cumsum(displacements, axis=1)
        
        self.trajectories = positions
        self.time = np.arange(self.n_steps) * self.dt
        
        return positions
    
    def compute_msd(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute mean square displacement (MSD) over time.
        
        MSD(t) = <r²(t)> = <(x(t) - x(0))²>
        
        Returns
        -------
        time : np.ndarray
            Time points
        msd : np.ndarray
            Mean square displacement at each time point
        """
        if self.trajectories is None:
            raise RuntimeError("Must call simulate() first")
        
        # Calculate displacement from origin
        displacements = self.trajectories  # Already relative to origin at (0,0,0)
        
        # Square displacement and sum over dimensions
        squared_displacements = np.sum(displacements**2, axis=2)
        
        # Average over all particles
        msd = np.mean(squared_displacements, axis=0)
        
        return self.time, msd
    
    def theoretical_msd(self) -> np.ndarray:
        """
        Compute theoretical MSD.
        
        Theory:
            MSD = 2*dim*D*t  (Einstein relation)
            2D: MSD = 4Dt
            3D: MSD = 6Dt
        
        Returns
        -------
        msd_theory : np.ndarray
            Theoretical MSD at each time point
        """
        if self.time is None:
            self.time = np.arange(self.n_steps) * self.dt
        
        return 2 * self.dim * self.D * self.time
    
    def fit_diffusion_coefficient(self) -> Tuple[float, float]:
        """
        Fit the diffusion coefficient from simulated MSD.
        
        Linear fit: MSD = (2*dim*D)*t
        Slope = 2*dim*D => D_fit = slope / (2*dim)
        
        Returns
        -------
        D_fit : float
            Fitted diffusion coefficient
        r_squared : float
            R² goodness of fit
        """
        time, msd = self.compute_msd()
        
        # Linear regression: MSD vs time
        # Skip first point (t=0) to avoid division issues
        t_fit = time[1:]
        msd_fit = msd[1:]
        
        # Fit through origin: MSD = slope * t
        slope = np.sum(t_fit * msd_fit) / np.sum(t_fit**2)
        
        # Extract diffusion coefficient
        D_fit = slope / (2 * self.dim)
        
        # Calculate R²
        msd_predicted = slope * t_fit
        ss_res = np.sum((msd_fit - msd_predicted)**2)
        ss_tot = np.sum((msd_fit - np.mean(msd_fit))**2)
        r_squared = 1 - (ss_res / ss_tot)
        
        return D_fit, r_squared
    
    def get_summary(self) -> str:
        """Generate a summary of the simulation parameters and results."""
        if self.trajectories is None:
            return f"BrownianSimulator (not yet run)\n" \
                   f"  D={self.D:.2f} μm²/s, dt={self.dt:.3f}s, " \
                   f"steps={self.n_steps}, particles={self.n_particles}, dim={self.dim}D"
        
        D_fit, r_squared = self.fit_diffusion_coefficient()
        theoretical_coef = 2 * self.dim
        fitted_coef = 2 * self.dim * D_fit / self.D
        
        status = "✅" if abs(fitted_coef - theoretical_coef) < 0.5 else "⚠️"
        
        summary = f"Brownian Motion Simulation Results\n"
        summary += f"{'='*50}\n"
        summary += f"Parameters:\n"
        summary += f"  Diffusion coefficient (D): {self.D:.2f} μm²/s\n"
        summary += f"  Time step (Δt): {self.dt:.3f} s\n"
        summary += f"  Total steps: {self.n_steps}\n"
        summary += f"  Particles: {self.n_particles}\n"
        summary += f"  Dimension: {self.dim}D\n"
        summary += f"  Total time: {self.time[-1]:.2f} s\n\n"
        summary += f"Results:\n"
        summary += f"  Theoretical: MSD ≈ {theoretical_coef}Dt\n"
        summary += f"  Fitted: MSD ≈ {fitted_coef:.2f}Dt {status}\n"
        summary += f"  D_fit = {D_fit:.3f} μm²/s (expected: {self.D:.3f})\n"
        summary += f"  R² = {r_squared:.4f}\n"
        
        return summary
    
    def get_final_positions(self) -> np.ndarray:
        """
        Get final positions of all particles.
        
        Returns
        -------
        final_pos : np.ndarray
            Shape (n_particles, dim) with final positions
        """
        if self.trajectories is None:
            raise RuntimeError("Must call simulate() first")
        
        return self.trajectories[:, -1, :]
    
    def get_displacement_distribution(self) -> np.ndarray:
        """
        Get final displacement magnitudes from origin.
        
        Returns
        -------
        displacements : np.ndarray
            Shape (n_particles,) with displacement magnitudes
        """
        final_pos = self.get_final_positions()
        return np.sqrt(np.sum(final_pos**2, axis=1))
