"""Parser CLI commands."""

import click
from kinetics_playground.core.parser import ReactionParser


@click.command()
@click.argument('reaction', nargs=-1, required=True)
@click.option('--file', '-f', type=click.Path(exists=True), help='Read reactions from file')
@click.option('--validate/--no-validate', default=True, help='Validate parsed reactions')
def parse_command(reaction, file, validate):
    """
    Parse reaction strings and display the result.
    
    Examples:
        kinetics parse "A + B -> C ; 0.1"
        kinetics parse -f reactions.yaml
    """
    parser = ReactionParser()
    
    try:
        if file:
            parsed_reactions = parser.parse_from_file(file)
            click.echo(f"Parsed {len(parsed_reactions)} reactions from {file}")
        else:
            reaction_string = ' '.join(reaction)
            if not reaction_string:
                click.echo("Error: No reaction specified", err=True)
                raise click.Abort()
            
            parsed_reactions = [parser.parse_single(reaction_string)]
            click.echo(f"Parsed reaction:")
        
        # Display parsed reactions
        for i, rxn in enumerate(parsed_reactions, 1):
            click.echo(f"\nReaction {i}:")
            click.echo(f"  Reactants: {rxn.reactants}")
            click.echo(f"  Products: {rxn.products}")
            click.echo(f"  Rate constant: {rxn.rate_constant}")
            click.echo(f"  Reversible: {rxn.reversible}")
            click.echo(f"  Kinetic law: {rxn.kinetic_law}")
            if rxn.parameters:
                click.echo(f"  Parameters: {rxn.parameters}")
        
        # Display species
        species = parser.get_all_species()
        click.echo(f"\nSpecies found: {', '.join(species)}")
        
        if validate:
            click.echo("\n✓ Parsing successful")
    
    except Exception as e:
        click.echo(f"Error parsing reactions: {e}", err=True)
        raise click.Abort()
