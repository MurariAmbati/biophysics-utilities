"""
Layout utilities for creating multi-panel figures.
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import Tuple, List, Optional


def create_comparison_layout(n_comparisons: int = 2) -> Tuple[plt.Figure, List[plt.Axes]]:
    """
    Create layout for comparing multiple simulations.
    
    Args:
        n_comparisons: Number of simulations to compare
        
    Returns:
        (figure, list of axes)
    """
    fig = plt.figure(figsize=(14, 5 * n_comparisons))
    gs = gridspec.GridSpec(n_comparisons, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    axes = []
    for i in range(n_comparisons):
        ax_time = fig.add_subplot(gs[i, 0])
        ax_phase = fig.add_subplot(gs[i, 1])
        axes.append((ax_time, ax_phase))
    
    return fig, axes


def create_dashboard_layout() -> Tuple[plt.Figure, dict]:
    """
    Create comprehensive dashboard layout.
    
    Returns:
        (figure, dict of named axes)
    """
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    axes = {
        'time_course': fig.add_subplot(gs[0:2, 0:2]),  # Large top-left
        'phase_space': fig.add_subplot(gs[0:2, 2]),    # Top-right
        'steady_state': fig.add_subplot(gs[2, 0]),     # Bottom-left
        'sensitivity': fig.add_subplot(gs[2, 1]),      # Bottom-middle
        'rates': fig.add_subplot(gs[2, 2])             # Bottom-right
    }
    
    return fig, axes


def create_parameter_sweep_layout(n_params: int) -> Tuple[plt.Figure, List[plt.Axes]]:
    """
    Create layout for parameter sweep visualization.
    
    Args:
        n_params: Number of parameters swept
        
    Returns:
        (figure, list of axes)
    """
    n_cols = min(3, n_params)
    n_rows = (n_params + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(6*n_cols, 5*n_rows))
    axes = axes.flatten() if n_params > 1 else [axes]
    
    # Hide unused axes
    for ax in axes[n_params:]:
        ax.set_visible(False)
    
    return fig, axes[:n_params]
