"""
Setup script for the Protein Hydration Shell Estimator.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="protein-hydration-shell-estimator",
    version="1.0.0",
    author="Biophysics Utilities",
    description="Theoretical estimation of water molecules in protein hydration shells",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/murari/biophysics-utilities/protein-hydration-shell-estimator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        # No external dependencies - pure Python
    ],
    entry_points={
        "console_scripts": [
            "hydration-estimator=src.cli:main",
        ],
    },
    keywords="protein hydration biophysics water shell molecular-biology",
    project_urls={
        "Bug Reports": "https://github.com/murari/biophysics-utilities/issues",
        "Source": "https://github.com/murari/biophysics-utilities/protein-hydration-shell-estimator",
    },
)
