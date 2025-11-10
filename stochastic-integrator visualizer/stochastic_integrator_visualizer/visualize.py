"""
Visualization functions for stochastic trajectories.

Provides:
- Single trajectory plots
- Multiple trajectory overlays
- Histogram of final values
- Phase-space plots (x vs dx/dt)
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Optional, Tuple
from .constants import (
    DEFAULT_LINEWIDTH,
    DEFAULT_ALPHA,
    DEFAULT_GRID,
    DEFAULT_BINS,
)


def plot_trajectory(
    t: np.ndarray,
    x: np.ndarray,
    title: str = "Euler–Maruyama Integration of SDE",
    xlabel: str = "Time (s)",
    ylabel: str = "x(t)",
    linewidth: float = DEFAULT_LINEWIDTH,
    grid: bool = DEFAULT_GRID,
    ax: Optional[plt.Axes] = None,
    show: bool = True,
) -> plt.Axes:
    """
    Plot a single trajectory x(t).
    
    Parameters
    ----------
    t : np.ndarray
        Time array
    x : np.ndarray
        Trajectory values
    title : str
        Plot title
    xlabel : str
        X-axis label
    ylabel : str
        Y-axis label
    linewidth : float
        Line width
    grid : bool
        Show grid
    ax : plt.Axes, optional
        Existing axes to plot on
    show : bool
        Whether to call plt.show()
        
    Returns
    -------
    ax : plt.Axes
        The axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(t, x, lw=linewidth, color='steelblue')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(grid, alpha=0.3)
    
    if show:
        plt.tight_layout()
        plt.show()
    
    return ax


def plot_multiple_trajectories(
    t: np.ndarray,
    trajectories: List[np.ndarray],
    title: str = "Multiple Stochastic Trajectories",
    xlabel: str = "Time (s)",
    ylabel: str = "x(t)",
    alpha: float = DEFAULT_ALPHA,
    grid: bool = DEFAULT_GRID,
    ax: Optional[plt.Axes] = None,
    show: bool = True,
    show_mean: bool = True,
    show_std: bool = True,
) -> plt.Axes:
    """
    Plot multiple trajectories on the same axes to visualize variance.
    
    Parameters
    ----------
    t : np.ndarray
        Time array
    trajectories : list of np.ndarray
        List of trajectory arrays
    title : str
        Plot title
    xlabel : str
        X-axis label
    ylabel : str
        Y-axis label
    alpha : float
        Transparency for individual trajectories
    grid : bool
        Show grid
    ax : plt.Axes, optional
        Existing axes to plot on
    show : bool
        Whether to call plt.show()
    show_mean : bool
        Whether to overlay ensemble mean
    show_std : bool
        Whether to show ±1 std deviation bands
        
    Returns
    -------
    ax : plt.Axes
        The axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot individual trajectories
    for i, x in enumerate(trajectories):
        ax.plot(t, x, lw=0.8, alpha=alpha, color='steelblue')
    
    # Calculate and plot ensemble statistics
    if show_mean or show_std:
        trajectories_array = np.array(trajectories)
        mean_traj = np.mean(trajectories_array, axis=0)
        std_traj = np.std(trajectories_array, axis=0)
        
        if show_mean:
            ax.plot(t, mean_traj, lw=2.5, color='darkred', 
                   label='Ensemble Mean', zorder=100)
        
        if show_std:
            ax.fill_between(t, mean_traj - std_traj, mean_traj + std_traj,
                           alpha=0.3, color='red', label='±1 Std Dev')
    
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(grid, alpha=0.3)
    
    if show_mean or show_std:
        ax.legend(loc='best', fontsize=10)
    
    if show:
        plt.tight_layout()
        plt.show()
    
    return ax


def plot_histogram(
    final_values: np.ndarray,
    bins: int = DEFAULT_BINS,
    title: str = "Distribution of Final Values",
    xlabel: str = "x(T)",
    ylabel: str = "Frequency",
    show_stats: bool = True,
    ax: Optional[plt.Axes] = None,
    show: bool = True,
) -> plt.Axes:
    """
    Plot histogram of final values from multiple trajectories.
    
    Parameters
    ----------
    final_values : np.ndarray
        Array of final x(T) values
    bins : int
        Number of histogram bins
    title : str
        Plot title
    xlabel : str
        X-axis label
    ylabel : str
        Y-axis label
    show_stats : bool
        Whether to display mean and std on plot
    ax : plt.Axes, optional
        Existing axes to plot on
    show : bool
        Whether to call plt.show()
        
    Returns
    -------
    ax : plt.Axes
        The axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot histogram
    n, bins_edges, patches = ax.hist(final_values, bins=bins, 
                                      color='steelblue', alpha=0.7, 
                                      edgecolor='black', linewidth=0.8)
    
    # Calculate statistics
    mean_val = np.mean(final_values)
    std_val = np.std(final_values)
    
    # Add vertical lines for mean
    ax.axvline(mean_val, color='darkred', linestyle='--', 
              linewidth=2, label=f'Mean = {mean_val:.3f}')
    
    # Add shaded region for ±1 std
    ax.axvspan(mean_val - std_val, mean_val + std_val, 
              alpha=0.2, color='red', label=f'±1 Std = {std_val:.3f}')
    
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend(loc='best', fontsize=10)
    
    if show_stats:
        # Add text box with statistics
        stats_text = f'Mean: {mean_val:.4f}\nStd: {std_val:.4f}\nMin: {np.min(final_values):.4f}\nMax: {np.max(final_values):.4f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    if show:
        plt.tight_layout()
        plt.show()
    
    return ax


def plot_phase_space(
    t: np.ndarray,
    x: np.ndarray,
    title: str = "Phase Space (x vs dx/dt)",
    xlabel: str = "x(t)",
    ylabel: str = "dx/dt",
    linewidth: float = DEFAULT_LINEWIDTH,
    grid: bool = DEFAULT_GRID,
    ax: Optional[plt.Axes] = None,
    show: bool = True,
) -> plt.Axes:
    """
    Plot phase-space diagram (x vs dx/dt).
    
    Parameters
    ----------
    t : np.ndarray
        Time array
    x : np.ndarray
        Trajectory values
    title : str
        Plot title
    xlabel : str
        X-axis label
    ylabel : str
        Y-axis label
    linewidth : float
        Line width
    grid : bool
        Show grid
    ax : plt.Axes, optional
        Existing axes to plot on
    show : bool
        Whether to call plt.show()
        
    Returns
    -------
    ax : plt.Axes
        The axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
    
    # Compute derivative (dx/dt) using finite differences
    dt = t[1] - t[0] if len(t) > 1 else 1.0
    dxdt = np.gradient(x, dt)
    
    # Plot trajectory in phase space
    ax.plot(x, dxdt, lw=linewidth, color='steelblue', alpha=0.7)
    
    # Mark initial and final points
    ax.scatter(x[0], dxdt[0], color='green', s=100, 
              marker='o', label='Start', zorder=100)
    ax.scatter(x[-1], dxdt[-1], color='red', s=100, 
              marker='s', label='End', zorder=100)
    
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(grid, alpha=0.3)
    ax.legend(loc='best', fontsize=10)
    ax.axhline(0, color='black', linewidth=0.5, linestyle='--', alpha=0.5)
    ax.axvline(0, color='black', linewidth=0.5, linestyle='--', alpha=0.5)
    
    if show:
        plt.tight_layout()
        plt.show()
    
    return ax


def create_comparison_plot(
    methods_data: dict,
    title: str = "Comparison of Integration Methods",
    figsize: Tuple[int, int] = (14, 5),
    show: bool = True,
) -> Tuple[plt.Figure, List[plt.Axes]]:
    """
    Create side-by-side comparison of different integration methods.
    
    Parameters
    ----------
    methods_data : dict
        Dictionary with method names as keys and (t, x) tuples as values
        Example: {"Euler-Maruyama": (t1, x1), "Milstein": (t2, x2)}
    title : str
        Overall figure title
    figsize : tuple
        Figure size
    show : bool
        Whether to call plt.show()
        
    Returns
    -------
    fig : plt.Figure
        The figure object
    axes : list of plt.Axes
        List of axes objects
    """
    num_methods = len(methods_data)
    fig, axes = plt.subplots(1, num_methods, figsize=figsize)
    
    if num_methods == 1:
        axes = [axes]
    
    for ax, (method_name, (t, x)) in zip(axes, methods_data.items()):
        ax.plot(t, x, lw=1.5, color='steelblue')
        ax.set_xlabel("Time (s)", fontsize=11)
        ax.set_ylabel("x(t)", fontsize=11)
        ax.set_title(method_name, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    if show:
        plt.tight_layout()
        plt.show()
    
    return fig, axes


def create_summary_plot(
    t: np.ndarray,
    trajectories: List[np.ndarray],
    final_values: np.ndarray,
    method_name: str = "Euler–Maruyama",
    figsize: Tuple[int, int] = (15, 10),
    show: bool = True,
) -> Tuple[plt.Figure, np.ndarray]:
    """
    Create a comprehensive 2x2 summary plot with:
    1. Multiple trajectories
    2. Single trajectory example
    3. Histogram of final values
    4. Phase space plot of one trajectory
    
    Parameters
    ----------
    t : np.ndarray
        Time array
    trajectories : list of np.ndarray
        List of trajectory arrays
    final_values : np.ndarray
        Array of final values
    method_name : str
        Name of integration method for titles
    figsize : tuple
        Figure size
    show : bool
        Whether to call plt.show()
        
    Returns
    -------
    fig : plt.Figure
        The figure object
    axes : np.ndarray
        2D array of axes objects
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    # 1. Multiple trajectories with statistics
    plot_multiple_trajectories(t, trajectories, 
                               title=f"{method_name}: Multiple Trajectories",
                               ax=axes[0, 0], show=False)
    
    # 2. Single trajectory example
    plot_trajectory(t, trajectories[0],
                   title=f"{method_name}: Single Trajectory Example",
                   ax=axes[0, 1], show=False)
    
    # 3. Histogram of final values
    plot_histogram(final_values,
                  title="Distribution of Final Values",
                  ax=axes[1, 0], show=False)
    
    # 4. Phase space plot
    plot_phase_space(t, trajectories[0],
                    title="Phase Space Diagram",
                    ax=axes[1, 1], show=False)
    
    fig.suptitle(f"SDE Integration Summary: {method_name}", 
                fontsize=16, fontweight='bold', y=0.995)
    
    if show:
        plt.tight_layout()
        plt.show()
    
    return fig, axes
