#!/usr/bin/env python3
"""
Demonstration script for the Protein Hydration Shell Estimator.

This script showcases various use cases and features of the tool.
"""

from src.model import HydrationShellEstimator
from src.utils import nm2_to_m2

def demo_basic_usage():
    """Demonstrate basic usage."""
    print("="*70)
    print("DEMO 1: Basic Usage")
    print("="*70)
    
    estimator = HydrationShellEstimator(
        surface_area=1.5e-17,
        hydrophilicity_index=0.65,
        shell_thickness=3.0
    )
    
    print(estimator.get_summary())


def demo_different_proteins():
    """Demonstrate calculations for different protein types."""
    print("\n" + "="*70)
    print("DEMO 2: Different Protein Types")
    print("="*70)
    
    proteins = [
        ("Small hydrophobic peptide", 5.0e-17, 0.3, 2.8),
        ("Typical globular protein", 1.0e-16, 0.6, 3.0),
        ("Large hydrophilic protein", 3.0e-16, 0.75, 3.5),
        ("Membrane protein domain", 8.0e-17, 0.15, 2.5),
    ]
    
    print(f"\n{'Protein Type':<30} {'Surface (nm²)':<15} {'H_index':<10} {'Waters':<10}")
    print("-" * 70)
    
    for name, area, hydro, thick in proteins:
        est = HydrationShellEstimator(area, hydro, thick)
        results = est.compute()
        area_nm2 = area / 1e-18
        print(f"{name:<30} {area_nm2:<15.0f} {hydro:<10.2f} {results['N_H2O']:<10.0f}")


def demo_parameter_effects():
    """Demonstrate how parameters affect water count."""
    print("\n" + "="*70)
    print("DEMO 3: Effect of Hydrophilicity")
    print("="*70)
    
    base_area = 1.5e-17
    base_thickness = 3.0
    
    print(f"\nFixed: Surface area = {base_area:.2e} m², Thickness = {base_thickness} Å")
    print(f"\n{'Hydrophilicity':<20} {'Water Count':<15} {'Density (×10²⁸)':<20}")
    print("-" * 70)
    
    for hydro in [0.0, 0.25, 0.5, 0.75, 1.0]:
        est = HydrationShellEstimator(base_area, hydro, base_thickness)
        results = est.compute()
        density_scaled = results['rho_shell'] / 1e28
        print(f"{hydro:<20.2f} {results['N_H2O']:<15.0f} {density_scaled:<20.2f}")
    
    print("\n" + "="*70)
    print("DEMO 4: Effect of Shell Thickness")
    print("="*70)
    
    base_hydro = 0.65
    
    print(f"\nFixed: Surface area = {base_area:.2e} m², Hydrophilicity = {base_hydro}")
    print(f"\n{'Thickness (Å)':<20} {'Volume (×10⁻²⁷)':<20} {'Water Count':<15}")
    print("-" * 70)
    
    for thick in [2.5, 3.0, 3.5, 4.0]:
        est = HydrationShellEstimator(base_area, base_hydro, thick)
        results = est.compute()
        volume_scaled = results['V_shell'] / 1e-27
        print(f"{thick:<20.1f} {volume_scaled:<20.2f} {results['N_H2O']:<15.0f}")


def demo_unit_conversion():
    """Demonstrate unit conversion utilities."""
    print("\n" + "="*70)
    print("DEMO 5: Unit Conversions")
    print("="*70)
    
    print("\nConverting surface area from nm² to m²:")
    areas_nm2 = [50, 100, 150, 300]
    
    for area_nm2 in areas_nm2:
        area_m2 = nm2_to_m2(area_nm2)
        est = HydrationShellEstimator(area_m2, 0.6, 3.0)
        results = est.compute()
        print(f"  {area_nm2} nm² = {area_m2:.2e} m² → {results['N_H2O']:.0f} waters")


def demo_detailed_properties():
    """Show all computed properties in detail."""
    print("\n" + "="*70)
    print("DEMO 6: Detailed Properties")
    print("="*70)
    
    est = HydrationShellEstimator(1.5e-17, 0.65, 3.0)
    results = est.compute()
    
    print("\nInput Parameters:")
    print(f"  Surface area:          {est.surface_area:.2e} m²")
    print(f"  Surface area:          {est.surface_area/1e-18:.1f} nm²")
    print(f"  Hydrophilicity index:  {est.hydrophilicity_index:.2f}")
    print(f"  Shell thickness:       {est.shell_thickness:.1f} Å")
    
    print("\nComputed Properties:")
    print(f"  Shell volume:          {results['V_shell']:.2e} m³")
    print(f"  Shell density:         {results['rho_shell']:.2e} molecules/m³")
    print(f"  Water count:           {results['N_H2O']:.2e} molecules")
    print(f"  Water count:           ~{results['N_H2O']:.0f} molecules")
    print(f"  Water amount:          {results['n_H2O']:.2e} mol")
    
    # Additional calculations
    f_hydrophilic = 0.8 + 0.4 * est.hydrophilicity_index
    print(f"\nDerived Values:")
    print(f"  f_hydrophilic factor:  {f_hydrophilic:.3f}")
    print(f"  Density enhancement:   {f_hydrophilic:.1%} of bulk water")


def main():
    """Run all demonstrations."""
    print("\n" + "="*70)
    print(" "*15 + "PROTEIN HYDRATION SHELL ESTIMATOR")
    print(" "*25 + "Demonstration")
    print("="*70)
    
    demo_basic_usage()
    demo_different_proteins()
    demo_parameter_effects()
    demo_unit_conversion()
    demo_detailed_properties()
    
    print("\n" + "="*70)
    print("Demonstrations complete!")
    print("="*70)
    print("\nFor more examples, see:")
    print("  - examples/protein_surface_example.txt")
    print("  - README.md")
    print("\nTo run interactively: python -m src.cli")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
