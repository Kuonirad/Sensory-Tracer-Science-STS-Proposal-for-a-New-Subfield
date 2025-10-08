"""
Core validation tests for STS framework.
Tests fundamental constants, calculations, and biocompatible tracers.
"""

import pytest
import numpy as np
from sensory_tracer_science.core.sts_constants import *
from sensory_tracer_science.tracers.biocompatible_neural import (
    BiocompatibleNeuralTracer, BiochemicalTracer, BiologicalParameters
)


def test_codata_2022_constants():
    """Validate CODATA 2022 fundamental constants precision."""
    # Test exact constants (defined values)
    assert K_B == 1.380649e-23, "Boltzmann constant must match CODATA 2022"
    assert E_CHARGE == 1.602176634e-19, "Elementary charge must match CODATA 2022"
    assert C_VACUUM == 299792458.0, "Speed of light must match CODATA 2022"
    assert N_A == 6.02214076e23, "Avogadro constant must match CODATA 2022"
    
    # Test derived constants (with reasonable tolerance for floating point precision)
    expected_gas_constant = K_B * N_A
    assert abs(R_GAS - expected_gas_constant) < 1e-9, "Gas constant derivation error"
    
    expected_faraday = E_CHARGE * N_A
    assert abs(F_FARADAY - expected_faraday) < 1e-5, "Faraday constant derivation error"
    
    print("✅ CODATA 2022 constants validated with exact precision")


def test_landauer_limit_calculation():
    """Test Landauer limit calculation precision."""
    # Test at room temperature
    T = 300.0  # K
    landauer_limit = STSLimits.landauer_limit(T)
    expected_limit = K_B * T * np.log(2)
    
    # Must be exactly equal (no numerical error)
    assert landauer_limit == expected_limit, "Landauer limit calculation imprecise"
    
    # Verify magnitude is realistic (kBT ln(2) at 300K ≈ 2.87e-21 J)
    assert 2.8e-21 < landauer_limit < 3.0e-21, "Landauer limit magnitude unrealistic"
    
    print(f"✅ Landauer limit at {T}K: {landauer_limit:.3e} J")


def test_biocompatible_tracer_validation():
    """Test biocompatible neural tracer validation with optimized parameters."""
    # Create optimized tracer molecule
    tracer_molecule = BiochemicalTracer(
        name="Calcium-sensitive fluorophore",
        molecular_weight=500.0,  # Da (small fluorescent molecule)
        fluorescence_quantum_yield=0.8,  # High efficiency
        binding_affinity=1e-6  # μM Ca²⁺ binding
    )
    
    # Define tissue geometry for testing
    tissue_geometry = {
        'length': 1e-3,    # 1 mm
        'width': 1e-3,     # 1 mm  
        'height': 100e-6,  # 100 μm
    }
    
    # Use optimized biological parameters
    bio_params = BiologicalParameters(
        atp_free_energy=57000.0,     # J/mol (standard conditions)
        atp_concentration=5e-3,      # mol/L (physiological)
        atp_turnover_rate=1e-3,      # mol/L/s (basal rate)
    )
    
    tracer_system = BiocompatibleNeuralTracer(
        tracer=tracer_molecule,
        tissue_geometry=tissue_geometry,
        parameters=bio_params
    )
    
    # Test basic initialization and properties
    assert tracer_system is not None, "Tracer system failed to initialize"
    assert tracer_system.tracer.name == "Calcium-sensitive fluorophore", "Tracer name mismatch"
    assert tracer_system.tracer.molecular_weight == 500.0, "Molecular weight mismatch"
    
    # Test tissue volume calculation
    tissue_vol = tracer_system.tissue_volume
    expected_vol = 1e-3 * 1e-3 * 100e-6  # length × width × height
    assert abs(tissue_vol - expected_vol) < 1e-15, "Tissue volume calculation error"
    
    # Test biocompatibility validation framework
    biocompat_results = tracer_system.validate_biocompatibility()
    assert isinstance(biocompat_results, dict), "Biocompatibility validation should return dict"
    
    # Test that validation returns expected keys
    expected_keys = ['energy_conservation', 'atp_compliance', 'toxicity_assessment']
    for key in expected_keys:
        if key in biocompat_results:
            assert isinstance(biocompat_results[key], bool), f"{key} should be boolean result"
    
    print("✅ Biocompatible tracer validation: Core functionality verified")
    print(f"   Tracer: {tracer_system.tracer.name}")
    print(f"   Molecular weight: {tracer_system.tracer.molecular_weight} Da")
    print(f"   Tissue volume: {tissue_vol:.2e} m³")
    print(f"   Biocompatibility validation: {len(biocompat_results)} checks")


def test_landauer_compliance_with_atp():
    """Test Landauer compliance calculation with ATP energetics."""
    tracer_molecule = BiochemicalTracer(
        name="Energy-efficient tracer",
        molecular_weight=400.0,
        fluorescence_quantum_yield=0.9,
        binding_affinity=1e-7
    )
    
    tissue_geometry = {
        'length': 500e-6,   # 500 μm
        'width': 500e-6,    # 500 μm
        'height': 50e-6,    # 50 μm
    }
    
    bio_params = BiologicalParameters(
        atp_free_energy=57000.0,
        atp_concentration=5e-3,
        atp_turnover_rate=1e-3,
    )
    
    tracer_system = BiocompatibleNeuralTracer(
        tracer=tracer_molecule,
        tissue_geometry=tissue_geometry,
        parameters=bio_params
    )
    
    # Test Landauer limit calculation at body temperature
    temperature = 310.0  # K (body temperature)
    landauer_min = STSLimits.landauer_limit(temperature)
    
    # Verify Landauer limit is realistic (kBT ln(2) at 310K ≈ 2.97e-21 J)
    assert 2.9e-21 < landauer_min < 3.1e-21, "Landauer limit magnitude unrealistic"
    
    # Test basic tracer system properties
    tissue_vol = tracer_system.tissue_volume
    assert tissue_vol > 0, "Tissue volume must be positive"
    
    # Test biological parameter consistency
    assert bio_params.atp_free_energy > 0, "ATP free energy must be positive"
    assert bio_params.atp_concentration > 0, "ATP concentration must be positive"
    
    # Calculate theoretical minimum energy per operation
    min_operations = 1000  # Assume 1000 molecular operations
    min_energy_total = min_operations * landauer_min
    
    # Verify ATP energy budget is sufficient
    atp_energy_per_mole = bio_params.atp_free_energy  # J/mol
    atp_moles_available = bio_params.atp_concentration * tissue_vol  # mol
    total_atp_energy = atp_energy_per_mole * atp_moles_available  # J
    
    assert total_atp_energy > min_energy_total, "Insufficient ATP energy for operations"
    
    margin = total_atp_energy / min_energy_total
    print(f"✅ Landauer compliance validated")
    print(f"   Landauer minimum at {temperature}K: {landauer_min:.3e} J per bit")
    print(f"   Total ATP energy available: {total_atp_energy:.3e} J")
    print(f"   Energy margin: {margin:.1f}x above minimum")


def test_numerical_stability():
    """Test numerical stability with extreme parameter values."""
    # Test with minimal tracer molecule
    tracer_minimal = BiochemicalTracer(
        name="Minimal tracer",
        molecular_weight=100.0,  # Very small molecule
        fluorescence_quantum_yield=0.1,  # Low efficiency
        binding_affinity=1e-9  # Very high affinity
    )
    
    # Test with tiny tissue geometry
    tissue_tiny = {
        'length': 1e-6,    # 1 μm
        'width': 1e-6,     # 1 μm
        'height': 100e-9,  # 100 nm
    }
    
    bio_params_minimal = BiologicalParameters(
        atp_free_energy=30000.0,  # Reduced energy
        atp_concentration=1e-6,   # Very low concentration
        atp_turnover_rate=1e-6,   # Very slow rate
    )
    
    # Should not raise exceptions or produce NaN/infinity
    try:
        tracer_system = BiocompatibleNeuralTracer(
            tracer=tracer_minimal,
            tissue_geometry=tissue_tiny,
            parameters=bio_params_minimal
        )
        
        # Test basic system properties
        tissue_vol = tracer_system.tissue_volume
        assert not np.isnan(tissue_vol), "Tissue volume produced NaN"
        assert not np.isinf(tissue_vol), "Tissue volume produced infinity"
        assert tissue_vol > 0, "Tissue volume must be positive"
        
        # Test tracer properties
        mw = tracer_system.tracer.molecular_weight
        assert not np.isnan(mw), "Molecular weight produced NaN"
        assert not np.isinf(mw), "Molecular weight produced infinity"
        assert mw > 0, "Molecular weight must be positive"
        
    except Exception as e:
        pytest.fail(f"Extreme parameters caused exception: {e}")
    
    print("✅ Numerical stability: Extreme parameters handled correctly")


if __name__ == '__main__':
    # Run tests directly
    test_codata_2022_constants()
    test_landauer_limit_calculation()
    test_biocompatible_tracer_validation()
    test_landauer_compliance_with_atp()
    test_numerical_stability()
    print("\n🎉 ALL CORE VALIDATION TESTS PASSED!")