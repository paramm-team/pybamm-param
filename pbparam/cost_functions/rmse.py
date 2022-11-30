#
# RMSE cost function class
#

import pbparam
import numpy as np



class RMSE(pbparam.BaseCostFunction):

    def __init__():
        super().__init__()

    def evaluate(y_sim, y_data, sd=None):

        err = y_sim - y_data
        err = err[~np.isnan(err)]

        MSE = np.sum(err**2) / len(err)
        RMSE = np.sqrt(MSE)

        return np.array(RMSE) 