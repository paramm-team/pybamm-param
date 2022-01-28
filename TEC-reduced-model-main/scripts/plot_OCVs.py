#
# Plot OCVs
#

import pybamm
import matplotlib.pyplot as plt
from os import path

plt.style.use(["science", "vibrant"])

plt.rcParams.update(
    {
        "font.size": 8,
        "axes.labelsize": 10,
    }
)

pybamm.set_logging_level("INFO")

root = path.dirname(path.dirname(__file__))

# Define parameter set Chen 2020 (see PyBaMM documentation for details)
param = pybamm.ParameterValues(chemistry=pybamm.parameter_sets.Chen2020)

Up = param["Positive electrode OCP [V]"][1]
Un = param["Negative electrode OCP [V]"][1]

fig, axes = plt.subplots(1, 2, figsize=(5.5, 2.5))

axes[0].plot(Up[:, 0], Up[:, 1])
axes[0].set_xlabel("Stoichiometry")
axes[0].set_ylabel("Positive electrode OCP (V)")

axes[1].plot(Un[:, 0], Un[:, 1])
axes[1].set_xlabel("Stoichiometry")
axes[1].set_ylabel("Negative electrode OCP (V)")

plt.tight_layout()

fig.savefig(path.join(root, "figures", "OCVs.png"), dpi=300)
