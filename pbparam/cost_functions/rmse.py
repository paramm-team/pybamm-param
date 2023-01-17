#
# RMSE cost function class
#

import pbparam
import numpy as np


class RMSE(pbparam.BaseCostFunction):
    """
    The Root-Mean Square Error (RMSE) class, to evaluate error of simulation
    dataset to true dataset.

    Parameters
    ----------
    y_sim : array or list
            contains simulation data points
    y_data : array or list
            contains reference data points
    Returns
    -------
    RMSE : array
            Calculated RMSE for given inputs.
    """
    def __init__(self):
        self.name = "Root Mean Square Error"

    def evaluate(self, y_sim, y_data, sd=None):
        y_sim = y_sim if isinstance(y_sim, list) else [y_sim]
        y_data = y_data if isinstance(y_data, list) else [y_data]

        RMSE = 0

        for sim, data in zip(y_sim, y_data):
            err = (sim - data) / np.nanmean(data)
            RMSE += np.sqrt(np.nanmean(err**2))

        return np.array(RMSE)
