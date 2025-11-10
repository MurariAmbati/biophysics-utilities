"""Utility functions for unit conversions and constants."""

import numpy as np

# Physical constants
AVOGADRO = 6.02214076e23  # mol^-1
BOLTZMANN = 1.380649e-23  # J/K
GAS_CONSTANT = 8.314462618  # J/(mol·K)

# Conversion factors
KJ_TO_J = 1000.0
ANGSTROM_TO_M = 1e-10
EV_TO_KJ_PER_MOL = 96.485  # 1 eV = 96.485 kJ/mol
KCAL_TO_KJ = 4.184  # 1 kcal = 4.184 kJ


def kj_to_kcal(energy_kj: float) -> float:
    """
    Convert energy from kJ/mol to kcal/mol.
    
    Parameters
    ----------
    energy_kj : float
        Energy in kJ/mol
        
    Returns
    -------
    float
        Energy in kcal/mol
    """
    return energy_kj / KCAL_TO_KJ


def kcal_to_kj(energy_kcal: float) -> float:
    """
    Convert energy from kcal/mol to kJ/mol.
    
    Parameters
    ----------
    energy_kcal : float
        Energy in kcal/mol
        
    Returns
    -------
    float
        Energy in kJ/mol
    """
    return energy_kcal * KCAL_TO_KJ


def ev_to_kj(energy_ev: float) -> float:
    """
    Convert energy from eV to kJ/mol.
    
    Parameters
    ----------
    energy_ev : float
        Energy in eV
        
    Returns
    -------
    float
        Energy in kJ/mol
    """
    return energy_ev * EV_TO_KJ_PER_MOL


def kj_to_ev(energy_kj: float) -> float:
    """
    Convert energy from kJ/mol to eV.
    
    Parameters
    ----------
    energy_kj : float
        Energy in kJ/mol
        
    Returns
    -------
    float
        Energy in eV
    """
    return energy_kj / EV_TO_KJ_PER_MOL


def nm_to_angstrom(distance_nm: float) -> float:
    """
    Convert distance from nanometers to Ångströms.
    
    Parameters
    ----------
    distance_nm : float
        Distance in nm
        
    Returns
    -------
    float
        Distance in Ångströms
    """
    return distance_nm * 10.0


def angstrom_to_nm(distance_angstrom: float) -> float:
    """
    Convert distance from Ångströms to nanometers.
    
    Parameters
    ----------
    distance_angstrom : float
        Distance in Ångströms
        
    Returns
    -------
    float
        Distance in nm
    """
    return distance_angstrom / 10.0


def format_energy(energy: float, decimals: int = 2) -> str:
    """
    Format energy value with appropriate sign and units.
    
    Parameters
    ----------
    energy : float
        Energy value in kJ/mol
    decimals : int, optional
        Number of decimal places (default: 2)
        
    Returns
    -------
    str
        Formatted energy string with units
    """
    return f"{energy:.{decimals}f} kJ/mol"


def format_distance(distance: float, decimals: int = 2) -> str:
    """
    Format distance value with units.
    
    Parameters
    ----------
    distance : float
        Distance value in Ångströms
    decimals : int, optional
        Number of decimal places (default: 2)
        
    Returns
    -------
    str
        Formatted distance string with units
    """
    return f"{distance:.{decimals}f} Å"


def save_potential_table(
    r: np.ndarray,
    V: np.ndarray,
    filename: str = "lj_potential.csv",
    include_force: bool = False,
    F: np.ndarray = None
) -> None:
    """
    Save potential (and optionally force) data to CSV file.
    
    Parameters
    ----------
    r : np.ndarray
        Distance array in Ångströms
    V : np.ndarray
        Potential energy array in kJ/mol
    filename : str, optional
        Output filename (default: "lj_potential.csv")
    include_force : bool, optional
        Whether to include force column (default: False)
    F : np.ndarray, optional
        Force array in kJ/mol/Å (required if include_force=True)
    """
    import csv
    
    with open(filename, 'w', newline='') as csvfile:
        if include_force and F is not None:
            writer = csv.writer(csvfile)
            writer.writerow(['r (Angstrom)', 'V (kJ/mol)', 'F (kJ/mol/Angstrom)'])
            for r_val, V_val, F_val in zip(r, V, F):
                writer.writerow([f"{r_val:.6f}", f"{V_val:.6f}", f"{F_val:.6f}"])
        else:
            writer = csv.writer(csvfile)
            writer.writerow(['r (Angstrom)', 'V (kJ/mol)'])
            for r_val, V_val in zip(r, V):
                writer.writerow([f"{r_val:.6f}", f"{V_val:.6f}"])
    
    print(f"Potential table saved to {filename}")


def load_potential_table(filename: str):
    """
    Load potential data from CSV file.
    
    Parameters
    ----------
    filename : str
        Input filename
        
    Returns
    -------
    dict
        Dictionary with 'r', 'V', and optionally 'F' arrays
    """
    import csv
    
    data = {'r': [], 'V': []}
    has_force = False
    
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        
        if len(header) > 2:
            has_force = True
            data['F'] = []
        
        for row in reader:
            data['r'].append(float(row[0]))
            data['V'].append(float(row[1]))
            if has_force:
                data['F'].append(float(row[2]))
    
    # Convert to numpy arrays
    for key in data:
        data[key] = np.array(data[key])
    
    return data
