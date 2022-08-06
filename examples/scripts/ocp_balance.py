import pbparam
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

anode_half = pd.read_csv(os.path.join("data", "anode_OCP_2.csv"), header=None)
cathode_half = pd.read_csv(os.path.join("data", "cathode_OCP_2.csv"), header=None)
anode_three = pd.read_csv(os.path.join("data", "anode_OCP_3.csv"), header=None)
cathode_three = pd.read_csv(os.path.join("data", "cathode_OCP_3.csv"), header=None)

idx_max = anode_half[0].idxmax()

anode_half_dch = anode_half[: idx_max + 1]
anode_half_ch = anode_half[idx_max:]

ocp_balance = pbparam.OCPBalance(anode_three, [anode_half_dch, anode_half_ch])
ocp_balance.setup_cost_function()
optimiser = pbparam.ScipyMinimize(method="Nelder-Mead", solver_options={"xatol": 1e-12, "fatol": 1e-12})

result = optimiser.optimise(ocp_balance)
print(result.x, result.fun)

plt.plot(anode_half[0], anode_half[1], label="anode_half")
plt.plot(result.x[0] + anode_three[0] / result.x[1], anode_three[1], linestyle="--", label="anode_three")
plt.legend()
plt.show()

idx_max = cathode_half[0].idxmin()

cathode_half_dch = cathode_half[: idx_max + 1]
cathode_half_ch = cathode_half[idx_max:]

ocp_balance = pbparam.OCPBalance(cathode_three, [cathode_half_dch, cathode_half_ch])
ocp_balance.setup_cost_function()
optimiser = pbparam.ScipyMinimize(method="Nelder-Mead", extra_options={"tol": 1e-6})

result = optimiser.optimise(ocp_balance)
print(result.x, result.fun)

plt.plot(cathode_half[0], cathode_half[1], label="cathode_half")
plt.plot(result.x[0] + cathode_three[0] / result.x[1], cathode_three[1], linestyle="--", label="cathode_three")
plt.legend()
plt.show()
