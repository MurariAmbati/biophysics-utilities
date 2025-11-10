"""
Command-line interface for the Stochastic Integrator Visualizer.

Usage examples:
    # Basic usage with default parameters
    python -m stochastic_integrator_visualizer
    
    # Custom drift and diffusion
    python -m stochastic_integrator_visualizer --drift 1.0 --diffusion 0.3 --steps 1000 --dt 0.01
    
    # Multiple trajectories
    python -m stochastic_integrator_visualizer --ensemble 100
    
    # Use Milstein method
    python -m stochastic_integrator_visualizer --method milstein
    
    # Reproducible results
    python -m stochastic_integrator_visualizer --seed 42
"""

import argparse
import sys
from typing import Callable
import numpy as np

from .core import (
    euler_maruyama,
    milstein,
    deterministic_solver,
    run_ensemble,
    make_constant_drift,
    make_linear_drift,
    make_constant_diffusion,
    make_linear_diffusion,
    make_constant_diffusion_derivative,
    make_linear_diffusion_derivative,
)
from .visualize import (
    plot_trajectory,
    plot_multiple_trajectories,
    plot_histogram,
    plot_phase_space,
    create_summary_plot,
)
from .constants import (
    DEFAULT_X0,
    DEFAULT_DT,
    DEFAULT_STEPS,
    DEFAULT_SEED,
    DEFAULT_DRIFT,
    DEFAULT_DIFFUSION,
    DEFAULT_NUM_TRAJECTORIES,
    AVAILABLE_METHODS,
    DEFAULT_METHOD,
)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Stochastic Integrator Visualizer - Simulate and visualize SDEs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --drift 1.0 --diffusion 0.3 --steps 500 --dt 0.01
  %(prog)s --ensemble 100 --seed 42
  %(prog)s --method milstein --drift-type linear
        """
    )
    
    # Simulation parameters
    sim_group = parser.add_argument_group('Simulation Parameters')
    sim_group.add_argument(
        '--x0', type=float, default=DEFAULT_X0,
        help=f'Initial condition (default: {DEFAULT_X0})'
    )
    sim_group.add_argument(
        '--dt', type=float, default=DEFAULT_DT,
        help=f'Time step (default: {DEFAULT_DT})'
    )
    sim_group.add_argument(
        '--steps', type=int, default=DEFAULT_STEPS,
        help=f'Number of steps (default: {DEFAULT_STEPS})'
    )
    sim_group.add_argument(
        '--seed', type=int, default=DEFAULT_SEED,
        help='Random seed for reproducibility (default: None/random)'
    )
    
    # SDE parameters
    sde_group = parser.add_argument_group('SDE Parameters')
    sde_group.add_argument(
        '--drift', type=float, default=DEFAULT_DRIFT,
        help=f'Drift coefficient a (default: {DEFAULT_DRIFT})'
    )
    sde_group.add_argument(
        '--diffusion', type=float, default=DEFAULT_DIFFUSION,
        help=f'Diffusion coefficient b (default: {DEFAULT_DIFFUSION})'
    )
    sde_group.add_argument(
        '--drift-type', choices=['constant', 'linear'], default='constant',
        help='Type of drift function: constant or linear (default: constant)'
    )
    sde_group.add_argument(
        '--diffusion-type', choices=['constant', 'linear'], default='constant',
        help='Type of diffusion function: constant or linear (default: constant)'
    )
    
    # Method selection
    method_group = parser.add_argument_group('Integration Method')
    method_group.add_argument(
        '--method', choices=AVAILABLE_METHODS, default=DEFAULT_METHOD,
        help=f'Integration method (default: {DEFAULT_METHOD})'
    )
    
    # Visualization options
    vis_group = parser.add_argument_group('Visualization Options')
    vis_group.add_argument(
        '--ensemble', type=int, default=None,
        help='Number of trajectories for ensemble simulation (default: single trajectory)'
    )
    vis_group.add_argument(
        '--plot-type', choices=['trajectory', 'histogram', 'phase', 'summary'], 
        default='trajectory',
        help='Type of plot to generate (default: trajectory)'
    )
    vis_group.add_argument(
        '--no-show', action='store_true',
        help='Do not display plot (save only)'
    )
    vis_group.add_argument(
        '--save', type=str, default=None,
        help='Save plot to file (e.g., output.png)'
    )
    
    return parser.parse_args()


def create_drift_function(drift_type: str, coefficient: float) -> Callable:
    """Create drift function based on type and coefficient."""
    if drift_type == 'constant':
        return make_constant_drift(coefficient)
    elif drift_type == 'linear':
        return make_linear_drift(coefficient)
    else:
        raise ValueError(f"Unknown drift type: {drift_type}")


def create_diffusion_function(diffusion_type: str, coefficient: float) -> Callable:
    """Create diffusion function based on type and coefficient."""
    if diffusion_type == 'constant':
        return make_constant_diffusion(coefficient)
    elif diffusion_type == 'linear':
        return make_linear_diffusion(coefficient)
    else:
        raise ValueError(f"Unknown diffusion type: {diffusion_type}")


def create_diffusion_derivative(diffusion_type: str, coefficient: float) -> Callable:
    """Create diffusion derivative based on type and coefficient."""
    if diffusion_type == 'constant':
        return make_constant_diffusion_derivative(coefficient)
    elif diffusion_type == 'linear':
        return make_linear_diffusion_derivative(coefficient)
    else:
        raise ValueError(f"Unknown diffusion type: {diffusion_type}")


def main():
    """Main entry point for CLI."""
    args = parse_args()
    
    # Print simulation parameters
    print("=" * 60)
    print("Stochastic Integrator Visualizer")
    print("=" * 60)
    print(f"Method: {args.method}")
    print(f"Drift: {args.drift_type} with coefficient {args.drift}")
    print(f"Diffusion: {args.diffusion_type} with coefficient {args.diffusion}")
    print(f"Initial condition: x0 = {args.x0}")
    print(f"Time step: dt = {args.dt}")
    print(f"Number of steps: {args.steps}")
    print(f"Total time: T = {args.steps * args.dt:.2f}")
    print(f"Random seed: {args.seed if args.seed is not None else 'random'}")
    print("=" * 60)
    
    # Create drift and diffusion functions
    drift_func = create_drift_function(args.drift_type, args.drift)
    diffusion_func = create_diffusion_function(args.diffusion_type, args.diffusion)
    diffusion_deriv = create_diffusion_derivative(args.diffusion_type, args.diffusion)
    
    # Run simulation
    if args.ensemble is not None:
        # Ensemble simulation
        print(f"\nRunning ensemble simulation with {args.ensemble} trajectories...")
        t, trajectories, final_values = run_ensemble(
            method=args.method,
            a=drift_func,
            b=diffusion_func,
            x0=args.x0,
            dt=args.dt,
            steps=args.steps,
            num_trajectories=args.ensemble,
            base_seed=args.seed,
            b_prime=diffusion_deriv if args.method == 'milstein' else None,
        )
        
        print(f"Simulation complete!")
        print(f"Final value statistics:")
        print(f"  Mean: {np.mean(final_values):.4f}")
        print(f"  Std:  {np.std(final_values):.4f}")
        print(f"  Min:  {np.min(final_values):.4f}")
        print(f"  Max:  {np.max(final_values):.4f}")
        
        # Generate appropriate plot
        if args.plot_type == 'summary':
            fig, axes = create_summary_plot(
                t, trajectories, final_values,
                method_name=args.method.title(),
                show=not args.no_show
            )
        elif args.plot_type == 'histogram':
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 6))
            plot_histogram(final_values, ax=ax, show=not args.no_show)
        elif args.plot_type == 'phase':
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8, 8))
            plot_phase_space(t, trajectories[0], ax=ax, show=not args.no_show)
        else:  # trajectory
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 6))
            plot_multiple_trajectories(t, trajectories, ax=ax, show=not args.no_show)
        
        # Save if requested
        if args.save:
            fig.savefig(args.save, dpi=300, bbox_inches='tight')
            print(f"\nPlot saved to: {args.save}")
        
    else:
        # Single trajectory simulation
        print(f"\nRunning single trajectory simulation...")
        
        if args.method == 'euler-maruyama':
            t, x = euler_maruyama(
                a=drift_func,
                b=diffusion_func,
                x0=args.x0,
                dt=args.dt,
                steps=args.steps,
                seed=args.seed,
            )
        elif args.method == 'milstein':
            t, x = milstein(
                a=drift_func,
                b=diffusion_func,
                b_prime=diffusion_deriv,
                x0=args.x0,
                dt=args.dt,
                steps=args.steps,
                seed=args.seed,
            )
        elif args.method == 'deterministic':
            t, x = deterministic_solver(
                a=drift_func,
                x0=args.x0,
                dt=args.dt,
                steps=args.steps,
            )
        else:
            print(f"Error: Unknown method '{args.method}'", file=sys.stderr)
            sys.exit(1)
        
        print(f"Simulation complete!")
        print(f"Initial value: x(0) = {x[0]:.4f}")
        print(f"Final value: x(T) = {x[-1]:.4f}")
        print(f"Mean: {np.mean(x):.4f}")
        print(f"Std:  {np.std(x):.4f}")
        
        # Generate appropriate plot
        import matplotlib.pyplot as plt
        
        if args.plot_type == 'phase':
            fig, ax = plt.subplots(figsize=(8, 8))
            plot_phase_space(t, x, ax=ax, show=not args.no_show)
        else:  # trajectory (histogram and summary not applicable for single trajectory)
            fig, ax = plt.subplots(figsize=(10, 6))
            plot_trajectory(
                t, x,
                title=f"{args.method.title()} Integration of SDE",
                ax=ax,
                show=not args.no_show
            )
        
        # Save if requested
        if args.save:
            fig.savefig(args.save, dpi=300, bbox_inches='tight')
            print(f"\nPlot saved to: {args.save}")
    
    if not args.no_show:
        import matplotlib.pyplot as plt
        plt.show()


if __name__ == '__main__':
    main()
