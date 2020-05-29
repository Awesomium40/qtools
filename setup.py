import setuptools
import os

with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qtools",
    version="0.6.0",
    author="Jay Walthers",
    author_email="justin_walthers@brown.edu",
    description="A package for managing and analyzing Interview data at CAAS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JayWaWa/qtools",
    install_requires=['openpyxl >= 2.6.3'],
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.6',
)