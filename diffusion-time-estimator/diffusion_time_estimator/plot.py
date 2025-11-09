"""
Optional visualization functions for diffusion analysis.
"""
import numpy as np
import matplotlib.pyplot as plt
from .core import mean_square_displacement


def plot_msd(D, dims=3, time_range=(-6, 2), num_points=200):
    """
    Plot mean-square displacement vs. time on a log-log scale.
    
    Parameters
    ----------
    D : float
        Diffusion coefficient (m²/s)
    dims : int, optional
        Number of spatial dimensions (1, 2, or 3), default is 3
    time_range : tuple, optional
        Log10 range for time axis (min_exp, max_exp), default is (-6, 2)
    num_points : int, optional
        Number of points to plot, default is 200
    """
    # Generate time array on log scale
    t = np.logspace(time_range[0], time_range[1], num_points)
    
    # Calculate MSD for each time point
    msd = mean_square_displacement(D, t, dims)
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.loglog(t, msd, 'b-', linewidth=2, label=f'{dims}D diffusion')
    
    # Add slope reference line (slope = 1 on log-log plot)
    t_ref = np.array([t[len(t)//4], t[3*len(t)//4]])
    msd_ref = mean_square_displacement(D, t_ref, dims)
    plt.loglog(t_ref, msd_ref, 'r--', alpha=0.5, linewidth=1, label='Slope = 1')
    
    # Labels and formatting
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Mean Square Displacement (m²)', fontsize=12)
    plt.title(f'Mean Square Displacement\nD = {D:.3e} m²/s, {dims}D', fontsize=14)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.legend(fontsize=10)
    
    # Add text box with equation
    textstr = f'⟨x²(t)⟩ = 2·{dims}·D·t'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.text(0.05, 0.95, textstr, transform=plt.gca().transAxes, fontsize=11,
             verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    plt.show()


def plot_msd_comparison(params_list, dims=3, time_range=(-6, 2), num_points=200):
    """
    Plot multiple MSD curves for comparison.
    
    Parameters
    ----------
    params_list : list of dict
        List of parameter dictionaries, each containing 'D' and 'label'
    dims : int, optional
        Number of spatial dimensions (1, 2, or 3), default is 3
    time_range : tuple, optional
        Log10 range for time axis (min_exp, max_exp), default is (-6, 2)
    num_points : int, optional
        Number of points to plot, default is 200
    """
    # Generate time array on log scale
    t = np.logspace(time_range[0], time_range[1], num_points)
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    
    for params in params_list:
        D = params['D']
        label = params.get('label', f'D = {D:.2e}')
        msd = mean_square_displacement(D, t, dims)
        plt.loglog(t, msd, linewidth=2, label=label)
    
    # Labels and formatting
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Mean Square Displacement (m²)', fontsize=12)
    plt.title(f'Mean Square Displacement Comparison ({dims}D)', fontsize=14)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.legend(fontsize=10)
    
    plt.tight_layout()
    plt.show()
