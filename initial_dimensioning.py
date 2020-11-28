from consts import *

import matplotlib.pyplot as plt
import numpy as np
from math import sqrt, pi

def get_material_props(mat_code):
    # Get material properties using the provided material code.
    # Aluminium Alloy Casting 356-T6: Ultimate Tensile Strength = 234MPa, 
    # Yield Tensile Strength = 165MPa, 
    # Tensile Modulus or Youngs Modulus = 72.4GPa
    material_props = { # Pa for stresses; kg/m**3 for density
        "Al356-T6": {
            "ult_ten_str": 234e6,
            "yield_ten_str": 165e6,
            "young_mod": 72.4e9,
            "density": 2670 #kg/m3
        },
        "xyz": {
            "ult_ten_str": 469e6,
            "yield_ten_str": 324e6,
            "young_mod": 73.1e9,
            "density": 2780 #kg/m3 
        }
    }

    return material_props[mat_code]

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
    # Had to be rewritten with loads of coffee
    # forces and moments are now returned as they are applied to the moments, so divide over lugs accordingly!
    # The only forces we consider for sizing are those experienced during launch, because the acceleration are much higher than those experienced in flight,
    #   the change in geometry affects the loads experienced, but the accelerations are significantly smaller.
    # Forces will be as applied at the lug, so if you have two lugs you need to divide them first!
    # Only the largest forces are considered here, they were solved for by hand on paper. This means we're designing one hinge, to be used in all cases.M_panel
    # This also means that the hinge might be overdesigned for it's application.
    # note that variable 'b' is the vertical (z) spacing between the two lugs.

    # Forces and moments due to Ax during launch (disregarding space due to insignificant accelerations) 
    Fx = (l_CoMretr_z_lower/b) * M_panel * Ax # Fx in the worst case, it's not the same for all lugs, so we're using the worst case.
    Mz_due_to_x = Fx * y_CoMretr/2  # moment around Z as applied to hinge

    # Forces and moments due to Ay during launch
    Fy = Ay * M_panel * (l_CoMretr_z_lower + b) / b 

    # z Forces during launch
    Fz = Az * M_panel * (y_CoMretr / b)
    # F1, because legacy code (help!)
    F1 = 'crap'
    # F1 = R_Mzx_y / 2  # Force per lug
    # Fy = Ryy / 2  # Force per lug
    # Fz = Rzz / 2  # Force per lug

    return F1, Fy, Fz, Fx, Mz, Mx, My

def Ftu(material_num):
    pass


def test_values(D, w, t, Ftu, sigma_y, F1, Fz, Kbru):
    """Ftu is ultimate tensile strength. Use Fig 1.12 from appendix to determine Kt
    An additional fitting factor of 0.15 should be added"""
    W_D = w/D

    if W_D <= 5 and W_D>=1:
        Kt = -0.0815*(W_D) + 0.7517 # For 7 (Aluminium)
        At = w*(1e-3)*t*(1e-3) - D*(1e-3)*t*(1e-3)

        Pu =  Kt * Ftu * At #Equation 6

        Abr = D*(1e-3)*t*(1e-3) #?
       
        #Kbru = 1 #e/D = 0.6 (so e is 1.4D of clearance from the end) 

        Pbru = Kbru * Ftu * Abr #Equation 7

        Ptu = Kt * Abr * Ftu # Equation 10
        #if min(Pu, Pbru)>0.01 and Ptu > 0.01:
        Ra = F1/(min(Pu, Pbru)) 
        Rtr = Fz / Ptu 

        n = Ra**1.6 + Rtr**1.6
        
        if n <=1 and n>0.1 :
            MS = (1/(n**0.625))-1 #Margin of safety
            if MS>0.5 and MS<0.6:  # basically pick the margin of safety here, og was 0.15 to 0.16
                sigma_allow = sigma_y/(1 + MS)
                return (True, sigma_allow, MS, Pu, Pbru)
            
        
    return (False, None, None, None, None)
    
"""
Kb_lst = [0.5, 0.6, 0.7, 0.8, 0.9, 1]
"""

def lug_analysis(F1, Fy, Fz, Kbru):
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
                        result, sigma_allow, MS, Pu, Pbru = test_values(D, w, t, Ftu, sigma_y, F1, Fz, Kbru)
                        if result:
                            if done_once is not True:
                                done_once = True
                            counter += 1
                            #print(counter, D, w, t)
                            lug_designs.append({"D": round(D, 2), "w": round(w, 2), "t": round(t, 2), "allow": round(sigma_allow/1e6, 3), "MS": round(MS, 2), "Pu": Pu, "Pbru": Pbru})
                        #else:
                            #print(result)

                        #elif done_once:
                                #pass
                                #running = False
                                #break
    return lug_designs, counter

def lug_dimensions_at_root_stresses(optimal_design, Fx, Fy, Fz, sigma_yield, t):
    survive = False
    i_count = 0
    t_new = optimal_design["t"]
    t_1 = 0
    while not survive and i_count < 2000:
        i_count +=1
        # increase t by small value
        t_new += 0.1 #if t_new is in mm
        
        
        # optimal_design = {"D_1": 49.0, "w": 94.0, "t": 1.5, "allow": 109.999,"MS": 0.5}
        D = optimal_design["D"] #mm
        w = optimal_design["w"] #mm
        Mz_1 = Fx * (y_CoMretr / 2) / 2 # Mz applied to one leg. 2 lugs, so divided by 2, divided by 2 again to get moment at one lug
        # Assumed function of the length of the lug
        L_lug = D * (3/2) #L_lug = 1.5D
        # Second Moments of Inertia
        Ixx = (1/12) * t_new * w**3
        Izz = (1/12) * w * t_new**3
        # Sum the stresses from tension/compression in y durection plus the stress of the force couple to counter My due to Fx plus Mz due to Fx plus Mx due to Fz
        # Each stresses due to:
            # tension in y
        sigma_y = (Fy / 2) / (t_new * w)
            # bending stress due to Fx
        Fr = Fx/2
        Mz_2 = L_lug * Fr 
        sigma_Mz_2 = (Mz_2 * t_new/2) / Izz
            # bending due to Mz
        sigma_Mz_1 = (Mz_1 * t_new/2) / Izz
            #bending due to Fz
        Mx = L_lug * Fz/2
        sigma_Mx = (Mx * w/2) / Ixx 
            #bending due to Fy
        
            # Mz var. can be used directly, already split up above.
        #Total stress in y direction
        sigma_y_total = sigma_y + sigma_Mz_2 + sigma_Mz_1 + sigma_Mx
        
        #Required thickness to handle the total stress
            #Taking a margin of safety of 5%
        MS = sigma_y_total / sigma_yield
        if 1.1*MS_goal > MS > 0.9*MS_goal:
            survive = True
            t_1 = t_new
            print(t_1)
    
    if not survive:
        print("Did not find within 2000 iterations.") # Debug
        return (None)
        
    return(t_1)

def fastener_backup_sizing(F_vect, h, t_1, w, D_1, M_z, l_lug, sigma_fail_Bplate, sigma_fail_wall):
    # try 4, 6, 8, 10 fasteners
    # optimize for each, pick best.
    # all units are SI units, so meters, newtons, all that fuckery unless specified
    h /= 1000
    t_1 /= 1000
    w /= 1000
    D_1 /= 1000
    sigma_fail_Bplate *= (10 ** 6)  # converting to Pa
    sigma_fail_wall *= (10 ** 6)
    r_1 = D_1 / 2  # used later
    r_w = w / 2  # used later as well
    # converting some things to meters

    storage = []  # list containing lists with values (2D lists)
    for Nf in np.linspace(4, 10, 4).astype(int):  # iterating over number of fasteners, from 4 to 10, steps of 2. half of them on each side
        # as we're spacing our fasteners such that their 'cg' is in the centre of the back-up plate, their cg is at (0,y,0), where y does not matter
        # this means there is no moment My_cg or Mx_cg, making life easier.

        lst = [Nf]  # list used to store info, we just punch this thing directly into another list, calling things will not be nice. Too bad!

        # calculating more useful force numbers
        F_IPx = F_vect[0] / Nf  # in-plane force in X direction, might be zero
        F_IPz = F_vect[2] / Nf  # in-plane force in Z direction
        F_IPT = sqrt(F_IPx ** 2 + F_IPz ** 2)  # total in-plane force acting on each fastener

        # sizing plates and holes for bearing
        D_2 = w / (Nf + 3)  # maximum fastener thickness, we do not want to exceed w to make our lifes easier.
        # D_2 is the biggest possible value we can find, so it's also D_2_max, we just call it to keep our life easier

        t_2 = F_IPT / (sigma_fail_Bplate * D_2)  # calculate thickness of back-up plate
        t_3 = F_IPT / (sigma_fail_wall * D_2)  # for now, same thickness as bplate because it's the same material
        # !!!! we need to find the area or whatever of the s/c wall for proper o p t i m i z a t i o n !!!!
        # by definition bearing check should be passed, as that is what we're sizing for.
        ''' no safety factor taken into account '''
        lst.extend([D_2, t_2, t_3])  # storing plate thicknesses and hole diameter

        # Pull through check
        # we're only sizing for the worst case, meaning the case where the force and moment do NOT cancel out, but add together.
        # Basically, we're adding the magnitudes and sizing for that
        l_x = t_1 + (h / 2) + (1.5 * D_2)  # x distance between cg and fasteners. Since they're on one line, this is constant.
        # sum of all radii, from centre of fastener to fastener cg
        radii_squared = []  # list we're storing values in
        for j in range(int(Nf / 2)):  # calculating the Z distance between the fastener and the cg, and then itterating down. int part cuz it might cry
            Dz = ((Nf / 2) - 1 - (j * 2)) * D_2
            radii_squared.append(2 * (l_x ** 2 + Dz ** 2))  # finding the radius, from cg to fastener. Since it's symmetric we can double it to account for left/right

        Sr = sum(radii_squared)  # summing squared radii
        Fy_max = F_vect[1] / Nf + M_z * (sqrt(l_x ** 2 + ((Nf / 2 - 1) * D_2) ** 2) / Sr)  # Maximum force experienced in Y direction.
        print("Fy_max =", Fy_max)
        # Pull-through stress:
        # sigma_pull = Fy_max / (pi * (D_fo / 2) ** 2 - pi * ( D_fi / 2) ** 2)
        # F is the applied load on each fastener, D_fo and D_fi are the outer and inner diameterers of the fastener head
        # I do have to say that I have no clue why this line exists

        # yolo going with shear only (y = sqrt(3Tau^2))
        Tau_max = sqrt((sigma_fail_Bplate ** 2) / 3)  # sc wall made out of same stuff as bplate
        R_2 = D_2 / 2  # make radius out of hole diameter
        D_fo = 2 * sqrt(Fy_max / (pi * Tau_max) + R_2 ** 2)  # find outer diameter from maximum stress. We might want a safety factor, and we need to consider other forces.
        # for now it's good enough, I'll fuck with it later.D_2
        plate_x = 2 * l_x + 3 * D_2  # twice x distance from centre to centres of holes + twice distance from centres of holes to edge
        lst.extend([D_fo, plate_x])

        storage.append(lst)

        # store data DONE! I hope

    # compare data
    # list order: ( Nf, D_2, t_2, t_3, D_fo, plate_x)
    # so list   : i.(0,   1,   2,   3,    4,      5)
    v_list = []
    for i in storage:
        V = (pi * (r_w ** 2) + (l_lug - r_w) * w - (r_1 ** 2) * pi)* 2 * t_1 + (i[5] * w - i[0] * pi * (i[1] / 2) ** 2 ) * i[3] # lug volume approx
        v_list.append(V)
        # optimal number will be the one with the lowest volume, as they all should reach the requirements
        fig_opt = v_list.index(min(v_list))  # index of the lowest value volume

        # pulling values out of storage from optimal solution to return to main. That's all folks, thanks for reading!
        num_fast = storage[fig_opt][0]
        d_2 = storage[fig_opt][1]
        t_2 = storage[fig_opt][2]
        t_3 = storage[fig_opt][3]
        d_fo = storage[fig_opt][4]
        plate_x = storage[fig_opt][5]
    # print(storage) # used for debugging, not formatted for human consumption

    return (d_2, t_2, t_3, num_fast, plate_x, d_fo)