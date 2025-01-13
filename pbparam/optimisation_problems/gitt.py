#
# Data fit class
#

import pbparam
import pybamm


class GITT(pbparam.DataFit):
    """
    A class to define an optimisation problem.

    Parameters
    ----------
    simulation : :class:`pybamm.Simulation`
        The simulation to be run to fit to data
    data : :class:`pandas.DataFrame`
         The experimental or reference data to be used in optimisation
         of simulation parameters.
    cost_function : :class:`pbparam.BaseCostFunction`
        Cost function class to be used in minimisation algorithm. The default
        is Root-Mean Square Error. It can be selected from pre-defined built-in
        functions or defined explicitly.
    solve_options : dict (optional)
        A dictionary of options to pass to the simulation. The default is None.
    """

    def __init__(
        self,
        param_dict,
        gitt_model,
        data,
        cost_function=pbparam.RMSE(),
        solve_options=None,
    ):
        simulation = pybamm.Simulation(gitt_model, parameter_values=param_dict)
        super().__init__(
            simulation=simulation,
            cost_function=cost_function,
            data=data,
            parameters={
                "Positive particle diffusivity [m2.s-1]": (
                    5e-14,
                    (2.06e-16, 2.06e-12),
                ),
                "Reference OCP [V]": (4.2, (0, 5)),
            },
            variables_to_fit=["Voltage [V]"],
            solve_options=solve_options,
        )
