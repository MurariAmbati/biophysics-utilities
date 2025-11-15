# electrostatic potential mapper

compute and visualize electrostatic potentials on a 3d grid around a set
of point charges using either coulomb summation or a linearized
poisson–boltzmann (pb) model.

## install

from the `esp-mapper` directory:

```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy matplotlib pytest
```

## run (single shot)

```bash
python -m src.cli \
  --input examples/water_dipole.txt \
  --mode pb \
  --dielectric 80 \
  --grid 60 \
  --spacing 0.5 \
  --ionic-strength 0.15 \
  --out water_phi.npy \
  --slice z=0
```

## run (repl)

```bash
python -m src.cli
```

example:

```text
esp-map> load examples/water_dipole.txt
esp-map> mode coulomb
esp-map> dielectric 80
esp-map> grid 80
esp-map> spacing 0.5
esp-map> compute
esp-map> export phi.npy
esp-map> visualize slice z=0
```

## tests

```bash
pytest
```
