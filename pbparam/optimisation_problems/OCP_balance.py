#
# OCP balance class
#

import pbparam
import pandas as pd
import numpy as np
from scipy import interpolate
import warnings


class OCPBalance(pbparam.BaseOptimisationProblem):
    """
    OCP balance optimisation problem class. This subclass uses data_fit for the base
    class 'data' and data_ref for the base class 'model'.
    """

    def __init__(self, data_fit, data_ref, weights=None, cost_function=pbparam.RMSE()):
        """
        Initialise the optimisation problem.
        data_fit : list or float
            id the fitting data, if float recast as list length 1
        data_ref : list or float
            is the reference data, if float recast as list length 1
        cost_function : :class:`pbparam.CostFunction`
            The cost function to use for the optimisation.
        """

        # Check data type of data and model, if not list recast as list
        if not isinstance(data_fit, (list)):
            data_fit = [data_fit]
            data_ref = [data_ref]

        # Check both lists have same length
        if len(data_fit) != len(data_ref):
            raise ValueError(
                "The number of fit and reference datasets must be the same."
            )
        
        super().__init__(
            cost_function=cost_function,
            data=data_fit,
            model=data_ref,
            weights=weights,
        )

        self.process_and_clean_data()
        
        # Process weights manually until we reformat OCPBalance
        # self.process_weights()

        # Give warning if weights are given with MLE
        if isinstance(cost_function, pbparam.MLE) and weights is not None:
            warnings.warn("Weights are provided but not used in the MLE calculation.")

        # Check the weights if it's None
        if weights is None:
            valid_data_ref = pd.to_numeric(data_ref, errors="coerce")
            self.weights = [1 / np.nanmean(valid_data_ref)] * len(data_ref)

        # Check if the weights has same lenght
        else:
            if len(weights) == 1:
                self.weights *= len(data_ref)
            elif len(weights) != len(data_ref):
                raise ValueError("Weights should have the same length as data_ref.")

    def objective_function(self, x):
        """
        Calculates the cost of the simulation based on the fitting parameters.

        Parameters
        ----------
        x : list
            List of fitting parameters.

        Returns
        -------
        cost : float
            The cost of the simulation.
        """

        # Iterate over the fit and reference data
        y_sim = []
        y_data = []
        for fit, ref in zip(self.data, self.model_fun):
            # Append simulated values to the y_sim list
            y_sim.append(ref(x[0] + x[1] * fit.iloc[:, 0]))
            # Append data values to the y_data list
            y_data.append(fit.iloc[:, 1].to_numpy())

        sd = list(x[2:])

        # Return the cost of the simulation using the cost function
        return self.cost_function.evaluate(y_sim, y_data, self.weights, sd)

    def process_and_clean_data(self):
        """
        Sets up the objective function for optimization.

        This function processes the reference data, interpolates it, and
        determines the initial guesses and bounds for the optimization.
        """
        # Process reference data, check if all elements are array-like
        if all([
            isinstance(x, (pd.DataFrame))
            for x in self.model]
        ):
            self.model_fun = []
            for data in self.model:
                # Interpolate reference data
                interp = interpolate.interp1d(
                    data.iloc[:, 0], data.iloc[:, 1], fill_value="extrapolate"
                )
                self.model_fun.append(interp)
        else:
            raise TypeError("data elements must be all array-like objects")

        # Determine initial guesses and bounds
        concat_model = pd.concat(self.data, axis=0, ignore_index=True)
        Q_V_max = concat_model.iloc[:, 0].loc[concat_model.iloc[:, 1].idxmax()]
        Q_V_min = concat_model.iloc[:, 0].loc[concat_model.iloc[:, 1].idxmin()]

        eps = 0.1  # tolerance
        self.x0 = [
            -Q_V_max / (Q_V_min - Q_V_max),
            1 / (Q_V_min - Q_V_max),
        ]

        if Q_V_min - Q_V_max > 0:
            ideal_bounds = [
                (-(1 + eps) * Q_V_max / (Q_V_min - Q_V_max), 1 + eps),
                (-eps, (1 + eps) / (Q_V_min - Q_V_max)),
            ]
        else:
            ideal_bounds = [
                (-eps, (1 + eps) * Q_V_max / (Q_V_max - Q_V_min)),
                (-(1 + eps) / (Q_V_max - Q_V_min), eps),
            ]

        self.bounds = [
            (min(x - 1e-6, bound[0]), max(x + 1e-6, bound[1]))
            for x, bound in zip(self.x0, ideal_bounds)
        ]

        if isinstance(self.cost_function, pbparam.MLE):
            self.x0 += [1] * len(self.model)
            self.bounds += [(1e-16, 1e3)] * len(self.model)

    def _plot(self, x_optimal):
        """
        Plot the reference and fit data.

        Parameters
        ----------
        x_optimal : list
            The optimal values of the parameters.

        Returns
        -------
        fig : :class:`matplotlib.figure.Figure`
            The figure object containing the plot.
        """
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 1)

        label = "Reference"
        for ref in self.data:
            ax.plot(ref.iloc[:, 0], ref.iloc[:, 1], "k-", label=label)
            label = None

        label = "Fit"
        for fit in self.model:
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
