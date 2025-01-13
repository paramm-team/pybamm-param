import pbparam
import pandas as pd
import os


def ocp_example(suppress_plot=False):
    # Change working directory to import data
    os.chdir(
        os.path.join(
            pbparam.__path__[0],
            "input",
            "data",
        )
    )

    anode_half_lit = pd.read_csv("anode_OCP_2_lit.csv")
    anode_half_delit = pd.read_csv("anode_OCP_2_delit.csv")
    anode_three_lit = pd.read_csv("anode_OCP_3_lit.csv")
    anode_three_delit = pd.read_csv("anode_OCP_3_delit.csv")


    ocp_balance = pbparam.OCPBalance(
        [anode_three_lit, anode_three_delit], [anode_half_lit, anode_half_delit]
    )

    optimiser = pbparam.ScipyMinimize(method="Nelder-Mead")
    result = optimiser.optimise(ocp_balance)

    print(result)
    if not suppress_plot:
        result.plot()

    cathode_half_lit = pd.read_csv("cathode_OCP_2_lit.csv")
    cathode_half_delit = pd.read_csv("cathode_OCP_2_delit.csv")
    cathode_three_lit = pd.read_csv("cathode_OCP_3_lit.csv")
    cathode_three_delit = pd.read_csv("cathode_OCP_3_delit.csv")

    ocp_balance = pbparam.OCPBalance(
        [cathode_three_lit, cathode_three_delit], [cathode_half_lit, cathode_half_delit]
    )

    optimiser = pbparam.ScipyMinimize(method="Nelder-Mead")
    result = optimiser.optimise(ocp_balance)

    print(result)
    if not suppress_plot:
        result.plot()


# Run the example
if __name__ == "__main__":
    ocp_example()
