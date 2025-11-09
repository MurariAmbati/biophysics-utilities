"""
Reaction parser for converting text-based reaction input into structured data.

Supports multiple input formats:
- Simple text: "A + B -> C ; k1"
- YAML/JSON structured format
- Custom .rkp format
"""

import re
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
import yaml
import json


@dataclass
class ParsedReaction:
    """Container for a parsed reaction."""
    reactants: Dict[str, float]  # species -> stoichiometric coefficient
    products: Dict[str, float]
    rate_constant: Optional[float]
    reversible: bool = False
    kinetic_law: str = "mass_action"
    parameters: Dict[str, float] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class ReactionParser:
    """
    Parser for chemical reaction strings.
    
    Examples:
        >>> parser = ReactionParser()
        >>> reaction = parser.parse_single("A + B -> C ; 0.1")
        >>> reaction.reactants
        {'A': 1.0, 'B': 1.0}
        >>> reaction.products
        {'C': 1.0}
    """
    
    # Regex patterns for parsing
    SIMPLE_REACTION_PATTERN = re.compile(
        r'^([^-<>]+?)\s*(-?>|<->|<-)\s*([^;]+?)(?:\s*;\s*(.+))?$'
    )
    STOICH_PATTERN = re.compile(r'(\d*\.?\d*)\s*\*?\s*([A-Za-z_]\w*)')
    
    def __init__(self):
        self.species_set = set()
    
    def parse_single(self, reaction_string: str) -> ParsedReaction:
        """
        Parse a single reaction string.
        
        Format: "reactants -> products ; rate_constant [; kinetic_law]"
        
        Args:
            reaction_string: String representation of reaction
            
        Returns:
            ParsedReaction object
            
        Raises:
            ValueError: If reaction string is malformed
        """
        reaction_string = reaction_string.strip()
        
        match = self.SIMPLE_REACTION_PATTERN.match(reaction_string)
        if not match:
            raise ValueError(f"Invalid reaction format: {reaction_string}")
        
        reactants_str, arrow, products_str, params_str = match.groups()
        
        # Parse reactants and products
        reactants = self._parse_species_list(reactants_str)
        products = self._parse_species_list(products_str)
        
        # Determine reversibility
        reversible = arrow == '<->'
        
        # Parse parameters
        rate_constant = None
        kinetic_law = "mass_action"
        parameters = {}
        
        if params_str:
            parts = [p.strip() for p in params_str.split(';')]
            # First parameter is rate constant
            try:
                rate_constant = float(parts[0])
            except ValueError:
                raise ValueError(f"Invalid rate constant: {parts[0]}")
            
            # Additional parameters
            if len(parts) > 1:
                kinetic_law = parts[1]
            if len(parts) > 2:
                # Parse additional parameters as key=value pairs
                for param in parts[2:]:
                    if '=' in param:
                        key, value = param.split('=')
                        parameters[key.strip()] = float(value.strip())
        
        # Update species set
        self.species_set.update(reactants.keys())
        self.species_set.update(products.keys())
        
        return ParsedReaction(
            reactants=reactants,
            products=products,
            rate_constant=rate_constant,
            reversible=reversible,
            kinetic_law=kinetic_law,
            parameters=parameters
        )
    
    def _parse_species_list(self, species_str: str) -> Dict[str, float]:
        """
        Parse a species list from a string like "2A + B + 3C".
        
        Returns:
            Dictionary mapping species names to stoichiometric coefficients
        """
        species_dict = {}
        
        # Split by + and parse each term
        terms = [t.strip() for t in species_str.split('+')]
        
        for term in terms:
            if not term:
                continue
                
            match = self.STOICH_PATTERN.match(term)
            if match:
                coeff_str, species = match.groups()
                coeff = float(coeff_str) if coeff_str else 1.0
                
                if species in species_dict:
                    species_dict[species] += coeff
                else:
                    species_dict[species] = coeff
            else:
                raise ValueError(f"Invalid species term: {term}")
        
        return species_dict
    
    def parse_multiple(self, reaction_strings: List[str]) -> List[ParsedReaction]:
        """
        Parse multiple reaction strings.
        
        Args:
            reaction_strings: List of reaction string representations
            
        Returns:
            List of ParsedReaction objects
        """
        return [self.parse_single(rs) for rs in reaction_strings]
    
    def parse_from_yaml(self, yaml_string: str) -> List[ParsedReaction]:
        """
        Parse reactions from YAML format.
        
        Expected format:
            reactions:
              - equation: A + B -> C
                rate_constant: 0.1
                kinetic_law: mass_action
              - equation: C -> A + B
                rate_constant: 0.05
        """
        data = yaml.safe_load(yaml_string)
        reactions = []
        
        for rxn_data in data.get('reactions', []):
            if 'equation' in rxn_data:
                # Parse equation part
                eq_str = rxn_data['equation']
                if 'rate_constant' in rxn_data:
                    eq_str += f" ; {rxn_data['rate_constant']}"
                if 'kinetic_law' in rxn_data:
                    eq_str += f" ; {rxn_data['kinetic_law']}"
                
                reaction = self.parse_single(eq_str)
                
                # Override with explicit parameters
                if 'parameters' in rxn_data:
                    reaction.parameters.update(rxn_data['parameters'])
                
                reactions.append(reaction)
            elif 'reactants' in rxn_data and 'products' in rxn_data:
                # Direct format
                reactions.append(ParsedReaction(
                    reactants=rxn_data['reactants'],
                    products=rxn_data['products'],
                    rate_constant=rxn_data.get('rate_constant'),
                    reversible=rxn_data.get('reversible', False),
                    kinetic_law=rxn_data.get('kinetic_law', 'mass_action'),
                    parameters=rxn_data.get('parameters', {})
                ))
        
        return reactions
    
    def parse_from_json(self, json_string: str) -> List[ParsedReaction]:
        """Parse reactions from JSON format."""
        data = json.loads(json_string)
        reactions = []
        
        for rxn_data in data.get('reactions', []):
            if 'equation' in rxn_data:
                eq_str = rxn_data['equation']
                if 'k' in rxn_data or 'rate_constant' in rxn_data:
                    k = rxn_data.get('k', rxn_data.get('rate_constant'))
                    eq_str += f" ; {k}"
                reaction = self.parse_single(eq_str)
            else:
                reaction = ParsedReaction(
                    reactants=rxn_data.get('reactants', {}),
                    products=rxn_data.get('products', {}),
                    rate_constant=rxn_data.get('k', rxn_data.get('rate_constant')),
                    reversible=rxn_data.get('reversible', False),
                    kinetic_law=rxn_data.get('kinetic_law', 'mass_action'),
                    parameters=rxn_data.get('parameters', {})
                )
            reactions.append(reaction)
        
        return reactions
    
    def parse_from_file(self, filepath: str) -> List[ParsedReaction]:
        """
        Parse reactions from a file.
        
        Automatically detects format based on extension:
        - .yaml, .yml: YAML format
        - .json: JSON format
        - .rkp, .txt: Simple text format (one reaction per line)
        """
        with open(filepath, 'r') as f:
            content = f.read()
        
        if filepath.endswith(('.yaml', '.yml')):
            return self.parse_from_yaml(content)
        elif filepath.endswith('.json'):
            return self.parse_from_json(content)
        else:
            # Text format: one reaction per line, skip comments and empty lines
            lines = [
                line.strip() 
                for line in content.split('\n') 
                if line.strip() and not line.strip().startswith('#')
            ]
            return self.parse_multiple(lines)
    
    def get_all_species(self) -> List[str]:
        """Get list of all species encountered during parsing."""
        return sorted(self.species_set)
    
    def reset(self):
        """Reset the parser state."""
        self.species_set.clear()


# Convenience functions
def parse_reactions(reactions: Union[str, List[str], dict]) -> List[ParsedReaction]:
    """
    Parse reactions from various input formats.
    
    Args:
        reactions: Can be:
            - Single reaction string
            - List of reaction strings
            - Dict with 'reactions' key (for programmatic construction)
            
    Returns:
        List of ParsedReaction objects
    """
    parser = ReactionParser()
    
    if isinstance(reactions, str):
        if '\n' in reactions:
            # Multi-line string
            return parser.parse_multiple(reactions.strip().split('\n'))
        else:
            return [parser.parse_single(reactions)]
    elif isinstance(reactions, list):
        return parser.parse_multiple(reactions)
    elif isinstance(reactions, dict):
        # Convert dict to JSON and parse
        return parser.parse_from_json(json.dumps({'reactions': reactions}))
    else:
        raise TypeError(f"Unsupported reaction format: {type(reactions)}")
