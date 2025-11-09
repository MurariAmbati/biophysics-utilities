# Visualization Guide

## Plotting Time Course Data

### Basic Time Course

```python
from kinetics_playground.visualization import plot_time_course

# Simple plot
plot_time_course(result)

# Select specific species
plot_time_course(result, species=['A', 'B'])

# Save to file
plot_time_course(result, filename='timecourse.png')
```

### Using Plotter Class

```python
from kinetics_playground.visualization import Plotter

plotter = Plotter(style='seaborn-v0_8-darkgrid')

# Time course plot
ax = plotter.plot_time_course(result, species=['A', 'B', 'C'])

# Customize
ax.set_yscale('log')
ax.set_title('My Reaction Network')

# Save
plotter.save('plot.png', dpi=300)
```

## Phase Space Plots

Visualize 2D trajectories:

```python
from kinetics_playground.visualization import plot_phase_space

# Basic phase plot
plot_phase_space(result, 'A', 'B')

# With direction arrows
plot_phase_space(
    result, 
    'A', 'B',
    show_direction=True
)
```

## Parameter Sweep Visualization

```python
import numpy as np
from kinetics_playground.visualization import Plotter

# Run parameter sweep
k_values = np.logspace(-2, 1, 20)
results = network.parameter_sweep(
    'k_0', k_values, initial_conditions
)

# Extract observable
final_C = [r.get_species('C')[-1] for r in results]

# Plot
plotter = Plotter()
plotter.plot_heatmap(
    k_values, 
    final_C,
    'Rate Constant',
    'Final [C]',
    log_scale=True
)
```

## Multiple Trajectories

Compare different simulations:

```python
plotter = Plotter()

# Multiple results from parameter sweep
plotter.plot_multiple_trajectories(
    results,
    species='C',
    labels=[f'k={k:.2f}' for k in k_values]
)
```

## Multi-Panel Layouts

### Comparison Layout

```python
from kinetics_playground.visualization.layout import create_comparison_layout

fig, axes = create_comparison_layout(n_comparisons=2)

# Plot on each axis pair
for (ax_time, ax_phase), result in zip(axes, results):
    plotter.plot_time_course(result, ax=ax_time)
    plotter.plot_phase_space(result, 'A', 'B', ax=ax_phase)

plt.tight_layout()
plt.show()
```

### Dashboard Layout

```python
from kinetics_playground.visualization.layout import create_dashboard_layout

fig, axes = create_dashboard_layout()

plotter.plot_time_course(result, ax=axes['time_course'])
plotter.plot_phase_space(result, 'A', 'B', ax=axes['phase_space'])
plotter.plot_steady_state(steady_states, species_names, ax=axes['steady_state'])
```

## Interactive Dashboard

Launch Streamlit dashboard:

```python
from kinetics_playground.visualization import Dashboard

# Note: Requires streamlit installation
dashboard = Dashboard()
dashboard.run(network, initial_state={'A': 1.0, 'B': 1.0})
```

Run from command line:

```bash
streamlit run your_script.py
```

## Customization Options

### Colors and Styles

```python
import matplotlib.pyplot as plt

# Set style
plt.style.use('ggplot')

# Custom colors
plotter.plot_time_course(
    result,
    color='red',
    linestyle='--',
    linewidth=3
)
```

### Subplot Grids

```python
from kinetics_playground.visualization.plotter import create_subplot_grid

fig, axes = create_subplot_grid(
    n_plots=6,
    n_cols=3,
    figsize=(15, 10)
)

# Plot each species
for ax, species in zip(axes, result.species_names):
    y = result.get_species(species)
    ax.plot(result.t, y)
    ax.set_title(species)
    ax.set_xlabel('Time')
    ax.set_ylabel('Concentration')
```

## Export Options

### Save Figures

```python
# PNG (raster)
plotter.save('figure.png', dpi=300)

# PDF (vector)
plotter.save('figure.pdf')

# SVG (vector)
plotter.save('figure.svg')
```

### Animation (Advanced)

```python
import matplotlib.animation as animation

fig, ax = plt.subplots()

def animate(i):
    ax.clear()
    ax.plot(result.t[:i], result.y[0, :i])
    ax.set_xlim(0, result.t[-1])
    ax.set_ylim(0, result.y[0, :].max())

anim = animation.FuncAnimation(
    fig, animate, frames=len(result.t), interval=50
)
anim.save('animation.gif')
```

## Tips and Best Practices

### 1. Plot Readability

- Use clear labels and titles
- Include units in axis labels
- Choose appropriate scales (linear vs log)
- Limit number of series per plot (≤7)

### 2. Color Schemes

```python
# Use color cycles for multiple species
from matplotlib import cm
colors = cm.viridis(np.linspace(0, 1, n_species))

for i, species in enumerate(species_names):
    plt.plot(t, y[i], color=colors[i])
```

### 3. Publication Quality

```python
# Set matplotlib rc parameters
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.linewidth': 1.5,
    'xtick.major.width': 1.5,
    'ytick.major.width': 1.5,
    'figure.dpi': 300
})
```

### 4. Interactive Exploration

Use Jupyter widgets for interactive parameter exploration:

```python
from ipywidgets import interact, FloatSlider

@interact(k=FloatSlider(min=0.01, max=10, step=0.1, value=1.0))
def plot_with_k(k):
    network.model.reactions[0].rate_constant = k
    result = network.simulate(ic, time_span=(0, 100))
    plot_time_course(result)
```

## Example Gallery

See `examples/notebook_demo.ipynb` for:
- Time course plots with multiple species
- Phase space trajectories
- Parameter sweep heatmaps
- Comparison plots
- Animation examples
- Interactive widgets
