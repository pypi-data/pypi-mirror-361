"""
DataText Library Setup
A simple database library that operates on plain text files
"""

from setuptools import setup, find_packages

# Read the contents of README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="datatext",
    version="1.0.0",
    author="tikipiya",
    author_email="s2501082@sendai-nct.jp",
    description="A simple database library that operates on plain text files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tikipiya/datatext",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No dependencies - zero dependency library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    keywords="database, text, file, simple, lightweight, zero-dependency",
    project_urls={
        "Bug Reports": "https://github.com/tikipiya/datatext/issues",
        "Source": "https://github.com/tikipiya/datatext",
    },
)