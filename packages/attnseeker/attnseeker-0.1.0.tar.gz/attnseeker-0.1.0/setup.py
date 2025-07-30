#!/usr/bin/env python3
"""
Setup script for the attnseeker package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="attnseeker",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python package for attention-seeking functionality",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/attnseeker",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/attnseeker/issues",
        "Source": "https://github.com/yourusername/attnseeker",
        "Documentation": "https://github.com/yourusername/attnseeker#readme",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "isort>=5.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "pre-commit>=2.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
    },
    entry_points={
        "console_scripts": [
            "attnseeker=attnseeker.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 