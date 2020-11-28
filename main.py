import matplotlib.pyplot as plt
import numpy as np
import csv

from consts import * # Get constants
from helpers import printResults, readResultsFromCSV, doResultsExist, saveResultsToCSV, newline, findOptimalLugDesigns, validateChoiceInput # Get helper functions
import initial_dimensioning
#import thermal

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

Fx, Fy, Fz, Mz = initial_dimensioning.force_decomposition(Ax, Ay, Az, l_CoM, M_panel, IfS_Az, Omega_max)
# forces and moments are now returned as they are applied to the moments, so divide over lugs accordingly!

# this spaghetti is making me hungry
# help
# ! Go make some spaghetti then!
newline()
print("Results:")

printResults(Fx=Fx, Fy=Fy, Fz=Fz, Mz=Mz)

# Get material properties
initial_dimensioning.get_material_props

forces = [Fx, Fy, Fz] # [Fx, Fy, Fz, F1] for fastener_backup_sizing (total force)
# Forces in this list should be for one hinge, not one lug!!!
newline()

# wait=input("Press enter to continue.")

if doResultsExist and not wantToRun:
    results, counter = readResultsFromCSV()
else:
    results, counter = initial_dimensioning.lug_analysis(Fy/2, Fz/2, Kbru=0.2)

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
    Pu = "N/A"
    Pbru = "N/A"
    if wantToRun:
        Pu = design["Pu"]
        Pbru = design["Pbru"]
    print(f"{counter}: D={D} w={w} t={t} Pu={Pu} Pbru={Pbru}")

design_choice_num = int(input("Choose a design (number): "))-1

optimal_design = optimal_designs[design_choice_num]

print(f"Optimal design is: {optimal_design}")



d_2, t_2, t_3, num_fast, plate_x, d_fo = initial_dimensioning.fastener_backup_sizing(forces, b, optimal_design["t"], optimal_design["w"], optimal_design["D"], Mz, l_lug, optimal_design["allow"], optimal_design["allow"])

printResults(d_2=d_2, t_2=t_2, t_3=t_3, num_fast=num_fast, plate_x=plate_x, d_fo=d_fo)

newline()

print("Now we do iterations :)")

newline()

optimal_design["t"] = 1e3 * initial_dimensioning.lug_dimensions_at_root_stresses(optimal_design, Fx, Fy, Fz, optimal_design["allow"]*1e6,Mz) 

d_2, t_2, t_3, num_fast, plate_x, d_fo = initial_dimensioning.fastener_backup_sizing(forces, b, optimal_design["t"], optimal_design["w"], optimal_design["D"], Mz, l_lug, optimal_design["allow"], optimal_design["allow"])

printResults(d_2=d_2, t_2=t_2, t_3=t_3, num_fast=num_fast, plate_x=plate_x, d_fo=d_fo)