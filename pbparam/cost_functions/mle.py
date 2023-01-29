# MLE cost function class
import pbparam

class MLE(pbparam.BaseCostFunction):
    """
    Maximum Likelihood Estimation (MLE) class, to evaluate error of simulation
    dataset to true dataset.
    
    Parameters
    ----------
    y_sim : array or list
            contains simulation data points
    y_data : array or list
            contains reference data points
    Returns
    -------
    MLE : array
            Calculated MLE for given inputs.
    """
    # Initializing the class and giving it a name
    def __init__(self):
        self.name = "Maximum Likelihood Estimation"

    # Define the evaluate method which will calculate the MLE
    def evaluate(self, y_sim, y_data, sd):
        # The code to calculate the MLE is not yet implemented
        # It is intended to use numpy and scipy libraries
        # negLL = -np.sum(stats.norm.logpdf(y_data, loc=y_sim, scale=sd))
        # return negLL
        
        # Placeholder for now
        pass