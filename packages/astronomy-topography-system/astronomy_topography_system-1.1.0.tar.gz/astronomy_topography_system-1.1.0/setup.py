#!/usr/bin/env python3
"""
Setup script for Astronomy AI Topography System.
"""

from setuptools import setup, find_packages
import os

this_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_dir, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open(os.path.join(this_dir, "requirements.txt"), "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="astronomy-topography-system",
    version="1.1.0",
    author="Astronomy AI Team",
    author_email="contact@astronomy-ai.com",
    description="A topography analysis system for astronomy enthusiasts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/astronomy-ai/topography-system",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "astronomy-ai=demo:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 