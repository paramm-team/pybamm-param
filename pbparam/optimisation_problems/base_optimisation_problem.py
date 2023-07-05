#
# Base optimisation problem class
#


class BaseOptimisationProblem:
    """
    Base optimisation problem class

    This class provides a base for defining optimization problems and contains
    methods that should be overridden in subclasses to provide specific implementations.
    """

    def __init__(
            self,
            cost_function=None,
            data=None,
            model=None,
            parameters=None,
            variables_to_fit=None
    ):
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
        data : :class:`pbparam.Data`
            Data object containing the data to be fitted
        model : :class:`pbparam.Model`
            Model object containing the model to be fitted
        variables_to_fit : list
            List of variables to be fitted
        """
        # Parameters to be defined in constructor
        self.x0 = None
        self.bounds = None
        self.scalings = None

        # Parameters that can be set by the user
        self.cost_function = cost_function
        assert self.cost_function is not None, "cost_function must be defined"
        self.data = data
        self.model = model
        self.parameters = parameters
        self.variables_to_fit = variables_to_fit

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
