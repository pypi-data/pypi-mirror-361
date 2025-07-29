from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="abdullah_graph_eq",
    version="0.1.0",
    author="abdullahmashhadi",
    author_email="abdullah6blue@gmail.com",  # Replace with your email
    description="A Python package for graphing mathematical equations from string input",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abdullahmashhadi/abdullah_graph_eq",  # Replace with your repo URL
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.7",
    install_requires=[
        "matplotlib>=3.5.0",
        "numpy>=1.20.0",
        "sympy>=1.9.0",
    ],
    keywords="mathematics, plotting, graphing, equations, visualization",
    project_urls={
        "Bug Reports": "https://github.com/abdullahmashhadi/abdullah_graph_eq/issues",
        "Source": "https://github.com/abdullahmashhadi/abdullah_graph_eq",
    },
)
