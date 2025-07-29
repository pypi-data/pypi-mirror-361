#!/usr/bin/env python3
"""
Setup script for Restorant - Terminal Restaurant Roguelike
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
    name="restorant",
    version="1.0.0",
    author="Restorant Development Team",
    author_email="dev@restorant.game",
    description="A terminal-based restaurant management roguelike game",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/restorant/restorant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "restorant=restaurant_game:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["data/*.yaml", "data/*.yml"],
    },
    keywords="game, restaurant, management, roguelike, terminal, text-based",
    project_urls={
        "Bug Reports": "https://github.com/restorant/restorant/issues",
        "Source": "https://github.com/restorant/restorant",
        "Documentation": "https://github.com/restorant/restorant/blob/main/README.md",
    },
) 