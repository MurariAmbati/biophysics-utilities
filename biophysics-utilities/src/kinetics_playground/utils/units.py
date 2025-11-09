"""
Unit conversion and dimensional analysis utilities.

Provides conversions between common concentration and time units
used in chemical kinetics.
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class Quantity:
    """Represents a physical quantity with value and units."""
    value: float
    units: str
    
    def __repr__(self):
        return f"{self.value} {self.units}"
    
    def to(self, target_units: str, converter: 'UnitConverter') -> 'Quantity':
        """Convert to different units."""
        new_value = converter.convert(self.value, self.units, target_units)
        return Quantity(new_value, target_units)


class UnitConverter:
    """
    Handles unit conversions for concentration and time.
    
    Concentration units: M (molar), mM, μM, nM, particles/volume
    Time units: s, ms, min, h
    Rate constant units: 1/s, 1/min, M/s, M²/s (order-dependent)
    """
    
    # Concentration conversion factors (to Molar)
    CONCENTRATION_TO_MOLAR = {
        'M': 1.0,
        'mM': 1e-3,
        'uM': 1e-6,
        'μM': 1e-6,
        'nM': 1e-9,
        'pM': 1e-12,
    }
    
    # Time conversion factors (to seconds)
    TIME_TO_SECONDS = {
        's': 1.0,
        'sec': 1.0,
        'ms': 1e-3,
        'min': 60.0,
        'h': 3600.0,
        'hour': 3600.0,
        'day': 86400.0,
    }
    
    def __init__(self):
        self.avogadro = 6.02214076e23  # molecules/mol
    
    def convert_concentration(
        self, 
        value: float, 
        from_units: str, 
        to_units: str
    ) -> float:
        """
        Convert between concentration units.
        
        Args:
            value: Concentration value
            from_units: Source units
            to_units: Target units
            
        Returns:
            Converted value
        """
        if from_units == to_units:
            return value
        
        # Convert to Molar
        if from_units not in self.CONCENTRATION_TO_MOLAR:
            raise ValueError(f"Unknown concentration unit: {from_units}")
        
        value_in_molar = value * self.CONCENTRATION_TO_MOLAR[from_units]
        
        # Convert to target units
        if to_units not in self.CONCENTRATION_TO_MOLAR:
            raise ValueError(f"Unknown concentration unit: {to_units}")
        
        result = value_in_molar / self.CONCENTRATION_TO_MOLAR[to_units]
        return result
    
    def convert_time(
        self, 
        value: float, 
        from_units: str, 
        to_units: str
    ) -> float:
        """
        Convert between time units.
        
        Args:
            value: Time value
            from_units: Source units
            to_units: Target units
            
        Returns:
            Converted value
        """
        if from_units == to_units:
            return value
        
        # Convert to seconds
        if from_units not in self.TIME_TO_SECONDS:
            raise ValueError(f"Unknown time unit: {from_units}")
        
        value_in_seconds = value * self.TIME_TO_SECONDS[from_units]
        
        # Convert to target units
        if to_units not in self.TIME_TO_SECONDS:
            raise ValueError(f"Unknown time unit: {to_units}")
        
        result = value_in_seconds / self.TIME_TO_SECONDS[to_units]
        return result
    
    def convert_rate_constant(
        self,
        value: float,
        reaction_order: int,
        from_conc_units: str,
        to_conc_units: str,
        from_time_units: str,
        to_time_units: str
    ) -> float:
        """
        Convert rate constant units.
        
        For a reaction of order n, rate constant has units:
        [concentration]^(1-n) / [time]
        
        Args:
            value: Rate constant value
            reaction_order: Order of the reaction
            from_conc_units: Source concentration units
            to_conc_units: Target concentration units
            from_time_units: Source time units
            to_time_units: Target time units
            
        Returns:
            Converted rate constant
        """
        # Convert concentration part: [conc]^(1-n)
        if reaction_order != 1:
            conc_factor = self.convert_concentration(1.0, from_conc_units, to_conc_units)
            conc_factor = conc_factor ** (1 - reaction_order)
        else:
            conc_factor = 1.0
        
        # Convert time part: 1/[time]
        time_factor = self.convert_time(1.0, to_time_units, from_time_units)
        
        return value * conc_factor * time_factor
    
    def particles_to_concentration(
        self,
        num_particles: float,
        volume: float,
        volume_units: str = 'L'
    ) -> float:
        """
        Convert particle count to molar concentration.
        
        Args:
            num_particles: Number of particles/molecules
            volume: Volume
            volume_units: Units of volume ('L', 'mL', 'μL', etc.)
            
        Returns:
            Concentration in Molar
        """
        # Convert volume to liters
        volume_factors = {
            'L': 1.0,
            'mL': 1e-3,
            'uL': 1e-6,
            'μL': 1e-6,
            'nL': 1e-9,
        }
        
        if volume_units not in volume_factors:
            raise ValueError(f"Unknown volume unit: {volume_units}")
        
        volume_in_liters = volume * volume_factors[volume_units]
        
        # moles = particles / Avogadro
        moles = num_particles / self.avogadro
        
        # Molarity = moles / volume
        return moles / volume_in_liters
    
    def concentration_to_particles(
        self,
        concentration: float,
        conc_units: str,
        volume: float,
        volume_units: str = 'L'
    ) -> float:
        """
        Convert molar concentration to particle count.
        
        Args:
            concentration: Concentration value
            conc_units: Concentration units
            volume: Volume
            volume_units: Volume units
            
        Returns:
            Number of particles
        """
        # Convert to Molar
        conc_in_molar = self.convert_concentration(concentration, conc_units, 'M')
        
        # Convert volume to liters
        volume_factors = {'L': 1.0, 'mL': 1e-3, 'uL': 1e-6, 'μL': 1e-6, 'nL': 1e-9}
        volume_in_liters = volume * volume_factors.get(volume_units, 1.0)
        
        # particles = concentration * volume * Avogadro
        return conc_in_molar * volume_in_liters * self.avogadro
    
    def convert(self, value: float, from_units: str, to_units: str) -> float:
        """
        Generic conversion function that auto-detects unit type.
        
        Args:
            value: Value to convert
            from_units: Source units
            to_units: Target units
            
        Returns:
            Converted value
        """
        # Try concentration conversion
        if from_units in self.CONCENTRATION_TO_MOLAR and to_units in self.CONCENTRATION_TO_MOLAR:
            return self.convert_concentration(value, from_units, to_units)
        
        # Try time conversion
        if from_units in self.TIME_TO_SECONDS and to_units in self.TIME_TO_SECONDS:
            return self.convert_time(value, from_units, to_units)
        
        raise ValueError(f"Cannot convert from '{from_units}' to '{to_units}'")


# Convenience functions
def to_molar(value: float, from_units: str) -> float:
    """Convert concentration to Molar."""
    converter = UnitConverter()
    return converter.convert_concentration(value, from_units, 'M')


def to_seconds(value: float, from_units: str) -> float:
    """Convert time to seconds."""
    converter = UnitConverter()
    return converter.convert_time(value, from_units, 's')
