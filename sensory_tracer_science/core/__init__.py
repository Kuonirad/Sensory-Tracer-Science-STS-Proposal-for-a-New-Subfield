"""
STS Core Module - Foundational Framework Implementation

This module contains the core theoretical framework, governing equations,
and fundamental constants for Sensory Tracer Science.
"""

from .sts_constants import (
    C_VACUUM,
    HBAR,
    K_B,
    ImplementationLimits,
    STSLimits,
    STSPhysics,
    ValidationTolerances,
)
from .sts_equations import (
    ConservationOfSensoryInformation,
    STSState,
    STSSystemSolver,
    TracerEnergyContinuity,
    WavePropagationWithAttenuation,
)

__all__ = [
    "STSLimits",
    "ValidationTolerances",
    "ImplementationLimits",
    "STSPhysics",
    "K_B",
    "HBAR",
    "C_VACUUM",
    "STSState",
    "ConservationOfSensoryInformation",
    "TracerEnergyContinuity",
    "WavePropagationWithAttenuation",
    "STSSystemSolver",
]
