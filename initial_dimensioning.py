from consts import *

import matplotlib.pyplot as plt
import numpy as np
from math import sqrt, pi
from helpers import printResults
# so this moment 
def get_material_props(mat_code):
    # Get material properties using the provided material code.
    # Aluminium Alloy Casting 356-T6: Ultimate Tensile Strength = 234MPa, 
    # Yield Tensile Strength = 165MPa, 
    # Tensile Modulus or Youngs Modulus = 72.4GPa
    material_props = { # Pa for stresses; kg/m**3 for density
        "Al356-T6": { # Curve 7 in fig D1.12
            "ult_ten_str": 234e6, #Pa,
            "yield_ten_str": 165e6, #Pa,
            "young_mod": 72.4e9, #Pa,
            "bearing_strength_allow": None, #cant find,
            "density": 2670 #kg/m3
        },
        "Al2024-T4": { # Curve 3 in fig D1.12
            "ult_ten_str": 469e6, #Pa,
            "yield_ten_str": 324e6, #Pa,
            "young_mod": 73.1e9, #Pa,
            "bearing_strength_allow": 248e6, #Pa,
            "density": 2780, #kg/m3
            "expansion_coef": 21.1e-6 # m/m * K             
        },
        "Al2014-T6": { # Curve 5 in fig D1.12
            "ult_ten_str": 483e6, #Pa,
            "yield_ten_str": 414e6, #Pa,
            "young_mod": 73.1e9, #Pa,
            "bearing_strength_allow": 572e6, #Pa,
            "density": 2800, #kg/m3
            "expansion_coef": 20.8e-6 #m/m * K
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
    # We also assumed no direction for forces, so we simply add the magnitudes. This will lead to an overdesigned hinge.
        # slightly heavier solar array mounts is probably worth it considering the mission
    # note that variable 'b' is the vertical (z) spacing between the two lugs.*

    # Forces and moments due to Ax during launch (disregarding space due to insignificant accelerations) 
    Fx = (l_CoMretr_z_lower/b) * M_panel * Ax # Fx in the worst case, it's not the same for all lugs, so we're using the worst case.
    Mz_due_to_Ax = Fx * l_CoMretr_y/2  # moment around Z as applied to hinge

    # Forces and moments due to Ay during launch
    Fy = Ay * M_panel * (l_CoMretr_z_lower + b) / b # As the sideways acceleration varies between -2 and 2 g's, no direction is assigned
    
    # z Forces during launch
    Fz = Az * M_panel / 2 # downwards, against thrust vector. Equal between upper and lower lug
    Fy_due_to_Az = l_CoMretr_y * Az * M_panel / b # both compressive and tensile, upper lug experiences tension, lower a tensile load
    print(Fy_due_to_Az)
    print(Fy)
    #legacy stuff
    # F1 = R_Mzx_y / 2  # Force per lug 
    # Fz = Rzz / 2  # Force per lug

    # summing forces again, because wacky moment arms
    # Fx doesn't change
    Fy = Fy + Fy_due_to_Az
    # Fz does not change either
    Mz = Mz_due_to_Ax # no other Mz thingies, should've done this immediately ))))))))))))
    return Fx, Fy, Fz, Mz

# def Ftu(material_num): #We won't use this I think bc we already have a dict with material props in the beggining 
#     pass


def test_values(D, w, t, Ftu, sigma_y, Fy, Fz, Kbru):
    """Ftu is ultimate tensile strength. Use Fig 1.12 from appendix to determine Kt
    An additional fitting factor of 0.15 should be added"""
    W_D = w/D

    if W_D <= 5 and W_D>=1:
        Kt = -0.0815*(W_D) + 0.7517 # For 7 (Aluminium)
        # At = w*(1e-3)*t*(1e-3) - D*(1e-3)*t*(1e-3)
        At = w*t - D*t

        Pu =  Kt * Ftu * At #Equation 6

        # Abr = D*(1e-3)*t*(1e-3) #?
        Abr = D*t #?
       
        #Kbru = 1 #e/D = 0.6 (so e is 1.4D of clearance from the end) 

        Pbru = Kbru * Ftu * Abr #Equation 7

        Ptu = Kt * Abr * Ftu # Equation 10
        #if min(Pu, Pbru)>0.01 and Ptu > 0.01:
        Ra = Fy/(min(Pu, Pbru)) # Fy
        Rtr = Fz / Ptu          # Fz

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

def lug_analysis(Fy, Fz, Kbru, sigma_y):
    lug_designs = []

    running = True
    done_once = False
    counter = 0
    # Material property
    #Al 356-T6 Mechanical Properties
    Ftu = 234e6 #Pa 
    # sigma_y = 165e6 #Pa
    
    for D in np.arange(1*1e-3, 100*1e-3, 1e-3):
        if running:
            for w in np.arange(D, 105*1e-3, 1e-3):
                if running:
                    for t in np.arange(0.1e-3, 30e-3, 0.1e-3):
                        result, sigma_allow, MS, Pu, Pbru = test_values(D, w, t, Ftu, sigma_y, Fy, Fz, Kbru)
                        if result:
                            if done_once is not True:
                                done_once = True
                            counter += 1
                            #print(counter, D, w, t)
                            lug_designs.append({"D": round(D, 5), "w": round(w, 5), "t": round(t, 5), "allow": round(sigma_allow, 6), "MS": round(MS, 5), "Pu": Pu, "Pbru": Pbru})
                        #else:
                            #print(result)

                        #elif done_once:
                                #pass
                                #running = False
                                #break
    return lug_designs, counter

def lug_dimensions_at_root_stresses(optimal_design, Fx, Fy, Fz, sigma_yield, Mz):
    survive = False
    i_count = 0
    # optimal_design = OUT OF DATE{"D_1": 49.0, "w": 94.0, "t": 1.5, "allow": 109.999,"MS": 0.5}
    t_new = optimal_design["t"]  #m 
    D = optimal_design["D"]  #m
    w = optimal_design["w"]  #m
    t_1 = 0
    MS_goal = 0.05
    while not survive and i_count < 2000:
        i_count +=1
        # increase t by small value
        t_new += 0.0001 #if t_new is in m

        Mz_1 = Mz / 2 # Mz applied to one leg. 2 lugs, divided by 2 again to get moment at one lug
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
        
        # Mz var. can be used directly, already split up above.
        #Total stress in y direction
        sigma_y_total = sigma_y + sigma_Mz_2 + sigma_Mz_1 + sigma_Mx
        
        #Required thickness to handle the total stress
            #Taking a margin of safety of 5%
        
        MS_lug_root = (sigma_yield / sigma_y_total) - 1
        if MS_lug_root > MS_goal:
            survive = True
            t_1 = t_new
            # printResults(t_1=t_1, MS_lug_root=MS_lug_root, sugma=sigma_y_total, Ixx=Ixx, Izz=Izz)
    
    if not survive:
        print("Did not find within 2000 iterations.") # Debug
        return (None)
        
    return(t_1, MS_lug_root)

def fastener_backup_sizing(F_vect, h, t_1, w, D_1, M_z, l_lug, sigma_fail_Bplate, sigma_fail_wall, sigma_bearing_bp, sigma_bearing_wall):
    # try 4, 6, 8, 10 fasteners
    # optimize for each, pick best.
    # all units are SI units, so meters, newtons, all that fuckery unless specified
    # checking if input is in MPa or not :/
    r_1 = D_1 / 2  # used later
    r_w = w / 2  # used later as well
    # while this code supports different materials for the back-up plate and the SC wall, we don't really do that. We're not changing it either.
    
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
        D_2 = w / (Nf + 2)  # maximum fastener diameter, we do not want to exceed w to make our lifes easier.
        # D_2 is the biggest possible value we can find, so it's also D_2_max, we just call it to keep our life easier

        # sizing using bearing
        t_2 = F_IPT / (sigma_bearing_bp * D_2)  # calculate thickness of back-up plate
        t_3 = F_IPT / (sigma_bearing_wall * D_2)  # for now, same thickness as bplate because it's the same material
        # leads to very thing plates, doesn't make sense with applied loads :))))
        # shear load 
        # sizing using trial-and-error and von mises stress. Sizing t_2 first.
        # only considering Fy, but halved because two lugs
        t_2 = max(t_2, sqrt(12 * F_vect[1] * sqrt(3 / (sigma_fail_Bplate ** 2))))
        t_3 = max(t_3, sqrt(12 * F_vect[1] * sqrt(3 / (sigma_fail_wall ** 2))))

            
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
        Fy_max = F_vect[1] / Nf + M_z * (sqrt(l_x ** 2 + ((Nf / 2 - 1) * D_2) ** 2) / Sr)  # Maximum force experienced in Y direction. Only sizing for this, conservative assumption.
        #print("Fy_max =", Fy_max)

        # yolo going with shear only (y = sqrt(3Tau^2))
        Tau_max = sqrt((sigma_fail_Bplate ** 2) / 3)  # sc wall made out of same stuff as bplate, so only sizing once.
        R_2 = D_2 / 2  # make radius out of hole diameter
        D_fo = 2 * sqrt((Fy_max / (pi * Tau_max)) + R_2 ** 2)  # find outer diameter from maximum stress. We might want a safety factor, and we need to consider other forces.

        plate_x = 2 * l_x + 3 * D_2  # twice x distance from centre to centres of holes + twice distance from centres of holes to edge
        lst.extend([D_fo, plate_x, Fy_max, F_IPT])

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
    Fy_max = storage[fig_opt][6]
    F_IPT = storage[fig_opt][7]
    # print(storage) # used for debugging, not formatted for human consumption
    
    #size fastener. somehow.
    # assuming constant fastener diameter of 99% of hole diameter.
    # d_f_shear = np.sqrt((8*F_applied)/(3*np.pi*Tau_max))
    # d_f_tension = F_applied / (pi * (d_2/2)**2)
    # d_fast = max(d_f_shear, d_f_tension)
    # E_fast = #we need to find this
    # compliance_fast = ((t_2 + t_3) + (0.8 * d_fast))/(E_fast * pi * (d_fast/2) **2)

    return (d_2, t_2, t_3, num_fast, plate_x, d_fo)

def phi(E_b, D_fo, E_a, t_2, t_3, d_2):
    # Fastener: E_b, alpha_b, D_fo, D_fi
    # Backplate: E_a
    # Assuming a constant cross section through the fastener with a diameter of 99% of the hole
    d_sha = 0.99*d_2
    D_fi = d_sha
    d_a = 4*t_3 / (E_a * np.pi * (D_fo ** 2 - D_fi ** 2))
    d_b = 1 / E_b * (t_2+t_3) / ((d_sha/2)**2 * np.pi)
    phi = d_a / (d_a + d_b)
    D_fast = D_fi
    return (phi)

def pullthrough_force_plate_width_func(F_vect, t_1, h, D_2, Nf, M_z):
    # this code was ripped from the backup plate sizing function, specifically, line 298 from this file
    # I'm not replacing the code in that function with this function, as it makes it less readable.
    # F's in chat for readability anyways, because this is some spaghetti if I've ever seen it )))))))))
    l_x = t_1 + (h / 2) + (1.5 * D_2)  # x distance between cg and fasteners. Since they're on one line, this is constant.
    # sum of all radii, from centre of fastener to fastener cg
    radii_squared = []  # list we're storing values in
    for j in range(int(Nf / 2)):  # calculating the Z distance between the fastener and the cg, and then itterating down. int part cuz it might cry
        Dz = ((Nf / 2) - 1 - (j * 2)) * D_2
        radii_squared.append(2 * (l_x ** 2 + Dz ** 2))  # finding the radius, from cg to fastener. Since it's symmetric we can double it to account for left/right

    Sr = sum(radii_squared)  # summing squared radii
    Fy_max = (F_vect[1] / Nf) + (M_z * (sqrt(l_x ** 2 + ((Nf / 2 - 1) * D_2) ** 2) / Sr))  # Maximum force experienced in Y direction. Only sizing for this, conservative assumption.
    plate_x = 2 * l_x + 3 * D_2 # recalculating plate width as well, because we need that eventually.

    return(Fy_max, plate_x)