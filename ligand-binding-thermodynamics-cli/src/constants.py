"""
Physical constants and conversion factors for thermodynamic calculations.
"""

# Gas constant (CODATA 2018 recommended value)
# R = 8.314462618 J·mol⁻¹·K⁻¹
GAS_CONSTANT_R = 8.314462618  # J/(mol·K)

# Conversion factors
J_TO_KJ = 0.001  # 1 J = 0.001 kJ
KJ_TO_J = 1000.0  # 1 kJ = 1000 J

# Standard conditions (for reference)
STANDARD_TEMP = 298.15  # K (25°C)
STANDARD_PRESSURE = 1e5  # Pa (1 bar)

# Physical limits for validation
MIN_TEMPERATURE = 0.0  # K (absolute zero)
MAX_TEMPERATURE = 500.0  # K (reasonable upper limit for biochemistry)
MIN_CONCENTRATION = 0.0  # M (cannot be negative)
MAX_CONCENTRATION = 1.0  # M (reasonable upper limit)
