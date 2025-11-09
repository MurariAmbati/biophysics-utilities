# biocalc

unit-aware biochemical calculator.

## install

```bash
cd biocalc
pip install -e .
```

## use

### interactive repl

```bash
bio-calc
>>> R * 300*K
>>> avogadro * 1e-3 mol
>>> convert(1 kcal/mol, J/mol)
>>> energy(ATP_hydrolysis)
```

### command line

```bash
# evaluate expression
bio-calc "R * 300*K"

# list constants
bio-calc --list

# search constants
bio-calc --search diffusion

# convert units
bio-calc --convert "1 kcal/mol" "J/mol"

# get energy value
bio-calc --energy ATP_hydrolysis
```

## features

- automatic unit tracking with pint
- symbolic math with sympy
- 50+ biochemical and physical constants
- safe expression evaluation
- unit conversion and validation

## constants

biochemical energies, diffusion coefficients, molecular masses, standard conditions, and more.

type `bio-calc --list` to see all available constants.

---

*murari ambati, 2025*
