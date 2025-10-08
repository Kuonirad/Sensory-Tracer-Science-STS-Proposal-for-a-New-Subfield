"""
STS Core Module - Foundational Framework Implementation

This module contains the core theoretical framework, governing equations,
and fundamental constants for Sensory Tracer Science.
"""

from .sts_constants import (
    STSLimits,
    ValidationTolerances,
    ImplementationLimits,
    STSPhysics,
    K_B, HBAR, C_VACUUM
)

from .sts_equations import (
    STSState,
    ConservationOfSensoryInformation,
    TracerEnergyContinuity,
    WavePropagationWithAttenuation,
    STSSystemSolver
)

__all__ = [
    'STSLimits',
    'ValidationTolerances', 
    'ImplementationLimits',
    'STSPhysics',
    'K_B', 'HBAR', 'C_VACUUM',
    'STSState',
    'ConservationOfSensoryInformation',
    'TracerEnergyContinuity',
    'WavePropagationWithAttenuation',
    'STSSystemSolver'
]