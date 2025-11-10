"""
Visualization module for Brownian motion trajectories.

Supports 2D and 3D trajectory plots with MSD comparison.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from typing import Optional, Tuple
import matplotlib as mpl

# Set style for minimalist plots
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.size'] = 10
mpl.rcParams['axes.linewidth'] = 1.0


def visualize_trajectories(
    trajectories: np.ndarray,
    time: np.ndarray,
    dim: int = 2,
    show_start: bool = True,
    show_end: bool = True,
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None,
    title: Optional[str] = None
) -> plt.Figure:
    """
    Visualize Brownian motion trajectories.
    
    Parameters
    ----------
    trajectories : np.ndarray
        Shape (n_particles, n_steps, dim) particle positions
    time : np.ndarray
        Time points
    dim : int
        Dimension (2 or 3)
    show_start : bool
        Mark starting positions
    show_end : bool
        Mark ending positions
    figsize : tuple
        Figure size
    save_path : Optional[str]
        Path to save figure
    title : Optional[str]
        Plot title
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    """
    n_particles = trajectories.shape[0]
    
    if dim == 2:
        fig, ax = plt.subplots(figsize=figsize)
        
        # Color map for particles
        colors = plt.cm.viridis(np.linspace(0, 1, n_particles))
        
        for i in range(n_particles):
            x = trajectories[i, :, 0]
            y = trajectories[i, :, 1]
            
            # Plot trajectory
            ax.plot(x, y, alpha=0.6, linewidth=1.5, color=colors[i], label=f'Particle {i+1}')
            
            # Mark start
            if show_start:
                ax.scatter(x[0], y[0], c='green', s=80, marker='o', 
                          edgecolors='black', linewidths=1, zorder=5)
            
            # Mark end
            if show_end:
                ax.scatter(x[-1], y[-1], c='red', s=80, marker='s', 
                          edgecolors='black', linewidths=1, zorder=5)
        
        ax.set_xlabel('x (μm)', fontsize=12)
        ax.set_ylabel('y (μm)', fontsize=12)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add legend for start/end markers
        if show_start or show_end:
            from matplotlib.patches import Patch
            legend_elements = []
            if show_start:
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                                  markerfacecolor='green', markersize=8,
                                                  markeredgecolor='black', label='Start'))
            if show_end:
                legend_elements.append(plt.Line2D([0], [0], marker='s', color='w', 
                                                  markerfacecolor='red', markersize=8,
                                                  markeredgecolor='black', label='End'))
            ax.legend(handles=legend_elements, loc='upper right')
        
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        else:
            ax.set_title(f'2D Brownian Motion ({n_particles} particles, T={time[-1]:.2f}s)', 
                        fontsize=14, fontweight='bold')
    
    elif dim == 3:
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        colors = plt.cm.viridis(np.linspace(0, 1, n_particles))
        
        for i in range(n_particles):
            x = trajectories[i, :, 0]
            y = trajectories[i, :, 1]
            z = trajectories[i, :, 2]
            
            # Plot trajectory
            ax.plot(x, y, z, alpha=0.6, linewidth=1.5, color=colors[i])
            
            # Mark start
            if show_start:
                ax.scatter(x[0], y[0], z[0], c='green', s=80, marker='o',
                          edgecolors='black', linewidths=1, zorder=5)
            
            # Mark end
            if show_end:
                ax.scatter(x[-1], y[-1], z[-1], c='red', s=80, marker='s',
                          edgecolors='black', linewidths=1, zorder=5)
        
        ax.set_xlabel('x (μm)', fontsize=12)
        ax.set_ylabel('y (μm)', fontsize=12)
        ax.set_zlabel('z (μm)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        else:
            ax.set_title(f'3D Brownian Motion ({n_particles} particles, T={time[-1]:.2f}s)', 
                        fontsize=14, fontweight='bold')
    
    else:
        raise ValueError("Dimension must be 2 or 3")
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")
    
    return fig


def plot_msd_comparison(
    time: np.ndarray,
    msd_simulated: np.ndarray,
    msd_theoretical: np.ndarray,
    D: float,
    dim: int,
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot MSD comparison between simulation and theory.
    
    Parameters
    ----------
    time : np.ndarray
        Time points
    msd_simulated : np.ndarray
        Simulated MSD values
    msd_theoretical : np.ndarray
        Theoretical MSD values
    D : float
        Diffusion coefficient
    dim : int
        Dimension (2 or 3)
    figsize : tuple
        Figure size
    save_path : Optional[str]
        Path to save figure
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Plot 1: MSD vs Time
    ax1.plot(time, msd_simulated, 'o-', linewidth=2, markersize=3, 
            label='Simulated', alpha=0.7, color='steelblue')
    ax1.plot(time, msd_theoretical, '--', linewidth=2.5, 
            label=f'Theory: {2*dim}Dt', color='orangered')
    
    ax1.set_xlabel('Time (s)', fontsize=12)
    ax1.set_ylabel('MSD (μm²)', fontsize=12)
    ax1.set_title(f'Mean Square Displacement (D={D:.2f} μm²/s, {dim}D)', 
                 fontsize=13, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # Plot 2: Residuals
    residuals = msd_simulated - msd_theoretical
    relative_error = 100 * residuals / (msd_theoretical + 1e-10)
    
    ax2.plot(time, relative_error, 'o-', linewidth=1.5, markersize=3, 
            color='crimson', alpha=0.7)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax2.fill_between(time, -5, 5, alpha=0.2, color='green', label='±5% band')
    
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Relative Error (%)', fontsize=12)
    ax2.set_title('Simulation vs Theory Deviation', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"MSD comparison saved to {save_path}")
    
    return fig


def animate_trajectories(
    trajectories: np.ndarray,
    time: np.ndarray,
    dim: int = 2,
    interval: int = 50,
    trail_length: int = 50,
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None
) -> FuncAnimation:
    """
    Create an animated visualization of Brownian motion.
    
    Parameters
    ----------
    trajectories : np.ndarray
        Shape (n_particles, n_steps, dim) particle positions
    time : np.ndarray
        Time points
    dim : int
        Dimension (2 or 3)
    interval : int
        Milliseconds between frames
    trail_length : int
        Number of past positions to show as trail
    figsize : tuple
        Figure size
    save_path : Optional[str]
        Path to save animation (.mp4 or .gif)
        
    Returns
    -------
    anim : FuncAnimation
        Animation object
    """
    n_particles, n_steps, _ = trajectories.shape
    colors = plt.cm.viridis(np.linspace(0, 1, n_particles))
    
    if dim == 2:
        fig, ax = plt.subplots(figsize=figsize)
        
        # Calculate plot limits
        all_x = trajectories[:, :, 0].flatten()
        all_y = trajectories[:, :, 1].flatten()
        margin = 0.1 * max(np.ptp(all_x), np.ptp(all_y))
        ax.set_xlim(all_x.min() - margin, all_x.max() + margin)
        ax.set_ylim(all_y.min() - margin, all_y.max() + margin)
        
        ax.set_xlabel('x (μm)', fontsize=12)
        ax.set_ylabel('y (μm)', fontsize=12)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Initialize plot elements
        trails = [ax.plot([], [], alpha=0.5, linewidth=1.5, color=colors[i])[0] 
                 for i in range(n_particles)]
        points = [ax.plot([], [], 'o', markersize=8, color=colors[i])[0] 
                 for i in range(n_particles)]
        time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, 
                           fontsize=12, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        def init():
            for trail, point in zip(trails, points):
                trail.set_data([], [])
                point.set_data([], [])
            time_text.set_text('')
            return trails + points + [time_text]
        
        def update(frame):
            start_idx = max(0, frame - trail_length)
            
            for i in range(n_particles):
                # Update trail
                x = trajectories[i, start_idx:frame+1, 0]
                y = trajectories[i, start_idx:frame+1, 1]
                trails[i].set_data(x, y)
                
                # Update current position
                points[i].set_data([trajectories[i, frame, 0]], 
                                  [trajectories[i, frame, 1]])
            
            time_text.set_text(f'Time: {time[frame]:.3f} s\nStep: {frame}/{n_steps-1}')
            return trails + points + [time_text]
        
        anim = FuncAnimation(fig, update, init_func=init, frames=n_steps,
                           interval=interval, blit=True, repeat=True)
    
    elif dim == 3:
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        # Calculate plot limits
        all_x = trajectories[:, :, 0].flatten()
        all_y = trajectories[:, :, 1].flatten()
        all_z = trajectories[:, :, 2].flatten()
        margin = 0.1 * max(np.ptp(all_x), np.ptp(all_y), np.ptp(all_z))
        
        ax.set_xlim(all_x.min() - margin, all_x.max() + margin)
        ax.set_ylim(all_y.min() - margin, all_y.max() + margin)
        ax.set_zlim(all_z.min() - margin, all_z.max() + margin)
        
        ax.set_xlabel('x (μm)', fontsize=12)
        ax.set_ylabel('y (μm)', fontsize=12)
        ax.set_zlabel('z (μm)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        trails = [ax.plot([], [], [], alpha=0.5, linewidth=1.5, color=colors[i])[0] 
                 for i in range(n_particles)]
        points = [ax.plot([], [], [], 'o', markersize=8, color=colors[i])[0] 
                 for i in range(n_particles)]
        
        title_text = ax.set_title('', fontsize=12)
        
        def init():
            for trail, point in zip(trails, points):
                trail.set_data([], [])
                trail.set_3d_properties([])
                point.set_data([], [])
                point.set_3d_properties([])
            title_text.set_text('')
            return trails + points + [title_text]
        
        def update(frame):
            start_idx = max(0, frame - trail_length)
            
            for i in range(n_particles):
                x = trajectories[i, start_idx:frame+1, 0]
                y = trajectories[i, start_idx:frame+1, 1]
                z = trajectories[i, start_idx:frame+1, 2]
                
                trails[i].set_data(x, y)
                trails[i].set_3d_properties(z)
                
                points[i].set_data([trajectories[i, frame, 0]], 
                                  [trajectories[i, frame, 1]])
                points[i].set_3d_properties([trajectories[i, frame, 2]])
            
            title_text.set_text(f'3D Brownian Motion | Time: {time[frame]:.3f} s | Step: {frame}/{n_steps-1}')
            return trails + points + [title_text]
        
        anim = FuncAnimation(fig, update, init_func=init, frames=n_steps,
                           interval=interval, blit=False, repeat=True)
    
    else:
        raise ValueError("Dimension must be 2 or 3")
    
    if save_path:
        print(f"Saving animation to {save_path}... (this may take a while)")
        if save_path.endswith('.gif'):
            anim.save(save_path, writer='pillow', fps=1000//interval, dpi=100)
        elif save_path.endswith('.mp4'):
            anim.save(save_path, writer='ffmpeg', fps=1000//interval, dpi=100)
        else:
            raise ValueError("save_path must end with .gif or .mp4")
        print(f"Animation saved successfully!")
    
    return anim


def plot_displacement_histogram(
    displacements: np.ndarray,
    D: float,
    time: float,
    dim: int,
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot histogram of final displacement magnitudes.
    
    Parameters
    ----------
    displacements : np.ndarray
        Final displacement magnitudes
    D : float
        Diffusion coefficient
    time : float
        Total simulation time
    dim : int
        Dimension (2 or 3)
    figsize : tuple
        Figure size
    save_path : Optional[str]
        Path to save figure
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot histogram
    n, bins, patches = ax.hist(displacements, bins=30, density=True, 
                               alpha=0.7, color='steelblue', edgecolor='black')
    
    # Theoretical distribution (Rayleigh in 2D, Maxwell-Boltzmann in 3D)
    r = np.linspace(0, displacements.max() * 1.2, 200)
    
    if dim == 2:
        # Rayleigh distribution: p(r) = (r/σ²) * exp(-r²/(2σ²)), σ² = 2Dt
        sigma_sq = 2 * D * time
        pdf = (r / sigma_sq) * np.exp(-r**2 / (2 * sigma_sq))
        label = 'Rayleigh (theory)'
    elif dim == 3:
        # Maxwell-Boltzmann: p(r) = sqrt(2/π) * (r²/σ³) * exp(-r²/(2σ²)), σ² = 2Dt
        sigma_sq = 2 * D * time
        sigma = np.sqrt(sigma_sq)
        pdf = np.sqrt(2/np.pi) * (r**2 / sigma**3) * np.exp(-r**2 / (2 * sigma_sq))
        label = 'Maxwell-Boltzmann (theory)'
    else:
        raise ValueError("Dimension must be 2 or 3")
    
    ax.plot(r, pdf, 'r-', linewidth=2.5, label=label)
    
    ax.set_xlabel('Displacement (μm)', fontsize=12)
    ax.set_ylabel('Probability Density', fontsize=12)
    ax.set_title(f'Final Displacement Distribution ({dim}D, D={D:.2f}, T={time:.2f}s)', 
                fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Histogram saved to {save_path}")
    
    return fig
