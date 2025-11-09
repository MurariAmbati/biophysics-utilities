"""Visualization CLI commands."""

import click


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--species', '-s', multiple=True, help='Species to plot (default: all)')
@click.option('--phase', '-p', nargs=2, help='Phase space plot: species1 species2')
@click.option('--output', '-o', type=click.Path(), help='Save figure to file')
@click.option('--format', '-f', type=click.Choice(['png', 'pdf', 'svg']), default='png',
              help='Output format')
@click.option('--dpi', default=300, help='Resolution for raster formats')
def visualize_command(input_file, species, phase, output, format, dpi):
    """
    Visualize simulation results from CSV file.
    
    Examples:
        kinetics visualize results.csv
        kinetics visualize results.csv -s A -s B
        kinetics visualize results.csv --phase A B -o plot.png
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    from kinetics_playground.visualization.plotter import Plotter
    
    try:
        # Load data
        click.echo(f"Loading data from {input_file}...")
        df = pd.read_csv(input_file)
        
        # Get time and species
        if 't' not in df.columns:
            click.echo("Error: CSV must contain 't' column", err=True)
            raise click.Abort()
        
        t = df['t'].values
        available_species = [col for col in df.columns if col != 't']
        
        click.echo(f"Found {len(available_species)} species: {', '.join(available_species)}")
        
        plotter = Plotter()
        
        if phase:
            # Phase space plot
            species_x, species_y = phase
            
            if species_x not in available_species or species_y not in available_species:
                click.echo(f"Error: Species not found in data", err=True)
                raise click.Abort()
            
            x = df[species_x].values
            y = df[species_y].values
            
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.plot(x, y, linewidth=2)
            ax.plot(x[0], y[0], 'go', markersize=10, label='Start')
            ax.plot(x[-1], y[-1], 'ro', markersize=10, label='End')
            ax.set_xlabel(f'[{species_x}]', fontsize=12)
            ax.set_ylabel(f'[{species_y}]', fontsize=12)
            ax.set_title(f'Phase Space: {species_x} vs {species_y}', fontsize=14)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            click.echo(f"Generated phase space plot: {species_x} vs {species_y}")
        
        else:
            # Time course plot
            species_to_plot = list(species) if species else available_species
            
            fig, ax = plt.subplots(figsize=(10, 6))
            for sp in species_to_plot:
                if sp in available_species:
                    ax.plot(t, df[sp].values, label=sp, linewidth=2)
            
            ax.set_xlabel('Time', fontsize=12)
            ax.set_ylabel('Concentration', fontsize=12)
            ax.set_title('Species Concentrations vs Time', fontsize=14)
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)
            
            click.echo(f"Generated time course plot for {len(species_to_plot)} species")
        
        # Save or show
        if output:
            output_file = output if '.' in output else f"{output}.{format}"
            plt.savefig(output_file, dpi=dpi, bbox_inches='tight')
            click.echo(f"✓ Saved to {output_file}")
        else:
            click.echo("Displaying plot...")
            plt.show()
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
