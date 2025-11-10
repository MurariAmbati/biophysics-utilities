#!/bin/bash
# Setup script for Brownian Motion Simulator

echo "=========================================="
echo "Brownian Motion Simulator - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi

echo ""
echo "✓ Setup complete!"
echo ""
echo "=========================================="
echo "Quick Test"
echo "=========================================="
echo ""

# Run minimal demo
echo "Running quick demo..."
python brownian_minimal.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Installation successful!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "  1. Try examples:     python examples/example_2d.py"
    echo "  2. Run tutorial:     python tutorial.py"
    echo "  3. Interactive mode: python src/cli.py"
    echo "  4. Run tests:        python tests/test_core.py"
    echo ""
    echo "See QUICKSTART.md for more information."
else
    echo ""
    echo "⚠️ Demo failed. Please check error messages above."
fi
