from setuptools import setup, find_packages

install_requires = [
    "pybamm == 0.4.0",
    "matplotlib",
    "prettytable",
    "jax",
    "jaxlib",
    "SciencePlots",
]

setup(
    name="tec_reduced_model",
    version="0.2",
    author="Ferran Brosa Planella",
    author_email="Ferran.Brosa-Planella@warwick.ac.uk",
    packages=find_packages(),
    license="LICENSE",
    description='Code and data for the paper "Systematic derivation and validation of'
    " a reduced thermal-electrochemical model for lithium-ion batteries using"
    ' asymptotic methods" by Ferran Brosa Planella, Muhammad Sheikh and W. Dhammika'
    " Widanage (2020).",
    install_requires=install_requires,
)
