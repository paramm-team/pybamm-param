#
# Base optimiser class
#
import pybamm


class BaseOptimiser(object):
    """
    Optimise and OptimisationProblem object.

    Parameters
    ----------
    method : str, optional
        The method to use for optimisation, specific to each optimiser
    additional args :
        TODO: write this
    """

    def __init__(self):
        # Defaults, can be overwritten by specific optimisers
        self.name = "Base optimiser"
        self.single_variable = False
        self.global_optimiser = False

    def optimise(
        self, optimisation_problem, x0=None, bounds=None, pybamm_logging_level=None
    ):
        """
        Optimise the optimisation problem.

        Parameters
        ----------
        optimisation_problem : :class:`OptimisationProblem`
            The optimisation problem to be optimised.
        x0 : numpy array (optional)
            The initial guesses for the optimisation.
        bounds : list of tuples (optional)
            The bounds for the optimisation.
        pybamm_logging_level : str, optional
            The logging level to use when running the PyBaMM simulations. If None, it
            defaults to "ERROR"
        Returns
        -------
        :class:`OptimisationResult` object.
            The results of the optimisation.
        """
        # Setup cost function which resets simulation.solve.integrator_specs
        # Otherwise the multiprocessing will fail
        optimisation_problem.setup_cost_function()

        # Change logging level
        old_logging_level = pybamm.logger.level
        if pybamm_logging_level:
            pybamm.set_logging_level(pybamm_logging_level)
        else:
            pybamm.set_logging_level("ERROR")

        self.x0 = x0 or optimisation_problem.x0
        self.bounds = bounds or optimisation_problem.bounds

        result = self._run_optimiser(optimisation_problem, self.x0, self.bounds)

        # Restore original logging level
        pybamm.set_logging_level(old_logging_level)

        return result
