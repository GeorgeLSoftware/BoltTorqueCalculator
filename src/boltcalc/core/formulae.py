"""Pure formulae required for calculations only.
Inputs are assumed positive; validation is done at the model level
"""

import math

# Thread flank angle is always 60 deg for ISO threads
THREAD_FLANK_ANGLE_DEG = 60


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


def calculate_tensile_stress(preload_n: float, stress_area_m2: float) -> float:
    """Returns the tensile stress in Pa
    from the preload.
    
    σ = F / As
    Where F is preload in N
    and As is the stress area in m2
    """
    return preload_n / stress_area_m2


def calculate_custom_k(pitch_m: float, thread_friction: float,
                       pitch_diameter_m: float, bearing_friction: float,
                       bearing_diameter_m: float, nominal_diameter_m: float) -> float:
    """Returns the unitless K (nut) factor from
    the thread pitch, thread friction, pitch diameter, flank angle,
    bearing friction, bearing diameter and nominal diameter

    K = [ P/(2π) + μ_th*d₂/(2*cos(α/2)) + μ_b*D_b/2 ] / d
    Where P is thread pitch in m, μ_th is thread friction,
    d2 is pitch diameter in m, α is thread flank angle in deg,
    μ_b is bearing friction, D_b is bearing diameter in m
    and d is nominal diameter in m.

    Calculation split into three terms for easier reading.
    """
    pitch_term = pitch_m / (2 * math.pi)
    
    thread_friction_term = (
        (thread_friction * pitch_diameter_m)
        / (2 * math.cos(math.radians(THREAD_FLANK_ANGLE_DEG/2)))
    )

    bearing_friction_term = (bearing_friction * bearing_diameter_m) / 2

    return (pitch_term + thread_friction_term + bearing_friction_term) / nominal_diameter_m


def calculate_thread_torque(preload_n: float, pitch_m: float,
                            thread_friction: float, pitch_diameter_m: float,
                            ) -> float:
    """Returns the thread torque - explicitly the part of the tightening
    torque acting on the threads, excluding under-head friction.
    Required for calculating torsional shear and von-mises.
    Do not confuse with tightening torque.
    
    T_th = F * [P/(2π) + μ_th*d₂/(2*cos(α/2))]
    Where F is preload in N, P is thread pitch in m,
    μ_th is thread friction, d2 is pitch diameter in m,
    α is thread flank angle in deg
    
    Calculation split into two terms for easier reading.
    """
    pitch_term = pitch_m / (2 * math.pi)

    thread_friction_term = (
        (thread_friction * pitch_diameter_m)
        / (2 * math.cos(math.radians(THREAD_FLANK_ANGLE_DEG/2)))
    )

    return preload_n * (pitch_term + thread_friction_term)


def calculate_torsional_shear_stress(thread_torque_nm: float, stress_area_m2: float) -> float:
    """Returns the peak torsional shear stress at the shank
     of the bolt, which is required for the von mises calc.
     
     τ = 16*T_th / (π*d_s³)
     Where T_th is the thread torque in Nm,
     and d_s is the shank cross sectional diameter
     given by d_s = √((4*A_s) / π)
     where A_s is the stress area in m2
     """

    d_s = math.sqrt((4 * stress_area_m2) / math.pi)

    return (16 * thread_torque_nm) / (math.pi * (d_s ** 3))


def calculate_von_mises_stress(
        tensile_stress_pa: float,
        torsional_shear_stress_pa: float
) -> float:
    """Returns the von mises stress.
    
    σ_vm = √(σ² + 3τ²)
    Where σ is the tensile stress in Pa and
    τ is the torsional shear stress in Pa.
    """
    stress_square = tensile_stress_pa ** 2
    torsional_shear_stress_square = torsional_shear_stress_pa ** 2

    return math.sqrt(stress_square + (3 * torsional_shear_stress_square))


def calculate_proof_load_utilisation(
        stress_pa: float,
        proof_strength_pa: float
) -> float:
    """Returns the proof-load utilisation
    which is a ratio given by
    utilisation = stress / proof strength
    """
    return stress_pa / proof_strength_pa