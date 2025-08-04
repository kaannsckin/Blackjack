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

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Expose ports
EXPOSE 6379 8265 10001

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 