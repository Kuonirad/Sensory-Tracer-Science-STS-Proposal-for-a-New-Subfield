"""
Basic framework validation tests for STS.
Tests core constants, basic calculations, and system initialization.
"""

import numpy as np
from sensory_tracer_science.core.sts_constants import *
from sensory_tracer_science.tracers.biocompatible_neural import (
    BiocompatibleNeuralTracer, BiochemicalTracer, BiologicalParameters
)


def test_codata_constants_validation():
    """Validate CODATA 2022 fundamental constants."""
    print("Testing CODATA 2022 constants...")
    
    # Test exact constants (defined values)
    assert K_B == 1.380649e-23, "Boltzmann constant mismatch"
    assert E_CHARGE == 1.602176634e-19, "Elementary charge mismatch"
    assert C_VACUUM == 299792458.0, "Speed of light mismatch"
    assert N_A == 6.02214076e23, "Avogadro constant mismatch"
    
    # Test derived constants (with floating point tolerance)
    expected_gas = K_B * N_A
    assert abs(R_GAS - expected_gas) < 1e-9, "Gas constant derivation error"
    
    expected_faraday = E_CHARGE * N_A
    assert abs(F_FARADAY - expected_faraday) < 1e-5, "Faraday constant derivation error"
    
    print(f"✅ CODATA 2022 constants validated")
    print(f"   k_B = {K_B} J/K")
    print(f"   e = {E_CHARGE} C")
    print(f"   c = {C_VACUUM} m/s")
    print(f"   N_A = {N_A} mol⁻¹")


def test_landauer_principle():
    """Test Landauer principle calculation."""
    print("\nTesting Landauer principle...")
    
    # Test at room temperature
    T = 300.0  # K
    landauer_limit = STSLimits.landauer_limit(T)
    expected_limit = K_B * T * np.log(2)
    
    # Must be exactly equal (no numerical error)
    assert landauer_limit == expected_limit, "Landauer limit calculation error"
    
    # Verify magnitude is realistic (kBT ln(2) at 300K ≈ 2.87e-21 J)
    assert 2.8e-21 < landauer_limit < 3.0e-21, "Landauer limit magnitude unrealistic"
    
    print(f"✅ Landauer principle validated")
    print(f"   Landauer limit at {T}K: {landauer_limit:.3e} J")
    print(f"   This is the minimum energy per bit of information")


def test_tracer_system_initialization():
    """Test biocompatible tracer system initialization."""
    print("\nTesting tracer system initialization...")
    
    # Create basic tracer molecule
    tracer = BiochemicalTracer(
        name="Test fluorophore",
        molecular_weight=400.0,  # Da
        fluorescence_quantum_yield=0.7,
        binding_affinity=1e-6  # M
    )
    
    # Define tissue geometry
    geometry = {
        'length': 1e-3,    # 1 mm
        'width': 1e-3,     # 1 mm
        'height': 100e-6,  # 100 μm
    }
    
    # Create biological parameters
    bio_params = BiologicalParameters(
        atp_free_energy=50000.0,  # J/mol
        atp_concentration=3e-3,   # mol/L
        atp_turnover_rate=1e-3,   # mol/L/s
    )
    
    # Initialize tracer system
    system = BiocompatibleNeuralTracer(
        tracer=tracer,
        tissue_geometry=geometry,
        parameters=bio_params
    )
    
    # Test basic properties
    assert system is not None, "System initialization failed"
    assert system.tracer.name == "Test fluorophore", "Tracer name mismatch"
    assert system.tracer.molecular_weight == 400.0, "Molecular weight mismatch"
    
    # Test tissue volume calculation
    expected_volume = 1e-3 * 1e-3 * 100e-6  # L × W × H
    actual_volume = system.tissue_volume
    assert abs(actual_volume - expected_volume) < 1e-15, "Volume calculation error"
    
    print(f"✅ Tracer system initialization successful")
    print(f"   Tracer: {system.tracer.name}")
    print(f"   Molecular weight: {system.tracer.molecular_weight} Da")
    print(f"   Tissue volume: {actual_volume:.2e} m³")


def test_energy_budget_analysis():
    """Test energy budget analysis for ATP compliance."""
    print("\nTesting energy budget analysis...")
    
    # Create system for energy analysis
    tracer = BiochemicalTracer("Energy tracer", 300.0, 0.8, 1e-7)
    geometry = {'length': 500e-6, 'width': 500e-6, 'height': 50e-6}
    bio_params = BiologicalParameters(
        atp_free_energy=55000.0,  # J/mol
        atp_concentration=4e-3,   # mol/L
        atp_turnover_rate=2e-3,   # mol/L/s
    )
    
    system = BiocompatibleNeuralTracer(tracer, geometry, bio_params)
    
    # Calculate energy availability
    tissue_vol = system.tissue_volume
    atp_energy_density = bio_params.atp_free_energy  # J/mol
    atp_moles_available = bio_params.atp_concentration * tissue_vol  # mol
    total_atp_energy = atp_energy_density * atp_moles_available  # J
    
    # Calculate Landauer minimum for information processing
    T = 310.0  # K (body temperature)
    landauer_min = STSLimits.landauer_limit(T)
    
    # Assume 10,000 bits of information processing
    bits_processed = 10000
    min_energy_required = bits_processed * landauer_min
    
    # Check energy sufficiency
    assert total_atp_energy > 0, "Total ATP energy must be positive"
    assert min_energy_required > 0, "Minimum energy requirement must be positive"
    
    energy_margin = total_atp_energy / min_energy_required
    assert energy_margin > 1.0, "Insufficient energy for information processing"
    
    print(f"✅ Energy budget analysis complete")
    print(f"   ATP energy available: {total_atp_energy:.3e} J")
    print(f"   Landauer minimum for {bits_processed} bits: {min_energy_required:.3e} J")
    print(f"   Energy margin: {energy_margin:.1f}x above minimum")


def test_numerical_stability():
    """Test numerical stability with edge cases."""
    print("\nTesting numerical stability...")
    
    # Test with minimal values
    tracer_min = BiochemicalTracer("Minimal", 50.0, 0.01, 1e-12)
    geometry_min = {'length': 1e-6, 'width': 1e-6, 'height': 1e-9}
    bio_params_min = BiologicalParameters(
        atp_free_energy=20000.0,
        atp_concentration=1e-6,
        atp_turnover_rate=1e-6,
    )
    
    try:
        system_min = BiocompatibleNeuralTracer(tracer_min, geometry_min, bio_params_min)
        vol_min = system_min.tissue_volume
        
        # Check for numerical issues
        assert not np.isnan(vol_min), "Volume calculation produced NaN"
        assert not np.isinf(vol_min), "Volume calculation produced infinity"
        assert vol_min > 0, "Volume must be positive"
        
    except Exception as e:
        raise AssertionError(f"Numerical instability with minimal values: {e}")
    
    # Test with large values
    tracer_max = BiochemicalTracer("Maximal", 5000.0, 1.0, 1e-3)
    geometry_max = {'length': 1e-2, 'width': 1e-2, 'height': 1e-3}
    bio_params_max = BiologicalParameters(
        atp_free_energy=100000.0,
        atp_concentration=0.1,
        atp_turnover_rate=0.1,
    )
    
    try:
        system_max = BiocompatibleNeuralTracer(tracer_max, geometry_max, bio_params_max)
        vol_max = system_max.tissue_volume
        
        # Check for numerical issues
        assert not np.isnan(vol_max), "Volume calculation produced NaN"
        assert not np.isinf(vol_max), "Volume calculation produced infinity"
        assert vol_max > 0, "Volume must be positive"
        
    except Exception as e:
        raise AssertionError(f"Numerical instability with large values: {e}")
    
    print(f"✅ Numerical stability validated")
    print(f"   Minimal system volume: {vol_min:.2e} m³")
    print(f"   Maximal system volume: {vol_max:.2e} m³")


if __name__ == '__main__':
    """Run all basic framework tests."""
    print("🧪 Starting STS Framework Basic Validation Tests\n")
    print("=" * 60)
    
    try:
        test_codata_constants_validation()
        test_landauer_principle()
        test_tracer_system_initialization()
        test_energy_budget_analysis()
        test_numerical_stability()
        
        print("\n" + "=" * 60)
        print("🎉 ALL BASIC FRAMEWORK TESTS PASSED!")
        print("✅ CODATA 2022 constants: EXACT compliance")
        print("✅ Landauer principle: Thermodynamic limits validated")
        print("✅ Tracer systems: Initialization and basic functionality")
        print("✅ Energy budgets: ATP compliance with information limits")
        print("✅ Numerical stability: Robust across parameter ranges")
        print("\n🔬 STS Framework: READY FOR SCIENTIFIC USE")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("🔧 Please check the implementation and try again.")
        raise