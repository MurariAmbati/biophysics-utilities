"""
Preset reaction networks for quick experimentation.

Includes classic models from chemical kinetics and systems biology.
"""

from typing import Dict, List
from kinetics_playground.api.reaction_network import ReactionNetwork


PRESETS = {}


def register_preset(name: str, description: str):
    """Decorator to register a preset."""
    def decorator(func):
        PRESETS[name] = {
            'function': func,
            'description': description
        }
        return func
    return decorator


@register_preset(
    "simple_equilibrium",
    "Simple reversible reaction: A <-> B"
)
def simple_equilibrium() -> ReactionNetwork:
    """Simple reversible reaction."""
    reactions = [
        "A -> B ; 1.0",
        "B -> A ; 0.5"
    ]
    network = ReactionNetwork(reactions, name="simple_equilibrium")
    return network


@register_preset(
    "enzyme_kinetics",
    "Michaelis-Menten enzyme kinetics: E + S <-> ES -> E + P"
)
def enzyme_kinetics() -> ReactionNetwork:
    """Michaelis-Menten enzyme kinetics."""
    reactions = [
        "E + S -> ES ; 1.0",
        "ES -> E + S ; 0.5",
        "ES -> E + P ; 0.2"
    ]
    network = ReactionNetwork(reactions, name="enzyme_kinetics")
    return network


@register_preset(
    "brusselator",
    "Brusselator oscillator: A -> X, B + X -> Y + D, 2X + Y -> 3X, X -> E"
)
def brusselator() -> ReactionNetwork:
    """
    Brusselator chemical oscillator.
    
    Classic example of oscillating chemical reaction.
    """
    reactions = [
        "A -> X ; 1.0",
        "B + X -> Y + D ; 1.0",
        "2X + Y -> 3X ; 1.0",
        "X -> E ; 1.0"
    ]
    network = ReactionNetwork(reactions, name="brusselator")
    # Set A and B as constant species
    network.model.get_species('A').is_constant = True
    network.model.get_species('B').is_constant = True
    return network


@register_preset(
    "lotka_volterra",
    "Lotka-Volterra predator-prey: X + Y -> 2X, X -> 0, Y -> 2Y"
)
def lotka_volterra() -> ReactionNetwork:
    """
    Lotka-Volterra predator-prey model.
    
    Classic oscillating system representing predator-prey dynamics.
    """
    reactions = [
        "X + Y -> 2X ; 0.1",  # Prey reproduction with predator
        "X -> 0 ; 0.01",       # Prey death
        "Y -> 2Y ; 0.1"        # Predator reproduction
    ]
    network = ReactionNetwork(reactions, name="lotka_volterra")
    return network


@register_preset(
    "oregonator",
    "Oregonator (Belousov-Zhabotinsky reaction)"
)
def oregonator() -> ReactionNetwork:
    """
    Oregonator model of Belousov-Zhabotinsky reaction.
    
    Famous oscillating chemical reaction.
    """
    reactions = [
        "A + Y -> X + P ; 1.28",
        "X + Y -> 2P ; 8.0e5",
        "A + X -> 2X + 2Z ; 8.0e2",
        "2X -> A + P ; 2.0e3",
        "B + Z -> Y ; 1.0"
    ]
    network = ReactionNetwork(reactions, name="oregonator")
    # A and B are in excess
    network.model.get_species('A').is_constant = True
    network.model.get_species('B').is_constant = True
    return network


@register_preset(
    "glycolysis",
    "Simplified glycolysis pathway"
)
def glycolysis() -> ReactionNetwork:
    """Simplified glycolysis model."""
    reactions = [
        "Glucose + ATP -> G6P + ADP ; 0.1",
        "G6P -> F6P ; 0.5",
        "F6P + ATP -> FBP + ADP ; 0.1",
        "FBP -> 2GAP ; 1.0",
        "GAP + NAD -> BPG + NADH ; 0.2",
        "BPG + ADP -> 3PG + ATP ; 0.3",
        "3PG -> PEP ; 0.4",
        "PEP + ADP -> Pyruvate + ATP ; 0.2"
    ]
    network = ReactionNetwork(reactions, name="glycolysis")
    return network


@register_preset(
    "competitive_inhibition",
    "Enzyme with competitive inhibitor"
)
def competitive_inhibition() -> ReactionNetwork:
    """Enzyme kinetics with competitive inhibitor."""
    reactions = [
        "E + S -> ES ; 1.0",
        "ES -> E + S ; 0.5",
        "ES -> E + P ; 0.2",
        "E + I -> EI ; 2.0",
        "EI -> E + I ; 0.1"
    ]
    network = ReactionNetwork(reactions, name="competitive_inhibition")
    return network


@register_preset(
    "circadian_clock",
    "Simplified circadian clock model"
)
def circadian_clock() -> ReactionNetwork:
    """Simple circadian clock model."""
    reactions = [
        "0 -> mRNA ; 1.0",
        "mRNA -> mRNA + Protein ; 0.5",
        "mRNA -> 0 ; 0.1",
        "Protein -> 0 ; 0.05",
        "Protein -> Protein_n ; 0.2",
        "Protein_n -> Protein ; 0.1"
    ]
    network = ReactionNetwork(reactions, name="circadian_clock")
    return network


@register_preset(
    "autocatalysis",
    "Simple autocatalytic reaction: A + B -> 2B"
)
def autocatalysis() -> ReactionNetwork:
    """Autocatalytic reaction showing nonlinear dynamics."""
    reactions = [
        "A + B -> 2B ; 0.8",
        "B -> C ; 0.4"
    ]
    network = ReactionNetwork(reactions, name="autocatalysis")
    return network


@register_preset(
    "sequential_reactions",
    "Sequential first-order reactions: A -> B -> C -> D"
)
def sequential_reactions() -> ReactionNetwork:
    """Chain of sequential reactions."""
    reactions = [
        "A -> B ; 1.0",
        "B -> C ; 0.5",
        "C -> D ; 0.2"
    ]
    network = ReactionNetwork(reactions, name="sequential_reactions")
    return network


def load_preset(name: str) -> ReactionNetwork:
    """
    Load a preset reaction network.
    
    Args:
        name: Preset name
        
    Returns:
        ReactionNetwork instance
        
    Raises:
        ValueError: If preset not found
    """
    if name not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise ValueError(
            f"Unknown preset '{name}'. "
            f"Available presets: {available}"
        )
    
    return PRESETS[name]['function']()


def list_presets() -> Dict[str, str]:
    """
    List all available presets.
    
    Returns:
        Dict mapping preset names to descriptions
    """
    return {
        name: info['description']
        for name, info in PRESETS.items()
    }


def print_presets():
    """Print formatted list of available presets."""
    print("Available Reaction Network Presets:")
    print("=" * 60)
    for name, description in list_presets().items():
        print(f"\n{name}:")
        print(f"  {description}")
    print()
