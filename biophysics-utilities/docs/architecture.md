# Reaction Kinetics Playground - Architecture

## Overview

The Reaction Kinetics Playground is designed as a modular computational framework for constructing and simulating chemical reaction networks. The architecture follows a clean separation of concerns with distinct layers for parsing, modeling, computation, and visualization.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Python API  │  │   CLI Tool   │  │  Streamlit GUI   │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             │
┌─────────────────────────────────────────────────────────────┐
│                   High-Level API Layer                       │
│  ┌──────────────────┐  ┌───────────────────────────────┐   │
│  │ ReactionNetwork  │  │   SimulationSession           │   │
│  │  - Model Setup   │  │   - Batch Processing          │   │
│  │  - Simulation    │  │   - Parameter Sweeps          │   │
│  │  - Validation    │  │   - Sensitivity Analysis      │   │
│  └──────────────────┘  └───────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                             │
┌─────────────────────────────────────────────────────────────┐
│                      Core Engine Layer                       │
│  ┌───────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │  Parser   │  │  Kinetics    │  │   Integrator        │  │
│  │  - Text   │  │  - Symbolic  │  │   - ODE Solver      │  │
│  │  - YAML   │  │  - Rate Laws │  │   - Adaptive Steps  │  │
│  │  - JSON   │  │  - ODEs      │  │   - Event Detection │  │
│  └───────────┘  └──────────────┘  └─────────────────────┘  │
│                                                              │
│  ┌──────────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │    Model     │  │ Stoichiometry  │  │   Validator    │  │
│  │  - Species   │  │  - Matrix Ops  │  │   - Checks     │  │
│  │  - Reactions │  │  - Conservation│  │   - Warnings   │  │
│  └──────────────┘  └────────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             │
┌─────────────────────────────────────────────────────────────┐
│                    Utility & Support Layer                   │
│  ┌───────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │   Units   │  │  Math    │  │ Exporters│  │  Logging  │  │
│  │ Converter │  │ Helpers  │  │ SBML/LaTeX│ │  System   │  │
│  └───────────┘  └──────────┘  └──────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Parser Layer
- **ReactionParser**: Tokenizes reaction strings
- Supports multiple formats: simple text, YAML, JSON, custom .rkp
- Extracts: species, stoichiometry, rate constants, kinetic laws

### 2. Model Layer
- **Species**: Internal representation with properties
- **Reaction**: Stores stoichiometry and kinetic parameters
- **ReactionModel**: Container for complete network

### 3. Symbolic Computation
- **KineticSystem**: Generates symbolic ODEs using SymPy
- **KineticLaw**: Abstract class for rate laws
  - MassActionKinetics (default)
  - MichaelisMentenKinetics
  - HillKinetics
  - CustomKineticLaw

### 4. Numerical Integration
- **ODEIntegrator**: Wrapper for scipy.integrate.solve_ivp
- Supports multiple methods: RK45, LSODA, BDF, Radau
- Adaptive time-stepping
- Event detection for steady states

### 5. Analysis Tools
- **StoichiometricMatrix**: Network topology analysis
- Conservation law detection (nullspace computation)
- Mass balance validation
- Stability analysis (Jacobian eigenvalues)

### 6. Visualization
- **Plotter**: Matplotlib-based plotting
  - Time course plots
  - Phase space diagrams
  - Parameter sweep heatmaps
- **Dashboard**: Streamlit interactive GUI (optional)

## Data Flow

### Typical Simulation Pipeline

```
Text Input → Parser → ReactionModel → KineticSystem → ODEIntegrator → Results
    ↓                      ↓               ↓              ↓            ↓
  .yaml              Species List    Symbolic ODEs   Numerical     Visualization
  .json              Reactions       Rate Equations   Solution      Analysis
  string             Stoich Matrix   Lambdified func  TimeSeries    Export
```

### Key Design Decisions

1. **Stateless Components**: Core components don't maintain simulation state
2. **Composability**: Each module can be used independently
3. **Symbolic → Numerical**: Leverage SymPy for correctness, NumPy for speed
4. **Extensibility**: Easy to add custom kinetic laws and solvers

## Performance Considerations

- **SymPy**: Used for symbolic manipulation (one-time cost)
- **Lambdify**: Convert symbolic→numerical for fast evaluation
- **NumPy**: Vectorized operations throughout
- **SciPy**: Industrial-strength ODE solvers
- **Optional**: Numba/Cython backends for large networks

## Extension Points

Users can extend the framework through:

1. **Custom Kinetic Laws**: Subclass `KineticLaw`
2. **Custom Validation**: Extend `ReactionValidator`
3. **Custom Export Formats**: Add to `exporters.py`
4. **Integration with Other Tools**: SBML, Tellurium, COPASI

## Dependencies

### Core
- numpy: Numerical computations
- scipy: ODE integration
- sympy: Symbolic mathematics

### Visualization
- matplotlib: Plotting
- streamlit (optional): Interactive dashboard
- plotly (optional): Interactive plots

### Utilities
- pyyaml: YAML parsing
- pandas: Data handling
- click: CLI framework

### Export (Optional)
- python-libsbml: SBML export
