from setuptools import setup

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="tsg-lib",
    version="0.1.2",
    description="A modular library for synthetic time series generation.",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Important for PyPI to render README correctly
    author="Mathis Jander",
    author_email="your.email@domain.com",
    url="https://github.com/MSCA-DN-Digital-Finance/tsg",
    packages=["tsg"],
    install_requires=["numpy"],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
