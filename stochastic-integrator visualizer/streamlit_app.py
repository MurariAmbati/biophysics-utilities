"""
Interactive Streamlit web app for Stochastic Integrator Visualizer.

Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from stochastic_integrator_visualizer.core import (
    euler_maruyama,
    milstein,
    deterministic_solver,
    run_ensemble,
    make_constant_drift,
    make_linear_drift,
    make_constant_diffusion,
    make_linear_diffusion,
    make_constant_diffusion_derivative,
    make_linear_diffusion_derivative,
)
from stochastic_integrator_visualizer.visualize import (
    plot_trajectory,
    plot_multiple_trajectories,
    plot_histogram,
    plot_phase_space,
    create_summary_plot,
)
from stochastic_integrator_visualizer.constants import (
    DEFAULT_X0,
    DEFAULT_DT,
    DEFAULT_STEPS,
    DEFAULT_DRIFT,
    DEFAULT_DIFFUSION,
    SLIDER_DT_MIN,
    SLIDER_DT_MAX,
    SLIDER_STEPS_MIN,
    SLIDER_STEPS_MAX,
    SLIDER_DRIFT_MIN,
    SLIDER_DRIFT_MAX,
    SLIDER_DIFFUSION_MIN,
    SLIDER_DIFFUSION_MAX,
    SLIDER_NUM_TRAJ_MIN,
    SLIDER_NUM_TRAJ_MAX,
)


# Page configuration
st.set_page_config(
    page_title="Stochastic Integrator Visualizer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Title and description
st.title("📈 Stochastic Integrator Visualizer")
st.markdown("""
Interactive simulator for **Stochastic Differential Equations (SDEs)**. 
Explore how noise and drift affect trajectories using various integration methods.

**SDE Form:** $dx_t = a(x_t, t) \, dt + b(x_t, t) \, dW_t$

where:
- $a(x,t)$ = drift term
- $b(x,t)$ = diffusion term  
- $dW_t$ = Wiener process increment
""")

st.divider()

# Sidebar for parameters
with st.sidebar:
    st.header("⚙️ Simulation Parameters")
    
    # Method selection
    method = st.selectbox(
        "Integration Method",
        ["euler-maruyama", "milstein", "deterministic"],
        index=0,
        help="Numerical method for solving the SDE"
    )
    
    st.subheader("Initial Conditions")
    x0 = st.number_input(
        "Initial value (x₀)",
        value=DEFAULT_X0,
        format="%.2f",
        help="Starting value of the trajectory"
    )
    
    st.subheader("Time Parameters")
    col1, col2 = st.columns(2)
    with col1:
        dt = st.slider(
            "Time step (dt)",
            min_value=SLIDER_DT_MIN,
            max_value=SLIDER_DT_MAX,
            value=DEFAULT_DT,
            format="%.3f",
            help="Size of each time step"
        )
    with col2:
        steps = st.slider(
            "Number of steps",
            min_value=SLIDER_STEPS_MIN,
            max_value=SLIDER_STEPS_MAX,
            value=DEFAULT_STEPS,
            step=100,
            help="Total number of integration steps"
        )
    
    total_time = dt * steps
    st.info(f"**Total simulation time:** {total_time:.2f} s")
    
    st.subheader("SDE Coefficients")
    
    # Drift settings
    drift_type = st.radio(
        "Drift function type",
        ["constant", "linear"],
        horizontal=True,
        help="Shape of drift term: constant a or linear a·x"
    )
    drift_coeff = st.slider(
        "Drift coefficient (a)",
        min_value=SLIDER_DRIFT_MIN,
        max_value=SLIDER_DRIFT_MAX,
        value=DEFAULT_DRIFT,
        step=0.1,
        help="Coefficient for the drift term"
    )
    
    # Display drift equation
    if drift_type == "constant":
        st.latex(r"a(x,t) = " + f"{drift_coeff:.2f}")
    else:
        st.latex(r"a(x,t) = " + f"{drift_coeff:.2f} \\cdot x")
    
    # Diffusion settings
    diffusion_type = st.radio(
        "Diffusion function type",
        ["constant", "linear"],
        horizontal=True,
        help="Shape of diffusion term: constant b or linear b·x"
    )
    diffusion_coeff = st.slider(
        "Diffusion coefficient (b)",
        min_value=SLIDER_DIFFUSION_MIN,
        max_value=SLIDER_DIFFUSION_MAX,
        value=DEFAULT_DIFFUSION,
        step=0.05,
        help="Coefficient for the diffusion (noise) term"
    )
    
    # Display diffusion equation
    if diffusion_type == "constant":
        st.latex(r"b(x,t) = " + f"{diffusion_coeff:.2f}")
    else:
        st.latex(r"b(x,t) = " + f"{diffusion_coeff:.2f} \\cdot x")
    
    st.subheader("Ensemble Options")
    num_trajectories = st.slider(
        "Number of trajectories",
        min_value=SLIDER_NUM_TRAJ_MIN,
        max_value=SLIDER_NUM_TRAJ_MAX,
        value=1,
        help="Number of trajectories to simulate (1 = single trajectory)"
    )
    
    st.subheader("Randomness Control")
    use_seed = st.checkbox("Use fixed random seed", value=False)
    if use_seed:
        seed = st.number_input("Random seed", value=42, min_value=0, step=1)
    else:
        seed = None
    
    # Buttons
    st.divider()
    col_run, col_reset = st.columns(2)
    with col_run:
        run_button = st.button("▶️ Run Simulation", type="primary", use_container_width=True)
    with col_reset:
        if st.button("🔄 Reset", use_container_width=True):
            st.rerun()


# Main content area
if run_button or 'first_run' not in st.session_state:
    st.session_state.first_run = True
    
    # Create drift and diffusion functions
    if drift_type == "constant":
        drift_func = make_constant_drift(drift_coeff)
    else:
        drift_func = make_linear_drift(drift_coeff)
    
    if diffusion_type == "constant":
        diffusion_func = make_constant_diffusion(diffusion_coeff)
        diffusion_deriv = make_constant_diffusion_derivative(diffusion_coeff)
    else:
        diffusion_func = make_linear_diffusion(diffusion_coeff)
        diffusion_deriv = make_linear_diffusion_derivative(diffusion_coeff)
    
    # Run simulation
    with st.spinner("Running simulation..."):
        if num_trajectories == 1:
            # Single trajectory
            if method == "euler-maruyama":
                t, x = euler_maruyama(drift_func, diffusion_func, x0, dt, steps, seed)
            elif method == "milstein":
                t, x = milstein(drift_func, diffusion_func, diffusion_deriv, x0, dt, steps, seed)
            else:  # deterministic
                t, x = deterministic_solver(drift_func, x0, dt, steps)
            
            # Display results
            st.subheader("📊 Results")
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Initial Value", f"{x[0]:.4f}")
            with col2:
                st.metric("Final Value", f"{x[-1]:.4f}")
            with col3:
                st.metric("Mean", f"{np.mean(x):.4f}")
            with col4:
                st.metric("Std Dev", f"{np.std(x):.4f}")
            
            # Plots
            tab1, tab2 = st.tabs(["📈 Trajectory", "🔄 Phase Space"])
            
            with tab1:
                fig, ax = plt.subplots(figsize=(12, 6))
                plot_trajectory(
                    t, x,
                    title=f"{method.replace('-', ' ').title()} Integration",
                    ax=ax,
                    show=False
                )
                st.pyplot(fig)
                plt.close()
            
            with tab2:
                fig, ax = plt.subplots(figsize=(10, 8))
                plot_phase_space(t, x, ax=ax, show=False)
                st.pyplot(fig)
                plt.close()
        
        else:
            # Ensemble simulation
            t, trajectories, final_values = run_ensemble(
                method=method,
                a=drift_func,
                b=diffusion_func,
                x0=x0,
                dt=dt,
                steps=steps,
                num_trajectories=num_trajectories,
                base_seed=seed,
                b_prime=diffusion_deriv if method == "milstein" else None,
            )
            
            # Display results
            st.subheader("📊 Ensemble Results")
            
            # Statistics
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Mean Final", f"{np.mean(final_values):.4f}")
            with col2:
                st.metric("Std Final", f"{np.std(final_values):.4f}")
            with col3:
                st.metric("Min Final", f"{np.min(final_values):.4f}")
            with col4:
                st.metric("Max Final", f"{np.max(final_values):.4f}")
            with col5:
                st.metric("Trajectories", num_trajectories)
            
            # Plots
            tab1, tab2, tab3, tab4 = st.tabs([
                "📈 All Trajectories",
                "📊 Histogram",
                "🔄 Phase Space",
                "📋 Summary"
            ])
            
            with tab1:
                fig, ax = plt.subplots(figsize=(12, 6))
                plot_multiple_trajectories(
                    t, trajectories,
                    title=f"{method.replace('-', ' ').title()}: {num_trajectories} Trajectories",
                    ax=ax,
                    show=False,
                    alpha=min(0.7, 30.0 / num_trajectories)  # Adjust alpha for visibility
                )
                st.pyplot(fig)
                plt.close()
            
            with tab2:
                fig, ax = plt.subplots(figsize=(12, 6))
                plot_histogram(final_values, ax=ax, show=False)
                st.pyplot(fig)
                plt.close()
            
            with tab3:
                fig, ax = plt.subplots(figsize=(10, 8))
                plot_phase_space(t, trajectories[0], ax=ax, show=False)
                st.pyplot(fig)
                plt.close()
            
            with tab4:
                fig, axes = create_summary_plot(
                    t, trajectories[:min(50, num_trajectories)],  # Limit for performance
                    final_values,
                    method_name=method.replace('-', ' ').title(),
                    show=False
                )
                st.pyplot(fig)
                plt.close()
    
    st.success("✅ Simulation complete!")

else:
    st.info("👈 Configure parameters in the sidebar and click **Run Simulation**")
    
    # Show example
    st.subheader("📚 About")
    st.markdown("""
    This tool simulates **Stochastic Differential Equations (SDEs)** of the form:
    
    $$dx_t = a(x_t, t) \, dt + b(x_t, t) \, dW_t$$
    
    **Available Methods:**
    - **Euler-Maruyama**: First-order method, fast and simple
    - **Milstein**: Second-order method, more accurate for nonlinear diffusion
    - **Deterministic**: ODE solver (b=0), no stochastic term
    
    **Drift Functions:**
    - **Constant**: $a(x,t) = a$ (linear growth)
    - **Linear**: $a(x,t) = a \\cdot x$ (exponential growth/decay)
    
    **Diffusion Functions:**
    - **Constant**: $b(x,t) = b$ (additive noise)
    - **Linear**: $b(x,t) = b \\cdot x$ (multiplicative noise)
    
    **Tips:**
    - Use **ensemble simulations** to visualize stochastic variance
    - Set a **fixed seed** for reproducible results
    - Try **negative drift** with **positive diffusion** for mean-reverting behavior
    - Use **linear diffusion** for geometric Brownian motion
    """)

# Footer
st.divider()
st.caption("🔬 Stochastic Integrator Visualizer | Built with Streamlit")
