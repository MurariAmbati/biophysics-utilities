# ligand binding thermodynamics cli

lightweight command-line tool for computing binding constants (Ka, Kd) and free energy (ΔG) from equilibrium data.

pure thermodynamics • interactive repl • zero dependencies • educational

## equations

**association constant**
$$K_a = \frac{[PL]}{[P][L]} \quad (M^{-1})$$

**dissociation constant**
$$K_d = \frac{1}{K_a} \quad (M)$$

**free energy**
$$\Delta G = -RT \ln K_a \quad (kJ/mol)$$

**thermodynamics**
$$\Delta G = \Delta H - T\Delta S$$

where $R = 8.314462618 \, J \cdot mol^{-1} \cdot K^{-1}$

## installation

```bash
pip install -e .
```

or run directly:

```bash
python -m src.cli
```

## usage

```
>>> T = 298              # temperature (K)
>>> P = 1e-6             # protein concentration (M)
>>> L = 1e-6             # ligand concentration (M)
>>> PL = 5e-7            # complex concentration (M)
>>> compute()

Ka = 5.00e+05 M^-1
Kd = 2.00e-06 M
ΔG = -32.51 kJ/mol
```

### entropy calculation

```
>>> ΔH = -50             # enthalpy (kJ/mol)
>>> compute_entropy()

ΔS = -59.8 J/(mol·K)
```

## commands

| command | description |
|---------|-------------|
| `T = <value>` | set temperature (K) |
| `P = <value>` | set protein concentration (M) |
| `L = <value>` | set ligand concentration (M) |
| `PL = <value>` | set complex concentration (M) |
| `ΔH = <value>` | set enthalpy (kJ/mol) |
| `compute()` | calculate Ka, Kd, ΔG |
| `compute_entropy()` | calculate ΔS |
| `show()` | show current state |
| `clear()` | clear all variables |
| `quit()` | exit |

## input/output

**inputs**
- temperature T (K)
- concentrations [P], [L], [PL] (M)
- optional: ΔH (kJ/mol), ΔS (J/(mol·K))

**outputs**
- Ka (M⁻¹) - association constant
- Kd (M) - dissociation constant  
- ΔG (kJ/mol) - free energy
- ΔS (J/(mol·K)) - entropy (if ΔH provided)

## structure

```
ligand-binding-thermodynamics-cli/
├── src/
│   ├── constants.py         # physical constants (R)
│   ├── core.py              # calculations (Ka, Kd, ΔG, ΔS)
│   ├── parser.py            # input parsing & validation
│   └── cli.py               # interactive repl
├── tests/
│   └── test_core.py         # 23 unit tests
├── examples/
│   └── example_session.txt  # example session
└── README.md
```

## development

### running tests

```bash
python -m unittest discover tests
```

### code structure

- `src/core.py` - add new thermodynamic calculations
- `src/cli.py` - extend repl commands
- `src/parser.py` - add input patterns
- `src/constants.py` - define physical constants

### contributing

fork, branch, test, pull request. keep it simple and well-tested.

## features

- zero dependencies (pure python stdlib)
- precise calculations (CODATA 2018 constants)
- transparent (shows all equations)
- educational (teaching tool)
- extensible (van't Hoff, Hill equation)
- well-tested (23 unit tests)

## examples

**strong binding**
```
Ka ≈ 9e+08 M⁻¹, Kd ≈ 1e-09 M, ΔG ≈ -50 kJ/mol
```

**weak binding**
```
Ka ≈ 1e+00 M⁻¹, Kd ≈ 1e+00 M, ΔG ≈ 0 kJ/mol
```

## license

MIT

## author

murari ambati

## contributing

fork, branch, test, pull request.

## references

thermodynamics, equilibrium binding, CODATA 2018 constants
