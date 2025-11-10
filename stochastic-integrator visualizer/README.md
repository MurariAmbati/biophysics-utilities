# Stochastic Integrator Visualizer

Interactive simulator for **Stochastic Differential Equations (SDEs)**: $dx_t = a(x_t, t) \, dt + b(x_t, t) \, dW_t$

Implements Euler–Maruyama and Milstein methods with real-time visualization.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

**CLI:**
```bash
# Basic
python -m stochastic_integrator_visualizer

# Ensemble
python -m stochastic_integrator_visualizer --ensemble 100 --drift 1.0 --diffusion 0.3
```

**Web App:**
```bash
streamlit run streamlit_app.py
```

**Python API:**
```python
from stochastic_integrator_visualizer.core import euler_maruyama, make_constant_drift, make_constant_diffusion
from stochastic_integrator_visualizer.visualize import plot_trajectory

drift = make_constant_drift(1.0)
diffusion = make_constant_diffusion(0.3)
t, x = euler_maruyama(drift, diffusion, x0=0.0, dt=0.01, steps=1000, seed=42)
plot_trajectory(t, x)
```

## Testing

```bash
pytest
```

## License

MIT
