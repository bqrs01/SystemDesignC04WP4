import matplotlib.pyplot as plt
import numpy as np
from math import pi, sqrt
import csv

from consts import * # Get constants
from helpers import printResults, readResultsFromCSV, doResultsExist, saveResultsToCSV, newline, findOptimalLugDesigns, validateChoiceInput # Get helper functions
import initial_dimensioning
import thermal

wantToRun = True # Used for lug analysis calculation
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

forces = [Fx, Fy, Fz] # [Fx, Fy, Fz] for fastener_backup_sizing (total force)
# Forces in this list should be for one hinge, not one lug!!!

newline()

dim_storage = [] # dimension list to compare options
MS_storage = [] # margin of safety list to compare options

# Get material properties
materials = ["Al2024-T4", "Al2014-T6"]
for material in materials:
    print("Trying material", material)

    newline()
    
    props = initial_dimensioning.get_material_props(material)
    sigma_y = props["yield_ten_str"]
    sigma_bear = props["bearing_strength_allow"]
    
    # Opposite material
    ind_cur_mat = materials.index(material) # Index of current material
    if ind_cur_mat == 0:
        opp_props = initial_dimensioning.get_material_props(materials[1])
        a_b = opp_props["expansion_coef"]
        E_b = opp_props["young_mod"]
    else:
        opp_props = initial_dimensioning.get_material_props(materials[0])
        a_b = opp_props["expansion_coef"]
        E_b = opp_props["young_mod"]
    
    # For current material
    a_c = props["expansion_coef"] # expansion coef. for plates
    E_a = props["young_mod"]
    
    
    if doResultsExist and not wantToRun:
        results, counter = readResultsFromCSV()
    else:
        results, counter = initial_dimensioning.lug_analysis(Fy/2, Fz/2, 0.2, sigma_y)

    #saveResultsToCSV(results)

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
    #design_choice_num = 1
    # For quick automation without the need of interaction.

    optimal_design = optimal_designs[design_choice_num]

    print(f"Optimal design is: {optimal_design}")

    newline()
    # h = 2 * optimal_design["t"] # approx. distance between lugs in meters, estimated by summing the widths of the lugs.
    # d_2, t_2, t_3, num_fast, plate_x, d_fo = initial_dimensioning.fastener_backup_sizing(forces, h, optimal_design["t"], optimal_design["w"], optimal_design["D"], Mz, l_lug, sigma_y, sigma_y, sigma_bear, sigma_bear)

    # printResults(d_2=d_2, t_2=t_2, t_3=t_3, num_fast=num_fast, plate_x=plate_x, d_fo=d_fo)

    #optimal_design["t"], junk = initial_dimensioning.lug_dimensions_at_root_stresses(optimal_design, Fx, Fy, Fz, optimal_design["allow"]*1e6,Mz) 
    new_t, MS = (initial_dimensioning.lug_dimensions_at_root_stresses(optimal_design, Fx, Fy, Fz, sigma_y, Mz) )
    optimal_design["t"] = new_t
    h = 2 * optimal_design["t"] # need new h as we have a new t_1
    newline()

    d_2, t_2, t_3, num_fast, plate_x, d_fo = initial_dimensioning.fastener_backup_sizing(forces, b, optimal_design["t"], optimal_design["w"], optimal_design["D"], Mz, l_lug, sigma_y, sigma_y, sigma_bear, sigma_bear)

    newline()
    
    print(optimal_design)
    printResults(d_2=d_2, t_2=t_2, t_3=t_3, num_fast=num_fast, plate_x=plate_x, d_fo=d_fo)
    
    

    # final initial dimensions (funny how this took 90% of our time but ok)
    d_1 = optimal_design["D"]
    t_1 = optimal_design["t"]
    w = optimal_design["w"]   
    l_lug = d_1 * 3/2
    # d_2, t_2, t_3, D_fo already known and in SI base units

    
    done = False
    i_count = 0
    while not done and i_count < 4269:
        i_count += 1
        change = False
        Asm = (np.pi/4)*((d_2*0.99)**2) # cross section of fasteners, used later.
        phi = initial_dimensioning.phi(E_b, d_fo, E_a, t_2, t_3, d_2)
        # calculate ALL MS values, store them + current dimensions
        # compare MS to reference, so how close to optimal, or close to failure, we want to run
        # adjust values accordingly
        # compare MS and updatee SET CHANGE TO TRUE ON UPDATE PLOX, THX

        # MS = sigma_allow / sigma_applied - 1
        # MS calculators, basically loading the hinges with, you know, loads

        F_pullthrough, plate_x = initial_dimensioning.pullthrough_force_plate_width_func(forces, t_1, h, d_2, num_fast, Mz) # F_pullthrough is the same in both cases

        # MS Lug and lug root
        junk, MS_lug = initial_dimensioning.lug_dimensions_at_root_stresses(optimal_design, Fx, Fy, Fz, sigma_y, Mz) 

        dT = thermal.temp_differentials()
        
        #MS for back-up plate
        MS_Bp_bearing = sigma_bear / (sqrt((forces[0] / num_fast) ** 2 + (forces[2] / num_fast) ** 2) / (d_2 * t_2)) - 1
        MS_Bp_bearing_thermal = sigma_bear / ( ((a_c - a_b) * min(dT) * E_b * Asm * (1 - phi)) / (d_2 * t_2)) - 1
        MS_Bp_pullthrough = sigma_y / (sqrt(3) * ( F_pullthrough / (pi * ((d_fo/2) ** 2 - (d_2 / 2) ** 2)))) - 1
        
        #MS for sc wall
        MS_VW_bearing = sigma_bear / ( sqrt((forces[0] / num_fast) ** 2 + (forces[2] / num_fast) ** 2) / (d_2 * t_3)) - 1
        MS_VW_bearing_thermal = sigma_bear / ( ((a_c - a_b) * min(dT) * E_b * Asm * (1 - phi)) / (d_2 * t_3)) - 1
        MS_VW_pullthrough = sigma_y / (sqrt(3) * ( F_pullthrough / (pi * ((d_fo/2) ** 2 - (d_2 / 2) ** 2)))) - 1
        printResults(sigma_y=sigma_y, Fp = F_pullthrough)
        # compare MS Lug and update
        # if MS_lug < MS_goal: # increase t_1 if too small
        #     t_1 *= 1.001
        #     h = 2 * t_1 # update h
        #     change = True
        # elif MS_lug > 1.1 * MS_goal: # decrease t_1 if too big
        #     t_1 *= 0.999 
        #     change = True


        # # compare MS Back-up wall bearing and update
        # if MS_Bp_bearing < MS_goal: # increase t_2 if too small
        #     t_2 *= 1.001
        #     change = True
        # elif MS_Bp_bearing > 1.1 * MS_goal: # decrease t_2 if too big
        #     t_2 *= 0.999 
        #     change = True

        # # compare MS Back-up wall bearing THERMAL and update
        # if MS_Bp_bearing_thermal < MS_goal: # increase t_2 if too small
        #     t_2 *= 1.001
        #     change = True
        # elif MS_Bp_bearing_thermal > 1.1 * MS_goal: # decrease t_2 if too big
        #     t_2 *= 0.999 
        #     change = True
        # MS BW pullthrough

        # compare MS SC wall bearing and update

        # compare MS SC wall bearing THERMAL and update

        # MS SCW pullthrough

        if not change:
            done = True
            dim_storage.append([t_1, d_1, w, h, t_2, d_2, t_3, plate_x, d_fo, l_lug, num_fast])
            MS_storage.append([MS_lug, MS_Bp_bearing, MS_Bp_bearing_thermal, MS_Bp_pullthrough, MS_VW_bearing, MS_VW_bearing_thermal, MS_VW_pullthrough, material])

    if len(dim_storage) == 0 or len(MS_storage) == 0:
        # If we get nothing after about 4000 iterations in the loop
        print("Somethings going wrong..")
        print(t_1, d_1, w, h, t_2, d_2, t_3, plate_x, d_fo, l_lug, num_fast)
            
            


V_list = []
for s in dim_storage: # s for solution, suggestions are slow so 's' is quicker to type out
    V = (s[7]*s[2] - s[10] * pi * (s[5]/2)**2 )*s[4] + 2 * s[0] * ((s[9]-s[2]/2)*s[2] + pi * ( ((s[2]/2)**2 / 2 ) - (s[1]/2)**2) ) # volume
    V_list.append(V)

dim_print = ['t_1', 'd_1', 'w', 'h', 't_2', 'd_2', 't_3', 'plate_x', 'd_fo', 'l_lug', 'num_fast'] # list for printing
MS_print = ['MS_lug_root', 'MS_Bp_bearing', 'MS_Bp_bearing_thermal', 'MS_Bp_pullthrough', 'MS_VW_bearing','MS_VW_bearing_thermal','MS_VW_pullthrough', 'material'] # also used for printing
ind = V_list.index(min(V_list)) # index of best solution
# prints out list of dimensions:
for i in range(len(dim_print)): 
    print(dim_print[i],'=', dim_storage[ind][i])

# prints out list of MS's:
for i in range(len(MS_print)):
    print(MS_print[i],'=', MS_storage[ind][i])


# comparing things after iterating
# nested list:
# keep a and ind for reference, makes it easier to find indices
#   a = [t_1, d_1, w, h, t_2, d_2, t_3, plate_x, d_fo, l_lug,  nf]
# ind = [0,    1,  2, 3,   4,   5,   6,     7,      8 ,   9,   10]
# MS_lst = [MS_lug, MS_lug, MS_Bp_bearing, MS_Bp_bearing_thermal, MS_Bp_pullthrough, MS_VW_bearing, MS_VW_bearing_thermal, MS_VW_pullthrough, material]
# MS_ind = [ 0,          1,           2,                 3,                     4,         5,                         6,           7,               8]