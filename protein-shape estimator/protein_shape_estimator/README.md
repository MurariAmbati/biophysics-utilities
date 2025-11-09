# protein shape estimator

estimates protein physical properties from sequence length: hydrodynamic radius, net charge, diffusion coefficient.

## usage

```bash
python -m protein_shape_estimator --length 300
```

output:
```
Hydrodynamic radius: 3.10 nm
Net charge (approx.): +3.0 e
Diffusion coefficient: 7.0e-11 m²/s
```

## options

```
--length      number of residues (required)
--temp        temperature in kelvin (default: 298)
--viscosity   solvent viscosity in pa·s (default: 1e-3)
--pos-frac    fraction of basic residues (default: 0.08)
--neg-frac    fraction of acidic residues (default: 0.07)
```

## install

```bash
pip install -r requirements.txt
```

## test

```bash
pytest protein_shape_estimator/tests/
```
