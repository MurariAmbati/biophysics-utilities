#!/usr/bin/env python3
"""
Quick validation script to test Force Field Evaluator functionality.
Run this to verify the installation is working correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from src import constants, potentials, derivatives, evaluator, cli
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_potentials():
    """Test basic potential calculations."""
    print("\nTesting potential functions...")
    try:
        from src.potentials import lennard_jones, morse, coulomb
        
        # Test LJ
        U_lj = lennard_jones(0.4, epsilon=0.2, sigma=0.34)
        assert isinstance(U_lj, (float, int)), "LJ should return numeric value"
        
        # Test Morse
        U_morse = morse(0.4, De=0.4, a=1.5, re=0.3)
        assert isinstance(U_morse, (float, int)), "Morse should return numeric value"
        
        # Test Coulomb
        U_coulomb = coulomb(0.5, q1=1e-19, q2=-1e-19)
        assert isinstance(U_coulomb, (float, int)), "Coulomb should return numeric value"
        
        print(f"✓ Potential functions working")
        print(f"  LJ(0.4 nm) = {U_lj:.6f} eV")
        print(f"  Morse(0.4 nm) = {U_morse:.6f} eV")
        print(f"  Coulomb(0.5 nm) = {U_coulomb:.6f} eV")
        return True
    except Exception as e:
        print(f"✗ Potential test failed: {e}")
        return False


def test_forces():
    """Test force calculations."""
    print("\nTesting force functions...")
    try:
        from src.derivatives import lj_force, morse_force, coulomb_force
        
        F_lj = lj_force(0.4, epsilon=0.2, sigma=0.34)
        F_morse = morse_force(0.4, De=0.4, a=1.5, re=0.3)
        F_coulomb = coulomb_force(0.5, q1=1e-19, q2=-1e-19)
        
        print(f"✓ Force functions working")
        print(f"  F_LJ(0.4 nm) = {F_lj:.6f} eV/nm")
        print(f"  F_Morse(0.4 nm) = {F_morse:.6f} eV/nm")
        print(f"  F_Coulomb(0.5 nm) = {F_coulomb:.6f} eV/nm")
        return True
    except Exception as e:
        print(f"✗ Force test failed: {e}")
        return False


def test_evaluator():
    """Test the evaluator class."""
    print("\nTesting evaluator...")
    try:
        from src.evaluator import ForceFieldEvaluator, create_distance_range
        
        evaluator = ForceFieldEvaluator()
        r_range = create_distance_range(0.2, 0.8, 50)
        
        params = {'epsilon': 0.2, 'sigma': 0.34}
        result = evaluator.evaluate_potential('LJ', params, r_range)
        
        assert 'r_eq' in result, "Result should contain r_eq"
        assert 'U_min' in result, "Result should contain U_min"
        assert 'U' in result, "Result should contain U array"
        assert 'F' in result, "Result should contain F array"
        
        print(f"✓ Evaluator working")
        print(f"  r_eq = {result['r_eq']:.4f} nm")
        print(f"  U_min = {result['U_min']:.6f} eV")
        return True
    except Exception as e:
        print(f"✗ Evaluator test failed: {e}")
        return False


def test_numpy_scipy():
    """Test that numpy and scipy are available."""
    print("\nTesting dependencies...")
    try:
        import numpy as np
        import scipy
        print(f"✓ NumPy version: {np.__version__}")
        print(f"✓ SciPy version: {scipy.__version__}")
        return True
    except ImportError as e:
        print(f"✗ Dependency missing: {e}")
        print("  Install with: pip install numpy scipy")
        return False


def test_matplotlib():
    """Test that matplotlib is available (optional)."""
    print("\nTesting matplotlib (optional)...")
    try:
        import matplotlib
        print(f"✓ Matplotlib version: {matplotlib.__version__}")
        return True
    except ImportError:
        print("○ Matplotlib not found (optional, needed for plotting)")
        print("  Install with: pip install matplotlib")
        return True  # Not a failure


def main():
    """Run all tests."""
    print("="*60)
    print("Force Field Evaluator - Validation Test")
    print("="*60)
    
    tests = [
        test_numpy_scipy,
        test_imports,
        test_potentials,
        test_forces,
        test_evaluator,
        test_matplotlib,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✓ All tests passed ({passed}/{total})")
        print("\nInstallation verified! You can now use:")
        print("  python main.py --help")
        print("  python main.py --potential all --output plot")
        return 0
    else:
        print(f"✗ Some tests failed ({passed}/{total} passed)")
        print("\nPlease install missing dependencies:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == '__main__':
    sys.exit(main())
