#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="planctl",
    version="1.0.0",
    author="Will G.",
    author_email="noreply@users.noreply.github.com",
    description="A CLI tool for managing daily engineering tasks and priorities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/planctl",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "typer[all]>=0.9.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "planctl=planctl.cli:app",
        ],
    },
)