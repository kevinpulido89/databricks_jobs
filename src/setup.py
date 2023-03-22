"""
basic setup script to install package in development mode

pip install -e . --no-deps
"""
from setuptools import find_packages, setup

setup(
    name="smart_discounts",
    author="AB-InBev MAZ Data & Analytics",
    description="Lighthouse Smart Discounts promotion optimization",
    packages=find_packages(),
    version="0.1.0",
    license="Copyright 2021-2022 AB-InBev",
    python_requires=">=3.8",
)
