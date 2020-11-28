from initial_dimensioning import lug_analysis
from helpers import findOptimalLugDesigns, newline
Kb_lst = [0.2, 0.4, 0.6, 0.85] #0.6, 0.7, 0.8, 1

F1=2214.3131999999996
Fy=485.595
Fz=1107.1565999999998

for Kbru in Kb_lst:
    print(f"Kbr = {Kbru}:")
    designs, counter = lug_analysis(F1, Fy, Fz, Kbru)
    optimalDesigns = (findOptimalLugDesigns(designs))
    for d in optimalDesigns:
        print(d)
    newline()