"""
Main CLI entry point for kinetics playground.

Provides commands for parsing, simulating, and visualizing reaction networks.
"""

import click
from kinetics_playground.cli.parser_cli import parse_command
from kinetics_playground.cli.simulate_cli import simulate_command
from kinetics_playground.cli.visualize_cli import visualize_command


@click.group()
@click.version_option(version='0.1.0')
def main():
    """
    Reaction Kinetics Playground - A framework for chemical reaction network simulation.
    
    Use 'kinetics COMMAND --help' for more information on a specific command.
    """
    pass


# Register subcommands
main.add_command(parse_command, name='parse')
main.add_command(simulate_command, name='simulate')
main.add_command(visualize_command, name='visualize')


# Additional commands
@main.command()
def presets():
    """List available preset reaction networks."""
    from kinetics_playground.api.presets import print_presets
    print_presets()


@main.command()
@click.argument('name')
@click.option('--initial', '-i', multiple=True, help='Initial condition: species=value')
@click.option('--time', '-t', default=100.0, help='Simulation time')
@click.option('--plot/--no-plot', default=True, help='Show plot')
def preset(name, initial, time, plot):
    """Run a preset reaction network."""
    from kinetics_playground.api.presets import load_preset
    import matplotlib.pyplot as plt
    
    try:
        network = load_preset(name)
        click.echo(f"Loaded preset: {name}")
        click.echo(network.summary())
        
        # Parse initial conditions
        ic = {}
        for init_str in initial:
            species, value = init_str.split('=')
            ic[species.strip()] = float(value)
        
        if not ic:
            click.echo("\nNo initial conditions specified. Use -i species=value")
            return
        
        # Simulate
        click.echo(f"\nRunning simulation for {time} time units...")
        result = network.simulate(ic, time_span=(0, time))
        
        if result.success:
            click.echo("✓ Simulation successful")
            
            # Show final state
            click.echo("\nFinal concentrations:")
            for species, conc in result.final_state().items():
                click.echo(f"  {species}: {conc:.6f}")
            
            if plot:
                network.plot(result)
        else:
            click.echo(f"✗ Simulation failed: {result.message}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    main()
