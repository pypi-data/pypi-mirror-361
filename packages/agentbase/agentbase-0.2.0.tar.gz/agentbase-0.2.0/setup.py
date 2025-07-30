#!/usr/bin/env python3
"""
Setup script for AgentBase - Open Source AI Agent Storage with Learning and Adaptation
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# Get the long description from the README file
here = Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

# Read version from __init__.py
def get_version():
    version_file = here / "agentbase" / "__init__.py"
    version_line = [line for line in version_file.read_text().split('\n') if line.startswith('__version__')][0]
    return version_line.split('=')[1].strip().strip('"').strip("'")

# Core dependencies - minimal requirements
core_requirements = [
    "numpy>=1.20.0",
]

# Optional dependencies for enhanced functionality
optional_requirements = {
    "full": [
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "psutil>=5.8.0",
        "memory-profiler>=0.60.0",
    ],
    "ml": [
        "scikit-learn>=1.0.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
    ],
    "viz": [
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "plotly>=5.0.0",
    ],
    "config": [
        "pydantic>=1.8.0",
        "pyyaml>=5.4.0",
    ],
    "logging": [
        "colorlog>=6.0.0",
        "structlog>=21.0.0",
    ],
    "database": [
        "sqlalchemy>=1.4.0",
        "redis>=3.5.0",
    ],
    "web": [
        "flask>=2.0.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
    ],
    "notebook": [
        "jupyter>=1.0.0",
        "ipywidgets>=7.6.0",
    ],
    "parallel": [
        "joblib>=1.0.0",
        "dask>=2021.8.0",
    ],
    "dev": [
        "pytest>=6.0.0",
        "pytest-cov>=2.12.0",
        "black>=21.0.0",
        "flake8>=3.9.0",
        "mypy>=0.910",
        "coverage>=5.5.0",
        "pre-commit>=2.15.0",
        "bandit>=1.7.0",
    ],
    "docs": [
        "sphinx>=4.0.0",
        "sphinx-rtd-theme>=0.5.0",
    ],
}

# Add 'all' option that includes everything
all_requirements = []
for reqs in optional_requirements.values():
    all_requirements.extend(reqs)
optional_requirements["all"] = list(set(all_requirements))

setup(
    name="agentbase",
    version=get_version(),
    description="Open Source AI Agent Storage with Learning and Adaptation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bestagents/agentbase",
    author="AgentBase Contributors",
    author_email="hello@agentbase.org",
    license="MIT",
    
    # Classifiers help users find your project by categorizing it
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
    ],
    
    # Keywords that describe your project
    keywords="ai, agent, storage, machine-learning, reinforcement-learning, memory, cache, drift-detection, lifelong-learning",
    
    # Package discovery
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Core dependencies
    install_requires=core_requirements,
    
    # Optional dependencies
    extras_require=optional_requirements,
    
    # Include non-Python files
    include_package_data=True,
    
    # Data files
    package_data={
        "agentbase": [
            "py.typed",  # Marker file for type checking
        ],
    },
    
    # Entry points for command-line scripts
    # entry_points={
    #     "console_scripts": [
    #         "agentbase=agentbase.cli:main",  # If we add a CLI in the future
    #     ],
    # },
    
    # Project URLs
    project_urls={
        "Documentation": "https://agentbase.readthedocs.io/",
        "Source": "https://github.com/bestagents/agentbase",
        "Tracker": "https://github.com/bestagents/agentbase/issues",
        "Homepage": "https://bestagents.github.io/agentbase/",
    },
    
    # Zip safety
    zip_safe=False,
    
    # Platform compatibility
    platforms=["any"],
    
    # Test suite
    test_suite="tests",
    
    # Additional metadata
    download_url="https://github.com/bestagents/agentbase/archive/main.zip",
) 