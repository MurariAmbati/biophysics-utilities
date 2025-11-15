# viscoelastic response analyzer

a tiny tool for analytical maxwell and kelvin–voigt responses.

## install
```bash
/Users/murari/biophysics-utilities/viscoelastic-response-analyzer/.conda/bin/python -m pip install -e '.[dev]'
```

## run
```bash
viscoelastic-analyzer \
  --model maxwell \
  --mode relaxation \
  --E 1000 \
  --eta 5000 \
  --strain0 0.02 \
  --t_max 10 \
  --dt 0.01 \
  --plot-file plots/maxwell_relaxation.png \
  --json-out outputs/relaxation.json
```

## api
```python
from viscoelastic_analyzer import SimulationConfig, compute_response

cfg = SimulationConfig(
    model="maxwell",
    mode="relaxation",
    E=1200.0,
    eta=6000.0,
    strain0=0.01,
    stress0=None,
    t_max=8.0,
    dt=0.05,
)
result = compute_response(cfg)
print(result.tau)
```

## test
```bash
/Users/murari/biophysics-utilities/viscoelastic-response-analyzer/.conda/bin/python -m pytest
```
