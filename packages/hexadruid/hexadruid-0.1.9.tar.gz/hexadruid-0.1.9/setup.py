from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hexadruid",
    version="0.1.9",
    author="Omar Attia",
    description="Smart Spark Optimizer: Skew Rebalancer + Key Detector + DRTree",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OmarAttia95/hexadruid",
    packages=find_packages(include=["hexadruid", "hexadruid.*"]),
    include_package_data=True,
    package_data={
        "hexadruid": ["hexadruid_core.pyd", "hexadruid_core.pyi"],  # Only compiled/core files!
    },
    python_requires=">=3.8",
    install_requires=[
        "pyspark>=3.5.1",
        "pandas",
        "matplotlib",
        "seaborn",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
