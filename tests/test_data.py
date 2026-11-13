"""Automated tests to check threads.toml"""

import math
import pytest

from boltcalc.data.loader import load_threads


def test_load_threads_m10():
    """Checks M10 loads with the right designation and SI values."""
    result = load_threads()
    thread = result["M10"]

    # Thread designation should be "M10"
    assert thread.designation == "M10"
    # M10 nominal diameter = 10mm = 10e-3m
    assert thread.nominal_diameter_m == pytest.approx(10e-3)
    # M10 pitch = 1.5mm = 1.5e-3m
    assert thread.pitch_m == pytest.approx(1.5e-3)
    # M10 pitch diameter = 9.026mm = 9.026e-3m
    assert thread.pitch_diameter_m == pytest.approx(9.026e-3)
    # M10 stress area = 58mm2 = 58e-6m2 (since (1e-3)^2 = 1e-6)
    assert thread.stress_area_m2 == pytest.approx(58e-6)


def test_thread_completeness():
    """Checks that the full set of threads has been loaded
    in and labelled correctly.
    """
    result = load_threads()

    # Check loaded sizes are exactly the expected sizes
    expected_entries = ["M2", "M2.5", "M3", "M4", "M5", "M6", "M8", "M10",
                        "M12", "M14", "M16", "M18", "M20", "M22", "M24"]
    assert set(result) == set(expected_entries)

    # Check each entry is labelled correctly
    for key, thread in result.items():
        assert thread.designation == key


def test_thread_consistency():
    """Loops over every thread and computes pitch diameter and
    stress area from nominal diameter and pitch and checks they
    match values in threads.toml
    """
    result = load_threads()

    for key, thread in result.items():
        d = thread.nominal_diameter_m
        p = thread.pitch_m

        # d2 = d - (0.6495 * p)
        expected_d2 = d - (0.6495 * p)
        assert thread.pitch_diameter_m == pytest.approx(expected_d2, rel=1e-3), key

        # d3 = d - (1.2269 * p)
        expected_d3 = d - (1.2269 * p)
        expected_stress_area = (math.pi / 4) * (((expected_d2 + expected_d3) / 2) ** 2)
        assert thread.stress_area_m2 == pytest.approx(expected_stress_area, rel=5e-3), key


def test_spot_check_m24():
    """Checks M24 data against a reference table"""
    result = load_threads()
    thread = result["M24"]
    
    # Reference thread designation should be "M24"
    assert thread.designation == "M24"
    # M24 reference nominal diameter = 24mm = 24e-3m
    assert thread.nominal_diameter_m == pytest.approx(24e-3)
    # M24 reference pitch = 3mm = 3e-3m
    assert thread.pitch_m == pytest.approx(3e-3)
    # M24 reference pitch diameter = 22.051mm = 22.051e-3m
    assert thread.pitch_diameter_m == pytest.approx(22.051e-3, rel=1e-3)
    # M24 reference stress area = 353mm2 = 353e-6m2 (since (1e-3)^2 = 1e-6)
    assert thread.stress_area_m2 == pytest.approx(353e-6, rel=5e-3)


def test_spot_check_m2_5():
    """Checks M2.5 data against a reference table"""
    result = load_threads()
    thread = result["M2.5"]

    # Reference thread designation should be "M2.5"
    assert thread.designation == "M2.5"
    # M2.5 reference nominal diameter = 2.5mm = 2.5e-3m
    assert thread.nominal_diameter_m == pytest.approx(2.5e-3)
    # M2.5 reference pitch = 0.45mm = 0.45e-3m
    assert thread.pitch_m == pytest.approx(0.45e-3)
    # M2.5 reference pitch diameter = 2.208mm = 2.208e-3m
    assert thread.pitch_diameter_m == pytest.approx(2.208e-3, rel=1e-3)
    # M2.5 reference stress area = 3.39mm2 = 3.39e-6m2 (since (1e-3)^2 = 1e-6)
    assert thread.stress_area_m2 == pytest.approx(3.39e-6, rel=5e-3)