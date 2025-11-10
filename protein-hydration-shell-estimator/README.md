# protein hydration shell estimator

estimate water molecules in protein hydration shells from surface area and hydrophilicity. pure theoretical model, no experimental data needed.

## what it does

calculates hydration shell properties using:
- ρ_shell = ρ_bulk × (0.8 + 0.4 × h_index)
- v_shell = a_surface × t_shell
- n_h2o = ρ_shell × v_shell

where ρ_bulk = 3.34×10²⁸ molecules/m³, h_index = hydrophilicity (0-1), t_shell = thickness (~3 å)

## install

```bash
pip install -e .
```

requires python 3.10+, no external dependencies

## use

### command line
```bash
hydration-estimator --surface-area 1.5e-17 --hydrophilicity 0.65 --thickness 3.0
```

### interactive
```bash
hydration-estimator
>>> surface_area = 1.5e-17
>>> hydrophilicity = 0.65
>>> compute()
```

### python
```python
from src.model import HydrationShellEstimator

est = HydrationShellEstimator(
    surface_area=1.5e-17,  # m²
    hydrophilicity_index=0.65,
    shell_thickness=3.0  # å
)

results = est.compute()
print(f"{results['N_H2O']:.0f} water molecules")
```

## parameters

| parameter | default | units | range |
|-----------|---------|-------|-------|
| surface_area | 1e-17 | m² | typical: 1e-18 to 1e-15 |
| hydrophilicity_index | 0.6 | - | 0 (hydrophobic) to 1 (hydrophilic) |
| shell_thickness | 3.0 | å | typical: 2.5-3.5 |

## examples

```python
# small hydrophobic peptide (~50 nm²)
HydrationShellEstimator(5e-17, 0.3, 2.8)  # → ~430 waters

# typical globular protein (~100 nm²)
HydrationShellEstimator(1e-16, 0.6, 3.0)  # → ~1,041 waters

# large hydrophilic protein (~300 nm²)
HydrationShellEstimator(3e-16, 0.75, 3.5)  # → ~3,858 waters
```

## test

```bash
python tests/test_model.py  # 32 tests
python demo.py              # demonstrations
```

## files

```
src/
  constants.py    # physical constants
  model.py        # core calculations
  utils.py        # conversions & validation
  cli.py          # interactive interface
tests/
  test_model.py   # test suite
examples/
  protein_surface_example.txt  # detailed examples
demo.py           # demonstrations
```

## design

- minimal but physically grounded
- zero data dependencies
- reproducible results
- educational + practical

## license

mit
