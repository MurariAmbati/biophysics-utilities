"""
Setup script for Brownian Motion Simulator.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="brownian-motion-sim",
    version="1.0.0",
    author="Biophysics Utilities",
    description="A tool for simulating and visualizing stochastic Brownian motion in 2D and 3D",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/brownian-motion-sim",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
        "animation": [
            "ffmpeg-python>=0.2.0",
            "pillow>=9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "brownian-sim=src.cli:main",
        ],
    },
)
