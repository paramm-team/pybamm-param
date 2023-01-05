#
# MLE cost function class
#

import pbparam
import numpy as np
import scipy.stats as stats


class MLE(pbparam.BaseCostFunction):
    def __init__(self):
        self.name = "Maximum Likelihood Estimation Method"

    def evaluate(self, y_sim, y_data, sd):
        negLL = -np.sum(stats.norm.logpdf(y_data, loc=y_sim, scale=sd))
        return negLL
