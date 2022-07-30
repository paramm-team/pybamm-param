from setuptools import setup, find_packages

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
)
