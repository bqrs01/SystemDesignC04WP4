import os

import matplotlib.pyplot as plt
import numpy as np
import csv

from consts import * # Get constants
from helpers import printResults, getHighestAllowResult, saveResultsToCSV # Get helper functions
import initial_dimensioning

### START ###

Ax, Ay, Az, IfS_Az, Omega_max = initial_dimensioning.determine_acc()

print(Ax, Ay, Az, IfS_Az, Omega_max)

F1, Fy, Fz = initial_dimensioning.force_decomposition(Ax, Ay, Az, l_CoM, M_panel, IfS_Az, Omega_max)

forces = [F1, Fy, Fz]

print(F1, Fy, Fz)

results, counter = initial_dimensioning.lug_analysis(F1, Fy, Fz)

saveResultsToCSV(results)

print(f"Got {counter} results.")

optimal_design = getHighestAllowResult(results)

print(f"Optimal design is: {optimal_design}")