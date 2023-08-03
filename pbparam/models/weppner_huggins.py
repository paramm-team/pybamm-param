#
# Basic GITT Model (temporary)
#
import pybamm


class WeppnerHuggins(pybamm.BaseModel):
    """WeppnerHuggins Model for GITT.

    Parameters
    ----------
    name : str, optional
        The name of the model.
    """

    def __init__(self, name="WeppnerHuggins model"):
        super().__init__({}, name)
        # `param` is a class containing all the relevant parameters and functions for
        # this model. These are purely symbolic at this stage, and will be set by the
        # `ParameterValues` class when the model is processed.
        param = self.param

        model = pybamm.BaseModel()
        t = pybamm.t

        model.variables = {
            "linear": t,
            "quadratic": t**2,
            "sinusoidal": pybamm.sin(t)
        }

        solver = pybamm.DummySolver()
        return solver.solve(model, self.t_eval)