import numpy as np


def Temp_Differentials(alpha, L):
    dT = []
    #Temperatures of Spacecraft body
    T_min = 192.71 #K
    T_max = 236.55 #K
    T_sc = [T_min, T_max]

    #Temperatures of Space around the SC
    T_min_spc = 3 #K
    T_max_spc = 393.15 #K
    T_space = [T_min_spc, T_max_spc]

    #Assembly refence temperature
    T_reference = 288.15 #K
    for i in T_space:
        d_t = i - T_reference
        dT.append(d_t)

    for j in T_sc:
        d_t = j - T_reference
        dT.append(d_t)

    for i in T_sc:
        d_t = i - T_reference
        dT.append(np.abs(d_t))

    return (min(dT), max(dT))

Temp_Differentials(1, 10)