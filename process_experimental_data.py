#
# Auxiliary functions to load and process experimental data
#

import numpy as np
import pandas as pd
import os


def clean_dataset(dataset):
    new_dataset = dataset.dropna(axis=1, how="all")
    replace_dict = {
        "Step Time": "Step Time [s]",
        "Prog Time": "Time [s]",
        "Voltage": "Voltage [V]",
        "Current": "Current [A]",
        "AhAccu": "AhAccu [Ah]",
        "AhPrev": "AhPrev [Ah]",
        "WhAccu": "WhAccu [Wh]",
        "Watt": "Watt [W]",
    }

    if "LogTemp002" in new_dataset.columns:
        T_dict = {"LogTemp001": "Temp Cell [degC]", "LogTemp002": "Temp Ambient [degC]"}
    elif "LogTemp001" in new_dataset.columns:
        if "LogTempPositive" in new_dataset.columns:
            T_dict = {
                "LogTempPositive": "Temp Positive [degC]",
                "LogTempMid": "Temp Cell [degC]",
                "LogTempNegative": "Temp Negative [degC]",
                "LogTemp001": "Temp Ambient [degC]",
            }
        else:
            T_dict = {"LogTemp001": "Temp Cell [degC]"}
    else:
        T_dict = {
            "LogTempPositive": "Temp Positive [degC]",
            "LogTempMid": "Temp Cell [degC]",
            "LogTempNegative": "Temp Negative [degC]",
        }

    replace_dict.update(T_dict)

    new_dataset = new_dataset.rename(columns=replace_dict, errors="raise")

    return new_dataset


def import_thermal_data(Crate, T):
    if Crate == 0.1:
        cells = ["781", "782", "783", "784"]
    elif Crate == 0.5:
        cells = ["785", "786", "787", "788"]
    elif Crate == 1:
        cells = ["789", "790", "791", "792"]
    elif Crate == 2:
        cells = ["793", "794", "795", "796"]
    else:
        raise ValueError("Invalid C-rate")

    if T not in [0, 10, 25]:
        raise ValueError("Invalid temperature value")

    datasets = {}
    skiprows = list(range(15))
    skiprows.append(16)

    root = os.path.dirname(os.path.realpath(__file__))
    folder = "{}degC".format(T)

    for cell in cells:
        filename = "Cell{}_{}C_".format(cell, Crate).replace(".", "p") + folder + ".csv"
        imported_data = pd.read_csv(
            os.path.join(root, "data", folder, filename),
            skiprows=skiprows,
        )

        dataset = clean_dataset(imported_data)
        datasets.update({cell: dataset})

    return datasets


def get_idxs(dataset, I_dch, I_ch):
    i = dataset["Current [A]"]
    diff_i = np.diff(i)
    idx_start = np.where((diff_i < 0.95 * (-I_dch)) & (diff_i > 1.05 * (-I_dch)))
    idx_end = np.where((diff_i > 0.95 * I_ch) & (diff_i < 1.05 * I_ch))
    return idx_start[0], idx_end[0]
