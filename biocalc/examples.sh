# Example usage scripts for biocalc

## Simple calculations
bio-calc "R * 298.15*K"
bio-calc "avogadro / 1000"

## Energy calculations
bio-calc "energy(ATP_hydrolysis)"
bio-calc "ATP_hydrolysis / R / 300"

## Unit conversions
bio-calc --convert "50 kJ/mol" "kcal/mol"
bio-calc --convert "1 bar" "Pa"
bio-calc --convert "37 celsius" "K"

## Diffusion calculations
bio-calc "diffusion_O2_water * 1e9"
bio-calc "sqrt(4 * diffusion_O2_water * 1)"

## Concentration calculations
bio-calc "conc_ATP_cell * avogadro * 1e-15"
bio-calc "mass_glucose / avogadro"

## Temperature-dependent calculations
bio-calc "R * body_temperature"
bio-calc "exp(-ATP_hydrolysis / (R * 310.15))"
