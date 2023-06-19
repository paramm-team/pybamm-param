#
# Shared objective functions for testing
#
import numpy as np


def sphere(x):
    return np.inner(x, x)


def rosenbrock(x):
    return np.sum(100 * (x[1:] - x[:-1] ** 2) ** 2 + (1 - x[:-1]) ** 2)
