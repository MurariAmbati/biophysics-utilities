"""
Internal representation of reaction network models.

Provides data structures for species, reactions, and complete reaction networks.
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
import numpy as np


@dataclass
class Species:
    """Represents a chemical species in the reaction network."""
    name: str
    index: int
    initial_concentration: float = 0.0
    is_constant: bool = False  # For boundary species
    units: str = "M"  # Molar concentration by default
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if isinstance(other, Species):
            return self.name == other.name
        return False
    
    def __repr__(self):
        return f"Species(name='{self.name}', index={self.index})"


@dataclass
class Reaction:
    """Represents a single chemical reaction."""
    index: int
    reactants: Dict[str, float]  # species name -> stoichiometric coefficient
    products: Dict[str, float]
    rate_constant: Optional[float] = None
    reversible: bool = False
    kinetic_law: str = "mass_action"
    parameters: Dict[str, float] = field(default_factory=dict)
    name: Optional[str] = None
    
    def __post_init__(self):
        if self.name is None:
            # Auto-generate name
            reactant_str = " + ".join(
                f"{v:.0f}{k}" if v != 1 else k 
                for k, v in self.reactants.items()
            )
            product_str = " + ".join(
                f"{v:.0f}{k}" if v != 1 else k 
                for k, v in self.products.items()
            )
            arrow = "<->" if self.reversible else "->"
            self.name = f"R{self.index}: {reactant_str} {arrow} {product_str}"
    
    def get_all_species(self) -> Set[str]:
        """Get all species involved in this reaction."""
        return set(self.reactants.keys()) | set(self.products.keys())
    
    def net_stoichiometry(self) -> Dict[str, float]:
        """
        Calculate net stoichiometry for each species.
        
        Returns:
            Dictionary mapping species to net change (products - reactants)
        """
        net = {}
        
        # Subtract reactants
        for species, coeff in self.reactants.items():
            net[species] = net.get(species, 0.0) - coeff
        
        # Add products
        for species, coeff in self.products.items():
            net[species] = net.get(species, 0.0) + coeff
        
        return net
    
    def __repr__(self):
        return f"Reaction({self.name})"


class ReactionModel:
    """
    Complete internal representation of a reaction network.
    
    Manages species list, reaction list, and provides methods for
    querying network topology and constructing computational models.
    """
    
    def __init__(self):
        self.species: List[Species] = []
        self.reactions: List[Reaction] = []
        self._species_map: Dict[str, Species] = {}  # name -> Species
        self._species_index_map: Dict[str, int] = {}  # name -> index
    
    def add_species(self, name: str, initial_concentration: float = 0.0, 
                   is_constant: bool = False) -> Species:
        """
        Add a species to the model.
        
        Args:
            name: Species name
            initial_concentration: Initial concentration value
            is_constant: Whether this is a boundary/constant species
            
        Returns:
            The created Species object
        """
        if name in self._species_map:
            return self._species_map[name]
        
        index = len(self.species)
        species = Species(
            name=name,
            index=index,
            initial_concentration=initial_concentration,
            is_constant=is_constant
        )
        
        self.species.append(species)
        self._species_map[name] = species
        self._species_index_map[name] = index
        
        return species
    
    def add_reaction(self, reactants: Dict[str, float], products: Dict[str, float],
                    rate_constant: Optional[float] = None, reversible: bool = False,
                    kinetic_law: str = "mass_action", 
                    parameters: Optional[Dict[str, float]] = None) -> Reaction:
        """
        Add a reaction to the model.
        
        Args:
            reactants: Dictionary of reactant species and their coefficients
            products: Dictionary of product species and their coefficients
            rate_constant: Forward rate constant
            reversible: Whether the reaction is reversible
            kinetic_law: Type of kinetic law to apply
            parameters: Additional parameters for the kinetic law
            
        Returns:
            The created Reaction object
        """
        # Ensure all species exist
        for species_name in set(reactants.keys()) | set(products.keys()):
            if species_name not in self._species_map:
                self.add_species(species_name)
        
        index = len(self.reactions)
        reaction = Reaction(
            index=index,
            reactants=reactants,
            products=products,
            rate_constant=rate_constant,
            reversible=reversible,
            kinetic_law=kinetic_law,
            parameters=parameters or {}
        )
        
        self.reactions.append(reaction)
        return reaction
    
    def get_species(self, name: str) -> Optional[Species]:
        """Get species by name."""
        return self._species_map.get(name)
    
    def get_species_index(self, name: str) -> int:
        """Get species index by name."""
        return self._species_index_map[name]
    
    def set_initial_concentration(self, species_name: str, concentration: float):
        """Set initial concentration for a species."""
        species = self.get_species(species_name)
        if species:
            species.initial_concentration = concentration
        else:
            raise ValueError(f"Species '{species_name}' not found in model")
    
    def get_initial_concentrations(self) -> np.ndarray:
        """Get array of initial concentrations for all species."""
        return np.array([s.initial_concentration for s in self.species])
    
    def num_species(self) -> int:
        """Get number of species in the model."""
        return len(self.species)
    
    def num_reactions(self) -> int:
        """Get number of reactions in the model."""
        return len(self.reactions)
    
    def get_species_names(self) -> List[str]:
        """Get list of all species names."""
        return [s.name for s in self.species]
    
    def get_reaction_names(self) -> List[str]:
        """Get list of all reaction names."""
        return [r.name for r in self.reactions]
    
    def summary(self) -> str:
        """Generate a text summary of the model."""
        lines = [
            f"Reaction Network Model",
            f"  Species: {self.num_species()}",
            f"  Reactions: {self.num_reactions()}",
            f"",
            f"Species:",
        ]
        
        for species in self.species:
            const_str = " (constant)" if species.is_constant else ""
            lines.append(f"  {species.name}: {species.initial_concentration}{const_str}")
        
        lines.append("")
        lines.append("Reactions:")
        
        for reaction in self.reactions:
            lines.append(f"  {reaction.name}")
            if reaction.rate_constant is not None:
                lines.append(f"    k = {reaction.rate_constant}")
        
        return "\n".join(lines)
    
    def __repr__(self):
        return f"ReactionModel(species={self.num_species()}, reactions={self.num_reactions()})"
