# setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hexadruid",
    version="0.2.2",
    author="Omar Hossam Attia",
    author_email="omar@123915@hotmail.com",
    description="Advanced Spark Data Skew, Schema, and Partitioning Optimizer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OmarAttia95/hexadruid",
    packages=find_packages(include=["hexadruid", "hexadruid.*"]),
    package_data={
        "hexadruid": ["hexadruid.cp311-win_amd64.pyd"],
    },
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "pyspark>=3.5.0,<4.0.0",
        "pandas>=1.0",
        "matplotlib>=3.0",
        "python-dateutil>=2.8",
    ],
    extras_require={
        "dev": ["pytest>=6.0", "flake8", "black"],
        "viz": ["seaborn>=0.11"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "hexadruid=hexadruid.cli:main",
        ],
    },
)
