#!/bin/bash

echo "🚀 Starting Blackjack AI HPC Training Container"
echo "================================================"
echo "Python version: $(python --version)"

# Test Ray import
python -c "import ray; print(f'Ray version: {ray.__version__}')" 2>/dev/null || echo "Ray: Not available"

# Test Optuna import  
python -c "import optuna; print(f'Optuna version: {optuna.__version__}')" 2>/dev/null || echo "Optuna: Not available"

echo "================================================"

# Start Ray cluster if ray is available
if python -c "import ray" 2>/dev/null; then
    echo "Starting Ray cluster..."
    ray start --head --port=6379 --dashboard-port=8265 --dashboard-host=0.0.0.0 &
    sleep 5
fi

# Run the specified command or default to interactive mode
if [ $# -eq 0 ]; then
    echo "No command specified, starting interactive mode..."
    echo "Available commands:"
    echo "  python test_f3_integration.py"
    echo "  python faz3_kritik_sorunlar_cozum_plani.py"
    echo "  python comprehensive_ai_analysis.py"
    echo "  bash"
    exec bash
else
    echo "Running command: $@"
    exec "$@"
fi 