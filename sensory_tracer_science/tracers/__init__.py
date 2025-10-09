"""
STS Tracers Module - Specific Sensory Tracer Implementations

This module contains implementations of specific sensory tracers that demonstrate
the STS framework across different physical domains and scales.
"""

from .biocompatible_neural import (
    BiochemicalTracer,
    BiocompatibleNeuralTracer,
    BiologicalParameters,
    NeuralTracerExperiment,
)
from .fiber_optic_brillouin import (
    BrillouinScatteringParameters,
    BrillouinTracerExperiment,
    FiberOpticBrillouinTracer,
)
from .quantum_enhanced import (
    QuantumEnhancedSensoryTracer,
    QuantumPhotonPair,
    QuantumSensorParameters,
    QuantumTracerExperiment,
)

__all__ = [
    # Fiber-optic implementations (Optical Temporalics)
    "FiberOpticBrillouinTracer",
    "BrillouinTracerExperiment",
    "BrillouinScatteringParameters",
    # Biocompatible implementations (Bio-Temporalics)
    "BiocompatibleNeuralTracer",
    "NeuralTracerExperiment",
    "BiochemicalTracer",
    "BiologicalParameters",
    # Quantum implementations (Quantum Temporalics)
    "QuantumEnhancedSensoryTracer",
    "QuantumTracerExperiment",
    "QuantumSensorParameters",
    "QuantumPhotonPair",
]
