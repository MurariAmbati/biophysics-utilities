"""
Physical constants used for protein shape estimation.
"""

# Boltzmann constant (J/K)
K_B = 1.380649e-23

# Average molecular weight per amino acid residue (Da)
AVG_MW_PER_RESIDUE = 110

# Empirical coefficient for hydrodynamic radius calculation
RH_COEFFICIENT = 0.066

# Empirical exponent for hydrodynamic radius calculation
RH_EXPONENT = 0.37

# Default temperature (K)
DEFAULT_TEMP = 298

# Default viscosity for water at 25°C (Pa·s)
DEFAULT_VISCOSITY = 1e-3

# Default fraction of positively charged residues (Lys + Arg)
DEFAULT_POS_FRAC = 0.08

# Default fraction of negatively charged residues (Asp + Glu)
DEFAULT_NEG_FRAC = 0.07
