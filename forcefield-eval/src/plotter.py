"""
Plotting utilities for visualizing potential energy and force curves.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Optional


def plot_potentials(
    results: List[Dict],
    save_path: Optional[str] = None,
    show_forces: bool = False,
    figsize: tuple = (10, 6)
):
    """
    Plot potential energy curves for multiple potentials.
    
    Parameters
    ----------
    results : list of dict
        List of evaluation results from ForceFieldEvaluator
    save_path : str, optional
        Path to save the figure
    show_forces : bool, optional
        If True, also plot force curves in a second panel
    figsize : tuple, optional
        Figure size (width, height) in inches
    """
    if show_forces:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)
    else:
        fig, ax1 = plt.subplots(1, 1, figsize=figsize)
    
    # Define colors for different potentials
    colors = {
        'LJ': '#1f77b4',
        'Morse': '#ff7f0e',
        'Coulomb': '#2ca02c',
    }
    
    # Plot potential energy curves
    for result in results:
        pot_name = result['potential']
        color = colors.get(pot_name, 'black')
        
        ax1.plot(
            result['r'],
            result['U'],
            label=f"{pot_name} (r$_{{eq}}$={result['r_eq']:.3f} nm)",
            color=color,
            linewidth=2
        )
        
        # Mark equilibrium point
        ax1.plot(
            result['r_eq'],
            result['U_min'],
            'o',
            color=color,
            markersize=8,
            markeredgecolor='black',
            markeredgewidth=1
        )
    
    ax1.set_ylabel('Potential Energy [eV]', fontsize=12)
    ax1.set_title('Potential Energy Curves', fontsize=14, fontweight='bold')
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='k', linestyle='--', linewidth=0.8, alpha=0.5)
    
    # Set reasonable y-limits
    all_U = np.concatenate([r['U'] for r in results])
    U_finite = all_U[np.isfinite(all_U)]
    if len(U_finite) > 0:
        y_min = np.percentile(U_finite, 5)
        y_max = np.percentile(U_finite, 95)
        margin = (y_max - y_min) * 0.1
        ax1.set_ylim(y_min - margin, y_max + margin)
    
    # Plot force curves if requested
    if show_forces:
        for result in results:
            pot_name = result['potential']
            color = colors.get(pot_name, 'black')
            
            ax2.plot(
                result['r'],
                result['F'],
                label=pot_name,
                color=color,
                linewidth=2
            )
        
        ax2.set_xlabel('Distance r [nm]', fontsize=12)
        ax2.set_ylabel('Force [eV/nm]', fontsize=12)
        ax2.set_title('Force Curves (F = -dU/dr)', fontsize=14, fontweight='bold')
        ax2.legend(loc='best', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='k', linestyle='--', linewidth=0.8, alpha=0.5)
        
        # Set reasonable y-limits
        all_F = np.concatenate([r['F'] for r in results])
        F_finite = all_F[np.isfinite(all_F)]
        if len(F_finite) > 0:
            y_min = np.percentile(F_finite, 5)
            y_max = np.percentile(F_finite, 95)
            margin = (y_max - y_min) * 0.1
            ax2.set_ylim(y_min - margin, y_max + margin)
    else:
        ax1.set_xlabel('Distance r [nm]', fontsize=12)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()


def plot_forces(
    results: List[Dict],
    save_path: Optional[str] = None,
    figsize: tuple = (10, 5)
):
    """
    Plot force curves for multiple potentials.
    
    Parameters
    ----------
    results : list of dict
        List of evaluation results from ForceFieldEvaluator
    save_path : str, optional
        Path to save the figure
    figsize : tuple, optional
        Figure size (width, height) in inches
    """
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    
    colors = {
        'LJ': '#1f77b4',
        'Morse': '#ff7f0e',
        'Coulomb': '#2ca02c',
    }
    
    for result in results:
        pot_name = result['potential']
        color = colors.get(pot_name, 'black')
        
        ax.plot(
            result['r'],
            result['F'],
            label=pot_name,
            color=color,
            linewidth=2
        )
        
        # Mark equilibrium point (F=0)
        ax.plot(
            result['r_eq'],
            0,
            'o',
            color=color,
            markersize=8,
            markeredgecolor='black',
            markeredgewidth=1
        )
    
    ax.set_xlabel('Distance r [nm]', fontsize=12)
    ax.set_ylabel('Force [eV/nm]', fontsize=12)
    ax.set_title('Force Curves (F = -dU/dr)', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linestyle='--', linewidth=0.8, alpha=0.5)
    
    # Set reasonable y-limits
    all_F = np.concatenate([r['F'] for r in results])
    F_finite = all_F[np.isfinite(all_F)]
    if len(F_finite) > 0:
        y_min = np.percentile(F_finite, 5)
        y_max = np.percentile(F_finite, 95)
        margin = (y_max - y_min) * 0.1
        ax.set_ylim(y_min - margin, y_max + margin)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()


def plot_comparison(
    results: List[Dict],
    save_path: Optional[str] = None,
    figsize: tuple = (12, 8)
):
    """
    Create a comprehensive comparison plot with energy, force, and details.
    
    Parameters
    ----------
    results : list of dict
        List of evaluation results from ForceFieldEvaluator
    save_path : str, optional
        Path to save the figure
    figsize : tuple, optional
        Figure size (width, height) in inches
    """
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    ax1 = fig.add_subplot(gs[0, :])  # Energy curve (top, full width)
    ax2 = fig.add_subplot(gs[1, 0])  # Force curve (bottom left)
    ax3 = fig.add_subplot(gs[1, 1])  # Equilibrium comparison (bottom right)
    
    colors = {
        'LJ': '#1f77b4',
        'Morse': '#ff7f0e',
        'Coulomb': '#2ca02c',
    }
    
    # Plot 1: Energy curves
    for result in results:
        pot_name = result['potential']
        color = colors.get(pot_name, 'black')
        
        ax1.plot(
            result['r'],
            result['U'],
            label=pot_name,
            color=color,
            linewidth=2
        )
        ax1.plot(
            result['r_eq'],
            result['U_min'],
            'o',
            color=color,
            markersize=8,
            markeredgecolor='black',
            markeredgewidth=1
        )
    
    ax1.set_xlabel('Distance r [nm]', fontsize=11)
    ax1.set_ylabel('Potential Energy [eV]', fontsize=11)
    ax1.set_title('Potential Energy Curves', fontsize=13, fontweight='bold')
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='k', linestyle='--', linewidth=0.8, alpha=0.5)
    
    # Plot 2: Force curves
    for result in results:
        pot_name = result['potential']
        color = colors.get(pot_name, 'black')
        
        ax2.plot(
            result['r'],
            result['F'],
            label=pot_name,
            color=color,
            linewidth=2
        )
        ax2.plot(
            result['r_eq'],
            0,
            'o',
            color=color,
            markersize=8,
            markeredgecolor='black',
            markeredgewidth=1
        )
    
    ax2.set_xlabel('Distance r [nm]', fontsize=11)
    ax2.set_ylabel('Force [eV/nm]', fontsize=11)
    ax2.set_title('Force Curves', fontsize=13, fontweight='bold')
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='k', linestyle='--', linewidth=0.8, alpha=0.5)
    
    # Plot 3: Equilibrium comparison (bar chart)
    pot_names = [r['potential'] for r in results]
    r_eqs = [r['r_eq'] for r in results]
    U_mins = [r['U_min'] for r in results]
    
    x = np.arange(len(pot_names))
    width = 0.35
    
    ax3_twin = ax3.twinx()
    
    bars1 = ax3.bar(x - width/2, r_eqs, width, label='r$_{eq}$ [nm]',
                    color=[colors.get(p, 'gray') for p in pot_names], alpha=0.7)
    bars2 = ax3_twin.bar(x + width/2, U_mins, width, label='U$_{min}$ [eV]',
                         color=[colors.get(p, 'gray') for p in pot_names], alpha=0.4)
    
    ax3.set_xlabel('Potential', fontsize=11)
    ax3.set_ylabel('Equilibrium Distance r$_{eq}$ [nm]', fontsize=10)
    ax3_twin.set_ylabel('Minimum Energy U$_{min}$ [eV]', fontsize=10)
    ax3.set_title('Equilibrium Properties', fontsize=13, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(pot_names)
    ax3.legend(loc='upper left', fontsize=9)
    ax3_twin.legend(loc='upper right', fontsize=9)
    ax3.grid(True, alpha=0.3, axis='y')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Comparison plot saved to {save_path}")
    else:
        plt.show()
