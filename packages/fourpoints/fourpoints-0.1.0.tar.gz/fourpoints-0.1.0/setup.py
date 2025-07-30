#!/usr/bin/env python3
"""
FourPoints - A production-grade Python library for real-time vehicle telemetry and diagnostics
"""

import os
from setuptools import setup, find_packages

# Read the contents of the README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Define package metadata
setup(
    name="fourpoints",
    version="0.1.0",
    description="A production-grade Python library for real-time vehicle telemetry and diagnostics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="FourPoints Team",
    author_email="info@fourpoints.example.com",
    url="https://github.com/fourpoints/fourpoints",
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "python-obd>=0.7.1",
        "fastapi>=0.95.0",
        "uvicorn>=0.21.1",
        "pydantic>=1.10.7",
        "google-generativeai==0.1.0rc1",
        "jinja2>=3.1.2",
        "weasyprint>=59.0",
        "matplotlib>=3.7.1",
        "gpsd-py3>=0.3.0",
        "pyserial>=3.5",
        "websockets>=11.0.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.3.1",
            "pytest-asyncio>=0.21.0",
            "black>=23.3.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.3.0",
        ],
        "docs": [
            "sphinx>=6.2.1",
            "sphinx-rtd-theme>=1.2.1",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords="obd, vehicle, telemetry, diagnostics, automotive",
    project_urls={
        "Bug Tracker": "https://github.com/fourpoints/fourpoints/issues",
        "Documentation": "https://fourpoints.readthedocs.io/",
        "Source Code": "https://github.com/fourpoints/fourpoints",
    },
)
