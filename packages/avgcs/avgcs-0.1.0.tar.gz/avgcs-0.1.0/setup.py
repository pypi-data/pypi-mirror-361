#!/usr/bin/env python3
"""
Setup script for AVGCS package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

setup(
    name="avgcs",
    version="0.1.0",
    author="AVGCS Team",
    author_email="team@avgcs.dev",
    description="Audio-Visual Game Control System - Real-time motion tracking and game control",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/avgcs/avgcs",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        "avgcs": ["configs/*.json"],
    },
) 