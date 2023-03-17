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

    def evaluate(self, y_sim, y_data, weights, sd=None ):
        """
        Evaluate RMSE cost function.

        Parameters
        ----------
        y_sim : array or list
            contains simulation data points
        y_data : array or list
            contains reference data points
        sd : array or list, optional
            contains the standard deviation of the data points, used for weighting
            the cost function. This variable will NOT be used in RMSE. Default is None.
        weights : array or list, optional
            contains custom weights for each data point. Size of weights must be
            equal to size of reference data points!

        Returns
        -------
        RMSE : array
            Calculated RMSE for given inputs.
        """
        # Ensure y_sim and y_data are lists
        y_sim = y_sim if isinstance(y_sim, list) else [y_sim]
        y_data = y_data if isinstance(y_data, list) else [y_data]

        RMSE = 0

        # Check if custom weights are provided and raise error if not correct
        # if weights is None:
        #     weights = [1 for _ in y_data]
        # elif len(weights) != len(y_data):
        #     raise
        #     ValueError("Length of weights must be equal to the length of data points")

        # Recalculate y_data with the weights provided
        weighted_y_data = [v * w for v, w in zip(y_data, weights)]

        # Iterate over each simulation and data point
        for sim, data in zip(y_sim, weighted_y_data):
            # Calculate the error and normalize by the mean of the data
            err = (sim - data) / np.nanmean(data)
            # Add the square root of the mean square error to the RMSE variable
            RMSE += np.sqrt(np.nanmean(err**2))

        return np.array(RMSE)
