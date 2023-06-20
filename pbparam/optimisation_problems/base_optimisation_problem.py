#
# Base optimisation problem class
#


class BaseOptimisationProblem:
    """
    Base optimisation problem class

    This class provides a base for defining optimization problems and contains
    methods that should be overridden in subclasses to provide specific implementations.
    """

    def __init__(self, cost_function=None):
        """
        Initialize the class properties

        x0 : array-like
            Initial guess for the optimization problem
        bounds : tuple
            bounds of the optimization problem
        scalings : array-like
            scalings for the optimization problem
        cost_function : :class:`pbparam.BaseCostFunction`
            Cost function class to be used in minimisation algorithm.
            The default is Root-Mean Square Error. It can be selected from
            pre-defined built-in functions or defined explicitly
        """
        self.x0 = None
        self.bounds = None
        self.scalings = None
        self.cost_function = cost_function
        assert self.cost_function is not None, "cost_function must be defined"

    def objective_function(self, x):
        """
        Placeholder method for the objective function

        Subclasses will override this method to provide specific implementations

        Parameters
        ----------
        x : array-like
            independent variable for the objective function

        Returns
        -------
        float
            the value of the objective function
        """
        raise NotImplementedError(
            "objective_function not defined, setup_objective_function needs to"
            " be called first"
        )

    def setup_objective_function(self):
        """
        Placeholder method for setting up the objective function

        Subclasses will override this method to provide specific implementations
        """
        pass

    def calculate_solution(self):
        """
        Placeholder method for calculating the solution of the optimization problem

        Subclasses will override this method to provide specific implementations
        """
        pass

    def _plot(self, x):
        """
        Placeholder method for plotting the optimization problem

        Subclasses will override this method to provide specific implementations

        Parameters
        ----------
        x : array-like
            independent variable for the plot
        """
        pass
