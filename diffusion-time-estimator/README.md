# Diffusion Time Estimator

Estimate molecular diffusion timescales from first principles using the Stokes-Einstein relation.

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
diffusion-time --radius 1e-9 --viscosity 1e-3 --distance 1e-6
```

Output:
```
Estimated diffusion coefficient: 2.18e-10 m²/s
Characteristic diffusion time: 764 μs
```

## Usage

### CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `--radius` `-r` | Molecule radius (m) | Required |
| `--viscosity` `-v` | Viscosity (Pa·s) | 1e-3 |
| `--temperature` `-T` | Temperature (K) | 298 |
| `--distance` `-L` | Distance (m) | 1e-6 |
| `--dims` `-n` | Dimensions (1/2/3) | 3 |
| `--plot` `-p` | Plot MSD | — |
| `--verbose` | Detailed output | — |

### Examples

```bash
# Protein in cytoplasm
diffusion-time --radius 2e-9 --viscosity 3e-3 --temperature 310

# 2D membrane diffusion
diffusion-time --radius 3e-9 --dims 2 --plot

# Verbose output
diffusion-time --radius 1e-9 --verbose
```

## Python API

```python
from diffusion_time_estimator import diffusion_coefficient, diffusion_time

D = diffusion_coefficient(radius=1e-9, viscosity=1e-3, temperature=298)
t = diffusion_time(distance=1e-6, D=D, dims=3)
```

## Physics

**Stokes-Einstein:** $D = \frac{k_B T}{6\pi\eta r}$

**MSD:** $\langle x^2(t) \rangle = 2nDt$

**Diffusion time:** $t_{\text{diff}} \approx \frac{L^2}{2nD}$

## Testing

```bash
pytest
```

## License

MIT
