#
# MLE cost function class
#

import pbparam
import numpy as np
import scipy.stats as stats


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

    # Initializing the class and giving it a name
    def __init__(self):
        self.name = "Maximum Likelihood Estimation"

    # Define the evaluate method which will calculate the MLE
    def evaluate(self, y_sim, y_data, weights, sd):
        y_sim = y_sim if isinstance(y_sim, list) else [y_sim]
        y_data = y_data if isinstance(y_data, list) else [y_data]
        weights = weights if isinstance(weights, list) else [weights]
        sd = sd if isinstance(sd, list) else [sd]

        mle = 0
        for sim, data, s, weight in zip(y_sim, y_data, sd, weights):
            mle += -np.nansum(weight * stats.norm.logpdf(data, loc=sim, scale=s))

        return mle

    def _get_parameters(self, variables):
        """
        Get the optimisation parameters introduced by the cost function.

        Parameters
        ----------
        variables : list
            List of variables to optimise.

        Returns
        -------
        parameters : dict
            Dictionary of parameters.
        """
        parameters = {}
        for variable in variables:
            name = "Standard deviation of " + variable[0].lower() + variable[1:]
            # TODO: provide better guesses for the bounds
            parameters[name] = (1, (1e-16, 1e3))
        return parameters
