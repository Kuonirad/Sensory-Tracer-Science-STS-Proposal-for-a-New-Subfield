"""
STS Tracers Module - Specific Sensory Tracer Implementations

This module contains implementations of specific sensory tracers that demonstrate
the STS framework across different physical domains and scales.
"""

from .fiber_optic_brillouin import (
    FiberOpticBrillouinTracer,
    BrillouinTracerExperiment,
    BrillouinScatteringParameters
)

from .biocompatible_neural import (
    BiocompatibleNeuralTracer,
    NeuralTracerExperiment,
    BiochemicalTracer,
    BiologicalParameters
)

from .quantum_enhanced import (
    QuantumEnhancedSensoryTracer,
    QuantumTracerExperiment,
    QuantumSensorParameters,
    QuantumPhotonPair
)

__all__ = [
    # Fiber-optic implementations (Optical Temporalics)
    'FiberOpticBrillouinTracer',
    'BrillouinTracerExperiment', 
    'BrillouinScatteringParameters',
    
    # Biocompatible implementations (Bio-Temporalics)
    'BiocompatibleNeuralTracer',
    'NeuralTracerExperiment',
    'BiochemicalTracer',
    'BiologicalParameters',
    
    # Quantum implementations (Quantum Temporalics)
    'QuantumEnhancedSensoryTracer',
    'QuantumTracerExperiment',
    'QuantumSensorParameters',
    'QuantumPhotonPair'
]