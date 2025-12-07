"""
WIKAI - Wisdom Keeper for Artificial Intelligence

A universal pattern library for AI systems.
"""

from setuptools import setup, find_packages
from pathlib import Path

readme = Path(__file__).parent / "README.md"
long_description = readme.read_text(encoding="utf-8") if readme.exists() else ""

setup(
    name="wikai",
    version="0.1.0",
    author="WIKAI Contributors",
    author_email="",
    description="Universal pattern library for AI systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yufok1/Wikai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wikai-server=wikai.web_ui:main",
        ],
    },
    include_package_data=True,
    package_data={
        "wikai": ["patterns/*.json"],
    },
)
