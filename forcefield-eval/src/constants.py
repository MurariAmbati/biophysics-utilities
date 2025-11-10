"""
Physical constants and unit conversion factors for force field calculations.
"""

import numpy as np

# Physical constants
EPSILON_0 = 8.854187817e-12  # Vacuum permittivity [F/m = C²/(J·m)]
K_E = 8.987551787e9  # Coulomb constant [N·m²/C²]
ELEMENTARY_CHARGE = 1.602176634e-19  # [C]
AVOGADRO = 6.02214076e23  # [1/mol]

# Unit conversions
J_TO_EV = 6.241509074e18  # Joules to electronvolts
EV_TO_J = 1.602176634e-19  # Electronvolts to joules
NM_TO_M = 1e-9  # Nanometers to meters
ANGSTROM_TO_M = 1e-10  # Angstroms to meters
ANGSTROM_TO_NM = 0.1  # Angstroms to nanometers
KJ_MOL_TO_EV = 0.0103642695  # kJ/mol to eV
EV_TO_KJ_MOL = 96.4853075  # eV to kJ/mol

# Default parameters for potentials
DEFAULT_LJ = {
    "epsilon": 0.2,  # eV - depth of potential well
    "sigma": 0.34,   # nm - distance at which U=0
}

DEFAULT_MORSE = {
    "De": 0.4,       # eV - well depth
    "a": 1.5,        # 1/nm - width parameter
    "re": 0.3,       # nm - equilibrium distance
}

DEFAULT_COULOMB = {
    "q1": 1e-19,     # C - charge of particle 1
    "q2": -1e-19,    # C - charge of particle 2
}

# Distance sweep defaults
DEFAULT_RANGE = {
    "rmin": 0.1,     # nm
    "rmax": 1.0,     # nm
    "npoints": 100,
}

# Unit system configuration
UNIT_SYSTEMS = {
    "SI": {
        "distance": "m",
        "energy": "J",
        "force": "N",
    },
    "nanometer_eV": {
        "distance": "nm",
        "energy": "eV",
        "force": "eV/nm",
    },
    "angstrom_eV": {
        "distance": "Å",
        "energy": "eV",
        "force": "eV/Å",
    },
    "nanometer_kJ_mol": {
        "distance": "nm",
        "energy": "kJ/mol",
        "force": "kJ/(mol·nm)",
    },
}

# Default unit system
DEFAULT_UNIT_SYSTEM = "nanometer_eV"
