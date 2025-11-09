"""
Convert reaction network to SBML format.

Usage: python convert_to_sbml.py input.yaml output.xml
"""

import sys
from kinetics_playground.api import ReactionNetwork
from kinetics_playground.utils.exporters import export_to_sbml

def main():
    if len(sys.argv) < 3:
        print("Usage: python convert_to_sbml.py input_file output_file")
        print("  input_file: YAML, JSON, or text file with reactions")
        print("  output_file: Output SBML file (.xml)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print(f"Loading reactions from {input_file}...")
    
    # Parse reactions
    from kinetics_playground.core.parser import ReactionParser
    parser = ReactionParser()
    reactions = parser.parse_from_file(input_file)
    
    # Create network
    network = ReactionNetwork()
    for rxn in reactions:
        network.model.add_reaction(
            reactants=rxn.reactants,
            products=rxn.products,
            rate_constant=rxn.rate_constant,
            reversible=rxn.reversible
        )
    
    print(f"Loaded {len(reactions)} reactions")
    print(f"Species: {', '.join(network.get_species_names())}")
    
    # Export to SBML
    print(f"\nExporting to SBML format...")
    try:
        export_to_sbml(network.model, output_file)
        print(f"✓ Successfully exported to {output_file}")
    except ImportError:
        print("Error: SBML export requires python-libsbml")
        print("Install with: pip install python-libsbml")
        sys.exit(1)

if __name__ == '__main__':
    main()
