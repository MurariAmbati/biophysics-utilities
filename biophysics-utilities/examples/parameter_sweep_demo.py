"""
Parameter Sweep Demonstration

Shows how to perform parameter sweeps and visualize the results.
"""

import numpy as np
import matplotlib.pyplot as plt
from kinetics_playground.api import ReactionNetwork

# Create simple reversible reaction
reactions = [
    "A -> B ; 1.0",
    "B -> A ; 0.5"
]

network = ReactionNetwork(reactions)

# Parameter sweep: vary forward rate constant
k_values = np.logspace(-2, 1, 20)  # 0.01 to 10
final_B = []

for k in k_values:
    # Update rate constant
    network.model.reactions[0].rate_constant = k
    network._rebuild_kinetic_system()
    
    # Simulate
    result = network.simulate(
        initial_conditions={'A': 1.0, 'B': 0.0},
        time_span=(0, 100),
        num_points=1000
    )
    
    # Store final concentration of B
    final_B.append(result.get_species('B')[-1])

# Plot results
plt.figure(figsize=(10, 6))
plt.semilogx(k_values, final_B, 'o-', linewidth=2, markersize=8)
plt.xlabel('Forward Rate Constant (k)', fontsize=12)
plt.ylabel('Final [B] Concentration', fontsize=12)
plt.title('Parameter Sweep: Effect of Rate Constant on Equilibrium', fontsize=14)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('parameter_sweep_result.png', dpi=300)
print("✓ Plot saved to parameter_sweep_result.png")
plt.show()
