# pybamm-param: PyBaMM Parameter Optimization Tool

[![pybamm-param](https://github.com/paramm-team/pybamm-param/actions/workflows/test_on_push.yml/badge.svg?branch=main)](https://github.com/paramm-team/pybamm-param/actions/workflows/test_on_push.yml)
[![Documentation Status](https://readthedocs.org/projects/pybamm-param/badge/?version=latest)](https://pybamm-param.readthedocs.io/en/latest/?badge=latest)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/paramm-team)
[![codecov](https://codecov.io/gh/paramm-team/pybamm-param/branch/main/graph/badge.svg?token=CMFXMUU1SJ)](https://codecov.io/gh/paramm-team/pybamm-param)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![DOI:10.5281/zenodo.11282637](https://zenodo.org/badge/DOI/10.5281/zenodo.11282638.svg)](https://doi.org/10.5281/zenodo.11282638)
**WARNING:** this package is still under development and significant API changes might take please in the upcoming releases.

This package is provides parameter optimization for PyBaMM (Python Battery Mathematical Modelling) using different optimization techniques. Examples on how to run this package can be found in the [examples folder](./examples)

## 🚀 Installing pybamm-param

### Using pip

The recommended way to install pybamm-param is by installing the latest release from PyPI. This can be done running

```bash
pip install pbparam
```

We strongly recommend using virtual environments, see more detailed instructions below (steps 1 and 2).

### Install from source

Another option is to install from source. This is not recommended, unless you want to make edits to the code.

The first step is to install `virtualenv` in order to create virtual environments

```bash
pip install virtualenv
```

The module dependencies are listed in `pyproject.toml`, the dependancies which are non optional which are installed with the package.

The optional dependancies are split into `dev` and `docs`. `dev` are used for testing and linting, `docs` are used for building the sphinx documentation.

#### Linux & MacOS

1. Create a virtual environment (this is strongly recommended to avoid clashes with the dependencies)

    ```bash
    virtualenv --python="<path to python 3.11>" env
    ```

2. Activate the virtual environment

    ```bash
    source env/bin/activate
    ```

    The virtual environment can later be deactivated (if needed) by running

    ```bash
    deactivate
    ```

3. Install packages into the virtual envronment

    ```bash
    pip install -e ./[dev,docs]
    ```

#### Windows

1. Create a virtual environment (this is strongly recommended to avoid clashes with the dependencies)

    ```bash
    python -m virtualenv env
    ```

2. Activate the virtual environment

    ```bash
    env\Scripts\activate.bat
    ```

    The virtual environment can later be deactivated (if needed) by running

    ```bash
    deactivate
    ```

3. Install package from Github

    ```bash
    pip install -e .\\[dev,docs]
    ```

## 🛠️ Contributing to pybamm-param

If you'd like to help us develop pybamm-param by adding new methods, writing documentation, or fixing embarrassing bugs, please have a look at these [guidelines](https://github.com/paramm-team/pybamm-param/blob/main/CONTRIBUTING.md) first.

## Notes

### requirements.txt

This is not intended for modification or use installing dependencies, it is a result of a git runner to ensure full package information is included on all pushes. Strict requirements are found in pyproject.toml

### coverage.xml

This is produced during a git run and not intended to be modified directly

## FAIRS

We are working towards conformity with the FAIRS software standards for research software.
The following items should help detail contributions to and ways to work with this software:

### Codemeta

https://github.com/paramm-team/pybamm-param/blob/develop/codemeta.json

### Contributors

#### Active

Ferran Brosa Planella, [github.com/brosaplanella](https://github.com/brosaplanella)
Philip John Grylls, [github.com/pipgrylls](https://github.com/pipgrylls)

#### Inactive or past

Muhammed Nedim Sogut, [github.com/muhammedsogut](https://github.com/muhammedsogut)
Alexandru Pascu, [github.com/AlexandruPascu](https://github.com/AlexandruPascu)

### Other Information

domain:
funder:
programming language: Python
keywords: battery modelling, optimization,
date created:
