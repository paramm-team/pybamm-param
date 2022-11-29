#
# RMSE cost function class
#

import pbparam
import numpy as np



class RMSE(pbparam.BaseCostFunction):

    def __init__(self, simulation, data, variables_optimise, x):
        super().__init__()
        # Allocate init variables
        self.simulation = simulation
        self.data = data
        self.variables_optimise = variables_optimise
        self.x = x

    def evaluate(self):
        TNRMSE = 0
        for variable in variables_optimise:
            y_sim = solution[variable](data["Time [s]"])
            y_data = data[variable]

            err = y_sim - y_data
            err = err[~np.isnan(err)]

            MSE = np.sum(err**2) / len(err)
            RMSE = np.sqrt(MSE)
            NRMSE = RMSE / np.mean(y_data)
            TNRMSE = TNRMSE + NRMSE

        return np.array(TNRMSE) 