"""
Default constants and parameters for the Stochastic Integrator Visualizer.
"""

# Default simulation parameters
DEFAULT_X0 = 0.0           # Initial condition
DEFAULT_DT = 0.01          # Time step
DEFAULT_STEPS = 1000       # Number of steps
DEFAULT_SEED = None        # Random seed (None = random)

# Default drift and diffusion coefficients
DEFAULT_DRIFT = 1.0        # Drift coefficient (a)
DEFAULT_DIFFUSION = 0.3    # Diffusion coefficient (b)

# Visualization defaults
DEFAULT_LINEWIDTH = 1.0
DEFAULT_ALPHA = 0.7
DEFAULT_GRID = True

# Ensemble simulation defaults
DEFAULT_NUM_TRAJECTORIES = 100
DEFAULT_BINS = 50

# Method options
AVAILABLE_METHODS = ["euler-maruyama", "milstein", "deterministic"]
DEFAULT_METHOD = "euler-maruyama"

# Streamlit UI defaults
SLIDER_DT_MIN = 0.001
SLIDER_DT_MAX = 0.1
SLIDER_STEPS_MIN = 100
SLIDER_STEPS_MAX = 5000
SLIDER_DRIFT_MIN = -5.0
SLIDER_DRIFT_MAX = 5.0
SLIDER_DIFFUSION_MIN = 0.0
SLIDER_DIFFUSION_MAX = 2.0
SLIDER_NUM_TRAJ_MIN = 1
SLIDER_NUM_TRAJ_MAX = 500
