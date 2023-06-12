#
# Base cost function class
#


class BaseCostFunction:
    """
    Base cost function class

    This class provide a base for defining cost functions, it defines the method that
    should be implemented in subclasses to evaluate the cost of a prediction.
    """

    def __init__(self):
        """
        Initialize the name of the cost function as "Base Cost Function"
        """
        self.name = "Base Cost Function"

    def evaluate(self, y_sim, y_data, sd=None, weights=[1]):
        """
        Placeholder method for evaluating the cost of a prediction

        Subclasses will override this method to provide specific implementations

        Parameters
        ----------
        y_sim : array-like
            predicted values
        y_data: array-like
            actual values
        weights: array-like
            weights of the parameters
        sd : float, optional
            standard deviation of error, not all cost function need it.

        """
        pass
