#!/usr/bin/env python3
"""
Setup script for yfinance-mcp-server
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="yfinance-mcp-server",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    author="Jayesh", 
    author_email="jaypatel6963@gmail.com", 
    description="A comprehensive yfinance MCP server providing access to Yahoo Finance data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/itsmejay80/yfinance-mcp-server",  # Replace with your GitHub repo
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "yfinance-mcp-server=main:main",
        ],
    },
    keywords="mcp, model-context-protocol, yfinance, yahoo-finance, stocks, financial-data",
    project_urls={
        "Bug Reports": "https://github.com/itsmejay80/yfinance-mcp-server/issues",
        "Source": "https://github.com/itsmejay80/yfinance-mcp-server",
        "Documentation": "https://github.com/itsmejay80/yfinance-mcp-server#readme",
    },
) 