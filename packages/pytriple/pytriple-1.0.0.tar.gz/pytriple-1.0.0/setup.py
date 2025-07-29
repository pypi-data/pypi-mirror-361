"""Setup configuration for pytriple - Python triple-quoted string formatter."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pytriple",
    version="1.0.0",
    author="Martin Kalema",
    description="Python tool for fixing triple-quoted string indentation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "colorama>=0.4.6",
        "dependency-injector>=4.41.0",
    ],
    entry_points={
        "console_scripts": [
            "pytriple=presentation.cli.cli:main",
        ],
    },
)