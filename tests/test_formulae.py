"""Automated tests to check formulae.py"""

import pytest
from boltcalc.core.formulae import calculate_preload, calculate_torque, calculate_tensile_stress


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