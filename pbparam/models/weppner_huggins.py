#
# Basic GITT Model (temporary)
#
import pybamm
import numpy as np

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
        t = pybamm.t
        ######################
        # Parameters
        ######################
        d_s = pybamm.Parameter("Diffusion coefficient")
        i_cell = param.current_density_with_time
        # Linearised voltage
        U = pybamm.Parameter("Reference OCP [V]")
        Uprime = pybamm.Parameter("Derivative of the OCP wrt stoichiometry [V]")
        R = pybamm.Parameter("Effective resistance [Ohm]")
        a = pybamm.Parameter("Surface area per unit volume of particles")
        F = pybamm.Parameter("Faraday constant")
        l_w = pybamm.Parameter("Thickness of the working electrode")
        I = param.current_with_time

         ######################
        # Variables
        ######################
        # Variables that depend on time only are created without a domain
        Q = pybamm.Variable("Discharge capacity [A.h]")
        # Variables that vary spatially are created with a domain
        c_s_p = pybamm.Variable(
            "X-averaged positive particle concentration [mol.m-3]",
            domain="positive particle",
        )
        ######################
        # Governing equations
        ######################
        u_surf = (2/np.pi)*(i_cell/(np.sqrt(d_s*c_s_p)*a*F*l_w))*np.sqrt(t)
        V = U + Uprime * u_surf - R * I
        ######################
        # (Some) variables
        ######################
        self.variables = {
            "Discharge capacity [A.h]": Q,
            "Positive particle surface "
            "concentration [mol.m-3]": pybamm.PrimaryBroadcast(
                c_s_p, "positive electrode"
            ),
            "Current [A]": I,
            "Voltage [V]": V,
        }
    property
    def default_geometry(self):
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