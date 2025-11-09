"""
Plotting utilities for visualizing reaction kinetics.

Provides time-course plots, phase diagrams, parameter sweeps, and more.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from typing import List, Optional, Dict, Tuple, Union
from kinetics_playground.core.integrator import IntegrationResult


class Plotter:
    """
    Main plotting class for reaction kinetics visualization.
    
    Handles time-course plots, phase plots, heatmaps, and more.
    """
    
    def __init__(self, style: str = 'seaborn-v0_8-darkgrid'):
        """
        Initialize plotter with a matplotlib style.
        
        Args:
            style: Matplotlib style name
        """
        try:
            plt.style.use(style)
        except:
            pass  # Use default if style not available
        
        self.fig = None
        self.axes = None
    
    def plot_time_course(
        self,
        result: IntegrationResult,
        species: Optional[List[str]] = None,
        ax: Optional[plt.Axes] = None,
        **kwargs
    ) -> plt.Axes:
        """
        Plot species concentrations over time.
        
        Args:
            result: IntegrationResult from simulation
            species: List of species to plot (None = all)
            ax: Matplotlib axes to plot on (creates new if None)
            **kwargs: Additional arguments for plot customization
            
        Returns:
            Matplotlib axes object
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            self.fig = fig
            self.axes = ax
        
        # Select species to plot
        if species is None:
            species_to_plot = result.species_names
        else:
            species_to_plot = species
        
        # Plot each species
        for species_name in species_to_plot:
            if species_name in result.species_names:
                y = result.get_species(species_name)
                ax.plot(result.t, y, label=species_name, linewidth=2, **kwargs)
        
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Concentration', fontsize=12)
        ax.set_title('Species Concentrations vs Time', fontsize=14)
        ax.legend(loc='best', frameon=True)
        ax.grid(True, alpha=0.3)
        
        return ax
    
    def plot_phase_space(
        self,
        result: IntegrationResult,
        species_x: str,
        species_y: str,
        ax: Optional[plt.Axes] = None,
        show_direction: bool = True,
        **kwargs
    ) -> plt.Axes:
        """
        Plot phase space (2D trajectory) for two species.
        
        Args:
            result: IntegrationResult from simulation
            species_x: Species for x-axis
            species_y: Species for y-axis
            ax: Matplotlib axes
            show_direction: Whether to show trajectory direction with arrows
            **kwargs: Additional plot arguments
            
        Returns:
            Matplotlib axes object
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))
            self.fig = fig
            self.axes = ax
        
        x = result.get_species(species_x)
        y = result.get_species(species_y)
        
        # Plot trajectory
        ax.plot(x, y, linewidth=2, **kwargs)
        
        # Mark start and end
        ax.plot(x[0], y[0], 'go', markersize=10, label='Start', zorder=5)
        ax.plot(x[-1], y[-1], 'ro', markersize=10, label='End', zorder=5)
        
        # Add direction arrows
        if show_direction and len(x) > 10:
            n_arrows = 5
            indices = np.linspace(0, len(x)-2, n_arrows, dtype=int)
            for idx in indices:
                dx = x[idx+1] - x[idx]
                dy = y[idx+1] - y[idx]
                ax.arrow(x[idx], y[idx], dx*0.5, dy*0.5,
                        head_width=0.05*max(x.max()-x.min(), y.max()-y.min()),
                        head_length=0.03*max(x.max()-x.min(), y.max()-y.min()),
                        fc='black', ec='black', alpha=0.6, zorder=4)
        
        ax.set_xlabel(f'[{species_x}]', fontsize=12)
        ax.set_ylabel(f'[{species_y}]', fontsize=12)
        ax.set_title(f'Phase Space: {species_x} vs {species_y}', fontsize=14)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        return ax
    
    def plot_multiple_trajectories(
        self,
        results: List[IntegrationResult],
        species: str,
        labels: Optional[List[str]] = None,
        ax: Optional[plt.Axes] = None,
        **kwargs
    ) -> plt.Axes:
        """
        Plot multiple trajectories (e.g., from parameter sweep) for comparison.
        
        Args:
            results: List of IntegrationResult objects
            species: Species to plot
            labels: Labels for each trajectory
            ax: Matplotlib axes
            **kwargs: Additional plot arguments
            
        Returns:
            Matplotlib axes object
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            self.fig = fig
            self.axes = ax
        
        if labels is None:
            labels = [f'Run {i+1}' for i in range(len(results))]
        
        # Use color map for multiple lines
        colors = plt.cm.viridis(np.linspace(0, 1, len(results)))
        
        for result, label, color in zip(results, labels, colors):
            y = result.get_species(species)
            ax.plot(result.t, y, label=label, color=color, linewidth=2, **kwargs)
        
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel(f'[{species}]', fontsize=12)
        ax.set_title(f'{species} - Multiple Trajectories', fontsize=14)
        ax.legend(loc='best', frameon=True)
        ax.grid(True, alpha=0.3)
        
        return ax
    
    def plot_heatmap(
        self,
        parameter_values: np.ndarray,
        observable_values: np.ndarray,
        parameter_name: str,
        observable_name: str,
        ax: Optional[plt.Axes] = None,
        log_scale: bool = False,
        **kwargs
    ) -> plt.Axes:
        """
        Plot heatmap for parameter sweep results.
        
        Args:
            parameter_values: Array of parameter values
            observable_values: Array of observable values
            parameter_name: Name of parameter
            observable_name: Name of observable
            ax: Matplotlib axes
            log_scale: Use log scale for parameter axis
            **kwargs: Additional arguments for imshow
            
        Returns:
            Matplotlib axes object
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            self.fig = fig
            self.axes = ax
        
        im = ax.plot(parameter_values, observable_values, 'o-', linewidth=2, markersize=8)
        
        if log_scale:
            ax.set_xscale('log')
        
        ax.set_xlabel(parameter_name, fontsize=12)
        ax.set_ylabel(observable_name, fontsize=12)
        ax.set_title(f'{observable_name} vs {parameter_name}', fontsize=14)
        ax.grid(True, alpha=0.3)
        
        return ax
    
    def plot_steady_state(
        self,
        steady_states: List[np.ndarray],
        species_names: List[str],
        ax: Optional[plt.Axes] = None
    ) -> plt.Axes:
        """
        Plot steady state concentrations as bar chart.
        
        Args:
            steady_states: List of steady state vectors
            species_names: Names of species
            ax: Matplotlib axes
            
        Returns:
            Matplotlib axes object
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            self.fig = fig
            self.axes = ax
        
        x = np.arange(len(species_names))
        width = 0.8 / len(steady_states)
        
        for idx, ss in enumerate(steady_states):
            offset = (idx - len(steady_states)/2) * width
            ax.bar(x + offset, ss, width, label=f'SS {idx+1}', alpha=0.8)
        
        ax.set_xlabel('Species', fontsize=12)
        ax.set_ylabel('Concentration', fontsize=12)
        ax.set_title('Steady State Concentrations', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(species_names)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        return ax
    
    def save(self, filename: str, dpi: int = 300, **kwargs):
        """
        Save the current figure.
        
        Args:
            filename: Output filename
            dpi: Resolution in dots per inch
            **kwargs: Additional arguments for savefig
        """
        if self.fig is not None:
            self.fig.savefig(filename, dpi=dpi, bbox_inches='tight', **kwargs)
    
    def show(self):
        """Display the current figure."""
        plt.show()


# Convenience functions
def plot_time_course(
    result: IntegrationResult,
    species: Optional[List[str]] = None,
    filename: Optional[str] = None,
    **kwargs
) -> plt.Axes:
    """
    Quick time-course plot.
    
    Args:
        result: Integration result
        species: Species to plot (None = all)
        filename: Optional filename to save plot
        **kwargs: Additional plot arguments
        
    Returns:
        Matplotlib axes
    """
    plotter = Plotter()
    ax = plotter.plot_time_course(result, species, **kwargs)
    
    if filename:
        plotter.save(filename)
    
    return ax


def plot_phase_space(
    result: IntegrationResult,
    species_x: str,
    species_y: str,
    filename: Optional[str] = None,
    **kwargs
) -> plt.Axes:
    """
    Quick phase space plot.
    
    Args:
        result: Integration result
        species_x: X-axis species
        species_y: Y-axis species
        filename: Optional filename to save plot
        **kwargs: Additional plot arguments
        
    Returns:
        Matplotlib axes
    """
    plotter = Plotter()
    ax = plotter.plot_phase_space(result, species_x, species_y, **kwargs)
    
    if filename:
        plotter.save(filename)
    
    return ax


def create_subplot_grid(
    n_plots: int,
    n_cols: int = 3,
    figsize: Optional[Tuple[int, int]] = None
) -> Tuple[plt.Figure, np.ndarray]:
    """
    Create a grid of subplots.
    
    Args:
        n_plots: Number of plots needed
        n_cols: Number of columns
        figsize: Figure size tuple
        
    Returns:
        (figure, axes_array) tuple
    """
    n_rows = int(np.ceil(n_plots / n_cols))
    
    if figsize is None:
        figsize = (5 * n_cols, 4 * n_rows)
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    axes = np.atleast_1d(axes).flatten()
    
    # Hide unused subplots
    for idx in range(n_plots, len(axes)):
        axes[idx].set_visible(False)
    
    return fig, axes
