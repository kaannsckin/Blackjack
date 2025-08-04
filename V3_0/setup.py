"""
================================================================================
F3.6: PYPI PACKAGE SETUP
================================================================================

🎯 **AMAÇ:** pip install blackjack_ai_sim çalışır hale getirme
📋 **KAPSAM:** PyPI distribution, Sphinx docs, example notebooks
🔧 **ENTEGRASYON:** Professional package structure

================================================================================
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Blackjack AI Simulation Package"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="blackjack_ai_sim",
    version="3.0.0",
    author="Blackjack AI Team",
    author_email="blackjack.ai@example.com",
    description="Advanced Multi-Player Dynamic Blackjack AI Simulation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/blackjack-ai/blackjack-ai-sim",
    project_urls={
        "Bug Tracker": "https://github.com/blackjack-ai/blackjack-ai-sim/issues",
        "Documentation": "https://blackjack-ai-sim.readthedocs.io/",
        "Source Code": "https://github.com/blackjack-ai/blackjack-ai-sim",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Games/Entertainment :: Simulation",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="blackjack, ai, reinforcement-learning, simulation, multi-player, dynamic-adaptation",
    packages=find_packages(include=[
        "blackjack_ai_sim",
        "blackjack_ai_sim.*",
        "utils",
        "utils.*",
        "scripts",
        "scripts.*"
    ]),
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "hpc": [
            "ray[tune]>=2.7.0",
            "optuna>=3.4.0",
            "boto3>=1.34.0",
            "sagemaker>=2.198.0",
            "mlflow>=2.8.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=0.18.0",
            "sphinx-autodoc-typehints>=1.19.0",
        ],
        "full": [
            "torch>=1.13.0",
            "tensorboard>=2.12.0",
            "wandb>=0.16.0",
            "matplotlib>=3.6.0",
            "seaborn>=0.12.0",
            "plotly>=5.14.0",
            "pandas>=1.5.0",
            "numpy>=1.24.0",
            "scipy>=1.10.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "blackjack-ai=blackjack_ai_sim.cli:main",
            "blackjack-train=scripts.train_play_agent:main",
            "blackjack-evaluate=scripts.evaluate_play_agent:main",
            "blackjack-hpo=scripts.optimize_hyperparameters:main",
            "blackjack-hpc=scripts.hpc_training_launcher:main",
        ],
    },
    include_package_data=True,
    package_data={
        "blackjack_ai_sim": [
            "config/*.yaml",
            "config/*.json",
            "models/*.zip",
            "data/*.csv",
            "data/*.json",
        ],
    },
    zip_safe=False,
    platforms=["any"],
    license="MIT",
    download_url="https://github.com/blackjack-ai/blackjack-ai-sim/archive/v3.0.0.tar.gz",
) 