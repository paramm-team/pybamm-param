#
# Base optimisation problem class
#

# import pybamm
import numpy as np


class BaseModel:
    """
    Base model class

    This class provides a base for models and contains
    methods that should be overridden in subclasses to provide specific implementations.


    This base class will always have the following properties, in subclasses they may
    be renamed to be more specific to the problem being solved but for internal use they
    will be renamed back to the generic names. Use in subclasses will use the generic
    names.
    Non generic names are for use in the constructor only as a communication to the
    user.

    Parameters (required)
    ---------------------
    model : :class:`pybamm.Simulation` (or pandas.DataFrame)
        The object to be used in optimisation of simulation parameters.

    Parameters (optional)
    ---------------------
    parameters : dict
        The parameters to be optimised. They should be provided as a dictionary where
        the keys are the names of the variables to be optimised and the values are a
        tuple with the initial guesses and the lower and upper bounds of the
        optimisation.

    """

    def __init__(
            self,
            *args,
            model=None,
            parameters=None
    ):
        """
        Initialize the class properties

        model : :class:`pybamm.Simulation` (or pandas.DataFrame)
            Model object containing the model to be fitted
        parameters : dict
            Parameters object containing the parameters to be fitted
        """

        if len(args) > 0:
            # if positional arguments are passed raise an error, this enforces the use
            # of proper names for the arguments during subclass constructors making
            # inspection easier for future developers.
            raise NotImplementedError(
                "BaseModel does not take any positional arguments"
            )



        # Parameters that can be set by the user
        self.model = model
        self.parameters = parameters


