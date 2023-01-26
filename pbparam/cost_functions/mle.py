#
# MLE cost function class
#

import pbparam
import numpy as np
import scipy.stats as stats


class MLE(pbparam.BaseCostFunction):
    def __init__(self):
        self.name = "Maximum Likelihood Estimation"

    def evaluate(self, y_sim, y_data, sd):
        y_sim = y_sim if isinstance(y_sim, list) else [y_sim]
        y_data = y_data if isinstance(y_data, list) else [y_data]
        sd = sd if isinstance(sd, list) else [sd]

        mle = 0
        for sim, data, s in zip(y_sim, y_data, sd):
            mle += -np.sum(stats.norm.logpdf(data, loc=sim, scale=s))

        return mle
