"""
Interactive dashboard for reaction kinetics using Streamlit.

Provides web-based GUI for model exploration and visualization.
"""

from typing import Optional, Dict, List
import numpy as np

try:
    import streamlit as st
    import plotly.graph_objects as go
    import plotly.express as px
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


class Dashboard:
    """
    Streamlit-based interactive dashboard for reaction kinetics.
    
    Note: Requires streamlit and plotly packages.
    """
    
    def __init__(self):
        if not STREAMLIT_AVAILABLE:
            raise ImportError(
                "Dashboard requires streamlit and plotly. "
                "Install with: pip install streamlit plotly"
            )
    
    def run(self, model, initial_state: Optional[Dict] = None):
        """
        Launch interactive dashboard.
        
        Args:
            model: ReactionNetwork model
            initial_state: Optional initial conditions
        """
        st.title("⚗️ Reaction Kinetics Playground")
        st.markdown("Interactive simulation and visualization dashboard")
        
        # Sidebar for parameters
        st.sidebar.header("Simulation Parameters")
        
        # Time settings
        t_end = st.sidebar.number_input("Simulation Time", value=100.0, min_value=0.1)
        n_points = st.sidebar.number_input("Number of Points", value=1000, min_value=10)
        
        # Initial conditions
        st.sidebar.header("Initial Conditions")
        init_conds = {}
        for species_name in model.get_species_names():
            default_val = initial_state.get(species_name, 0.0) if initial_state else 0.0
            init_conds[species_name] = st.sidebar.number_input(
                f"[{species_name}]₀",
                value=float(default_val),
                min_value=0.0,
                format="%.4f"
            )
        
        # Rate constants
        st.sidebar.header("Rate Constants")
        rate_constants = {}
        for rxn in model.model.reactions:
            if rxn.rate_constant is not None:
                rate_constants[f"k_{rxn.index}"] = st.sidebar.number_input(
                    f"k_{rxn.index} ({rxn.name})",
                    value=float(rxn.rate_constant),
                    min_value=0.0,
                    format="%.6f"
                )
        
        # Run simulation button
        if st.sidebar.button("▶️ Run Simulation"):
            with st.spinner("Running simulation..."):
                result = model.simulate(
                    initial_conditions=init_conds,
                    time_span=(0, t_end),
                    num_points=int(n_points)
                )
                
                # Store result in session state
                st.session_state['result'] = result
                st.success("✅ Simulation complete!")
        
        # Display results
        if 'result' in st.session_state:
            result = st.session_state['result']
            
            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["📈 Time Course", "🔄 Phase Space", "📊 Summary"])
            
            with tab1:
                self.plot_time_course_plotly(result)
            
            with tab2:
                self.plot_phase_space_plotly(result)
            
            with tab3:
                self.show_summary(result, model)
    
    def plot_time_course_plotly(self, result):
        """Plot time course using Plotly."""
        st.subheader("Species Concentrations vs Time")
        
        # Species selection
        selected_species = st.multiselect(
            "Select species to display:",
            options=result.species_names,
            default=result.species_names
        )
        
        if selected_species:
            fig = go.Figure()
            
            for species_name in selected_species:
                y = result.get_species(species_name)
                fig.add_trace(go.Scatter(
                    x=result.t,
                    y=y,
                    mode='lines',
                    name=species_name,
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Concentration",
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def plot_phase_space_plotly(self, result):
        """Plot phase space using Plotly."""
        st.subheader("Phase Space Trajectory")
        
        if len(result.species_names) < 2:
            st.warning("Need at least 2 species for phase space plot")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            species_x = st.selectbox("X-axis species:", result.species_names, index=0)
        
        with col2:
            species_y = st.selectbox("Y-axis species:", result.species_names, index=min(1, len(result.species_names)-1))
        
        x = result.get_species(species_x)
        y = result.get_species(species_y)
        
        fig = go.Figure()
        
        # Trajectory line
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Trajectory',
            line=dict(width=2)
        ))
        
        # Start point
        fig.add_trace(go.Scatter(
            x=[x[0]],
            y=[y[0]],
            mode='markers',
            name='Start',
            marker=dict(size=12, color='green', symbol='circle')
        ))
        
        # End point
        fig.add_trace(go.Scatter(
            x=[x[-1]],
            y=[y[-1]],
            mode='markers',
            name='End',
            marker=dict(size=12, color='red', symbol='circle')
        ))
        
        fig.update_layout(
            xaxis_title=f"[{species_x}]",
            yaxis_title=f"[{species_y}]",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def show_summary(self, result, model):
        """Display simulation summary."""
        st.subheader("Simulation Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Species Count", len(result.species_names))
            st.metric("Reactions Count", model.model.num_reactions())
            st.metric("Time Points", len(result.t))
        
        with col2:
            st.metric("Final Time", f"{result.t[-1]:.2f}")
            st.metric("Integration Success", "✅" if result.success else "❌")
            st.metric("Function Evaluations", result.nfev)
        
        # Final concentrations table
        st.subheader("Final Concentrations")
        final_state = result.final_state()
        
        import pandas as pd
        df = pd.DataFrame({
            'Species': list(final_state.keys()),
            'Concentration': list(final_state.values())
        })
        st.dataframe(df, use_container_width=True)


def launch_dashboard(model, initial_state: Optional[Dict] = None):
    """
    Convenience function to launch dashboard.
    
    Args:
        model: ReactionNetwork model
        initial_state: Optional initial conditions
    """
    dashboard = Dashboard()
    dashboard.run(model, initial_state)
