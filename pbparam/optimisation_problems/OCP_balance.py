#
# OCP balance class
#

import pbparam
import pandas as pd
from scipy import interpolate


class OCPBalance(pbparam.BaseOptimisationProblem):
    """
    OCP balance optimisation problem class.

    Parameters
    ----------
    data_fit : :class:`pandas.DataFrame`
        The OCP dataset to fit. This is experimental data that will be shifted and stretched
        to be same with :class:`data_ref`Either an array-like object or a list of array-like
        objects.
    data_ref : :class:`pandas.DataFrame`
        The OCP reference dataset(s). This dataset will be used as reference and :class:`data_fit`
        will be shifted and stretched to meet this dataset.
        They can be passed either as an array-like object
        or a list of array-like objects.
    cost_function : pbparam.BaseCostFunction
        Cost function class to evaluate error between two databases. It can be explicitly
        defined if any other method is used.

    """

    def __init__(self, data_fit, data_ref, cost_function=pbparam.RMSE()):
        super().__init__()

        # Allocate init variables
        if isinstance(data_fit, list):
            self.data_fit = data_fit
            self.data_ref = data_ref
        else:
            self.data_fit = [data_fit]
            self.data_ref = [data_ref]

        self.cost_function = cost_function

        # Check both lists have same length
        if len(self.data_fit) != len(self.data_ref):
            raise ValueError(
                "The number of fit and reference datasets must be the same."
            )

    def objective_function(self, x):
        y_sim = []
        y_data = []

        for fit, ref in zip(self.data_fit, self.data_ref_fun):
            y_sim.append(ref(x[0] + x[1] * fit.iloc[:, 0]))
            y_data.append(fit.iloc[:, 1].to_numpy())

        cost = self.cost_function.evaluate(y_sim, y_data)

        return cost

    def setup_objective_function(self):
        # Process reference data
        if all([isinstance(x, pd.DataFrame) for x in self.data_ref]):
            self.data_ref_fun = []
            for data in self.data_ref:
                interp = interpolate.interp1d(
                    data.iloc[:, 0], data.iloc[:, 1], fill_value="extrapolate"
                )
                self.data_ref_fun.append(interp)
        else:
            raise TypeError("data_ref elements must be all array-like objects")

        # Determine initial guesses and bounds
        concat_data_fit = pd.concat(self.data_fit, axis=0, ignore_index=True)
        Q_V_max = concat_data_fit.iloc[:, 0].loc[concat_data_fit.iloc[:, 1].idxmax()]
        Q_V_min = concat_data_fit.iloc[:, 0].loc[concat_data_fit.iloc[:, 1].idxmin()]

        eps = 0.1  # tolerance
        self.x0 = [
            -Q_V_max / (Q_V_min - Q_V_max),
            1 / (Q_V_min - Q_V_max),
        ]

        if Q_V_min - Q_V_max > 0:
            self.bounds = [
                (-(1 + eps) * Q_V_max / (Q_V_min - Q_V_max), 1 + eps),
                (-eps, (1 + eps) / (Q_V_min - Q_V_max)),
            ]
        else:
            self.bounds = [
                (-eps, (1 + eps) * Q_V_max / (Q_V_max - Q_V_min)),
                (-(1 + eps) / (Q_V_max - Q_V_min), eps),
            ]

    def _plot(self, x_optimal):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 1)

        label = "Reference"
        for ref in self.data_ref:
            ax.plot(ref.iloc[:, 0], ref.iloc[:, 1], "k-", label=label)
            label = None

        label = "Fit"
        for fit in self.data_fit:
            ax.plot(
                x_optimal[0] + x_optimal[1] * fit.iloc[:, 0],
                fit.iloc[:, 1],
                linestyle="--",
                color="C0",
                label=label,
            )
            label = None

        ax.set_xlabel("Stoichiometry")
        ax.set_ylabel("OCP [V]")
        ax.legend()
        fig.tight_layout()

        return fig
