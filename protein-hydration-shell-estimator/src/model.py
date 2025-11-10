"""
Core model for hydration shell estimation.

Implements the theoretical framework for calculating water molecule density,
volume, and count in the protein hydration shell.
"""

from typing import Dict, Any
from .constants import (
    RHO_BULK_WATER,
    AVOGADRO_NUMBER,
    ANGSTROM_TO_METER,
    DEFAULT_SHELL_THICKNESS,
    DEFAULT_HYDROPHILICITY_INDEX,
)


class HydrationShellEstimator:
    """
    Estimates the hydration shell properties of a protein based on
    surface area and hydrophilicity.
    
    The model assumes a quasi-ordered water layer surrounding the protein
    with properties influenced by surface polarity.
    """
    
    def __init__(
        self,
        surface_area: float,
        hydrophilicity_index: float = DEFAULT_HYDROPHILICITY_INDEX,
        shell_thickness: float = DEFAULT_SHELL_THICKNESS,
    ):
        """
        Initialize the hydration shell estimator.
        
        Parameters
        ----------
        surface_area : float
            Solvent-accessible surface area in m²
        hydrophilicity_index : float, optional
            Fraction of polar/hydrophilic residues (0 to 1)
            Default: 0.6
        shell_thickness : float, optional
            Effective thickness of hydration layer in Angstroms
            Default: 3.0 Å
        """
        self.surface_area = surface_area
        self.hydrophilicity_index = hydrophilicity_index
        self.shell_thickness = shell_thickness
        
        # Computed properties (cached)
        self._shell_volume = None
        self._shell_density = None
        self._water_count = None
        self._water_moles = None
    
    def calculate_shell_density(self) -> float:
        """
        Calculate water density in the hydration shell.
        
        The density is modulated by surface hydrophilicity:
        ρ_shell = ρ_bulk × f_hydrophilic
        
        where f_hydrophilic = 0.8 + 0.4 × H_index
        
        Returns
        -------
        float
            Shell water density in molecules/m³
        """
        f_hydrophilic = 0.8 + 0.4 * self.hydrophilicity_index
        shell_density = RHO_BULK_WATER * f_hydrophilic
        return shell_density
    
    def calculate_shell_volume(self) -> float:
        """
        Calculate the hydration shell volume.
        
        V_shell = A_surface × t_shell
        
        Returns
        -------
        float
            Shell volume in m³
        """
        thickness_m = self.shell_thickness * ANGSTROM_TO_METER
        shell_volume = self.surface_area * thickness_m
        return shell_volume
    
    def calculate_water_count(self) -> float:
        """
        Calculate the number of water molecules in the hydration shell.
        
        N_H2O = ρ_shell × V_shell
        
        Returns
        -------
        float
            Number of water molecules
        """
        if self._shell_density is None:
            self._shell_density = self.calculate_shell_density()
        if self._shell_volume is None:
            self._shell_volume = self.calculate_shell_volume()
        
        water_count = self._shell_density * self._shell_volume
        return water_count
    
    def calculate_water_moles(self) -> float:
        """
        Calculate the amount of water in moles.
        
        n_H2O = N_H2O / N_A
        
        Returns
        -------
        float
            Amount of water in mol
        """
        if self._water_count is None:
            self._water_count = self.calculate_water_count()
        
        water_moles = self._water_count / AVOGADRO_NUMBER
        return water_moles
    
    def compute(self) -> Dict[str, Any]:
        """
        Compute all hydration shell properties.
        
        Returns
        -------
        dict
            Dictionary containing all computed properties:
            - V_shell: shell volume (m³)
            - rho_shell: shell density (molecules/m³)
            - N_H2O: water molecule count
            - n_H2O: water amount (mol)
        """
        self._shell_volume = self.calculate_shell_volume()
        self._shell_density = self.calculate_shell_density()
        self._water_count = self.calculate_water_count()
        self._water_moles = self.calculate_water_moles()
        
        return {
            "V_shell": self._shell_volume,
            "rho_shell": self._shell_density,
            "N_H2O": self._water_count,
            "n_H2O": self._water_moles,
        }
    
    def get_summary(self) -> str:
        """
        Get a formatted summary of the hydration shell calculation.
        
        Returns
        -------
        str
            Human-readable summary with scientific notation
        """
        results = self.compute()
        
        summary = f"""
Hydration Shell Estimation Results
{'='*50}
Input Parameters:
  Surface Area:         {self.surface_area:.2e} m²
  Hydrophilicity Index: {self.hydrophilicity_index:.2f}
  Shell Thickness:      {self.shell_thickness:.1f} Å

Computed Properties:
  V_shell  = {results['V_shell']:.2e} m³
  ρ_shell  = {results['rho_shell']:.2e} molecules/m³
  N_H2O    = {results['N_H2O']:.2e}
  n_H2O    = {results['n_H2O']:.2e} mol

≈ {results['N_H2O']:.0f} water molecules in hydration shell
"""
        return summary
