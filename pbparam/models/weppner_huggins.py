#
# Weppner Huggins Model
#
import pybamm
import numpy as np


class WeppnerHuggins(pybamm.lithium_ion.BaseModel):
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
        t = pybamm.t
        ######################
        # Parameters
        ######################
        d_s = pybamm.Parameter("EC diffusivity [m2.s-1]")
        i_app = param.current_density_with_time
        U = pybamm.Parameter("Reference OCP [V]")
        Uprime = pybamm.Parameter("Derivative of the OCP wrt stoichiometry [V]")
        R = pybamm.Parameter("Effective resistance [Ohm]")
        a = pybamm.Parameter("Surface area per unit volume of particles")
        F = pybamm.Parameter("Faraday constant [C.mol-1]")
        l_w = pybamm.Parameter("Thickness of the working electrode")

        I = param.current_with_time

        ######################
        # Governing equations
        ######################
        u_surf = (
            (2 / np.pi) * (i_app / (pybamm.sqrt(d_s) * a * F * l_w)) * pybamm.sqrt(t)
        )
        # Linearised voltage
        V = U + Uprime * u_surf - R * I
        ######################
        # (Some) variables
        ######################
        self.variables = {
            "Positive particle surface " "concentration [mol.m-3]": u_surf,
            "Current [A]": I,
            "Voltage [V]": V,
        }

    property

    def geometry(self):
        return pybamm.Geometry()

    @property
    def default_submesh_types(self):
        return {}

    @property
    def default_var_pts(self):
        return {}

    @property
    def default_spatial_methods(self):
        return {}

    @property
    def default_solver(self):
        return pybamm.DummySolver()
