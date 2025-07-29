from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(this_directory, 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = "A Python package for calculating option Greeks and implied volatility."

setup(
    name="volg",
    version="0.1.5",
    author="Vinod Bhadala",
    author_email="vinodbhadala@gmail.com",
    description="A Python package for calculating option Greeks and implied volatility.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vbhadala/volg",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.19.0",
        "scipy>=1.5.0",
        "setuptools>=59.6.0"
        
    ],
    keywords="greeks, stock market, financial data, volatility, trading, candlestick data",
)