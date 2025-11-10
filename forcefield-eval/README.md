# force field evaluator

minimal tool to evaluate classical pair potentials (lj, morse, coulomb) for a diatomic system.

## usage

install dependencies:

```bash
pip install -r requirements.txt
```

run cli:

```bash
python main.py --potential lj,morse --rmin 0.1 --rmax 1.0 --npoints 100 --output plot
```

quick text summary:

```bash
python main.py --potential all
```

export numeric data:

```bash
python main.py --potential lj --output data > lj_data.csv
```

python api (minimal):

```python
from src.evaluator import ForceFieldEvaluator, create_distance_range

r = create_distance_range(0.1, 1.0, 100)
e = ForceFieldEvaluator()
lj = e.evaluate_potential('LJ', {'epsilon':0.2, 'sigma':0.34}, r)
print(f"lj: r_eq={lj['r_eq']:.3f} nm, u_min={lj['U_min']:.3f} ev")
```

compare lennard-jones and morse:

```bash
python main.py --potential lj,morse --rmin 0.2 --rmax 0.8 --output plot
```

## notes

- units: distances in nm, energy in ev, force in ev/nm
- equilibrium finder uses scipy if available, otherwise falls back to discrete min
- potentials: lennard-jones (12-6), morse, coulomb

## signature

murari ambati as. asignature
