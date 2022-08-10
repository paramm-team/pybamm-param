#
# OCP balance class
#

import pbparam
import numpy as np
import pandas as pd
from scipy import interpolate


class OCPBalance(pbparam.BaseOptimisationProblem):
    """
    OCP balance class.

    Parameters
    ----------
    data_fit : pandas.DataFrame
        The OCP dataset to fit to.
    data_ref : tuple
        The OCP reference data. It is a tuple with the discharge and charge curves,
        either as a function or an array-like object. If the latter, the data is
        interpolated.
    """

    def __init__(self, data_fit, data_ref):
        # Allocate init variables
        self.data_fit = data_fit
        self.data_ref = data_ref

    def cost_function(self, x):
        err_ch = (
            self.data_fit_ch[1] / self.data_ref_ch(x[0] + self.data_fit_ch[0] / x[1])
            - 1
        )
        err_dch = (
            self.data_fit_dch[1] / self.data_ref_dch(x[0] + self.data_fit_dch[0] / x[1])
            - 1
        )

        err_ch = err_ch[~np.isnan(err_ch)]
        err_dch = err_dch[~np.isnan(err_dch)]

        MSE = np.mean(err_ch**2) + np.mean(err_dch**2)

        return MSE

    def setup_cost_function(self):
        # Process reference data
        if all([callable(x) for x in self.data_ref]):
            self.data_ref_dch = self.data_ref[0]
            self.data_ref_ch = self.data_ref[1]
            x_min, x_max = 0, 1
        elif all([isinstance(x, pd.DataFrame) for x in self.data_ref]):
            self.data_ref_dch = interpolate.interp1d(
                self.data_ref[0][0], self.data_ref[0][1], fill_value="extrapolate"
            )
            self.data_ref_ch = interpolate.interp1d(
                self.data_ref[1][0], self.data_ref[1][1], fill_value="extrapolate"
            )
            x_min = min([data[0].min() for data in self.data_ref])
            x_max = max([data[0].max() for data in self.data_ref])
        else:
            raise TypeError(
                "data_ref elements must be same type, and either functions or"
                "array-like objects"
            )
        # Process experimental data
        idx_max = self.data_fit[0].idxmax()
        Q_V_max = self.data_fit[0].loc[self.data_fit[1].idxmax()]
        Q_V_min = self.data_fit[0].loc[self.data_fit[1].idxmin()]

        # Determine initial guesses and bounds
        self.x0 = [
            (Q_V_max * x_max - Q_V_min * x_min) / (Q_V_max - Q_V_min),
            (Q_V_min - Q_V_max) / (x_max - x_min),
        ]
        self.bounds = [
            (-10 * abs(self.x0[0]), 10 * abs(self.x0[0])),
            (-10 * abs(self.x0[1]), 10 * abs(self.x0[1])),
        ]

        self.data_fit_ch = self.data_fit[: idx_max + 1]
        self.data_fit_dch = self.data_fit[idx_max:]

    def _plot(self, x_optimal):
        import matplotlib.pyplot as plt

        if all([callable(x) for x in self.data_ref]):
            # TODO: need to think how we pass the limits of the reference function
            raise NotImplementedError

        fig, ax = plt.subplots(1, 1)
        ax.plot(self.data_ref[0][0], self.data_ref[0][1], "k-", label="Reference")
        ax.plot(self.data_ref[1][0], self.data_ref[1][1], "k-")
        ax.plot(
            x_optimal[0] + self.data_fit[0] / x_optimal[1],
            self.data_fit[1],
            "--",
            label="Fit",
        )
        ax.set_xlabel("Stoichiometry")
        ax.set_ylabel("OCP [V]")
        ax.legend()
        fig.tight_layout()

        return fig
