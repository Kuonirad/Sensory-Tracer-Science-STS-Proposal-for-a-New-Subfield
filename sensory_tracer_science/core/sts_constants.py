"""
Sensory Tracer Science (STS) - Physical Constants and Fundamental Limits

This module defines all physical constants and fundamental limits used throughout
the STS framework. All values are derived from established physics and are
non-negotiable constraints on any STS implementation.
"""

import math
from typing import Dict, Any

# ============================================================================
# FUNDAMENTAL PHYSICAL CONSTANTS
# ============================================================================

# Boltzmann constant (J/K)
K_B = 1.380649e-23

# Reduced Planck constant (J·s)
HBAR = 1.054571817e-34

# Speed of light in vacuum (m/s)
C_VACUUM = 299792458.0

# Elementary charge (C)
E_CHARGE = 1.602176634e-19

# Avogadro constant (1/mol)
N_A = 6.02214076e23

# ============================================================================
# STS FOUNDATIONAL LIMITS (DERIVED FROM AXIOMS)
# ============================================================================

class STSLimits:
    """
    Fundamental limits for Sensory Tracer Science implementations.
    These are non-negotiable constraints derived from the five foundational axioms.
    """
    
    # A1: Landauer Limit - Minimum energy per bit (J/bit at T=300K)
    @staticmethod
    def landauer_limit(temperature: float = 300.0) -> float:
        """
        Minimum energy required to erase one bit of information.
        
        Args:
            temperature: Temperature in Kelvin (default 300K = room temperature)
            
        Returns:
            Minimum energy in Joules per bit
            
        Physical Origin: Landauer's Principle + Thermodynamics
        """
        return K_B * temperature * math.log(2)
    
    # A2: Speed limit in medium
    @staticmethod
    def max_speed_in_medium(refractive_index: float) -> float:
        """
        Maximum propagation speed in a medium with given refractive index.
        
        Args:
            refractive_index: Refractive index of medium (n ≥ 1)
            
        Returns:
            Maximum speed in m/s
            
        Physical Origin: Special Relativity
        """
        if refractive_index < 1.0:
            raise ValueError("Refractive index must be ≥ 1.0")
        return C_VACUUM / refractive_index
    
    # A3: Minimum entropy production (always positive)
    MIN_ENTROPY_PRODUCTION = 0.0  # J/K (strict inequality ΔS > 0 for irreversible processes)
    
    # A4: Heisenberg uncertainty limit
    @staticmethod
    def heisenberg_uncertainty() -> float:
        """
        Fundamental quantum uncertainty limit.
        
        Returns:
            ℏ/2 in J·s
            
        Physical Origin: Heisenberg Uncertainty Principle
        """
        return HBAR / 2.0
    
    # A5: Biological energy constraints
    ATP_FREE_ENERGY = 57000.0  # J/mol (ΔG of ATP hydrolysis under physiological conditions)
    MAX_ATP_DEPLETION_RATE = 0.1e-3  # mol/L/s (maximum sustainable rate before cell death)

# ============================================================================
# VALIDATION TOLERANCES (FAIL-SAFE DESIGN)
# ============================================================================

class ValidationTolerances:
    """
    Strict tolerances for the STS validation protocol.
    These define the maximum allowable errors before system failure.
    """
    
    # Energy audit tolerance (relative to input energy)
    ENERGY_AUDIT_TOLERANCE = 1e-12  # 1 picojoule per joule (more realistic for numerical precision)
    
    # Information balance tolerance (relative to injected information)
    INFORMATION_BALANCE_TOLERANCE = 0.01  # 1%
    
    # Causality check tolerance (absolute - zero tolerance)
    CAUSALITY_TOLERANCE = 0.0  # No tolerance for faster-than-light propagation

# ============================================================================
# IMPLEMENTATION-SPECIFIC CONSTRAINTS
# ============================================================================

class ImplementationLimits:
    """
    Practical limits for specific STS implementations.
    These are derived from the combination of fundamental limits and
    engineering constraints.
    """
    
    # Fiber-optic tracer constraints
    class FiberOptic:
        MAX_INPUT_ENERGY = 1e-9  # J (1 nJ - prevents nonlinear damage)
        BRILLOUIN_FREQUENCY_SHIFT_RANGE = (9e9, 13e9)  # Hz (typical for silica fiber)
        FIBER_ATTENUATION_COEFFICIENT = 0.2e-3  # 1/m (typical for telecom fiber at 1550nm)
        SILICA_REFRACTIVE_INDEX = 1.46  # dimensionless
    
    # Biocompatible neural tracer constraints  
    class Biocompatible:
        MAX_TRACER_CONCENTRATION = 1e-6  # mol/L (1 μM)
        MAX_ATP_DEPLETION_RATE = -0.1e-3  # mol/L/s
        TYPICAL_DIFFUSION_COEFFICIENT = 1e-12  # m²/s (small molecules in tissue)
        BLOOD_BRAIN_BARRIER_CLEARANCE = 1e-6  # 1/s (typical clearance rate)
    
    # Quantum-enhanced tracer constraints
    class Quantum:
        MAX_PHOTON_FLUX = 1e9  # photons/pixel/s (prevents detector saturation)
        MIN_ENTANGLEMENT_FIDELITY = 0.9  # dimensionless (minimum for quantum advantage)
        MAX_CORRELATION_FUNCTION = 0.1  # g²(0) for antibunching
        QUANTUM_COHERENCE_TIME_LIMIT = lambda T: HBAR / (2 * K_B * T)  # s

# ============================================================================
# DERIVED PHYSICAL QUANTITIES
# ============================================================================

class STSPhysics:
    """
    Physical quantities and relationships specific to STS.
    All derived from fundamental constants and STS axioms.
    """
    
    @staticmethod
    def information_energy_coupling(temperature: float = 300.0) -> float:
        """
        Energy cost per bit of information at given temperature.
        
        Args:
            temperature: Temperature in Kelvin
            
        Returns:
            Energy per bit in Joules
        """
        return STSLimits.landauer_limit(temperature)
    
    @staticmethod
    def thermal_energy(temperature: float = 300.0) -> float:
        """
        Thermal energy k_B T at given temperature.
        
        Args:
            temperature: Temperature in Kelvin
            
        Returns:
            Thermal energy in Joules
        """
        return K_B * temperature
    
    @staticmethod
    def quantum_coherence_time(temperature: float = 300.0) -> float:
        """
        Fundamental limit on quantum coherence time due to thermal decoherence.
        
        Args:
            temperature: Temperature in Kelvin
            
        Returns:
            Maximum coherence time in seconds
        """
        return HBAR / (2 * K_B * temperature)
    
    @staticmethod
    def maximum_propagation_distance(velocity: float, attenuation: float, 
                                   initial_energy: float, temperature: float = 300.0) -> float:
        """
        Maximum distance a tracer can propagate before signal drops below thermal noise.
        
        Args:
            velocity: Propagation speed (m/s)
            attenuation: Attenuation coefficient (1/m)
            initial_energy: Initial tracer energy (J)
            temperature: Temperature in Kelvin
            
        Returns:
            Maximum propagation distance in meters
        """
        thermal_energy = STSPhysics.thermal_energy(temperature)
        if initial_energy <= thermal_energy:
            return 0.0
        return (velocity / attenuation) * math.log(initial_energy / thermal_energy)

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_physical_consistency() -> Dict[str, Any]:
    """
    Validate that all STS constants and limits are physically consistent.
    
    Returns:
        Dictionary with validation results
    """
    results = {
        'landauer_limit_300K': STSLimits.landauer_limit(300.0),
        'heisenberg_limit': STSLimits.heisenberg_uncertainty(),
        'light_speed_in_silica': STSLimits.max_speed_in_medium(1.46),
        'thermal_energy_300K': STSPhysics.thermal_energy(300.0),
        'quantum_coherence_300K': STSPhysics.quantum_coherence_time(300.0),
        'atp_energy_per_molecule': ImplementationLimits.Biocompatible.MAX_ATP_DEPLETION_RATE,
    }
    
    # Basic consistency checks
    assert results['landauer_limit_300K'] > 0, "Landauer limit must be positive"
    assert results['heisenberg_limit'] > 0, "Heisenberg limit must be positive" 
    assert results['light_speed_in_silica'] < C_VACUUM, "Speed in medium must be less than c"
    assert results['thermal_energy_300K'] > 0, "Thermal energy must be positive"
    
    results['validation_status'] = 'PASSED'
    return results

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

if __name__ == "__main__":
    # Run self-validation when module is executed directly
    validation_results = validate_physical_consistency()
    print("STS Constants Validation Results:")
    for key, value in validation_results.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.6e}")
        else:
            print(f"  {key}: {value}")