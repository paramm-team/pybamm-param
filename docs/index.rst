.. Root of all pybamm-param docs

.. _GitHub: https://github.com/paramm-team/pybamm-param
.. pybamm-param documentation master file, created by
   sphinx-quickstart on Wed Aug  3 12:41:11 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pybamm-param's documentation!
========================================

Python Battery Mathematical Modelling (**PyBAMM**) Parameter Optimisation package is developed for optimising battery parameters of
PyBAMM model parameters using various optimisation methods and error functions. 

PyBAMM-param is hosted on Github_. This page provides the *API*, or *developer documentation* for ''pybamm-param''.

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Quickstart
=========================
PyBaMM is available on GNU/Linux, MacOS and Windows.

Using pip
----------

GNU/Linux and Windows
~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   pip install pybamm-param

macOS
~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   brew install sundials && pip install pybamm-param

Using conda
-------------
PyBaMM is available as a conda package through the conda-forge channel.

.. code:: bash

   conda install -c conda-forge pybamm-param

API documentation
====================

.. module:: pybamm-param

.. toctree::
   :caption: Contents:

   source/cost_functions/index
   source/optimisation_problems/index
   source/optimisers/index
   source/optimisation_result

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Examples
========

Detailed examples can be viewed on the
`GitHub examples page <https://github.com/pybamm-team/PyBaMM/tree/develop/examples/notebooks>`_,
and run locally using ``jupyter notebook``, or online through
`Google Colab <https://colab.research.google.com/github/paramm-team/>`_.

Contributing
============

Contributions to PyBaMM and its development are welcome! If you have ideas for features, bug fixes, models, spatial methods, or solvers, we would love to hear from you.

Before contributing, please read the `Contribution Guidelines <https://github.com/paramm-team/pybamm-param/blob/main/CONTRIBUTING.md>`_.