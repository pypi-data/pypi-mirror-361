#!/usr/bin/env python3
"""
Setup script for APIProtector package
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="apiprotector",
    version="1.0.0",
    author="Kodukulla Phani Kumar",
    author_email="phanikumark715@gmail.com",
    description="A comprehensive API protection library for Python with rate limiting, authentication, and security features",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/phanikumar715/apiprotector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Security",
        "Topic :: System :: Networking :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: Flask",
        "Framework :: Django",
        "Framework :: FastAPI",
        "Framework :: Pyramid",
    ],
    python_requires=">=3.6",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "pre-commit>=2.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
    },
    entry_points={
        "console_scripts": [
            "apiprotector=apiprotector.cli:main",
        ],
    },
    keywords=[
        "api",
        "protection",
        "rate limiting",
        "authentication",
        "security",
        "flask",
        "django",
        "fastapi",
        "middleware",
        "ddos",
        "security",
        "validation",
        "throttling",
    ],
    project_urls={
        "Bug Reports": "https://github.com/phanikumar715/apiprotector/issues",
        "Source": "https://github.com/phanikumar715/apiprotector",
        "Documentation": "https://apiprotector.readthedocs.io/",
    },
    include_package_data=True,
    zip_safe=False,
)