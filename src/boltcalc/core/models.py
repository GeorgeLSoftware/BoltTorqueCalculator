"""Data classes utilised by the core, data and GUI layers.
everything in this file is a frozen dataclass, meaning that it cannot
be modified after creation.

All numeric field are in SI units (N, m, m^2, Pa, Nm etc.).
The unit is included in the field name for avoidance of confusion.

Conversion from mm, MPa etc. are always handled in the data loader
and GUI, never here for avoidance of doubt.

Nothing from the rest of boltcalc is imported for this file.
"""

# Import the dataclass decorator
from dataclasses import dataclass

# Validation checks
def _require_positive(name: str, value: float) -> None:
    """Raise ValueError if the passed values is not greater than zero."""
    if not value > 0:
        raise ValueError(f"{name} must be greater than zero, got {value!r}")

def _require_text(name: str, value: str) -> None:
    """Raise ValueError if the passed value is empty or whitespace."""
    if not value.strip():
        raise ValueError(f"{name} must not be empty")

# Dataclass definitions
@dataclass(frozen=True)
class Range:
    """A range of values with a low and high value, used for anything uncertain
    
    For example nut factor K, and subsequent preload, stress and utilisation
    """
    low: float
    high: float

    def __post_init__(self) -> None:
        """Validate that the low value is below the high one"""
        if self.low > self.high:
            raise ValueError(f"Range low value ({self.low}) is above high value ({self.high})")

@dataclass(frozen=True)
class FrictionInputs:
    """User values for the 'Custom K Value' option.
    
    The core turns these values into a K value using the torque equation.
    P and d2 are supplied from the Thread so are not repeated here
    to avoid duplication.
    """

    thread_friction: float     # mu_th Thread friction coefficient (unitless)
    bearing_friction: float    # mu_b Bearing friction coefficient (unitless)
    bearing_diameter_m: float  # D_b Effective under-head diameter (m)

    def __post_init__(self) -> None:
        # Validate that all values are positive
        _require_positive("thread_friction", self.thread_friction)
        _require_positive("bearing_friction", self.bearing_friction)
        _require_positive("bearing_diameter_m", self.bearing_diameter_m)


# Classes defined from the data files
@dataclass(frozen=True)
class Material:
    """A bolt material or property class such as 8.8 or A2-70.
    
    proof_strength_pa is "the stress used for utilisation checks".
    What that value is (e.g. ISO 898-1 proof stress, Rp0.2 etc.) is recorded
    in proof_basis, which means that materials with no formal proof
    stress still fit.
    """

    name: str
    family: str                 # "carbon steel", "stainless" etc.
    proof_strength_pa: float
    proof_basis: str            # "ISO 898-1 proof stress", "Rp0.2" etc.
    tensile_strength_pa: float
    source: str                 # "ISO 898-1 etc.", provides an audit trail of standards
    description: str = ""
    yield_strength_pa: float | None = None
    youngs_modulus_pa: float | None = None
    cte_per_k: float | None = None

    def __post_init__(self) -> None:
        # Validate values
        _require_text("name", self.name)
        _require_text("family", self.family)
        _require_text("proof_basis", self.proof_basis)
        _require_text("source", self.source)
        _require_positive("proof_strength_pa", self.proof_strength_pa)
        _require_positive("tensile_strength_pa", self.tensile_strength_pa)

        if self.proof_strength_pa > self.tensile_strength_pa:
            raise ValueError(
                f"{self.name}: proof strength ({self.proof_strength_pa}) is above "
                f"tensile strength ({self.tensile_strength_pa}). Check data file."
            )

        if self.yield_strength_pa is not None:
            _require_positive("yield_strength_pa", self.yield_strength_pa)

        if self.youngs_modulus_pa is not None:
            _require_positive("youngs_modulus_pa", self.youngs_modulus_pa)

@dataclass(frozen=True)
class Thread:
    """ISO metric thread size such as "M10"
    (one row of threads.toml)
    """

    designation: str           # e.g. M10
    nominal_diameter_m: float  # d
    pitch_m: float             # P
    pitch_diameter_m: float    # d2
    stress_area_m2: float      # As

    def __post_init__(self) -> None:
        # Validate values
        _require_text("designation", self.designation)
        _require_positive("nominal_diameter_m", self.nominal_diameter_m)
        _require_positive("pitch_m", self.pitch_m)
        _require_positive("pitch_diameter_m", self.pitch_diameter_m)
        _require_positive("stress_area_m2", self.stress_area_m2)

        if self.pitch_diameter_m >= self.nominal_diameter_m:
            raise ValueError(
                f"{self.designation}: pitch diameter must be smaller than the "
                "nominal diameter. Check data file."
            )

@dataclass(frozen=True)
class NutFactor:
    """One entry in the K dropdown (one row of nut_factors.toml)"""

    name: str   # e.g. "Dry, plain steel"
    k_range: Range
    source: str

    def __post_init__(self) -> None:
        # Validate values
        _require_text("name", self.name)
        _require_text("source", self.source)
        _require_positive("k_range.low", self.k_range.low)

# Two classes that bridge the GUI to Core boundary

@dataclass(frozen=True)
class Bolt:
    """A thread size made from a material"""

    thread: Thread
    material: Material

@dataclass(frozen=True)
class JointInput:
    """Contains everything core needs: the GUI builds a joint input.
    
    nut_factor can be either a K range from the dropdown or
    FrictionInputs from the Custom option. calculate.py works
    out which one was selected.
    """
    bolt: Bolt
    torque_nm: float
    nut_factor: Range | FrictionInputs

    def __post_init__(self) -> None:
        # Validate values
        _require_positive("torque_nm", self.torque_nm)

        if isinstance(self.nut_factor, Range):
            _require_positive("nut_factor.low", self.nut_factor.low)


@dataclass(frozen=True)
class Result:
    """Everything handed back by the core. GUI only displays the result.
    
    Each range runs from the K value low to high.
    High K = less preload for given torque,
    therefore preload_n.low comes from K.high and vice versa.
    
    torsional_shear_pa and von_mises_pa are None when they cannot
    be worked out
    """

    k: Range
    preload_n: Range
    tensile_stress_pa: Range
    proof_utilisation: Range
    warnings: tuple[str, ...] = ()
    torsional_shear_pa: Range | None = None
    von_mises_pa: Range | None = None