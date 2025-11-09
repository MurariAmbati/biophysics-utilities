# Solver Algorithms

## ODE Integration Methods

The Reaction Kinetics Playground uses SciPy's `solve_ivp` with multiple integration methods optimized for different types of problems.

## Available Methods

### 1. RK45 (Runge-Kutta 4(5))

**Best for**: Non-stiff problems, smooth dynamics

- Explicit Runge-Kutta method of order 5(4)
- Adaptive step sizing
- Low computational cost
- Not suitable for stiff systems

```python
result = network.simulate(..., method='RK45')
```

### 2. LSODA (Default)

**Best for**: Automatic stiffness detection

- Automatically switches between stiff and non-stiff solvers
- Most versatile choice
- Recommended as default

```python
result = network.simulate(..., method='LSODA')
```

### 3. BDF (Backward Differentiation Formula)

**Best for**: Stiff problems

- Implicit method
- Order 1-5 with automatic selection
- Excellent for stiff ODEs
- Higher computational cost per step

```python
result = network.simulate(..., method='BDF')
```

### 4. Radau

**Best for**: Stiff problems requiring high accuracy

- Implicit Runge-Kutta method
- Order 5
- A-stable and L-stable
- Good for very stiff systems

```python
result = network.simulate(..., method='Radau')
```

### 5. DOP853

**Best for**: High-precision non-stiff problems

- Explicit Runge-Kutta of order 8
- Very accurate for smooth problems
- Higher computational cost

```python
result = network.simulate(..., method='DOP853')
```

## Tolerance Settings

Control accuracy vs performance:

```python
result = network.simulate(
    ...,
    rtol=1e-6,  # Relative tolerance
    atol=1e-9   # Absolute tolerance
)
```

- **rtol**: Relative error tolerance (default: 1e-6)
- **atol**: Absolute error tolerance (default: 1e-9)
- Lower values = more accurate, slower
- Higher values = faster, less accurate

## Stiffness Detection

Check if your system is stiff:

```python
from kinetics_playground.core.integrator import check_stiffness

stiffness_info = check_stiffness(dydt, y0)

if stiffness_info['is_stiff']:
    print(f"Stiffness ratio: {stiffness_info['stiffness_ratio']}")
    print(f"Recommended: {stiffness_info['recommended_method']}")
```

Indicators of stiffness:
- Wide range of timescales
- Fast transients + slow dynamics
- Stiffness ratio > 1000

## Event Detection

Detect and respond to events during integration:

```python
def steady_state_event(t, y):
    """Stop when system reaches steady state."""
    dydt_val = compute_derivatives(t, y)
    return np.max(np.abs(dydt_val)) - 1e-6

steady_state_event.terminal = True

result = integrator.integrate(
    y0, t_span, events=[steady_state_event]
)
```

## Performance Tips

### 1. Choose the Right Method

- Non-stiff → RK45
- Stiff → BDF or Radau
- Unknown → LSODA (auto-detect)

### 2. Adjust Tolerances

- Start with defaults
- Tighten if results seem inaccurate
- Relax if speed is more important

### 3. Limit Time Points

```python
# Don't request too many points
result = network.simulate(
    ...,
    num_points=1000  # Usually sufficient
)
```

### 4. Use Dense Output Sparingly

```python
integrator = ODEIntegrator(
    ...,
    dense_output=False  # Disable if not needed
)
```

## Common Issues

### Solver Fails to Converge

Try:
1. Check for negative concentrations
2. Use BDF or Radau for stiff systems
3. Tighten tolerances
4. Check rate constants (not too large/small)

### Slow Integration

Try:
1. Relax tolerances slightly
2. Use RK45 for non-stiff problems
3. Reduce number of output points
4. Check for unnecessarily small time steps

### Oscillations or Instability

Try:
1. Use BDF or LSODA
2. Tighten tolerances
3. Check model validity
4. Verify initial conditions

## Algorithm Details

### Adaptive Step Sizing

All methods use adaptive step control:

```
h_new = h_old * (tol / error)^(1/order)
```

- Increases step size when error is small
- Decreases when error is large
- Ensures accuracy while maintaining efficiency

### Mass Matrix Support

For systems with conservation laws:

```python
# Future feature - not yet implemented
integrator = ODEIntegrator(
    ...,
    mass_matrix=M  # Conservation constraints
)
```

## References

- Hairer & Wanner: "Solving Ordinary Differential Equations"
- SciPy documentation: scipy.integrate.solve_ivp
- Ascher & Petzold: "Computer Methods for ODEs and DAEs"
