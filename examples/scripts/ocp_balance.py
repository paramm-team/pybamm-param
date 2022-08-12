import pbparam
import pandas as pd
import os

anode_half = pd.read_csv(os.path.join("data", "anode_OCP_2.csv"), header=None)
cathode_half = pd.read_csv(os.path.join("data", "cathode_OCP_2.csv"), header=None)
anode_three = pd.read_csv(os.path.join("data", "anode_OCP_3.csv"), header=None)
cathode_three = pd.read_csv(os.path.join("data", "cathode_OCP_3.csv"), header=None)

idx_max = anode_half[0].idxmax()

anode_half_dch = anode_half[: idx_max + 1]
anode_half_ch = anode_half[idx_max:]

ocp_balance = pbparam.OCPBalance(anode_three, [anode_half_dch, anode_half_ch])
ocp_balance.setup_cost_function()
optimiser = pbparam.ScipyMinimize(
    method="Nelder-Mead", solver_options={"xatol": 1e-12, "fatol": 1e-12}
)

result = optimiser.optimise(ocp_balance)
print(result.x, result.fun)

result.plot()

idx_max = cathode_half[0].idxmin()

cathode_half_dch = cathode_half[: idx_max + 1]
cathode_half_ch = cathode_half[idx_max:]

ocp_balance = pbparam.OCPBalance(cathode_three, [cathode_half_dch, cathode_half_ch])
ocp_balance.setup_cost_function()
optimiser = pbparam.ScipyMinimize(method="Nelder-Mead", extra_options={"tol": 1e-6})

result = optimiser.optimise(ocp_balance)
print(result.x, result.fun)

result.plot()
