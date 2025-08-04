# ================================================================================
# F3.4: HPC INFRASTRUCTURE - DOCKER CONFIGURATION
# ================================================================================
# 
# 🎯 **AMAÇ:** Cloud training için Docker container
# 📋 **KAPSAM:** AWS Spot, Ray, Optuna ile large-scale training
# 🔧 **ENTEGRASYON:** 50M hands training capability
# 
# ================================================================================

FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install additional HPC dependencies
RUN pip install --no-cache-dir \
    ray[tune]==2.7.0 \
    optuna==3.4.0 \
    boto3==1.34.0 \
    sagemaker==2.198.0 \
    wandb==0.16.0 \
    mlflow==2.8.0

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/models /app/runs /app/logs /app/data

# Set up Ray configuration
ENV RAY_DISABLE_IMPORT_WARNING=1
ENV RAY_ADDRESS=auto

# Create entrypoint script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting Blackjack AI HPC Training Container"\n\
echo "================================================"\n\
echo "Python version: $(python --version)"\n\
echo "Ray version: $(python -c \"import ray; print(ray.__version__)\")"\n\
echo "Optuna version: $(python -c \"import optuna; print(optuna.__version__)\")"\n\
echo "================================================"\n\
\n\
# Start Ray cluster\n\
ray start --head --port=6379 --dashboard-port=8265 --dashboard-host=0.0.0.0\n\
\n\
# Wait for Ray to be ready\n\
sleep 5\n\
\n\
# Run the specified command or default to training\n\
if [ $# -eq 0 ]; then\n\
    echo "No command specified, starting default training..."\n\
    python scripts/optimize_hyperparameters_advanced.py \\\n\
        --n-trials 50 \\\n\
        --total-steps 1000000 \\\n\
        --study-name hpc_blackjack_optimization \\\n\
        --out-dir /app/runs/hpc_training\n\
else\n\
    echo "Running command: $@"\n\
    exec "$@"\n\
fi\n\
\n\
# Keep container running\n\
tail -f /dev/null\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose ports
EXPOSE 6379 8265 10001

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 