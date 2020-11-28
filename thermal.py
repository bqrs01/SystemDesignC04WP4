import numpy as np

def temp_differentials():
    dT = []
    #Assembly refence temperature
    T_reference = 288.15 #K

    #Temperatures of Spacecraft body
    T_min = 192.71 #K
    T_max = 236.55 #K
    T_sc = [T_min, T_max]

    for i in T_sc:
        d_t = i - T_reference
        dT.append(d_t)

    return dT

dT = temp_differentials()
# print(dT)

def forces_due_thermal(E_b, a_b, a_c, phi, d_2, dT):
    """E_b = fastener Young Modulus, a_b is from fastener and a_c from flange"""
    d_sha = d_2 * 0.99 #assuming that the diameter of the cross section of the fastener is 99% of the hole diameter
    Asm = (np.pi/4)*(d_sha**2)
    F_dT_max = (a_c - a_b) * max(dT) * E_b * Asm * (1 - phi) #N
    F_dT_min = (a_c - a_b) * min(dT) * E_b * Asm * (1 - phi) #N

    return (F_dT_min, F_dT_max) #in N

print(stresses_due_thermal(1, 3,1, 4, 1, dT))