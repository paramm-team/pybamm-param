import pbparam
import pandas as pd
import os

anode_half_lit = pd.read_csv(os.path.join("data", "anode_OCP_2_lit.csv"))
anode_half_delit = pd.read_csv(os.path.join("data", "anode_OCP_2_delit.csv"))
anode_three_lit = pd.read_csv(os.path.join("data", "anode_OCP_3_lit.csv"))
anode_three_delit = pd.read_csv(os.path.join("data", "anode_OCP_3_delit.csv"))


ocp_balance = pbparam.OCPBalance(
    [anode_three_lit, anode_three_delit], [anode_half_lit, anode_half_delit]
)
optimiser = pbparam.ScipyMinimize(
    method="Nelder-Mead", solver_options={"xatol": 1e-12, "fatol": 1e-12}
)

result = optimiser.optimise(ocp_balance)
print(result)

result.plot()

cathode_half_lit = pd.read_csv(os.path.join("data", "cathode_OCP_2_lit.csv"))
cathode_half_delit = pd.read_csv(os.path.join("data", "cathode_OCP_2_delit.csv"))
cathode_three_lit = pd.read_csv(os.path.join("data", "cathode_OCP_3_lit.csv"))
cathode_three_delit = pd.read_csv(os.path.join("data", "cathode_OCP_3_delit.csv"))

ocp_balance = pbparam.OCPBalance(
    [cathode_three_lit, cathode_three_delit], [cathode_half_lit, cathode_half_delit]
)
optimiser = pbparam.ScipyMinimize(method="Nelder-Mead", extra_options={"tol": 1e-6})

result = optimiser.optimise(ocp_balance)
print(result)

result.plot()
