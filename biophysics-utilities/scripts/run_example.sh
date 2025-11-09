#!/bin/bash
# Run example simulations

echo "=== Reaction Kinetics Playground Examples ==="
echo ""

# Example 1: Parse reactions
echo "1. Parsing reactions..."
kinetics parse "A + B -> C ; 0.1"
echo ""

# Example 2: Run preset
echo "2. Running enzyme kinetics preset..."
kinetics preset enzyme_kinetics -i E=1.0 -i S=10.0 -i ES=0.0 -i P=0.0 -t 50 --no-plot
echo ""

# Example 3: Simulate from file
echo "3. Simulating from YAML file..."
kinetics simulate -i examples/simple_mass_action.yaml -c A=1.0 -c B=1.0 -c C=0.0 -t 100 -o results.csv
echo ""

# Example 4: List presets
echo "4. Available presets:"
kinetics presets
echo ""

echo "=== Examples complete ===" 