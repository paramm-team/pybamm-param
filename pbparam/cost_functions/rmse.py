#
# RMSE cost function class
#

import pbparam
import numpy as np


class RMSE(pbparam.BaseCostFunction):
    def __init__(self):
        self.name = "Root Mean Square Method"

    def evaluate(self, y_sim, y_data, sd=None):
        y_sim = y_sim if isinstance(y_sim, list) else [y_sim]
        y_data = y_data if isinstance(y_data, list) else [y_data]

        RMSE = 0

        for sim, data in zip(y_sim, y_data):
            err = (sim - data) / np.nanmean(data)
            RMSE += np.sqrt(np.nanmean(err**2))

        return np.array(RMSE)
