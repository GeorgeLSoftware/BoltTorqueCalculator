"""Pure formulae required for calculations only.
Inputs are assumed positive; validation is done at the model level
"""

def calculate_preload(torque_nm: float, nut_factor: float, nominal_diameter_m: float) -> float:
    """Returns the bolt preload in Newtons
    from the tightening torque.
    
    F = T / (K*d)
    where T is torque in Nm, 
    K is unitless nut factor
    and d is nominal diameter in m
    """
    return torque_nm / (nut_factor * nominal_diameter_m)

def calculate_torque(nut_factor: float, nominal_diameter_m: float, preload_n: float) -> float:
    """Returns the bolt torque in Newton Metres
    from the preload.
    
    T = K*d*F
    Where K is unitless nut factor
    d is nominal diameter in m
    and F is preload in N
    """
    return nut_factor * nominal_diameter_m * preload_n

def calculate_tensile_stress(preload_n, stress_area_m2):
    """Returns the tensile stress in Pa
    from the preload.
    
    σ = F / As
    Where F is preload in N
    and As is the stress area in m2
    """
    return preload_n / stress_area_m2
