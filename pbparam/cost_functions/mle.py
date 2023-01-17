#
# MLE cost function class
#

import pbparam

# import numpy as np
# import scipy.stats as stats


class MLE(pbparam.BaseCostFunction):
    """
    Maximum Likelihood Estimation (MLE) class, to evaluate error of simulation
    dataset to true dataset.

    Parameters
    ----------
    y_sim : array or list
            contains simulation data points
    y_data : array or list
            contains reference data points
    Returns
    -------
    MLE : array
            Calculated MLE for given inputs.
    """
    def __init__(self):
        self.name = "Maximum Likelihood Estimation"

    def evaluate(self, y_sim, y_data, sd):
        # TODO: to be implemented
        # negLL = -np.sum(stats.norm.logpdf(y_data, loc=y_sim, scale=sd))
        # return negLL

        pass
