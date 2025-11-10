#!/usr/bin/env python3
"""
Setup script for Ligand Binding Thermodynamics CLI
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

setup(
    name="ligand-binding-thermodynamics-cli",
    version="1.0.0",
    description="A lightweight CLI tool for computing ligand binding thermodynamics",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Biophysics Utilities",
    author_email="",
    url="https://github.com/biophysics-utilities/ligand-binding-thermodynamics-cli",
    license="MIT",
    
    # Package configuration
    packages=find_packages(),
    python_requires=">=3.10",
    
    # No external dependencies - pure Python standard library
    install_requires=[],
    
    # Optional dependencies for enhanced features
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
        ],
        'enhanced': [
            'rich>=13.0.0',  # For enhanced CLI formatting
        ],
    },
    
    # Entry points for command-line interface
    entry_points={
        'console_scripts': [
            'bind-thermo=src.cli:main',
            'ligand-thermo=src.cli:main',
        ],
    },
    
    # Package metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    
    keywords=[
        "biophysics",
        "thermodynamics",
        "binding",
        "ligand",
        "protein",
        "equilibrium",
        "dissociation-constant",
        "free-energy",
        "chemistry",
        "biochemistry",
    ],
    
    project_urls={
        "Bug Reports": "https://github.com/biophysics-utilities/ligand-binding-thermodynamics-cli/issues",
        "Source": "https://github.com/biophysics-utilities/ligand-binding-thermodynamics-cli",
    },
    
    # Include package data
    include_package_data=True,
    zip_safe=False,
)
