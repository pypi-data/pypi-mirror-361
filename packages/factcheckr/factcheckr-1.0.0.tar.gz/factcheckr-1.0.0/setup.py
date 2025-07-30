#!/usr/bin/env python3
"""
Setup script for FactCheckr package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="factcheckr",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered fact-checking tool using free Hack Club AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/factcheckr",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    keywords="fact-checking, ai, nlp, verification, truth, claims",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/factcheckr/issues",
        "Source": "https://github.com/yourusername/factcheckr",
        "Documentation": "https://github.com/yourusername/factcheckr#readme",
    },
    entry_points={
        "console_scripts": [
            "factcheckr=factcheckr.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)