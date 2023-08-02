# [Unreleased](https://github.com/paramm-team/pybamm-param/)

## Features

### Optimisation problems

* Fit PyBaMM simulation to data (`DataFit`)
* Balance OCP for half cells (`OCPBalance`)

### Optimisers

* SciPy Minimize (`ScipyMinimize`)
* SciPy Differential Evolution (`ScipyDifferentialEvolution`)

### Cost Functions
* Root Mean Square Error (`RMSE`)


## PRs

- Refactor for base_optimisation_problem conformity ([#42](https://github.com/paramm-team/pybamm-param/pull/42))
- Allow `DataFit` to take `simulation_options` ([#40](https://github.com/paramm-team/pybamm-param/pull/40))
- Allow weights in the objective function ([#36](https://github.com/paramm-team/pybamm-param/pull/36))
- Implement maximum likelihood estimation ([#32](https://github.com/paramm-team/pybamm-param/pull/32))
- Add `__str__` to `OptimisationResult` ([#31](https://github.com/paramm-team/pybamm-param/pull/31))
- Improve documentation ([#29](https://github.com/paramm-team/pybamm-param/pull/29))
- Implement `CostFunction` class ([#25](https://github.com/paramm-team/pybamm-param/pull/25))
- Improve initial guess and bounds for `OCPBalance`([#24](https://github.com/paramm-team/pybamm-param/pull/24))
- Scale variables in `DataFit` ([#19](https://github.com/paramm-team/pybamm-param/pull/19))
- Allow `DataFit` to optimise multiple variables ([#18](https://github.com/paramm-team/pybamm-param/pull/18))
- Fix plotting to work with multiple variables ([#16](https://github.com/paramm-team/pybamm-param/pull/16))
- Set up hatch ([#11](https://github.com/paramm-team/pybamm-param/pull/11))
- Reformat optimisation problem ([#9](https://github.com/paramm-team/pybamm-param/pull/0))
- Setup documentation infrastructure ([#8](https://github.com/paramm-team/pybamm-param/pull/8))
- Define package structure ([#2](https://github.com/paramm-team/pybamm-param/pull/2))