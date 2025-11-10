"""Interactive GUI using Plotly for real-time LJ potential exploration."""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional

from .model import (
    lj_potential,
    lj_force,
    lj_equilibrium,
    generate_lj_curve,
    morse_potential
)


def create_interactive_plot(
    epsilon_range: tuple = (0.1, 3.0),
    sigma_range: tuple = (2.0, 5.0),
    initial_epsilon: float = 1.0,
    initial_sigma: float = 3.5,
    show_force: bool = True,
    show_morse: bool = False,
    height: int = 700
):
    """
    Create an interactive Plotly figure with sliders for ε and σ.
    
    Parameters
    ----------
    epsilon_range : tuple, optional
        (min, max) range for epsilon slider (default: (0.1, 3.0))
    sigma_range : tuple, optional
        (min, max) range for sigma slider (default: (2.0, 5.0))
    initial_epsilon : float, optional
        Initial epsilon value (default: 1.0)
    initial_sigma : float, optional
        Initial sigma value (default: 3.5)
    show_force : bool, optional
        Whether to show force curve on secondary axis (default: True)
    show_morse : bool, optional
        Whether to show Morse potential comparison (default: False)
    height : int, optional
        Figure height in pixels (default: 700)
        
    Returns
    -------
    plotly.graph_objects.Figure
        Interactive Plotly figure with sliders
    """
    
    # Create figure with secondary y-axis if showing force
    if show_force:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
    else:
        fig = go.Figure()
    
    # Generate initial data
    r_min_default = 0.5 * initial_sigma
    r_max_default = 3.0 * initial_sigma
    
    # Create grid for all possible epsilon and sigma combinations
    epsilon_values = np.linspace(epsilon_range[0], epsilon_range[1], 30)
    sigma_values = np.linspace(sigma_range[0], sigma_range[1], 30)
    
    # Generate data for initial values
    r, V = generate_lj_curve(initial_epsilon, initial_sigma)
    F = lj_force(r, initial_epsilon, initial_sigma)
    r_eq, V_eq = lj_equilibrium(initial_epsilon, initial_sigma)
    
    # Add LJ potential trace
    if show_force:
        fig.add_trace(
            go.Scatter(
                x=r, y=V,
                mode='lines',
                name='LJ Potential',
                line=dict(color='blue', width=3),
                hovertemplate='r: %{x:.2f} Å<br>V: %{y:.2f} kJ/mol<extra></extra>'
            ),
            secondary_y=False
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=r, y=V,
                mode='lines',
                name='LJ Potential',
                line=dict(color='blue', width=3),
                hovertemplate='r: %{x:.2f} Å<br>V: %{y:.2f} kJ/mol<extra></extra>'
            )
        )
    
    # Add equilibrium point
    if show_force:
        fig.add_trace(
            go.Scatter(
                x=[r_eq], y=[V_eq],
                mode='markers',
                name=f'Minimum',
                marker=dict(color='red', size=10, symbol='circle'),
                hovertemplate=f'Equilibrium<br>r: {r_eq:.2f} Å<br>V: {V_eq:.2f} kJ/mol<extra></extra>'
            ),
            secondary_y=False
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=[r_eq], y=[V_eq],
                mode='markers',
                name=f'Minimum',
                marker=dict(color='red', size=10, symbol='circle'),
                hovertemplate=f'Equilibrium<br>r: {r_eq:.2f} Å<br>V: {V_eq:.2f} kJ/mol<extra></extra>'
            )
        )
    
    # Add V=0 reference line
    if show_force:
        fig.add_trace(
            go.Scatter(
                x=r, y=np.zeros_like(r),
                mode='lines',
                name='V = 0',
                line=dict(color='black', width=1, dash='dash'),
                showlegend=False,
                hoverinfo='skip'
            ),
            secondary_y=False
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=r, y=np.zeros_like(r),
                mode='lines',
                name='V = 0',
                line=dict(color='black', width=1, dash='dash'),
                showlegend=False,
                hoverinfo='skip'
            )
        )
    
    # Add force curve if requested
    if show_force:
        fig.add_trace(
            go.Scatter(
                x=r, y=F,
                mode='lines',
                name='LJ Force',
                line=dict(color='red', width=2, dash='dot'),
                opacity=0.7,
                hovertemplate='r: %{x:.2f} Å<br>F: %{y:.2f} kJ/mol/Å<extra></extra>'
            ),
            secondary_y=True
        )
        
        # Add F=0 reference line
        fig.add_trace(
            go.Scatter(
                x=r, y=np.zeros_like(r),
                mode='lines',
                name='F = 0',
                line=dict(color='red', width=1, dash='dash'),
                opacity=0.3,
                showlegend=False,
                hoverinfo='skip'
            ),
            secondary_y=True
        )
    
    # Add Morse potential if requested
    if show_morse:
        D_e = initial_epsilon
        r_e = r_eq
        a = np.sqrt(36 * initial_epsilon / (initial_sigma ** 2)) / 2
        V_morse = morse_potential(r, D_e, a, r_e)
        
        if show_force:
            fig.add_trace(
                go.Scatter(
                    x=r, y=V_morse,
                    mode='lines',
                    name='Morse Potential',
                    line=dict(color='green', width=2, dash='dash'),
                    opacity=0.7,
                    hovertemplate='r: %{x:.2f} Å<br>V: %{y:.2f} kJ/mol<extra></extra>'
                ),
                secondary_y=False
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=r, y=V_morse,
                    mode='lines',
                    name='Morse Potential',
                    line=dict(color='green', width=2, dash='dash'),
                    opacity=0.7,
                    hovertemplate='r: %{x:.2f} Å<br>V: %{y:.2f} kJ/mol<extra></extra>'
                )
            )
    
    # Create slider steps
    steps_epsilon = []
    for eps in epsilon_values:
        step = dict(
            method="skip",
            args=[],
            label=f"{eps:.2f}"
        )
        steps_epsilon.append(step)
    
    steps_sigma = []
    for sig in sigma_values:
        step = dict(
            method="skip",
            args=[],
            label=f"{sig:.2f}"
        )
        steps_sigma.append(step)
    
    # Add sliders
    sliders = [
        dict(
            active=np.argmin(np.abs(epsilon_values - initial_epsilon)),
            yanchor="top",
            y=0.15,
            xanchor="left",
            x=0.05,
            currentvalue=dict(
                prefix="ε (epsilon): ",
                suffix=" kJ/mol",
                visible=True,
                xanchor="left"
            ),
            pad=dict(b=10, t=50),
            len=0.4,
            steps=steps_epsilon,
            name="epsilon"
        ),
        dict(
            active=np.argmin(np.abs(sigma_values - initial_sigma)),
            yanchor="top",
            y=0.15,
            xanchor="right",
            x=0.95,
            currentvalue=dict(
                prefix="σ (sigma): ",
                suffix=" Å",
                visible=True,
                xanchor="right"
            ),
            pad=dict(b=10, t=50),
            len=0.4,
            steps=steps_sigma,
            name="sigma"
        )
    ]
    
    # Update layout
    title_text = f'Lennard-Jones Potential Explorer<br><sub>ε = {initial_epsilon:.2f} kJ/mol, σ = {initial_sigma:.2f} Å</sub>'
    
    if show_force:
        fig.update_xaxes(title_text="Distance r (Å)", gridcolor='lightgray')
        fig.update_yaxes(title_text="Potential V(r) (kJ/mol)", secondary_y=False, 
                        gridcolor='lightgray', titlefont=dict(color='blue'))
        fig.update_yaxes(title_text="Force F(r) (kJ/mol/Å)", secondary_y=True,
                        titlefont=dict(color='red'))
    else:
        fig.update_xaxes(title_text="Distance r (Å)", gridcolor='lightgray')
        fig.update_yaxes(title_text="Potential V(r) (kJ/mol)", gridcolor='lightgray')
    
    fig.update_layout(
        title=dict(text=title_text, x=0.5, xanchor='center'),
        sliders=sliders,
        height=height,
        hovermode='closest',
        template='plotly_white',
        legend=dict(x=0.98, y=0.98, xanchor='right', yanchor='top'),
        margin=dict(b=150)
    )
    
    # Add updatemenus for interactive parameter control
    # Note: Full interactivity requires JavaScript callback, which is beyond static Plotly
    # For notebook use, consider ipywidgets integration
    
    return fig


def create_interactive_widget(
    epsilon_range: tuple = (0.1, 3.0),
    sigma_range: tuple = (2.0, 5.0),
    initial_epsilon: float = 1.0,
    initial_sigma: float = 3.5
):
    """
    Create an interactive widget using ipywidgets (for Jupyter notebooks).
    
    This provides real-time updates as sliders are moved.
    
    Parameters
    ----------
    epsilon_range : tuple, optional
        (min, max) range for epsilon slider
    sigma_range : tuple, optional
        (min, max) range for sigma slider
    initial_epsilon : float, optional
        Initial epsilon value
    initial_sigma : float, optional
        Initial sigma value
        
    Returns
    -------
    ipywidgets.interactive
        Interactive widget with plot
    """
    try:
        from ipywidgets import interactive, FloatSlider, Checkbox, VBox, HBox, Output
        import plotly.graph_objects as go
    except ImportError:
        print("Error: ipywidgets not installed. Install with: pip install ipywidgets")
        return None
    
    def plot_lj(epsilon, sigma, show_force, show_morse):
        """Inner function to update plot based on slider values."""
        # Generate data
        r, V = generate_lj_curve(epsilon, sigma)
        r_eq, V_eq = lj_equilibrium(epsilon, sigma)
        
        # Create figure
        if show_force:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Add potential
            fig.add_trace(
                go.Scatter(x=r, y=V, mode='lines', name='LJ Potential',
                          line=dict(color='blue', width=3)),
                secondary_y=False
            )
            
            # Add equilibrium
            fig.add_trace(
                go.Scatter(x=[r_eq], y=[V_eq], mode='markers', name='Minimum',
                          marker=dict(color='red', size=10)),
                secondary_y=False
            )
            
            # Add force
            F = lj_force(r, epsilon, sigma)
            fig.add_trace(
                go.Scatter(x=r, y=F, mode='lines', name='LJ Force',
                          line=dict(color='red', width=2, dash='dot')),
                secondary_y=True
            )
            
            fig.update_yaxes(title_text="Potential (kJ/mol)", secondary_y=False)
            fig.update_yaxes(title_text="Force (kJ/mol/Å)", secondary_y=True)
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=r, y=V, mode='lines', name='LJ Potential',
                                    line=dict(color='blue', width=3)))
            fig.add_trace(go.Scatter(x=[r_eq], y=[V_eq], mode='markers', name='Minimum',
                                    marker=dict(color='red', size=10)))
            fig.update_yaxes(title_text="Potential V(r) (kJ/mol)")
        
        # Add Morse if requested
        if show_morse:
            D_e = epsilon
            r_e = r_eq
            a = np.sqrt(36 * epsilon / (sigma ** 2)) / 2
            V_morse = morse_potential(r, D_e, a, r_e)
            fig.add_trace(
                go.Scatter(x=r, y=V_morse, mode='lines', name='Morse',
                          line=dict(color='green', width=2, dash='dash')),
                secondary_y=False if show_force else None
            )
        
        fig.update_xaxes(title_text="Distance r (Å)")
        fig.update_layout(
            title=f'Lennard-Jones Potential (ε={epsilon:.2f} kJ/mol, σ={sigma:.2f} Å)<br>' + 
                  f'<sub>r_min = {r_eq:.2f} Å, V_min = {V_eq:.2f} kJ/mol</sub>',
            height=600,
            template='plotly_white'
        )
        
        fig.show()
    
    # Create widgets
    epsilon_slider = FloatSlider(
        value=initial_epsilon,
        min=epsilon_range[0],
        max=epsilon_range[1],
        step=0.05,
        description='ε (kJ/mol):',
        continuous_update=True
    )
    
    sigma_slider = FloatSlider(
        value=initial_sigma,
        min=sigma_range[0],
        max=sigma_range[1],
        step=0.1,
        description='σ (Å):',
        continuous_update=True
    )
    
    force_checkbox = Checkbox(
        value=True,
        description='Show Force',
        indent=False
    )
    
    morse_checkbox = Checkbox(
        value=False,
        description='Show Morse',
        indent=False
    )
    
    # Create interactive widget
    widget = interactive(
        plot_lj,
        epsilon=epsilon_slider,
        sigma=sigma_slider,
        show_force=force_checkbox,
        show_morse=morse_checkbox
    )
    
    return widget


def save_interactive_html(
    filename: str = "lj_interactive.html",
    epsilon_range: tuple = (0.1, 3.0),
    sigma_range: tuple = (2.0, 5.0),
    initial_epsilon: float = 1.0,
    initial_sigma: float = 3.5,
    show_force: bool = True
):
    """
    Save an interactive HTML file that can be opened in a browser.
    
    Parameters
    ----------
    filename : str, optional
        Output HTML filename (default: "lj_interactive.html")
    epsilon_range : tuple, optional
        Range for epsilon values
    sigma_range : tuple, optional
        Range for sigma values
    initial_epsilon : float, optional
        Initial epsilon value
    initial_sigma : float, optional
        Initial sigma value
    show_force : bool, optional
        Whether to show force curve
    """
    fig = create_interactive_plot(
        epsilon_range, sigma_range, initial_epsilon, initial_sigma, show_force
    )
    fig.write_html(filename)
    print(f"Interactive plot saved to {filename}")
    print(f"Open the file in a web browser to explore the LJ potential!")


if __name__ == '__main__':
    # Demo: create and show interactive plot
    fig = create_interactive_plot()
    fig.show()
