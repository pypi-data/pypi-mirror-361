# setup.py
from setuptools import setup, find_packages

setup(
    name="james_toolkit",
    version="0.1",
    packages=find_packages(),
    author="James Nithil",
    description="A custom AI utilities toolkit by James",
    long_description="A custom reusable package with utility functions for data science, math, and AI projects.",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
