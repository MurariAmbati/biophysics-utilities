"""Setup script for Lennard-Jones Playground."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lj-playground",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Interactive visual environment to explore the Lennard-Jones potential",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lj-playground",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "plotly>=5.0.0",
        "ipywidgets>=8.0.0",
        "pandas>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "jupyter>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lj-playground=src.cli:main",
        ],
    },
)
