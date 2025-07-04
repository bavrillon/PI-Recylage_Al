\* optimise_co2_with_scrap *\
Minimize
OBJ: calculed_composition_R1 + 6 calculed_composition_R10
 + 5 calculed_composition_R2 + 0.5 calculed_composition_R3
 + calculed_composition_R5 + 10 calculed_composition_R6
 + 3 calculed_composition_R7 + calculed_composition_R8
 + 7 calculed_composition_R9
Subject To
_C1: calculed_composition_R1 + calculed_composition_R10
 + calculed_composition_R2 + calculed_composition_R3 + calculed_composition_R4
 + calculed_composition_R5 + calculed_composition_R6 + calculed_composition_R7
 + calculed_composition_R8 + calculed_composition_R9 + calculed_composition_S0
 = 1
_C2: 0.99 calculed_composition_R1 + 0.0002 calculed_composition_R10
 + 0.02 calculed_composition_R2 + 0.01 calculed_composition_R6
 + 0.001 calculed_composition_R9 + 0.275 calculed_composition_S0 = 0.0025
_C3: 0.01 calculed_composition_R1 + 0.0002 calculed_composition_R10
 + 0.98 calculed_composition_R2 + 0.01 calculed_composition_R7
 + 0.002 calculed_composition_R9 + 0.425 calculed_composition_S0 = 0.004
_C4: calculed_composition_R3 + 0.075 calculed_composition_S0 = 0.001
_C5: 0.98 calculed_composition_R4 + 0.075 calculed_composition_S0 = 0.001
_C6: 0.99 calculed_composition_R5 + 0.075 calculed_composition_S0 = 0.024
_C7: 0.99 calculed_composition_R6 + 0.075 calculed_composition_S0 = 0.002
_C8: 0.98 calculed_composition_R7 + 0.075 calculed_composition_S0 = 0.001
_C9: 0.99 calculed_composition_R8 + 0.055 calculed_composition_S0 = 0.0015
Bounds
 calculed_composition_R1 <= 1
 calculed_composition_R10 <= 1
 calculed_composition_R2 <= 1
 calculed_composition_R3 <= 1
 calculed_composition_R4 <= 1
 calculed_composition_R5 <= 1
 calculed_composition_R6 <= 1
 calculed_composition_R7 <= 1
 calculed_composition_R8 <= 1
 calculed_composition_R9 <= 1
 calculed_composition_S0 <= 1
End
