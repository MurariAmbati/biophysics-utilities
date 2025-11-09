"""Tests for reaction parser."""

import pytest
from kinetics_playground.core.parser import ReactionParser, ParsedReaction


class TestReactionParser:
    """Test suite for reaction parser."""
    
    def test_simple_reaction(self):
        """Test parsing simple reaction."""
        parser = ReactionParser()
        reaction = parser.parse_single("A + B -> C ; 0.1")
        
        assert reaction.reactants == {'A': 1.0, 'B': 1.0}
        assert reaction.products == {'C': 1.0}
        assert reaction.rate_constant == 0.1
        assert not reaction.reversible
    
    def test_reversible_reaction(self):
        """Test parsing reversible reaction."""
        parser = ReactionParser()
        reaction = parser.parse_single("A <-> B ; 1.0")
        
        assert reaction.reactants == {'A': 1.0}
        assert reaction.products == {'B': 1.0}
        assert reaction.reversible
    
    def test_stoichiometry(self):
        """Test stoichiometric coefficients."""
        parser = ReactionParser()
        reaction = parser.parse_single("2A + 3B -> C ; 0.5")
        
        assert reaction.reactants == {'A': 2.0, 'B': 3.0}
        assert reaction.products == {'C': 1.0}
    
    def test_multiple_reactions(self):
        """Test parsing multiple reactions."""
        parser = ReactionParser()
        reactions_str = ["A -> B ; 1.0", "B -> C ; 0.5"]
        reactions = parser.parse_multiple(reactions_str)
        
        assert len(reactions) == 2
        assert reactions[0].rate_constant == 1.0
        assert reactions[1].rate_constant == 0.5
    
    def test_species_collection(self):
        """Test species collection."""
        parser = ReactionParser()
        parser.parse_single("A + B -> C ; 0.1")
        parser.parse_single("C + D -> E ; 0.2")
        
        species = parser.get_all_species()
        assert set(species) == {'A', 'B', 'C', 'D', 'E'}
    
    def test_invalid_format(self):
        """Test error handling for invalid format."""
        parser = ReactionParser()
        
        with pytest.raises(ValueError):
            parser.parse_single("invalid reaction string")


if __name__ == '__main__':
    pytest.main([__file__])
