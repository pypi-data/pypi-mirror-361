from setuptools import setup, find_packages

setup(
    name="vesselmatch",
    version="0.1.0",
    description="Python client for vessel name-to-IMO enrichment service",
    author="vesselmatch",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
        "requests",
        "pyarrow",
    ],
    python_requires=">=3.7",
)
