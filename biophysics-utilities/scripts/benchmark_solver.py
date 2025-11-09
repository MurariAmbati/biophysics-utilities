"""
Benchmark different ODE solvers on a reaction network.

Compares performance of RK45, LSODA, and BDF methods.
"""

import time
import numpy as np
import matplotlib.pyplot as plt
from kinetics_playground.api import load_preset

# Load a moderately complex network
network = load_preset('glycolysis')

# Initial conditions
initial_conditions = {
    'Glucose': 5.0,
    'ATP': 2.0,
    'ADP': 0.5,
    'G6P': 0.0,
    'F6P': 0.0,
    'FBP': 0.0,
    'GAP': 0.0,
    'NAD': 1.0,
    'NADH': 0.0,
    'BPG': 0.0,
    '3PG': 0.0,
    'PEP': 0.0,
    'Pyruvate': 0.0
}

methods = ['RK45', 'LSODA', 'BDF']
times = []
nfev_list = []

print("Benchmarking ODE solvers...")
print("=" * 60)

for method in methods:
    print(f"\nTesting {method}...")
    
    start_time = time.time()
    result = network.simulate(
        initial_conditions=initial_conditions,
        time_span=(0, 100),
        num_points=1000,
        method=method
    )
    elapsed = time.time() - start_time
    
    times.append(elapsed)
    nfev_list.append(result.nfev)
    
    print(f"  Time: {elapsed:.4f} s")
    print(f"  Function evaluations: {result.nfev}")
    print(f"  Success: {result.success}")

# Plot results
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Execution time
ax1.bar(methods, times, color=['#3498db', '#e74c3c', '#2ecc71'])
ax1.set_ylabel('Execution Time (s)', fontsize=12)
ax1.set_title('Solver Performance', fontsize=14)
ax1.grid(True, alpha=0.3, axis='y')

# Function evaluations
ax2.bar(methods, nfev_list, color=['#3498db', '#e74c3c', '#2ecc71'])
ax2.set_ylabel('Function Evaluations', fontsize=12)
ax2.set_title('Computational Cost', fontsize=14)
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('benchmark_results.png', dpi=300)
print("\n✓ Benchmark complete. Plot saved to benchmark_results.png")
plt.show()
