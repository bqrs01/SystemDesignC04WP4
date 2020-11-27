import os

import matplotlib.pyplot as plt
import numpy as np
import csv

from consts import * # Get constants
from helpers import printResults, readResultsFromCSV, doResultsExist, saveResultsToCSV, newline, findOptimalLugDesigns # Get helper functions
import initial_dimensioning

wantToRun = (input("Should I rerun the simulation (if not done before)? [y/N]: ").lower() == "y")

### START ###

print("~~~~~ JAX Initial Dimensioning Python Script ~~~~~")
newline()
print("1. Determining accelerations.")
newline()

Ax, Ay, Az, IfS_Az, Omega_max = initial_dimensioning.determine_acc()

print("Results:")

printResults(Ax=Ax, Ay=Ay, Az=Az, IfS_Az=IfS_Az, Omega_max=Omega_max)
newline()

print("2. Force decomposition.")
newline()

F1, Fy, Fz = initial_dimensioning.force_decomposition(Ax, Ay, Az, l_CoM, M_panel, IfS_Az, Omega_max)

newline()
print("Results:")

printResults(F1=F1, Fy=Fy, Fz=Fz)

forces = [F1, Fy, Fz]

newline()

wait=input("Press enter to continue.")

if doResultsExist and not wantToRun:
    results, counter = readResultsFromCSV()
else:
    results, counter = initial_dimensioning.lug_analysis(F1, Fy, Fz, Kbru=0.2)

saveResultsToCSV(results)

print(f"Got {counter} results.")

optimal_designs = findOptimalLugDesigns(results)

print(f"Optimal designs are:")

for design in optimal_designs:
    print(design)