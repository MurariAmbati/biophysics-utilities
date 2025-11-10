# brownian motion simulator

simulate and visualize stochastic particle motion in 2d and 3d.

## features

- 2d and 3d simulations
- adjustable diffusion coefficient (D) and time step (Δt)
- mean square displacement (msd) calculation
- multi-particle simulations
- interactive cli
- static plots, animations, histograms
- statistical validation
- educational output

## physics

brownian motion follows the stochastic differential equation:

$$dx_t = \sqrt{2D} \, dW_t$$

discrete approximation:

$$x_{t+\Delta t} = x_t + \sqrt{2D\Delta t} \, \mathcal{N}(0,1)$$

mean square displacement (einstein relation):

$$\langle r^2(t) \rangle = 2 \cdot \text{dim} \cdot D \cdot t$$

- 2d: msd = 4Dt
- 3d: msd = 6Dt

## installation

requirements:
- python 3.10+
- numpy
- matplotlib

install dependencies:

```bash
pip install -r requirements.txt
```

## usage

### interactive mode

```bash
python src/cli.py
```

example session:

```
>>> D = 2.5
>>> steps = 1000
>>> dim = 3
>>> run()
>>> plot()
>>> msd()
```

commands:
- `D = <value>` - set diffusion coefficient
- `dt = <value>` - set time step
- `steps = <value>` - set number of steps
- `particles = <value>` - set number of particles
- `dim = <2|3>` - set dimension
- `run()` - execute simulation
- `plot()` - show trajectories
- `msd()` - show msd comparison
- `animate()` - show animation
- `help` - show help
- `exit` - exit program

### command line

```bash
# 2d simulation with plots
python src/cli.py --dim 2 --particles 5 --D 1.0 --steps 2000 --plot --msd

# 3d animation
python src/cli.py --dim 3 --particles 3 --D 2.5 --steps 1000 --animate

# save outputs
python src/cli.py --dim 2 --plot --msd --save
```

### python api

```python
from src.core import BrownianSimulator
from src.viz import visualize_trajectories, plot_msd_comparison
import matplotlib.pyplot as plt

# create simulator
sim = BrownianSimulator(
    D=1.5,
    dt=0.01,
    n_steps=1000,
    n_particles=10,
    dim=2,
    seed=42
)

# run simulation
trajectories = sim.simulate()

# compute msd
time, msd_sim = sim.compute_msd()
msd_theory = sim.theoretical_msd()

# fit diffusion coefficient
D_fit, r_squared = sim.fit_diffusion_coefficient()
print(f"fitted D: {D_fit:.3f} μm²/s (R² = {r_squared:.4f})")

# visualize
visualize_trajectories(trajectories, time, dim=2)
plot_msd_comparison(time, msd_sim, msd_theory, D=1.5, dim=2)
plt.show()
```

## examples

```bash
# basic 2d simulation
python examples/example_2d.py

# 3d animation
python examples/example_3d.py

# minimal demo
python brownian_minimal.py
```

## testing

```bash
python tests/test_core.py -v
```

or with pytest:

```bash
pytest tests/ -v
```

## project structure

```
brownian-motion-sim/
├── src/
│   ├── __init__.py
│   ├── core.py          # simulation engine
│   ├── viz.py           # visualization
│   └── cli.py           # command-line interface
├── examples/
│   ├── example_2d.py
│   └── example_3d.py
├── tests/
│   └── test_core.py
├── requirements.txt
└── README.md
```

## what is brownian motion?

random movement of particles in a fluid, caused by collisions with fluid molecules. first observed by robert brown (1827), explained by albert einstein (1905).

key concepts:

**diffusion coefficient (D)**
- measures how quickly particles spread
- units: μm²/s

**mean square displacement (msd)**
- average squared distance from origin
- linear in time for normal diffusion

applications:
- protein diffusion in membranes
- drug delivery
- particle tracking
- cytoplasmic transport

## extensions

**add drift velocity:**
```python
displacements = drift_velocity * dt + np.sqrt(2 * self.D * self.dt) * noise
```

**add boundaries:**
```python
positions = np.clip(positions, -boundary, boundary)
```

**export trajectories:**
```python
import pandas as pd
df = pd.DataFrame({'x': traj[:, 0], 'y': traj[:, 1]})
df.to_csv('trajectory.csv')
```

## troubleshooting

**import errors:**
```bash
pip install -r requirements.txt
```

**module not found:**
```bash
cd brownian-motion-sim
python src/cli.py
```

**animation not saving:**
```bash
brew install ffmpeg  # macos
sudo apt install ffmpeg  # ubuntu
```

## references

1. einstein, a. (1905). "über die von der molekularkinetischen theorie der wärme geforderte bewegung von in ruhenden flüssigkeiten suspendierten teilchen." *annalen der physik*, 322(8), 549-560.

2. perrin, j. (1909). "mouvement brownien et réalité moléculaire." *annales de chimie et de physique*, 18, 5-114.

3. berg, h. c. (1993). *random walks in biology*. princeton university press.

## license

mit license

## contributing

contributions welcome! areas for improvement:
- anomalous diffusion
- gpu acceleration
- interactive jupyter widgets
- real-time plotting
