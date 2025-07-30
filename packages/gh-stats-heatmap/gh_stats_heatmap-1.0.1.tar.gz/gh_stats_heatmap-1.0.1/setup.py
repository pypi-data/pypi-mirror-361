#!/usr/bin/env python3
"""
Setup script for gh-stats-heatmap.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gh-stats-heatmap",
    version="1.0.1",
    author="Gizmet",
    author_email="gizmet@example.com",
    description="GitHub Contribution Graph in your terminal — for hackers who prefer Unicode over UI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gizmet/gh-stats-heatmap",
    py_modules=["ghstats", "github_api", "heatmap", "render", "utils"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Terminals",
        "Topic :: Utilities",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ghstats=ghstats:main",
        ],
    },
    keywords="github, terminal, heatmap, contributions, cli, rich",
    project_urls={
        "Bug Reports": "https://github.com/Gizmet/gh-stats-heatmap/issues",
        "Source": "https://github.com/Gizmet/gh-stats-heatmap",
        "Documentation": "https://github.com/Gizmet/gh-stats-heatmap#readme",
    },
) 