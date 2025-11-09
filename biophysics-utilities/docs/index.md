# Reaction Kinetics Playground Documentation

Welcome to the Reaction Kinetics Playground documentation!

## Table of Contents

1. [Getting Started](#getting-started)
2. [Architecture](architecture.md)
3. [Usage Guide](usage.md)
4. [Parser Specification](parser_spec.md)
5. [Solver Algorithms](solver_algorithms.md)
6. [Visualization Guide](visualization_guide.md)

## Getting Started

The Reaction Kinetics Playground is a modular computational framework for constructing and simulating chemical reaction networks directly from text-based input.

### Installation

```bash
pip install -e .
```

### First Example

```python
from kinetics_playground.api import ReactionNetwork

# Define reactions
reactions = ["A + B -> C ; 0.1"]

# Create and simulate
network = ReactionNetwork(reactions)
result = network.simulate(
    initial_conditions={"A": 1.0, "B": 1.0, "C": 0.0},
    time_span=(0, 100)
)

# Visualize
network.plot(result)
```

## Features

- **Text-based Input**: Define reactions naturally
- **Symbolic Computation**: Automatic ODE generation
- **Multiple Kinetic Laws**: Mass action, Michaelis-Menten, Hill, custom
- **Robust Integration**: Adaptive methods with event detection
- **Rich Visualization**: Time courses, phase plots, parameter sweeps
- **Export Capabilities**: SBML, LaTeX, MATLAB
- **CLI & GUI**: Command-line tools and optional web interface

## Learn More

- [Architecture Overview](architecture.md) - System design and components
- [Usage Guide](usage.md) - Comprehensive usage examples
- [Parser Spec](parser_spec.md) - Reaction input format details
- [Solver Algorithms](solver_algorithms.md) - Integration methods
- [Visualization](visualization_guide.md) - Plotting and dashboards

## Examples

Check the `examples/` directory for:
- Preset models (enzyme kinetics, oscillators, pathways)
- Parameter sweep demonstrations  
- Jupyter notebooks
- Batch simulation scripts

## Support

- GitHub Issues: Report bugs and request features
- Documentation: This directory
- Examples: `examples/` directory
