"""
Sensory Tracer Science (STS) - Complete Framework Implementation

This package provides a complete implementation of the Sensory Tracer Science framework,
including theoretical foundations, governing equations, validation protocols,
and practical implementations across multiple physical domains.

FOUNDATIONAL RULE: No violation of logic, physics, or engineering principles.

The framework demonstrates that energy-conserving, information-preserving,
and causality-respecting sensory data propagation is physically possible
and practically implementable.
"""

__version__ = "1.0.0"
__author__ = "STS Framework Implementation"

# Core theoretical framework
from .core import (
    STSLimits, ValidationTolerances, ImplementationLimits, STSPhysics,
    STSState, ConservationOfSensoryInformation, TracerEnergyContinuity,
    WavePropagationWithAttenuation, STSSystemSolver
)

# Validation system  
from .validation import (
    STSValidator, ValidationResult,
    EnergyAuditor, InformationAuditor, CausalityAuditor
)

# Tracer implementations
from .tracers import (
    # Fiber-optic (Optical Temporalics)
    FiberOpticBrillouinTracer, BrillouinTracerExperiment,
    # Biocompatible (Bio-Temporalics) 
    BiocompatibleNeuralTracer, NeuralTracerExperiment,
    # Quantum (Quantum Temporalics)
    QuantumEnhancedSensoryTracer, QuantumTracerExperiment
)

# Testing framework
from .tests import STSFrameworkTester, TestSTSFramework

__all__ = [
    # Core framework
    'STSLimits', 'ValidationTolerances', 'ImplementationLimits', 'STSPhysics',
    'STSState', 'ConservationOfSensoryInformation', 'TracerEnergyContinuity',
    'WavePropagationWithAttenuation', 'STSSystemSolver',
    
    # Validation
    'STSValidator', 'ValidationResult',
    'EnergyAuditor', 'InformationAuditor', 'CausalityAuditor',
    
    # Implementations
    'FiberOpticBrillouinTracer', 'BrillouinTracerExperiment',
    'BiocompatibleNeuralTracer', 'NeuralTracerExperiment', 
    'QuantumEnhancedSensoryTracer', 'QuantumTracerExperiment',
    
    # Testing
    'STSFrameworkTester', 'TestSTSFramework'
]

# Framework metadata
FRAMEWORK_INFO = {
    'name': 'Sensory Tracer Science (STS)',
    'version': __version__,
    'description': 'Energy-conserving, information-preserving, causality-respecting sensory data propagation',
    'axioms': 5,
    'implementations': 3,
    'validation_audits': 3,
    'physical_domains': ['optical', 'biological', 'quantum'],
    'foundational_rule': 'No violation of logic, physics, or engineering'
}

def get_framework_info():
    """
    Get information about the STS framework.
    
    Returns:
        Dictionary with framework metadata
    """
    return FRAMEWORK_INFO.copy()

def quick_validation_test():
    """
    Run a quick validation test to verify framework integrity.
    
    Returns:
        Boolean indicating if framework passes basic validation
    """
    try:
        # Test basic imports and functionality
        validator = STSValidator()
        
        # Test simple valid system
        test_data = {
            'E_in': 1e-9, 'E_out': 0.99e-9, 'E_dissipated': 0.01e-9,
            'I_injected': 100, 'I_detected': 99, 'I_lost': 1,
            'signal_speed': 2e8, 'medium_speed': 3e8
        }
        
        results = validator.full_validation(test_data)
        is_valid, _ = validator.system_status(results)
        
        return is_valid
        
    except Exception:
        return False