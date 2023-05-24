# pybamm-param: PyBaMM Parameter Optimization Tool

[![pybamm-param](https://github.com/paramm-team/pybamm-param/actions/workflows/test_on_push.yml/badge.svg?branch=main)](https://github.com/paramm-team/pybamm-param/actions/workflows/test_on_push.yml)
[![Documentation Status](https://readthedocs.org/projects/pybamm-param/badge/?version=latest)](https://pybamm-param.readthedocs.io/en/latest/?badge=latest)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/paramm-team)
[![codecov](https://codecov.io/gh/paramm-team/pybamm-param/branch/main/graph/badge.svg?token=CMFXMUU1SJ)](https://codecov.io/gh/paramm-team/pybamm-param)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**WARNING:** this package is still under development.

This package is provides parameter optimization for PyBaMM (Python Battery Mathematical Modelling) using different optimization techniques. Examples on how to run this package can be found in the [examples folder](./examples)

## 🚀 Installing pybamm-param

These installation instructions assume you have Python installed (versions 3.8 to 3.11) and that you have also installed the `virtualenv` package which can be done by running
```bash
pip install virtualenv
```

### Linux & MacOS
1. Create a virtual environment (this is strongly recommended to avoid clashes with the dependencies)
```bash
virtualenv env
```

2. Activate the virtual environment
```bash
source env/bin/activate
```
The virtual environment can later be deactivated (if needed) by running
```bash
deactivate
```

3. Install package from Github
```bash
pip install git+https://github.com/paramm-team/pybamm-param
```

### Windows
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
pip install git+https://github.com/paramm-team/pybamm-param
```

## 🛠️ Contributing to pybamm-param

If you'd like to help us develop pybamm-param by adding new methods, writing documentation, or fixing embarrassing bugs, please have a look at these [guidelines](https://github.com/paramm-team/pybamm-param/blob/main/CONTRIBUTING.md) first.
