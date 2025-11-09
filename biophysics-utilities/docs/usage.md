# Usage Guide

## Installation

```bash
# Basic installation
pip install -e .

# With all optional dependencies
pip install -e ".[all]"

# Development installation
pip install -e ".[dev]"
```

## Quick Start

### 1. Simple Reaction Network

```python
from kinetics_playground.api import ReactionNetwork

# Define reactions
reactions = [
    "A + B -> C ; 0.1",
    "C -> A + B ; 0.05"
]

# Create network
network = ReactionNetwork(reactions)

# Set initial conditions and simulate
result = network.simulate(
    initial_conditions={"A": 1.0, "B": 1.0, "C": 0.0},
    time_span=(0, 100),
    num_points=1000
)

# Plot results
network.plot(result)
```

### 2. Using Presets

```python
from kinetics_playground.api import load_preset, list_presets

# List available presets
print(list_presets())

# Load enzyme kinetics preset
network = load_preset('enzyme_kinetics')

# Simulate
result = network.simulate(
    initial_conditions={"E": 1.0, "S": 10.0, "ES": 0.0, "P": 0.0},
    time_span=(0, 50)
)
```

### 3. Parameter Sweeps

```python
import numpy as np

# Sweep rate constant
k_values = np.logspace(-2, 1, 20)
results = network.parameter_sweep(
    parameter="k_0",
    values=k_values,
    initial_conditions={"A": 1.0, "B": 1.0, "C": 0.0}
)

# Analyze results
for k, result in zip(k_values, results):
    final_C = result.get_species('C')[-1]
    print(f"k = {k:.3f}, final [C] = {final_C:.3f}")
```

### 4. Custom Kinetic Laws

```python
from kinetics_playground.core.kinetics import MichaelisMentenKinetics

# Create MM kinetics
mm_law = MichaelisMentenKinetics(
    vmax=1.0,
    km=0.5,
    substrate='S',
    enzyme='E'
)

# Apply to specific reaction
network.set_kinetic_law(reaction_index=0, kinetic_law=mm_law)
```

## Command Line Interface

### Parse Reactions

```bash
# Parse single reaction
kinetics parse "A + B -> C ; 0.1"

# Parse from file
kinetics parse -f reactions.yaml
```

### Run Simulations

```bash
# Simulate from file
kinetics simulate -i reactions.yaml -c A=1.0 -c B=1.0 -t 100 -o results.csv

# With plotting
kinetics simulate -i reactions.yaml -c A=1.0 -c B=1.0 --plot
```

### Use Presets

```bash
# List presets
kinetics presets

# Run preset
kinetics preset enzyme_kinetics -i E=1.0 -i S=10.0 -i ES=0.0 -i P=0.0 -t 50
```

### Visualize Results

```bash
# Plot time course
kinetics visualize results.csv

# Phase space plot
kinetics visualize results.csv --phase A B -o phase_plot.png
```

## Advanced Features

### Validation

```python
# Validate model
issues = network.validate()

# Raise exception on errors
network.validate(raise_on_error=True)
```

### Export

```python
# Export to SBML
network.export('model.xml', format='sbml')

# Export to LaTeX
network.export('model.tex', format='latex')

# Export to MATLAB
network.export('model.m', format='matlab')
```

### Simulation Sessions

```python
from kinetics_playground.api import SimulationSession

# Create session
session = SimulationSession(network, name="my_analysis")

# Run multiple simulations
for ic in initial_condition_list:
    session.add_simulation(ic, metadata={'condition': 'test'})

# Export all results
session.export_all('output_dir/')
```

### Steady State Analysis

```python
# Find steady states
result = integrator.integrate_to_steady_state(
    y0=initial_state,
    max_time=1e6,
    steady_state_tol=1e-6
)

# Analyze stability
from kinetics_playground.utils.math_helpers import analyze_stability

stability = analyze_stability(dydt, result.y[:, -1])
print(f"Stability: {stability['stability']}")
print(f"Eigenvalues: {stability['eigenvalues']}")
```

### Stiffness Detection

```python
from kinetics_playground.core.integrator import check_stiffness

# Check if system is stiff
stiffness_info = check_stiffness(dydt, y0)

if stiffness_info['is_stiff']:
    print(f"System is stiff! Recommended method: {stiffness_info['recommended_method']}")
    network.simulate(..., method='BDF')
```

## Tips and Best Practices

1. **Validation**: Always validate models before long simulations
2. **Method Selection**: Use LSODA (default) for automatic stiffness detection
3. **Tolerances**: Adjust rtol/atol for accuracy vs speed tradeoff
4. **Large Networks**: Consider Numba backend for performance
5. **Debugging**: Use verbose logging for troubleshooting

## Example Workflows

See `examples/` directory for:
- `simple_mass_action.yaml`: Basic reversible reaction
- `enzyme_kinetics.json`: Michaelis-Menten kinetics
- `oscillating_reaction.rkp`: Brusselator oscillator
- `parameter_sweep_demo.py`: Parameter exploration
- `notebook_demo.ipynb`: Interactive tutorial
