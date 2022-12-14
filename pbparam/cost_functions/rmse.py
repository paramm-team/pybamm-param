#
# RMSE cost function class
#

import pbparam
import numpy as np



class RMSE(pbparam.BaseCostFunction):

    def __init__(self):
        self.name = "Root Mean Square Method"
        # super().__init__()
        # self.y_sim = y_sim
        # self.y_data = y_data
        # self.sd = sd

    def evaluate(self, y_sim, y_data, sd=None):

        err = y_sim - y_data
        err = err[~np.isnan(err)]

        MSE = np.sum(err**2) / len(err)
        RMSE = np.sqrt(MSE)

        return np.array(RMSE) 