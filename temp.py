import os

import matplotlib.pyplot as plt
import numpy as np

from consts import *
from helpers import printResults
from initial_dimensioning import *

#os.environ['MPLCONFIGDIR'] = "/tmp/matplotlib/"

"""### CONSTANTS
g = 9.81  # m/s^2
Mdry = 843  # kg
Mwet = 1971  # kg
M_panel = 198/2  # kg
# distances are in y direction unless stated otherwise, rest is not considered for this. the lugs are positioned such that there is only an arm in y direction.
l_CoMRetracted = 1 #m #Distance between CoM Retracted Solar Array
l_CoM = 7.815  # m # distance between CoM of solar array and lugs
l_CoMsat = 1.1 # m # distance between CoM of s/c and lugs
l_arm = 2.2  # m   # length of arm connecting lugs to solar array
b = 1 # m     # distance between lugs in z 

# Static Launch

# z direction (roll axis)
LaS_Azmax = 2.5*g  # m/s^2
LaS_Azmin = -4.56*g  # m/s^2
Az_s = [LaS_Azmax, LaS_Azmin]

# x direction (yaw axis)
LaS_Axmax = 2*g  # m/s^2
LaS_Axmin = -2*g  # m/s^2
Ax_s = [LaS_Axmax, LaS_Axmin]

# y direction (pitch axis)
LaS_Aymax = 2*g  # m/s^2
LaS_Aymin = -2*g  # m/s^2
Ay_s = [LaS_Aymax, LaS_Aymin]

# Dynamic Launch
LaD_Azmax = 1.45*g  # m/s^2
LaD_Azmin = -1.45*g  # m/s^2

# in-flight at burnout
IfS_Az = 0.753  # m/s^2

# in-flight peak rotational rate:
Omega_max = 0.524  # rad/s


# Launch loads
Az_d = [LaD_Azmax, LaD_Azmin]

Az = []
for i in Az_s:
    Az.append(np.abs(i))
for i in Az_d:
    Az.append(np.abs(i))

Ay = []
for i in Ay_s:
    Ay.append(np.abs(i))

Ax = []
for i in Ax_s:
    Ax.append(np.abs(i))
"""


# Forces F = ma 
Fz_L = M_panel * max(Az)
Fx_L = M_panel * max(Ax)
Fy_L = M_panel * max(Ay)

Fz_L = Fz_L/2
Fx_L = Fx_L/2
Fy_L = Fy_L/2

# Finding the moment to be counteracted
Mx = -1 * Fz_L * 7.815




# in-flight loads
# identify x, y, z forces
# only accelerations in z, therefore ignoring x and y acceleration, there is a force in y due to rotation.
Fz_IF = M_panel * IfS_Az
Fy_IF = M_panel * Omega_max ** 2 * (l_CoM + l_CoMsat) # distance between CoM of s/c and CoM of solar array is used
# identify x, y, z moments
Mx_IF = Fz_IF * l_CoM  # do not use for dimensioning

# forces need to be translated to forces applied to the lugs themselves:
AFz_IF = Fz_IF / 2 # both divided by two because there are two lugs
AFy_IF = (Fy_IF / 2) + (Mx_IF / b) # only considering adding them together, because that's a heavier load case.

# now we take the forces, pick the biggest magnitude in every direction
#initial_double_lug_dimensions(max(Fx))

# This function is imported from the file "initial_dimensioning.py"
# The function accepts parameter (Fx, Fy, Fz, Mx, My, Mz) 
result = initial_dimensions_double_lug(Fx_L, max(Fy_L, AFy_IF), max(Fz_L, AFz_IF), 0, 0, 0)


# use loads to design for each individual failure
    # basically, find one equation or whatever for each load case.
    # In theory, the code that finds the dimensions needs to be written once, and punched into a function
        # this function should just take the forces and moments, and crap out dimensions
            # we need an efficient way to store these dimensions, as they will be compared.
            # if multiple loads in ONE load case define a dimension, pick whichever is greater.
