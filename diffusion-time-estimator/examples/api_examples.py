#!/usr/bin/env python3
"""
Example script demonstrating the use of diffusion-time-estimator as a Python library.
"""

from diffusion_time_estimator import (
    diffusion_coefficient,
    diffusion_time,
    mean_square_displacement,
    format_time,
    format_coefficient,
    WATER_VISCOSITY,
    ROOM_TEMPERATURE
)
import numpy as np

def main():
    print("=" * 60)
    print("Diffusion Time Estimator - Python API Examples")
    print("=" * 60)
    
    # Example 1: Small molecule in water
    print("\n1. Small molecule (1 nm radius) in water:")
    radius = 1e-9  # 1 nm
    D = diffusion_coefficient(radius, WATER_VISCOSITY, ROOM_TEMPERATURE)
    print(f"   Diffusion coefficient: {format_coefficient(D)}")
    
    # How long to diffuse 1 μm?
    distance = 1e-6
    t = diffusion_time(distance, D, dims=3)
    print(f"   Time to diffuse {distance*1e6:.1f} μm: {format_time(t)}")
    
    # Example 2: Protein in cytoplasm
    print("\n2. Small protein (2 nm radius) in cytoplasm:")
    radius = 2e-9  # 2 nm
    cytoplasm_viscosity = 3e-3  # 3x water
    body_temp = 310  # K
    D = diffusion_coefficient(radius, cytoplasm_viscosity, body_temp)
    print(f"   Diffusion coefficient: {format_coefficient(D)}")
    
    distance = 10e-6  # 10 μm (typical cell size)
    t = diffusion_time(distance, D, dims=3)
    print(f"   Time to cross a cell ({distance*1e6:.0f} μm): {format_time(t)}")
    
    # Example 3: 2D diffusion in membrane
    print("\n3. Membrane protein (3 nm radius) diffusing in 2D:")
    radius = 3e-9
    membrane_viscosity = 5e-3  # Higher viscosity
    D = diffusion_coefficient(radius, membrane_viscosity, ROOM_TEMPERATURE)
    print(f"   Diffusion coefficient: {format_coefficient(D)}")
    
    distance = 100e-9  # 100 nm
    t = diffusion_time(distance, D, dims=2)
    print(f"   Time to diffuse {distance*1e9:.0f} nm in 2D: {format_time(t)}")
    
    # Example 4: Mean-square displacement
    print("\n4. Mean-square displacement over time:")
    D = 1e-10  # m²/s
    times = np.array([1e-6, 1e-3, 1.0])  # μs, ms, s
    for t in times:
        msd = mean_square_displacement(D, t, dims=3)
        print(f"   At t = {format_time(t)}: MSD = {msd:.3e} m²")
    
    # Example 5: Comparing different sizes
    print("\n5. Comparing molecules of different sizes:")
    print("   (all in water at room temperature)")
    radii = [0.5e-9, 1e-9, 2e-9, 5e-9, 10e-9]  # nm
    for r in radii:
        D = diffusion_coefficient(r, WATER_VISCOSITY, ROOM_TEMPERATURE)
        print(f"   Radius = {r*1e9:.1f} nm: D = {format_coefficient(D)}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
