"""Automated tests to check formulae.py"""

import pytest
from boltcalc.core.formulae import (
    calculate_preload,
    calculate_torque,
    calculate_tensile_stress,
    calculate_custom_k,
    calculate_thread_torque,
    calculate_torsional_shear_stress,
    calculate_von_mises_stress,
    calculate_proof_load_utilisation
)


def test_preload_m10():
    """Test the calculate_preload function
    which is equal to F = T / (K*d)
    """
    result = calculate_preload(torque_nm=50, nut_factor=0.2, nominal_diameter_m=0.01)

    # 25000 = 50 / (0.2 * 0.01)
    assert result == pytest.approx(25000)


def test_torque_m10():
    """Test the calculate_torque function
    which is equal to T = K*d*F
    """
    result = calculate_torque(nut_factor=0.2, nominal_diameter_m=0.01, preload_n=25000)

    # 50 = 0.2 * 0.01 * 25000
    assert result == pytest.approx(50)


def test_round_trip():
    """Check preload and torque functions are true inverse
    of each other.
    """
    # Define test case variables (M16 different to M10 in other tests)
    original_torque = 200
    nut_factor = 0.15
    nominal_diameter = 0.016

    # Calculate preload from test values
    preload = calculate_preload(torque_nm=original_torque, nut_factor=nut_factor, nominal_diameter_m=nominal_diameter)

    # Calculate torque from calculated preload
    result = calculate_torque(nut_factor=nut_factor, nominal_diameter_m=nominal_diameter, preload_n=preload)

    # Compare calculated torque with orignal torque
    assert result == pytest.approx(original_torque)


def test_tensile_stress_m10():
    """Check the calculate_tensile_stress function
    which is equal to σ = F / As"""

    result = calculate_tensile_stress(preload_n=25000, stress_area_m2= 0.000058)

    # 431000000 ≈ 25000 / 0.000058
    assert result == pytest.approx(431000000, rel=0.001)


def test_custom_k_m10():
    """Check the calculate_custom_k function
    which is equal to
    K = [ P/(2π) + μ_th*d₂/(2*cos(α/2)) + μ_b*D_b/2 ] / d
    """
    result = calculate_custom_k(pitch_m=0.0015, thread_friction=0.15,
                                pitch_diameter_m=0.009026, bearing_friction=0.15,
                                bearing_diameter_m=0.013, nominal_diameter_m=0.01)

    # Pitch term ≈ 0.0015/6.2832 ≈ 2.387e-4 m
    # Thread friction term ≈ (0.15 x 9.026e-3) / (2 cos 30) ≈ 7.817e-4 m
    # Bearing friction term ≈ (0.15 x 0.013) / 2 = 9.75e-4 m
    # Therefore K ≈ (2.837e-4 + 7.817e-4 + 9.75e-4) / 0.010 ≈ 0.19954
    assert result == pytest.approx(0.19954, rel=0.001)


def test_custom_k_collapsed_m10():
    """Inputting 0 for both friction coefficients and
    keeping the other values the same as the original test
    collapses the equation to K = P / (2π * d)
    so this test checks the pure geometry in isolation"""
    result = calculate_custom_k(
        pitch_m=0.0015, thread_friction=0,
        pitch_diameter_m=0.009026, bearing_friction=0,
        bearing_diameter_m=0.013, nominal_diameter_m=0.01
    )

    # K ≈ 0.0015 / (2π * 0.01) ≈ 0.02387
    assert result == pytest.approx(0.02387, rel=0.001)


def test_thread_torque_m10():
    """Check the calculate_thread_torque function
    which is equal to T_th = F * [P/(2π) + μ_th*d₂/(2*cos(α/2))]
    """
    result = calculate_thread_torque(
        preload_n=25000, pitch_m=0.0015,
        thread_friction=0.15, pitch_diameter_m=0.009026
    )

    # Pitch term ≈ 0.0015 / 2π ≈ 2.387e-4
    # Thread friction term ≈ (0.15 * 0.009026) / (2 cos 30) ≈ 7.817e-4
    # T_th ≈ 25000 * (2.837e-4 + 7.817e-4) ≈ 25.51 Nm
    assert result == pytest.approx(25.51, rel=0.001)


def test_torsional_shear_stress():
    """Check the calculate_torsional_shear_stress function
    which is equal to τ = 16*T_th / (π*d_s³)
    """
    result = calculate_torsional_shear_stress(
        thread_torque_nm=25.51, stress_area_m2=58e-6
    )

    # d_s ≈ √((4 * 58e-6) / π) ≈ 8.5935e-3
    # τ = (16 * 25.51) / (π * d_s^3)
    assert result == pytest.approx(204726188.2, rel=0.001)


def test_von_mises_stress_m10():
    """Check the calculate_von_mises function
    which is equal to σ_vm = √(σ² + 3τ²)
    """
    result = calculate_von_mises_stress(
        tensile_stress_pa=431.01e6, torsional_shear_stress_pa=204.73e6
    )

    # 431.01e6 ^2 = 1.8577e17
    # 204.73e6 ^2 = 4.1914e16
    # σ_vm = √(1.8577e17 + (3 * 4.1914e16))
    assert result == pytest.approx(558133262.2, rel=0.001)


def test_proof_load_utilisation_m10_tensile():
    """Check the calculate_proof_load_utilisation function
    which is equal to stress / proof strength
    with a tensile stress test case.
    """
    result = calculate_proof_load_utilisation(
        stress_pa=431.03e6,
        proof_strength_pa=580e6
    )

    # 431.03e6 / 580e6 = 0.7431551724
    assert result == pytest.approx(0.7431551724)


def test_proof_load_utilisation_m10_vm():
    """Check the calculate_proof_load_utilisation function
    which is equal to stress / proof strength
    with a von mises stress test case.
    """
    result = calculate_proof_load_utilisation(
        stress_pa=558.15e6,
        proof_strength_pa=580e6
    )

    # 558.15e6 / 580e6 = 0.9623275862
    assert result == pytest.approx(0.9623275862)
