# Parser Specification

## Reaction Input Formats

The Reaction Kinetics Playground supports multiple input formats for defining chemical reactions.

## Simple Text Format

### Basic Syntax

```
reactants -> products ; rate_constant
```

### Examples

```python
# Simple reaction
"A -> B ; 1.0"

# Multiple reactants/products
"A + B -> C + D ; 0.5"

# Stoichiometric coefficients
"2A + B -> 3C ; 0.2"

# Reversible reaction
"A <-> B ; 1.0"
```

### Features

- **Operators**: `->` (forward), `<->` (reversible), `<-` (backward)
- **Coefficients**: Numeric prefixes (e.g., `2A`, `3.5B`)
- **Rate constants**: After semicolon
- **Comments**: Lines starting with `#`

## YAML Format

```yaml
species:
  - A
  - B
  - C

reactions:
  - equation: A + B -> C
    rate_constant: 0.1
    kinetic_law: mass_action
    
  - equation: C -> A + B
    rate_constant: 0.05
    reversible: false
    parameters:
      activation_energy: 50.0

initial_conditions:
  A: 1.0
  B: 1.0
  C: 0.0

simulation:
  time_span: [0, 100]
  method: LSODA
  rtol: 1.0e-6
  atol: 1.0e-9
```

## JSON Format

```json
{
  "reactions": [
    {
      "equation": "A + B -> C",
      "rate_constant": 0.1,
      "kinetic_law": "mass_action"
    },
    {
      "reactants": {"A": 1, "B": 1},
      "products": {"C": 1},
      "k": 0.1
    }
  ],
  "initial_conditions": {
    "A": 1.0,
    "B": 1.0,
    "C": 0.0
  }
}
```

## Custom .rkp Format

Simple text file, one reaction per line:

```
# Comments start with #
A + B -> C ; 0.1
C -> A + B ; 0.05

# Blank lines are ignored

# Special syntax for kinetic laws
E + S -> ES ; 1.0 ; michaelis_menten ; Vmax=1.0, Km=0.5
```

## Kinetic Law Specification

### Mass Action (Default)

```
A + B -> C ; 0.1
```

Rate = 0.1 * [A] * [B]

### Michaelis-Menten

```
E + S -> ES ; 1.0 ; michaelis_menten ; Vmax=1.0, Km=0.5
```

Rate = Vmax * [S] / (Km + [S])

### Hill Equation

```
S -> P ; 1.0 ; hill ; Vmax=1.0, K=0.5, n=2.0
```

Rate = Vmax * [S]^n / (K^n + [S]^n)

### Custom Formula

```python
from kinetics_playground.core.kinetics import CustomKineticLaw

law = CustomKineticLaw(
    formula="k * [A] * [B] / (1 + [A])",
    parameters={"k": 0.1}
)
```

## Species Naming Rules

- Must start with letter or underscore
- Can contain letters, numbers, underscores
- Case-sensitive
- Examples: `A`, `X_1`, `NADH`, `protein_p53`

## Parser API

```python
from kinetics_playground.core.parser import ReactionParser

parser = ReactionParser()

# Single reaction
reaction = parser.parse_single("A + B -> C ; 0.1")

# Multiple reactions
reactions = parser.parse_multiple([
    "A -> B ; 1.0",
    "B -> C ; 0.5"
])

# From file
reactions = parser.parse_from_file("reactions.yaml")

# Get species list
species = parser.get_all_species()
```

## Error Handling

Parser validates:
- Syntax correctness
- Species name validity
- Rate constant format
- Stoichiometric coefficient ranges

Common errors:
- Invalid arrow operators
- Missing rate constants
- Malformed stoichiometry
- Invalid JSON/YAML structure
