#!/usr/bin/env python3
"""Setup script for NerdMan - Nerd Fonts icon manager."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read version from the module
def get_version():
    """Extract version from nerdman.py without importing it."""
    with open('nerdman.py', 'r', encoding='utf-8') as f:
        for line in f:
            if 'Version V' in line:
                # Extract the version number
                version = line.split()[-1].strip('V')
                return version
    return '0.1.1'  # Default version

setup(
    name="nerdman",
    version=get_version(),
    author="Alfie McCabe",
    author_email="iamamccabe@gmail.com",
    description="A powerful Python library and CLI tool for working with Nerd Fonts icons",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mralfiem591/nerdman",
    project_urls={
        "Bug Reports": "https://github.com/mralfiem591/nerdman/issues",
        "Source": "https://github.com/mralfiem591/nerdman",
        "Documentation": "https://github.com/mralfiem591/nerdman#readme",
    },
    py_modules=["nerdman"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    keywords=[
        "nerd-fonts", "icons", "fonts", "cli", "terminal", "unicode", 
        "symbols", "glyphs", "developer-tools", "font-icons"
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "twine",
            "wheel",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov",
        ],
    },
    entry_points={
        "console_scripts": [
            "nerdman=nerdman:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    license="MIT",
    platforms=["any"],
)
