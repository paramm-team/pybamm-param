[![DOI](https://zenodo.org/badge/303453380.svg)](https://zenodo.org/badge/latestdoi/303453380)

# Systematic derivation and validation of a reduced thermal-electrochemical model for lithium-ion batteries using asymptotic methods
Code and data for the paper "[Systematic derivation and validation of a reduced thermal-electrochemical model for lithium-ion batteries using asymptotic methods](https://doi.org/10.1016/j.electacta.2021.138524)" by Ferran Brosa Planella, Muhammad Sheikh and W. Dhammika Widanage (2021).

## What is in this repository?
In this repository you can find the scripts used to generate the code for the paper.
* The folder `data/` contains the experimental data used for validation in a `.csv` format. The data is organised in subfolders for different temperatures (`0degC`, `10degC` and `25degC`). The methods in `scripts/process_experimental_data.py` can be used to import and process these files into your Python script.
* Running `scripts/compare_TSPMe_TDFN.py` generates the figures to compare the TSPMe against the TDFN model, reproducing Figures 5-7 in the paper. It also produces `errors_models.txt` which records the error between models shown in Table 2 of the paper. Note that new data is appended to this file every time the script is run.
* Running `scripts/compare_TSPMe_data.py` generates the figures to compare the TSPMe against experimental data, reproducing Figure 8-10 in the paper. It also produces `errors_experiments.txt` which records the error between TSPMe and experimental data shown in Table 5 of the paper. Note that new data is appended to this file every time the script is run.
* Running `scripts/time_TSPMe_TDFN.py` calculates the solving time for each model, reproducing the results in Table 3 of the paper.
* The Jupyter notebooks in `notebooks` reproduce the scripts but in a more interactive format.
* The scripts `process_experimental_data.py` and `set_parameters.py` contain auxiliary methods.

## How to cite the code or data?
If you found the code or the data useful please cite our paper
> F. Brosa Planella, M. Sheikh, and W. D. Widanage, [Systematic derivation and validation of a reduced thermal-electrochemical model for lithium-ion batteries using asymptotic methods](https://doi.org/10.1016/j.electacta.2021.138524), _Electrochimica Acta_ **388** (2021) 138524.

If you also find the code useful, apart from citing the paper above, please use the PyBaMM command

```python3
pybamm.print_citations()
```

at the end of your script to print in the terminal the bibtex of all the references that have contributed to your code (model, parameters, solvers...).

## How to use the code?
In order to run the code you need to install this package. We strongly recommend to install it in a Python virtual environment, in order not to alter any distribution Python files. Assuming you work on Linux-based system you need to run:

1. Clone the repository
1. Go into the `TEC-reduced-model` folder: `cd TEC-reduced-model`
1. Create the virtual environment: `virtualenv env`
1. Activate the virtual environment: `source env/bin/activate`
1. Install the package: `pip install .`

Then you can run the scripts and notebooks. If you encounter any bugs or errors please let us know either via email or raising a GitHub issue.


