# setup.py
from setuptools import setup, find_packages

setup(
    name="tns-browsing-history",  # must be globally unique on PyPI
    version="0.1.0",
    description="Reusable Python module to store user browsing history via function call",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Naveenkumar Koppala",
    author_email="naveenkumar.k@tnsservices.com.com",
    # url="https://github.com/yourusername/browsing_history",  # optional
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy>=1.4",
        "pydantic>=1.10"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7",
)
