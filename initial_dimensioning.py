from consts import *

import matplotlib.pyplot as plt
import numpy as np
from math import sqrt

def initial_dimensions_double_lug(Fx, Fy, Fz, Mx, My, Mz):
    Fx = 0
    
    return 0 # Just for now

# Determines acceleration in x, y and z.
def determine_acc():
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

    return (max(Ax), max(Ay), max(Az), IfS_Az, Omega_max)

def force_decomposition(Ax, Ay, Az, l_CoM, M_panel, IfS_Az, Omega_max):
    #Launch  
    Fx = M_panel * Ax
    Fy = M_panel * Ay
    Fz = M_panel * Az

    #Transformation of x-axis:
    Rxx = Fx / 2  #Reaction force at the lug against Ax in the x direction 
    Mxz = Fx * l_CoMRetracted #Total Moment applied by the force Fx
    Mxzr = Mxz / 2 #Reaction Moment In each Hinge of 2 lugs
    
    #Transformation of y-axis:
    Ryy = Fy / 2 #Reaction force at the lug against Ax in the y direction
    Myz = (b/2) * Fy
    
    #Transformations of z- axis 
    Rz = []
    Rzz_launch = Fz / 2
    Rz.append(Rzz_launch)
    Mzx = Fz * l_CoMRetracted #Total Moment applied by the force Fz
    R_Mzx_y = Mzx /b #The absolute value of the reaction couple needed to counter the moment Mzx
    
    #In Space
    #z-axis
    Fz_inflight = Mwet*IfS_Az
    Rzz_inflight = Fz_inflight / 2
    Mzx_inflight = Fz_inflight*l_CoM

    print("Fz_inflight=", Fz_inflight)
    print("Rzz_inflight=", Rzz_inflight)
    print("Mzx_inflight=", Mzx_inflight)

    Rz.append(Rzz_inflight)
    Rzz = max(Rz)

    F1 = R_Mzx_y /2 #Force per "leg"
    Fy = Ryy / 2 #Force per "leg"
    Fz = Rzz / 2 #Force per "leg"

    return (F1, Fy, Fz)

def Ftu(material_num):
    pass


def test_values(D, w, t, Ftu, sigma_y, F1, Fz):
    """Ftu is ultimate tensile strength. Use Fig 1.12 from appendix to determine Kt
    An additional fitting factor of 0.15 should be added"""
    W_D = w/D

    if W_D <= 5 and W_D>=1:
        Kt = -0.0815*(W_D) + 0.7517 # For 7 (Aluminium)
        At = w*(1e-3)*t*(1e-3) - D*(1e-3)*t*(1e-3)

        Pu =  Kt * Ftu * At #Equation 6

        Abr = D*(1e-3)*t*(1e-3) #?
        Kbru = 1.2 #e/D = 1.4 (so e is 1.4D of clearance from the end) 

        Pbru = Kbru * Ftu * Abr #Equation 7

        Ptu = Kt * Abr * Ftu # Equation 10
        #if min(Pu, Pbru)>0.01 and Ptu > 0.01:
        Ra = F1/(min(Pu, Pbru)) 
        Rtr = Fz / Ptu 

        n = Ra**1.6 + Rtr**1.6
        
        if n <=1 and n>0.1 :
            MS = (1/(n**0.625))-1 #Margin of safety
            if MS>0.15 and MS<0.16:
                sigma_allow = sigma_y/(1 + MS)
                return (True, sigma_allow, MS)
            
        
    return (False, None, None)
    
def lug_analysis(F1, Fy, Fz):
    lug_designs = []

    running = True
    done_once = False
    counter = 0
    # Material property
    #Al 356-T6 Mechanical Properties
    Ftu = 234e6 #Pa 
    sigma_y = 165e6 #Pa
    
    for D in np.arange(1, 100, 1):
        if running:
            for w in np.arange(D, 105, 1):
                if running:
                    for t in np.arange(0.1, 30, 0.1):
                        result, sigma_allow, MS = test_values(D, w, t, Ftu, sigma_y, F1, Fz)
                        if result:
                            if done_once is not True:
                                done_once = True
                            counter += 1
                            #print(counter, D, w, t)
                            lug_designs.append({"D": round(D, 2), "w": round(w, 2), "t": round(t, 2), "allow": round(sigma_allow/1e6, 3), "MS": round(MS, 2)})
                        #else:
                            #print(result)

                        #elif done_once:
                                #pass
                                #running = False
                                #break
    return lug_designs, counter

def fastener_backup_sizing(F_vect, h, t_1, W, D_1, sigma_fail_Bplate, sigma_fail_wall,  sigma_fail_fastener):
    # try 4, 6, 8, 10 fasteners
    # optimize for each, pick best.
    storage = [] # list containing lists with values
    for Nf in np.linspace(4, 10, 4): # iterating over number of fasteners, from 4 to 10, steps of 2. half of them on each side
        # as we're spacing our fasteners such that their 'cg' is in the centre of the back-up plate, their cg is at (0,y,0), where y does not matter
        # this means there is no moment My_cg or Mx_cg, making life easier.
        
        lst = [Nf] # list used to store info, we just punch this thing directly into another list, calling things will not be nice. Too bad!

        # calculating more useful force numbers
        F_IPx = F_vect[0] / Nf # in-plane force in X direction, might be zero
        F_IPz = F_vect[2] / Nf # in-plane force in Z direction
        F_IPT = sqrt(F_IPx ** 2 + F_IPz ** 2) # total in-plane force acting on each fastener


        # sizing for thicknesses and hole diameter. Sizing based on bearing failure.
        # adapted from sigma = F_ipt / (D_2 * t) where t is either t2 or t3. K is the product of D2 and t
        Kb = sigma_fail_Bplate / F_IPT # Kb is for backup plate
        Kw = sigma_fail_wall / F_IPT # Kw is for the s/c wall
        D2_max = W / (Nf + 1) # maximum fastener thickness, we do not want to exceed W to make our lifes easier.

        t_2 = Kb / D2_max # calculate thickness of back-up plate
        t_3 = Kw / D2_max # calcylate thickness of s/c wall 
        # !!!! we need to find the area or whatever of the s/c wall for proper o p t i m i z a t i o n !!!!
        lst.extend([D2_max, t_2, t_3])
        # by definition bearing check should be passed.
        
        # Pull through check
        



    return(D_2, T_2, T_3, Num_fast, Plate_z)