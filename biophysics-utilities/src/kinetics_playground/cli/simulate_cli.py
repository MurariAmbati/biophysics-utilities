"""Simulation CLI commands."""

import click
import json
from pathlib import Path


@click.command()
@click.option('--input', '-i', 'input_file', required=True, type=click.Path(exists=True),
              help='Input file with reactions (.yaml, .json, .txt)')
@click.option('--initial', '-c', multiple=True,
              help='Initial concentration: species=value')
@click.option('--time', '-t', default=100.0, help='Simulation end time')
@click.option('--points', '-n', default=1000, help='Number of time points')
@click.option('--method', '-m', default='LSODA', 
              type=click.Choice(['RK45', 'RK23', 'DOP853', 'Radau', 'BDF', 'LSODA']),
              help='Integration method')
@click.option('--output', '-o', type=click.Path(), help='Output file (.csv)')
@click.option('--plot/--no-plot', default=False, help='Display plot')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def simulate_command(input_file, initial, time, points, method, output, plot, verbose):
    """
    Simulate a reaction network from file.
    
    Examples:
        kinetics simulate -i reactions.yaml -c A=1.0 -c B=1.0 -t 100
        kinetics simulate -i model.json --plot
    """
    from kinetics_playground.api import ReactionNetwork
    from kinetics_playground.utils.logger import set_log_level
    import logging
    
    if verbose:
        set_log_level(logging.DEBUG)
    
    try:
        # Load network
        click.echo(f"Loading reactions from {input_file}...")
        network = ReactionNetwork()
        
        # Parse file
        from kinetics_playground.core.parser import ReactionParser
        parser = ReactionParser()
        reactions = parser.parse_from_file(input_file)
        
        for rxn in reactions:
            network.model.add_reaction(
                reactants=rxn.reactants,
                products=rxn.products,
                rate_constant=rxn.rate_constant,
                reversible=rxn.reversible,
                kinetic_law=rxn.kinetic_law,
                parameters=rxn.parameters
            )
        
        network._rebuild_kinetic_system()
        
        click.echo(f"Loaded {len(reactions)} reactions")
        click.echo(f"Species: {', '.join(network.get_species_names())}")
        
        # Parse initial conditions
        ic = {}
        for init_str in initial:
            if '=' not in init_str:
                click.echo(f"Invalid initial condition format: {init_str}", err=True)
                continue
            species, value = init_str.split('=')
            ic[species.strip()] = float(value)
        
        if not ic:
            click.echo("Error: No initial conditions specified. Use -c species=value", err=True)
            raise click.Abort()
        
        # Validate
        click.echo("\nValidating model...")
        issues = network.validate()
        if any(issue.severity == 'error' for issue in issues):
            click.echo("Validation failed. Aborting.", err=True)
            raise click.Abort()
        
        # Simulate
        click.echo(f"\nSimulating from t=0 to t={time}...")
        click.echo(f"Method: {method}, Points: {points}")
        
        result = network.simulate(
            initial_conditions=ic,
            time_span=(0, time),
            num_points=points,
            method=method
        )
        
        if result.success:
            click.echo("✓ Simulation successful")
            click.echo(f"  Function evaluations: {result.nfev}")
            
            # Final state
            click.echo("\nFinal concentrations:")
            for species, conc in result.final_state().items():
                click.echo(f"  {species}: {conc:.6e}")
            
            # Save output
            if output:
                from kinetics_playground.utils.exporters import export_results_to_csv
                export_results_to_csv(result, output)
                click.echo(f"\n✓ Results saved to {output}")
            
            # Plot
            if plot:
                import matplotlib.pyplot as plt
                network.plot(result)
        else:
            click.echo(f"✗ Simulation failed: {result.message}", err=True)
            raise click.Abort()
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()
