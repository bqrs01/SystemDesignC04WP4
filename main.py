import matplotlib.pyplot as plt
import numpy as np
import csv

from consts import * # Get constants
from helpers import printResults, readResultsFromCSV, doResultsExist, saveResultsToCSV, newline, findOptimalLugDesigns, validateChoiceInput # Get helper functions
import initial_dimensioning

wantToRun = False
#from thermal import stresses_due_thermal, temp_differentials

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

forces = [0, (2*Fy + F1), Fz] # [Fx, Fy, Fz] for fastener_backup_sizing

newline()

# wait=input("Press enter to continue.")

if doResultsExist and not wantToRun:
    results, counter = readResultsFromCSV()
else:
    results, counter = initial_dimensioning.lug_analysis(F1, Fy, Fz, Kbru=0.2)

saveResultsToCSV(results)

print(f"Got {counter} results.")

optimal_designs = findOptimalLugDesigns(results)

newline()

print(f"Optimal designs are:")

counter = 0
for design in optimal_designs:
    counter += 1
    D = design["D"]
    w = design["w"]
    t = design["t"]
    print(f"{counter}: D={D} w={w} t={t}")

design_choice_num = int(input("Choose a design (number): "))-1

optimal_design = optimal_designs[design_choice_num]

print(f"Optimal design is: {optimal_design}")

d_2, t_2, t_3, num_fast, plate_x, d_fo = initial_dimensioning.fastener_backup_sizing(forces, b, optimal_design["t"], optimal_design["w"], optimal_design["D"], 0, l_lug, optimal_design["allow"], optimal_design["allow"])

printResults(d_2=d_2, t_2=t_2, t_3=t_3, num_fast=num_fast, plate_x=plate_x, d_fo=d_fo)
