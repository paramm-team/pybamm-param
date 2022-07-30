
import pandas as pd
import numpy as np
from scipy import interpolate,optimize
import matplotlib.pyplot as plt

class ocp(object):
    def __init__(self,
                 anode_half_cell_data,
                 cathode_half_cell_data,
                 anode_three_electrode_data,
                 cathode_three_electrode_data
    ):
        self.anode_half_cell_data = anode_half_cell_data
        self.cathode_half_cell_data = cathode_half_cell_data
        self.anode_three_electrode_data = anode_three_electrode_data
        self.cathode_three_electrode_data = cathode_three_electrode_data
    def ocp_optimize(self):

    # Seperating the data for charge and discharge to get a better fit. this is done by splitting the data where it has maximum.

        ch_anode_half_cell = self.anode_half_cell_data[:(self.anode_half_cell_data[0].idxmax()+1)]
        dch_anode_half_cell = self.anode_half_cell_data[self.anode_half_cell_data[0].idxmax():]
        ch_anode_three_electrode = self.anode_three_electrode_data[:(self.anode_three_electrode_data[0].idxmax()+1)]
        dch_anode_three_electrode = self.anode_three_electrode_data[self.anode_three_electrode_data[0].idxmax():]

        ch_cathode_half_cell = self.cathode_half_cell_data[:(self.cathode_half_cell_data[0].idxmax() + 1)]
        dch_cathode_half_cell = self.cathode_half_cell_data[self.cathode_half_cell_data[0].idxmax():]
        ch_cathode_tree_electrode = self.cathode_three_electrode_data[:(self.cathode_three_electrode_data[0].idxmax() + 1)]
        dch_cathode_three_electrode = self.cathode_three_electrode_data[self.cathode_three_electrode_data[0].idxmax():]

    # Creating functions with this data via interpolating the values between the samples.

        f_ch_anode_2=interpolate.interp1d(ch_anode_half_cell[0], ch_anode_half_cell[1], fill_value ="extrapolate")
        f_dch_anode_2=interpolate.interp1d(dch_anode_half_cell[0], dch_anode_half_cell[1], fill_value ="extrapolate")
        f_ch_anode_3=interpolate.interp1d(ch_anode_three_electrode[0], ch_anode_three_electrode[1], fill_value ="extrapolate")
        f_dch_anode_3=interpolate.interp1d(dch_anode_three_electrode[0], dch_anode_three_electrode[1], fill_value ="extrapolate")

        f_ch_cathode_2=interpolate.interp1d(ch_cathode_half_cell[0], ch_cathode_half_cell[1], fill_value ="extrapolate")
        f_dch_cathode_2=interpolate.interp1d(dch_cathode_half_cell[0], dch_cathode_half_cell[1], fill_value ="extrapolate")
        f_ch_cathode_3=interpolate.interp1d(ch_cathode_tree_electrode[0], ch_cathode_tree_electrode[1], fill_value ="extrapolate")
        f_dch_cathode_3=interpolate.interp1d(dch_cathode_three_electrode[0], dch_cathode_three_electrode[1], fill_value ="extrapolate")

    # Take the maximum point in between the minimums of 2 lines and the minimum point between the maximums of 2 lines
    # This is done to making sure the function is minimized within interpolation range.
    # The extrapolation range might not valid.

        x_anode = np.linspace(max(min(self.anode_half_cell_data[0]), min(self.anode_three_electrode_data[0])), min(max(self.anode_half_cell_data[0]), max(self.anode_three_electrode_data[0])), num = 10000)
        x_cathode = np.linspace(max(min(self.cathode_half_cell_data[0]), min(self.cathode_three_electrode_data[0])), min(max(self.cathode_half_cell_data[0]), max(self.cathode_three_electrode_data[0])), num = 10000)
    
        
        # Optimizing functions
 
        
        # Defining the functions to minimize. The effect of charge and discharge is balanced with taking average.

        def anode_fit(p):
            return (sum((f_ch_anode_3(x_anode) - f_ch_anode_2(x_anode - p))**2) +
                    sum((f_dch_anode_3(x_anode) - f_dch_anode_2(x_anode - p))**2))/len(x_anode)

        def cathode_fit(p):
            return (sum((f_ch_cathode_3(x_cathode) - f_ch_cathode_2(x_cathode - p))**2) +
                    sum((f_dch_cathode_3(x_cathode) - f_dch_cathode_2(x_cathode - p))**2))/len(x_cathode)

        anode_optm = optimize.least_squares(anode_fit, 0)
        cathode_optm = optimize.least_squares(cathode_fit, 0)
        print('Anode Optimizer:',anode_optm)
        print('Cathode Optimizer:',cathode_optm)
        self.anode_optm = anode_optm
        self.cathode_optm = cathode_optm
    
    def anode_plot(self, anode_leftlimit = 0., anode_rightlimit =1.):
        self.anode_leftlimit = anode_leftlimit
        self.anode_rightlimit = anode_rightlimit
        self.shifted_anode = self.anode_half_cell_data[0] + self.anode_optm.x
        fig, ax = plt.subplots(constrained_layout=True)
        ax.plot(self.shifted_anode, self.anode_half_cell_data[1], 'r--', label='half cell')
        ax.plot(self.anode_three_electrode_data[0], self.anode_three_electrode_data[1], 'b', label='3-electrode full cell')
        ax.legend()
        ax.set_xlabel('Capacity (mAh cm^{-2})')
        ax.set_ylabel('Potential (V)')
        ax.set_title('Negative Electrode')


        def capacity2stoic(x):
            return (self.anode_rightlimit - self.anode_leftlimit) * ((x - min(self.shifted_anode)) / (max(self.shifted_anode) - min(self.shifted_anode))) + self.anode_leftlimit
        def stoic2capacity(x):
            return (x - self.anode_leftlimit) * ((max(self.shifted_anode) - min(self.shifted_anode)) / (self.anode_rightlimit - self.anode_leftlimit)) + min(self.shifted_anode)

        secax = ax.secondary_xaxis('top', functions=(capacity2stoic, stoic2capacity))
        secax.set_xlabel('Stoichiometry')
        plt.show()
        print("Negative Electrode Maximum Stoichiometry:", capacity2stoic(max(self.cathode_three_electrode_data[0])))
        print("Negative Electrode Minimum Stoichiometry:", capacity2stoic(min(self.cathode_three_electrode_data[0])))

    def cathode_plot(self, cathode_leftlimit = 1., cathode_rightlimit = 0.318):
        self.cathode_leftlimit = cathode_leftlimit
        self.cathode_rightlimit = cathode_rightlimit
        self.shifted_cathode=self.cathode_half_cell_data[0] + self.cathode_optm.x
        fig, ax = plt.subplots(constrained_layout=True)
        ax.plot(self.shifted_cathode, self.cathode_half_cell_data[1], 'r--', label='half cell')
        ax.plot(self.cathode_three_electrode_data[0], self.cathode_three_electrode_data[1], 'b', label='3-electrode full cell')
        ax.legend()
        ax.set_xlabel('Capacity (mAh cm^{-2})')
        ax.set_ylabel('Potential (V)')
        ax.set_title('Positive Electrode')


        def capacity2stoic(x):
            return (self.cathode_rightlimit - self.cathode_leftlimit) * ((x - min(self.shifted_cathode)) / (max(self.shifted_cathode) - min(self.shifted_cathode))) + self.cathode_leftlimit
        def stoic2capacity(x):
            return (x - self.cathode_leftlimit) * ((max(self.shifted_cathode) - min(self.shifted_cathode)) / (self.cathode_rightlimit - self.cathode_leftlimit)) + min(self.shifted_cathode)

        secax = ax.secondary_xaxis('top', functions=(capacity2stoic,stoic2capacity))
        secax.set_xlabel('Stoichiometry')
        plt.show()
        print("Positive Electrode Maximum Stoichiometry:",capacity2stoic(min(self.cathode_three_electrode_data[0])))
        print("Positive Electrode Minimum Stoichiometry:",capacity2stoic(max(self.cathode_three_electrode_data[0])))
