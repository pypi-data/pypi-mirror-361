# my_package/setup.py
from setuptools import setup, find_packages

setup(
    name="nantis_llm_toolbox",  # Name des Pakets
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],  # Abhängigkeiten, falls vorhanden
    description="A package containing my llm tools",
    author="Abakus Nantis",
    author_email="bastian.knaus@gmail.com",
    url="https://github.com/AbakusNantis/llm-toolbox",  # Optionale GitHub-URL
    python_requires=">=3.10",
)