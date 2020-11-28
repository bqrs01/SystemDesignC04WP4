import os

import matplotlib.pyplot as plt
import numpy as np
import csv

from consts import * # Get constants
from helpers import printResults, getHighestAllowResult, readResultsFromCSV, doResultsExist, saveResultsToCSV # Get helper functions
import initial_dimensioning

wantToRun = False
#from thermal import stresses_due_thermal, temp_differentials

### START ###

Ax, Ay, Az, IfS_Az, Omega_max = initial_dimensioning.determine_acc()

print(Ax, Ay, Az, IfS_Az, Omega_max)

F1, Fy, Fz = initial_dimensioning.force_decomposition(Ax, Ay, Az, l_CoM, M_panel, IfS_Az, Omega_max)

forces = [F1, Fy, Fz]

print(F1, Fy, Fz)

if doResultsExist and not wantToRun:
    results, counter = readResultsFromCSV()
else:
    results, counter = initial_dimensioning.lug_analysis(F1, Fy, Fz)

saveResultsToCSV(results)

print(f"Got {counter} results.")

optimal_design = getHighestAllowResult(results)

print(f"Optimal design is: {optimal_design}")

d_2, t_2, t_3, num_fast, plate_x, d_fo = initial_dimensioning.fastener_backup_sizing(forces, b, optimal_design["t"], optimal_design["w"], optimal_design["D"], 0, l_lug, optimal_design["allow"], optimal_design["allow"])

printResults(d_2=d_2, t_2=t_2, t_3=t_3, num_fast=num_fast, plate_x=plate_x, d_fo=d_fo)