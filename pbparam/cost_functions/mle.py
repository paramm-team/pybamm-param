#
# RMSE cost function class
#

import pbparam
import numpy as np
import scipy.stats as stats


class MLE(pbparam.BaseCostFunction):

    def __init__(self, simulation, data, variables_optimise, x):
        super().__init__()
        # Allocate init variables
        self.simulation = simulation
        self.data = data
        self.variables_optimise = variables_optimise
        self.x = x

    def calcloglikelihood(solution, x_data, y_data, sd):
        y_sim = solution(x_data)
        negLL = -np.sum( stats.norm.logpdf(y_data, loc=y_sim, scale=sd))
        return negLL