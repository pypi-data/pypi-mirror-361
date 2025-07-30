"""
Setup script for obsipub package.
This is a fallback for older pip/setuptools versions.
Modern packaging should use pyproject.toml.
"""

from setuptools import setup, find_packages

setup(
    name="obsipub",
    use_scm_version=False,
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.7",
)