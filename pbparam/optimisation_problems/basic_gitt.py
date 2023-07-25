#
# Basic GITT Model (temporary)
#
import pybamm


class BasicGITT(pybamm.lithium_ion.BaseModel):
    """Linearised Single Particle Model for GITT.

    Parameters
    ----------
    name : str, optional
        The name of the model.
    """

    def __init__(self, name="GITT model"):
        super().__init__({}, name)
        # `param` is a class containing all the relevant parameters and functions for
        # this model. These are purely symbolic at this stage, and will be set by the
        # `ParameterValues` class when the model is processed.
        param = self.param

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

        # Constant temperature
        T = param.T_init

        ######################
        # Other set-up
        ######################

        # Current density
        i_cell = param.current_density_with_time
        a_p = 3 * param.p.prim.epsilon_s_av / param.p.prim.R_typ
        j_p = -i_cell / (param.p.L * a_p)

        ######################
        # State of Charge
        ######################
        I = param.current_with_time
        # The `rhs` dictionary contains differential equations, with the key being the
        # variable in the d/dt
        self.rhs[Q] = I / 3600
        # Initial conditions must be provided for the ODEs
        self.initial_conditions[Q] = pybamm.Scalar(0)

        ######################
        # Particles
        ######################

        # The div and grad operators will be converted to the appropriate matrix
        # multiplication at the discretisation stage
        N_s_p = -param.p.prim.D(c_s_p, T) * pybamm.grad(c_s_p)
        self.rhs[c_s_p] = -pybamm.div(N_s_p)
        # Surf takes the surface value of a variable, i.e. its boundary value on the
        # right side. This is also accessible via `boundary_value(x, "right")`, with
        # "left" providing the boundary value of the left side
        c_s_surf_p = pybamm.surf(c_s_p)
        # Boundary conditions must be provided for equations with spatial derivatives
        self.boundary_conditions[c_s_p] = {
            "left": (pybamm.Scalar(0), "Neumann"),
            "right": (
                -j_p / param.F / param.p.prim.D(c_s_surf_p, T),
                "Neumann",
            ),
        }
        # c_n_init and c_p_init are functions of r and x, but for the SPM we
        # take the x-averaged value since there is no x-dependence in the particles
        self.initial_conditions[c_s_p] = pybamm.x_average(param.p.prim.c_init)
        # Events specify points at which a solution should terminate
        sto_surf_p = c_s_surf_p / param.p.prim.c_max
        self.events += [
            pybamm.Event(
                "Minimum positive particle surface stoichiometry",
                pybamm.min(sto_surf_p) - 0.01,
            ),
            pybamm.Event(
                "Maximum positive particle surface stoichiometry",
                (1 - 0.01) - pybamm.max(sto_surf_p),
            ),
        ]

        # Note that the SPM does not have any algebraic equations, so the `algebraic`
        # dictionary remains empty

        ######################
        # (Some) variables
        ######################
        # Linearised voltage
        U = pybamm.Parameter("Reference OCP [V]")
        Uprime = pybamm.Parameter("Derivative of the OCP wrt stoichiometry [V]")
        R = pybamm.Parameter("Effective resistance [Ohm]")
        delta_c_s = pybamm.boundary_value(
            c_s_surf_p - pybamm.surf(param.p.prim.c_init), "right"
        )
        V = U + Uprime * delta_c_s / param.p.prim.c_max - R * I

        # The `variables` dictionary contains all variables that might be useful for
        # visualising the solution of the model
        # Primary broadcasts are used to broadcast scalar quantities across a domain
        # into a vector of the right shape, for multiplying with other vectors
        self.variables = {
            "Discharge capacity [A.h]": Q,
            "Positive particle surface "
            "concentration [mol.m-3]": pybamm.PrimaryBroadcast(
                c_s_surf_p, "positive electrode"
            ),
            "Current [A]": I,
            "Voltage [V]": V,
        }
        # self.events += [
        #     pybamm.Event("Minimum voltage [V]", V - param.voltage_low_cut),
        #     pybamm.Event("Maximum voltage [V]", param.voltage_high_cut - V),
        # ]
