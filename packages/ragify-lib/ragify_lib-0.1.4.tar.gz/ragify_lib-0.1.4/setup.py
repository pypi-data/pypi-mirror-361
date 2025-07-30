"""
Setup script for Ragify
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "A simple, clean Python library for Retrieval-Augmented Generation (RAG)"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="ragify-lib",
    version="0.1.4",
    author="Ragify Team",
    author_email="contact@ragify.dev",
    description="A simple, clean Python library for Retrieval-Augmented Generation (RAG)",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ragify/ragify",
    license="MIT",
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
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "sentence-transformers>=2.2.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "tqdm>=4.62.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ragify=ragify.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="rag, retrieval-augmented-generation, embeddings, vector-database, ai, nlp",
    project_urls={
        "Bug Reports": "https://github.com/ragify/ragify/issues",
        "Source": "https://github.com/ragify/ragify",
        "Documentation": "https://ragify.readthedocs.io/",
    },
) 