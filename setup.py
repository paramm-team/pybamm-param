from setuptools import setup, find_packages
import os
import site
import shutil

install_requires = [
    "pybamm",
    "matplotlib",
]

setup(
    name="pbparam",
    version="0.1",
    author="WMG",
    author_email="Ferran.Brosa-Planella@warwick.ac.uk",
    packages=find_packages(),
    license="LICENSE",
    description="A package for optimising parameters in PyBaMM. Under development.",
    install_requires=install_requires,
    extras_require={
        "docs": ["sphinx>=1.5", "guzzle-sphinx-theme"],  # For doc generation
        "dev": [
            "flake8>=3",  # For code style checking
            "black",  # For code style auto-formatting
        ],
    },
)

# pybtex adds a folder "tests" to the site packages, so we manually remove this
path_to_sitepackages = site.getsitepackages()[0]
path_to_tests_dir = os.path.join(path_to_sitepackages, "tests")
if os.path.exists(path_to_tests_dir):
    shutil.rmtree(path_to_tests_dir)
