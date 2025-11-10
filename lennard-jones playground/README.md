# lennard-jones potential playground

interactive visual environment to explore the lennard-jones 12-6 potential.

## physical model

the lennard-jones 12-6 potential:

```
V(r) = 4ε[(σ/r)¹² - (σ/r)⁶]
```

where:
- V(r): potential energy
- r: interparticle distance
- ε: depth of potential well
- σ: distance where V(r) = 0

equilibrium properties:
- r_min = 2^(1/6) × σ ≈ 1.122σ
- V_min = -ε

## features

- compute lj potential curve for r ∈ [0.5σ, 3σ]
- display minimum energy point
- interactive parameter tuning
- real-time plot updates
- force curve visualization
- morse potential comparison
- reduced lj potential in dimensionless units
- csv export for md simulations
- command-line repl interface
- interactive plotly/jupyter widgets
- comprehensive unit tests

## installation

prerequisites:
- python 3.10 or higher
install dependencies:

```bash
cd "lennard-jones playground"
pip install numpy matplotlib plotly ipywidgets pandas
```

optional development mode:

```bash
pip install -e .
```

## usage

### command-line interface

## 📖 Usage

### command-line interface

interactive repl mode:

```bash
python -m src.cli
```

example session:
```
>>> epsilon = 0.8
ε = 0.8 kJ/mol

>>> sigma = 3.2
σ = 3.2 Å

>>> plot()
Min at r = 3.59 Å, V = -0.80 kJ/mol

>>> force
Force curve: ON

>>> plot()
Min at r = 3.59 Å, V = -0.80 kJ/mol

>>> export('my_potential.csv')
Potential table saved to my_potential.csv

>>> help
[Shows full command reference]

>>> quit
Goodbye!
```

available commands:

parameters:
- `epsilon = <value>` - set ε (well depth) in kj/mol
- `sigma = <value>` - set σ (collision diameter) in å
- `range <min> <max>` - set plotting range in å

actions:
- `plot()` - generate and display lj potential plot
- `plot('filename.png')` - save plot to file
- `info()` - show current parameters and equilibrium properties
- `export()` - export data to csv
- `export('file.csv')` - export data to specified file

toggles:
- `force` - toggle force curve display
- `morse` - toggle morse potential comparison
- `reduced` - toggle reduced lj potential

other:
- `help` - show help message
- `quit` / `exit` - exit the program

non-interactive mode:

```bash
non-interactive mode:

```bash
# plot with custom parameters
python -m src.cli --epsilon 1.2 --sigma 3.8 --plot

# save plot to file
python -m src.cli --epsilon 1.0 --sigma 3.5 --plot --output lj_plot.png

# export data to csv
python -m src.cli --epsilon 1.0 --sigma 3.5 --export data.csv

# include force curve
python -m src.cli --epsilon 1.0 --sigma 3.5 --plot --force
```

### jupyter notebook
```

### jupyter notebook

```bash
jupyter notebook examples/lj_interactive_demo.ipynb
```

the notebook includes:
- basic lj potential visualization
- potential and force plots
- interactive widgets with sliders
- reduced units analysis
- comparison of different systems
- data export examples

### python api

```python
from src.model import lj_potential, lj_force, lj_equilibrium, generate_lj_curve
from src.utils import format_energy, format_distance

# set parameters
epsilon = 1.0  # kj/mol
sigma = 3.5    # angstrom

# generate potential curve
r, V = generate_lj_curve(epsilon, sigma)

# calculate equilibrium properties
r_eq, V_eq = lj_equilibrium(epsilon, sigma)

print(f"equilibrium distance: {format_distance(r_eq)}")
print(f"minimum energy: {format_energy(V_eq)}")

# calculate force at specific distance
r_test = 4.0
F = lj_force(r_test, epsilon, sigma)
print(f"force at {r_test} å: {F:.4f} kj/mol/å")

# plot using matplotlib
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(r, V, 'b-', linewidth=2, label='lj potential')
plt.plot(r_eq, V_eq, 'ro', markersize=10, label='equilibrium')
plt.axhline(y=0, color='k', linestyle='--', alpha=0.5)
plt.xlabel('distance r (å)')
plt.ylabel('potential v(r) (kj/mol)')
plt.title(f'lennard-jones potential (ε={epsilon} kj/mol, σ={sigma} å)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

### interactive gui

```python
from src.gui import create_interactive_plot, save_interactive_html

# create interactive plotly figure
fig = create_interactive_plot(
    epsilon_range=(0.1, 3.0),
    sigma_range=(2.0, 5.0),
    initial_epsilon=1.0,
    initial_sigma=3.5,
    show_force=True
)

# show in browser
fig.show()

# or save to html file
save_interactive_html('lj_interactive.html')
```

for jupyter notebooks with ipywidgets:

```python
from src.gui import create_interactive_widget

# create widget with real-time updates
widget = create_interactive_widget(
    epsilon_range=(0.1, 3.0),
    sigma_range=(2.0, 5.0),
    initial_epsilon=1.0,
    initial_sigma=3.5
)

# display widget
display(widget)
```

## project structure
```

For Jupyter notebooks with ipywidgets:

```python
from src.gui import create_interactive_widget

# Create widget with real-time updates
widget = create_interactive_widget(
    epsilon_range=(0.1, 3.0),
    sigma_range=(2.0, 5.0),
    initial_epsilon=1.0,
    initial_sigma=3.5
)

# Display widget
display(widget)
```

## project structure

```
lennard-jones playground/
│
├── src/
│   ├── __init__.py          # package initialization
│   ├── model.py             # lj potential and derivatives
│   ├── cli.py               # command-line repl interface
│   ├── gui.py               # interactive plotly visualizations
│   └── utils.py             # unit conversions, constants
│
├── tests/
│   ├── __init__.py
│   └── test_model.py        # unit tests
│
├── examples/
│   ├── lj_interactive_demo.ipynb   # interactive jupyter notebook
│   └── lj_example_run.txt          # example cli session
│
└── README.md                # this file
```

## testing

```bash
# run all tests
python -m pytest tests/

# run specific test file
python tests/test_model.py

# run with verbose output
python -m pytest tests/ -v
```

or with unittest:

```bash
python -m unittest discover tests/
```

## parameters

| parameter | symbol | default | units | description |
|-----------|--------|---------|-------|-------------|
| epsilon | ε | 1.0 | kj/mol | well depth |
| sigma | σ | 3.5 | å | collision diameter |
| range | r_min, r_max | 0.5σ – 3σ | å | distance range for plotting |
| step | Δr | 0.01σ | å | sampling interval |

## outputs

| quantity | symbol | units | description |
|----------|--------|-------|-------------|
| potential array | v(r) | kj/mol | potential energy vs. distance |
| equilibrium distance | r_min | å | distance at minimum energy |
| minimum energy | v_min | kj/mol | value of potential minimum |
| force | f(r) | kj/mol/å | force = -dv/dr |

## physical interpretation

short range (r < r_min):
- strong repulsion dominates
- r⁻¹² term represents pauli exclusion (electron cloud overlap)
- potential becomes very positive (high energy cost)

equilibrium (r = r_min):
- energy minimum - most stable configuration
- balance between attraction and repulsion
- r_min = 2^(1/6)σ ≈ 1.122σ

long range (r > r_min):
- weak attraction prevails
- r⁻⁶ term represents van der waals attraction
- potential approaches zero from below

## example applications

1. noble gas interactions: argon, neon, xenon modeling
2. molecular dynamics: pairwise potential for md simulations
3. phase transitions: gas-liquid equilibria
4. protein folding: non-bonded interactions
5. material science: surface interactions and adhesion

example lj parameters:

| system | ε (kj/mol) | σ (å) | notes |
|--------|-----------|-------|-------|
| argon | 0.997 | 3.40 | noble gas |
| neon | 0.314 | 2.74 | smaller noble gas |
| xenon | 1.77 | 3.96 | larger noble gas |
| generic | 1.0 | 3.5 | reference values |

## references

## 🎯 Extensions & Future Work

- [x] Add Morse potential toggle for comparison
- [x] Plot reduced LJ form using V*(r*) = 4[(1/r*)¹² - (1/r*)⁶]
- [x] Compute force curve F(r) overlay
- [x] Export potential table as .csv for MD use
- [ ] Add temperature effects (kT comparison)
- [ ] Implement cutoff distance analysis
- [ ] Support for modified LJ forms (9-6, etc.)
- [ ] Multi-particle system visualization
- [ ] Integration with MD simulation tools

## references

1. lennard-jones, j.e. (1924). "on the determination of molecular fields". proc. r. soc. lond. a 106 (738): 463–477.
2. frenkel, d., & smit, b. (2001). understanding molecular simulation: from algorithms to applications. academic press.
3. allen, m.p., & tildesley, d.j. (2017). computer simulation of liquids (2nd ed.). oxford university press.

## license

mit license - free for educational and research purposes.
