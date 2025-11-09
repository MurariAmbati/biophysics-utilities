# Quick Start Guide

## Installation

```bash
cd /Users/murari/biophysics-utilities/diffusion-time-estimator
pip install -e .
```

## Basic Usage

### Command Line

**Simple calculation:**
```bash
diffusion-time --radius 1e-9
```

**Full specification:**
```bash
diffusion-time --radius 1e-9 --viscosity 1e-3 --distance 1e-6 --temperature 298
```

**Verbose output:**
```bash
diffusion-time --radius 1e-9 --verbose
```

**With plotting (opens matplotlib window):**
```bash
diffusion-time --radius 1e-9 --plot
```

**2D diffusion:**
```bash
diffusion-time --radius 2e-9 --dims 2
```

### Python API

```python
from diffusion_time_estimator import diffusion_coefficient, diffusion_time

# Calculate diffusion coefficient
D = diffusion_coefficient(radius=1e-9, viscosity=1e-3, temperature=298)
print(f"D = {D:.3e} m²/s")

# Calculate time to diffuse a distance
t = diffusion_time(distance=1e-6, D=D, dims=3)
print(f"Time = {t:.3e} s")
```

## Common Examples

### Glucose in water
```bash
diffusion-time --radius 5e-10 --distance 10e-6
# D ≈ 4.4e-10 m²/s, t ≈ 38 ms
```

### Protein in cytoplasm at body temperature
```bash
diffusion-time --radius 2e-9 --viscosity 3e-3 --temperature 310 --distance 10e-6
# D ≈ 3.8e-11 m²/s, t ≈ 440 ms
```

### Ion channel in membrane (2D)
```bash
diffusion-time --radius 3e-9 --viscosity 5e-3 --dims 2 --distance 100e-9
# D ≈ 1.5e-11 m²/s, t ≈ 172 μs
```

## Running Tests

```bash
pytest
```

## More Examples

See `examples/api_examples.py` for detailed Python API usage:
```bash
python examples/api_examples.py
```
