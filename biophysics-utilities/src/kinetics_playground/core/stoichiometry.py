"""
Stoichiometric matrix construction and operations.

The stoichiometric matrix S encodes the network topology where S[i,j] represents
the net change in species i due to reaction j.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from kinetics_playground.core.model import ReactionModel, Reaction


class StoichiometricMatrix:
    """
    Constructs and manages the stoichiometric matrix for a reaction network.
    
    The matrix S has dimensions (num_species x num_reactions), where:
    - S[i,j] = net change in species i due to reaction j
    - Positive values indicate production
    - Negative values indicate consumption
    """
    
    def __init__(self, model: ReactionModel):
        """
        Initialize stoichiometric matrix from a reaction model.
        
        Args:
            model: ReactionModel containing species and reactions
        """
        self.model = model
        self.matrix = self._build_matrix()
        self.species_names = model.get_species_names()
        self.reaction_names = model.get_reaction_names()
    
    def _build_matrix(self) -> np.ndarray:
        """
        Construct the stoichiometric matrix.
        
        Returns:
            numpy array of shape (num_species, num_reactions)
        """
        num_species = self.model.num_species()
        num_reactions = self.model.num_reactions()
        
        S = np.zeros((num_species, num_reactions))
        
        for reaction in self.model.reactions:
            j = reaction.index
            net_stoich = reaction.net_stoichiometry()
            
            for species_name, coeff in net_stoich.items():
                i = self.model.get_species_index(species_name)
                S[i, j] = coeff
        
        return S
    
    def get_matrix(self) -> np.ndarray:
        """Get the stoichiometric matrix."""
        return self.matrix
    
    def get_species_vector(self, reaction_index: int) -> np.ndarray:
        """
        Get the stoichiometric vector for a specific reaction.
        
        Args:
            reaction_index: Index of the reaction
            
        Returns:
            1D array of stoichiometric coefficients for all species
        """
        return self.matrix[:, reaction_index]
    
    def get_reaction_vector(self, species_index: int) -> np.ndarray:
        """
        Get all stoichiometric coefficients for a specific species.
        
        Args:
            species_index: Index of the species
            
        Returns:
            1D array showing how each reaction affects this species
        """
        return self.matrix[species_index, :]
    
    def compute_flux(self, reaction_rates: np.ndarray) -> np.ndarray:
        """
        Compute the rate of change for all species given reaction rates.
        
        d[S]/dt = S · v
        
        Args:
            reaction_rates: Array of reaction rate values (length = num_reactions)
            
        Returns:
            Array of species time derivatives (length = num_species)
        """
        return self.matrix @ reaction_rates
    
    def rank(self) -> int:
        """
        Calculate the rank of the stoichiometric matrix.
        
        The rank indicates the number of independent reactions.
        """
        return np.linalg.matrix_rank(self.matrix)
    
    def nullspace(self) -> np.ndarray:
        """
        Calculate the nullspace (kernel) of the stoichiometric matrix.
        
        The nullspace represents conservation laws in the system.
        Vectors in the nullspace correspond to linear combinations of
        species that remain constant throughout the reaction dynamics.
        
        Returns:
            Array where each column is a basis vector for the nullspace
        """
        u, s, vh = np.linalg.svd(self.matrix)
        null_mask = (s <= 1e-10)
        null_space = vh[null_mask].T
        return null_space
    
    def conservation_laws(self) -> List[Dict[str, float]]:
        """
        Find conservation laws (moiety conservations) in the network.
        
        Returns:
            List of dictionaries, where each dict maps species names to
            coefficients in a conservation law
        """
        null_vecs = self.nullspace()
        
        if null_vecs.size == 0:
            return []
        
        laws = []
        for i in range(null_vecs.shape[1]):
            vec = null_vecs[:, i]
            # Only include species with non-negligible coefficients
            law = {
                self.species_names[j]: float(vec[j])
                for j in range(len(self.species_names))
                if abs(vec[j]) > 1e-10
            }
            if law:
                laws.append(law)
        
        return laws
    
    def is_balanced(self, reaction_index: int, element_composition: Dict[str, Dict[str, int]]) -> bool:
        """
        Check if a reaction is element-balanced.
        
        Args:
            reaction_index: Index of reaction to check
            element_composition: Dict mapping species names to element counts
                                Example: {'A': {'C': 1, 'O': 2}, ...}
        
        Returns:
            True if the reaction conserves all elements
        """
        reaction = self.model.reactions[reaction_index]
        
        # Collect all elements
        all_elements = set()
        for species in reaction.get_all_species():
            if species in element_composition:
                all_elements.update(element_composition[species].keys())
        
        # Check balance for each element
        for element in all_elements:
            balance = 0.0
            
            # Subtract reactants
            for species, coeff in reaction.reactants.items():
                if species in element_composition:
                    balance -= coeff * element_composition[species].get(element, 0)
            
            # Add products
            for species, coeff in reaction.products.items():
                if species in element_composition:
                    balance += coeff * element_composition[species].get(element, 0)
            
            if abs(balance) > 1e-10:
                return False
        
        return True
    
    def to_latex(self) -> str:
        """
        Generate LaTeX representation of the stoichiometric matrix.
        
        Returns:
            LaTeX string for the matrix
        """
        latex = r"\begin{bmatrix}" + "\n"
        
        for i in range(self.matrix.shape[0]):
            row = " & ".join(f"{val:.2f}" if val != 0 else "0" 
                           for val in self.matrix[i, :])
            latex += row
            if i < self.matrix.shape[0] - 1:
                latex += r" \\" + "\n"
        
        latex += "\n" + r"\end{bmatrix}"
        return latex
    
    def summary(self) -> str:
        """Generate a text summary of the stoichiometric matrix."""
        lines = [
            f"Stoichiometric Matrix",
            f"  Shape: {self.matrix.shape[0]} species × {self.matrix.shape[1]} reactions",
            f"  Rank: {self.rank()}",
            f"  Conservation laws: {len(self.conservation_laws())}",
            "",
        ]
        
        # Find conservation laws
        laws = self.conservation_laws()
        if laws:
            lines.append("Conservation Laws:")
            for idx, law in enumerate(laws, 1):
                law_str = " + ".join(f"{coeff:.3f}·[{species}]" 
                                     for species, coeff in law.items())
                lines.append(f"  {idx}. {law_str} = constant")
            lines.append("")
        
        return "\n".join(lines)
    
    def __repr__(self):
        return f"StoichiometricMatrix(shape={self.matrix.shape})"
