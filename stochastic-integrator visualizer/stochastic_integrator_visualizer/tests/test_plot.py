"""
Tests for visualization functions.

Tests:
- Plot creation without errors
- Correct handling of matplotlib figures
- Proper axes configuration
"""

import pytest
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt

from stochastic_integrator_visualizer.visualize import (
    plot_trajectory,
    plot_multiple_trajectories,
    plot_histogram,
    plot_phase_space,
    create_comparison_plot,
    create_summary_plot,
)
from stochastic_integrator_visualizer.core import (
    euler_maruyama,
    make_constant_drift,
    make_constant_diffusion,
    run_ensemble,
)


@pytest.fixture
def sample_trajectory():
    """Generate a sample trajectory for testing."""
    drift = make_constant_drift(1.0)
    diffusion = make_constant_diffusion(0.3)
    t, x = euler_maruyama(drift, diffusion, x0=0.0, dt=0.01, steps=100, seed=42)
    return t, x


@pytest.fixture
def sample_ensemble():
    """Generate sample ensemble for testing."""
    drift = make_constant_drift(1.0)
    diffusion = make_constant_diffusion(0.3)
    t, trajectories, final_values = run_ensemble(
        method="euler-maruyama",
        a=drift,
        b=diffusion,
        x0=0.0,
        dt=0.01,
        steps=100,
        num_trajectories=20,
        base_seed=42
    )
    return t, trajectories, final_values


class TestPlotTrajectory:
    """Tests for single trajectory plotting."""
    
    def test_basic_plot(self, sample_trajectory):
        """Test that plot_trajectory creates a figure without errors."""
        t, x = sample_trajectory
        fig, ax = plt.subplots()
        ax_result = plot_trajectory(t, x, ax=ax, show=False)
        
        assert ax_result is not None
        assert len(ax.lines) == 1
        plt.close(fig)
    
    def test_plot_with_custom_labels(self, sample_trajectory):
        """Test plot with custom labels."""
        t, x = sample_trajectory
        fig, ax = plt.subplots()
        plot_trajectory(
            t, x,
            title="Custom Title",
            xlabel="Custom X",
            ylabel="Custom Y",
            ax=ax,
            show=False
        )
        
        assert ax.get_title() == "Custom Title"
        assert ax.get_xlabel() == "Custom X"
        assert ax.get_ylabel() == "Custom Y"
        plt.close(fig)
    
    def test_grid_option(self, sample_trajectory):
        """Test grid option."""
        t, x = sample_trajectory
        fig, ax = plt.subplots()
        plot_trajectory(t, x, grid=True, ax=ax, show=False)
        assert ax.xaxis._major_tick_kw['gridOn'] or ax.yaxis._major_tick_kw['gridOn']
        plt.close(fig)


class TestPlotMultipleTrajectories:
    """Tests for multiple trajectory plotting."""
    
    def test_basic_ensemble_plot(self, sample_ensemble):
        """Test plotting multiple trajectories."""
        t, trajectories, _ = sample_ensemble
        fig, ax = plt.subplots()
        ax_result = plot_multiple_trajectories(t, trajectories, ax=ax, show=False)
        
        assert ax_result is not None
        # Should have one line per trajectory
        assert len(ax.lines) >= len(trajectories)
        plt.close(fig)
    
    def test_ensemble_with_statistics(self, sample_ensemble):
        """Test ensemble plot with mean and std."""
        t, trajectories, _ = sample_ensemble
        fig, ax = plt.subplots()
        plot_multiple_trajectories(
            t, trajectories,
            show_mean=True,
            show_std=True,
            ax=ax,
            show=False
        )
        
        # Should have trajectories + mean line
        assert len(ax.lines) >= len(trajectories) + 1
        # Should have filled area for std
        assert len(ax.collections) >= 1
        plt.close(fig)
    
    def test_ensemble_without_statistics(self, sample_ensemble):
        """Test ensemble plot without statistics."""
        t, trajectories, _ = sample_ensemble
        fig, ax = plt.subplots()
        plot_multiple_trajectories(
            t, trajectories,
            show_mean=False,
            show_std=False,
            ax=ax,
            show=False
        )
        
        # Should only have trajectory lines
        assert len(ax.lines) == len(trajectories)
        plt.close(fig)


class TestPlotHistogram:
    """Tests for histogram plotting."""
    
    def test_basic_histogram(self, sample_ensemble):
        """Test basic histogram plotting."""
        _, _, final_values = sample_ensemble
        fig, ax = plt.subplots()
        ax_result = plot_histogram(final_values, ax=ax, show=False)
        
        assert ax_result is not None
        # Should have histogram patches
        assert len(ax.patches) > 0
        plt.close(fig)
    
    def test_histogram_with_stats(self, sample_ensemble):
        """Test histogram with statistics overlay."""
        _, _, final_values = sample_ensemble
        fig, ax = plt.subplots()
        plot_histogram(final_values, show_stats=True, ax=ax, show=False)
        
        # Should have mean line
        assert len(ax.lines) >= 1
        # Should have std span
        assert len(ax.collections) >= 1
        plt.close(fig)
    
    def test_histogram_bins(self, sample_ensemble):
        """Test histogram with custom number of bins."""
        _, _, final_values = sample_ensemble
        fig, ax = plt.subplots()
        plot_histogram(final_values, bins=20, ax=ax, show=False)
        
        # Number of patches should be close to number of bins
        # (may vary slightly based on data range)
        assert 15 <= len(ax.patches) <= 25
        plt.close(fig)


class TestPlotPhaseSpace:
    """Tests for phase space plotting."""
    
    def test_basic_phase_plot(self, sample_trajectory):
        """Test basic phase space plotting."""
        t, x = sample_trajectory
        fig, ax = plt.subplots()
        ax_result = plot_phase_space(t, x, ax=ax, show=False)
        
        assert ax_result is not None
        # Should have trajectory line
        assert len(ax.lines) >= 1
        # Should have start and end markers
        scatter_collections = [c for c in ax.collections if hasattr(c, 'get_offsets')]
        assert len(scatter_collections) >= 2
        plt.close(fig)
    
    def test_phase_space_markers(self, sample_trajectory):
        """Test that phase space has start and end markers."""
        t, x = sample_trajectory
        fig, ax = plt.subplots()
        plot_phase_space(t, x, ax=ax, show=False)
        
        # Check that legend exists (start/end points)
        assert ax.get_legend() is not None
        plt.close(fig)


class TestCreateComparisonPlot:
    """Tests for comparison plotting."""
    
    def test_comparison_plot(self):
        """Test comparison of multiple methods."""
        drift = make_constant_drift(1.0)
        diffusion = make_constant_diffusion(0.3)
        
        t1, x1 = euler_maruyama(drift, diffusion, x0=0.0, dt=0.01, steps=100, seed=42)
        t2, x2 = euler_maruyama(drift, diffusion, x0=0.0, dt=0.01, steps=100, seed=43)
        
        methods_data = {
            "Method 1": (t1, x1),
            "Method 2": (t2, x2),
        }
        
        fig, axes = create_comparison_plot(methods_data, show=False)
        
        assert fig is not None
        assert len(axes) == 2
        assert axes[0].get_title() == "Method 1"
        assert axes[1].get_title() == "Method 2"
        plt.close(fig)


class TestCreateSummaryPlot:
    """Tests for summary plotting."""
    
    def test_summary_plot(self, sample_ensemble):
        """Test comprehensive summary plot."""
        t, trajectories, final_values = sample_ensemble
        
        fig, axes = create_summary_plot(
            t, trajectories, final_values,
            method_name="Test Method",
            show=False
        )
        
        assert fig is not None
        assert axes.shape == (2, 2)
        
        # Check that all subplots have content
        for i in range(2):
            for j in range(2):
                assert len(axes[i, j].lines) > 0 or len(axes[i, j].patches) > 0
        
        plt.close(fig)
    
    def test_summary_plot_titles(self, sample_ensemble):
        """Test that summary plot has appropriate titles."""
        t, trajectories, final_values = sample_ensemble
        
        fig, axes = create_summary_plot(
            t, trajectories, final_values,
            method_name="Euler-Maruyama",
            show=False
        )
        
        # Check that titles contain method name or descriptive text
        titles = [axes[i, j].get_title() for i in range(2) for j in range(2)]
        assert any("Euler-Maruyama" in title or "Multiple" in title for title in titles)
        assert any("Distribution" in title or "Histogram" in title for title in titles)
        assert any("Phase" in title for title in titles)
        
        plt.close(fig)


class TestPlotProperties:
    """Tests for general plot properties."""
    
    def test_figure_size(self, sample_trajectory):
        """Test that figures can be created with custom sizes."""
        t, x = sample_trajectory
        fig, ax = plt.subplots(figsize=(8, 6))
        plot_trajectory(t, x, ax=ax, show=False)
        
        # Check approximate size (in inches)
        size = fig.get_size_inches()
        assert abs(size[0] - 8) < 0.1
        assert abs(size[1] - 6) < 0.1
        plt.close(fig)
    
    def test_no_show_option(self, sample_trajectory):
        """Test that show=False prevents display."""
        t, x = sample_trajectory
        # This should not raise any errors or block
        fig, ax = plt.subplots()
        plot_trajectory(t, x, ax=ax, show=False)
        plt.close(fig)
