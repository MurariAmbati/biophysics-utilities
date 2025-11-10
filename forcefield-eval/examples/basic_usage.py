"""
Example script demonstrating basic usage of Force Field Evaluator.
"""

import numpy as np
from src.evaluator import ForceFieldEvaluator, create_distance_range
from src.constants import DEFAULT_LJ, DEFAULT_MORSE, DEFAULT_COULOMB


def main():
    """Run basic examples."""
    
    print("="*60)
    print("Force Field Evaluator - Basic Examples")
    print("="*60)
    
    # Create evaluator
    evaluator = ForceFieldEvaluator()
    
    # Create distance range
    r_range = create_distance_range(0.1, 1.0, 100)
    
    # Example 1: Lennard-Jones
    print("\n" + "="*60)
    print("Example 1: Lennard-Jones Potential")
    print("="*60)
    lj_result = evaluator.evaluate_potential('LJ', DEFAULT_LJ, r_range)
    print(evaluator.get_summary('LJ'))
    
    # Example 2: Morse
    print("="*60)
    print("Example 2: Morse Potential")
    print("="*60)
    morse_result = evaluator.evaluate_potential('Morse', DEFAULT_MORSE, r_range)
    print(evaluator.get_summary('Morse'))
    
    # Example 3: Coulomb
    print("="*60)
    print("Example 3: Coulomb Potential")
    print("="*60)
    coulomb_result = evaluator.evaluate_potential('Coulomb', DEFAULT_COULOMB, r_range)
    print(evaluator.get_summary('Coulomb'))
    
    # Example 4: Comparison
    print("="*60)
    print("Example 4: Potential Comparison")
    print("="*60)
    
    comparison = evaluator.compare_potentials(
        ['LJ', 'Morse'],
        {'LJ': DEFAULT_LJ, 'Morse': DEFAULT_MORSE},
        r_range
    )
    
    print(f"\nLowest minimum: {comparison['lowest_minimum'][0]} "
          f"with U_min = {comparison['lowest_minimum'][1]:.6f} eV")
    
    # Example 5: Crossing points
    print("\n" + "="*60)
    print("Example 5: Finding Crossing Points")
    print("="*60)
    
    crossings = evaluator.find_crossing_points(
        'LJ', DEFAULT_LJ,
        'Morse', DEFAULT_MORSE,
        r_range
    )
    
    if crossings:
        print(f"LJ and Morse potentials cross at:")
        for r_cross in crossings:
            print(f"  r = {r_cross:.4f} nm")
    else:
        print("No crossing points found in range")
    
    # Example 6: Specific distance evaluation
    print("\n" + "="*60)
    print("Example 6: Evaluation at Specific Distance")
    print("="*60)
    
    r_test = 0.4
    print(f"\nAt r = {r_test} nm:")
    
    for pot_name, params in [('LJ', DEFAULT_LJ), ('Morse', DEFAULT_MORSE)]:
        U, F = evaluator.evaluate_at_distance(pot_name, params, r_test)
        print(f"  {pot_name:8s}: U = {U:8.4f} eV, F = {F:8.4f} eV/nm")
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)


if __name__ == '__main__':
    main()
