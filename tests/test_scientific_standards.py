"""
Scientific Standards Validation Tests

This module validates that the STS framework meets rigorous scientific 
computing and research standards including:
- CODATA 2022 physical constants precision
- Numerical accuracy and stability
- Physical units consistency  
- Mathematical derivation correctness
- Peer-reviewed reference compliance
"""

import pytest
import numpy as np
import numpy.testing as npt
from sensory_tracer_science.core.sts_constants import *
from sensory_tracer_science.validation.sts_validator import ValidationResult


class TestCODATACompliance:
    """Test compliance with CODATA 2022 fundamental constants."""
    
    def test_boltzmann_constant_precision(self):
        """Validate Boltzmann constant against CODATA 2022."""
        # CODATA 2022 exact value
        codata_kb = 1.380649e-23  # J/K (exact by definition)
        npt.assert_equal(K_B, codata_kb, 
                        "Boltzmann constant must match CODATA 2022 exactly")
    
    def test_planck_constant_precision(self):
        """Validate reduced Planck constant against CODATA 2022."""
        # CODATA 2022 exact value  
        codata_hbar = 1.054571817e-34  # J⋅s (exact by definition)
        npt.assert_allclose(HBAR, codata_hbar, rtol=1e-15,
                           err_msg="Planck constant precision insufficient")
    
    def test_speed_of_light_precision(self):
        """Validate speed of light against CODATA 2022."""
        # CODATA 2022 exact value
        codata_c = 299792458.0  # m/s (exact by definition)
        npt.assert_equal(C_VACUUM, codata_c,
                        "Speed of light must match CODATA 2022 exactly")
    
    def test_elementary_charge_precision(self):
        """Validate elementary charge against CODATA 2022."""
        # CODATA 2022 exact value
        codata_e = 1.602176634e-19  # C (exact by definition)
        npt.assert_equal(E_CHARGE, codata_e,
                        "Elementary charge must match CODATA 2022 exactly")
    
    def test_avogadro_constant_precision(self):
        """Validate Avogadro constant against CODATA 2022."""
        # CODATA 2022 exact value
        codata_na = 6.02214076e23  # mol⁻¹ (exact by definition)
        npt.assert_equal(N_A, codata_na,
                        "Avogadro constant must match CODATA 2022 exactly")

    def test_derived_constants_consistency(self):
        """Validate that derived constants are mathematically consistent."""
        # Gas constant: R = k_B × N_A
        r_calculated = K_B * N_A
        npt.assert_allclose(R_GAS, r_calculated, rtol=1e-15,
                           err_msg="Gas constant derivation inconsistent")
        
        # Faraday constant: F = e × N_A
        f_calculated = E_CHARGE * N_A  
        npt.assert_allclose(F_FARADAY, f_calculated, rtol=1e-15,
                           err_msg="Faraday constant derivation inconsistent")


class TestNumericalPrecision:
    """Test numerical precision and stability."""
    
    def test_landauer_limit_calculation(self):
        """Test Landauer limit calculation precision."""
        # Test at room temperature
        T_room = 300.0  # K
        landauer_expected = K_B * T_room * np.log(2)
        landauer_calculated = STSLimits.landauer_limit(T_room)
        
        npt.assert_allclose(landauer_calculated, landauer_expected, rtol=1e-15,
                           err_msg="Landauer limit calculation imprecise")
    
    def test_numerical_stability_edge_cases(self):
        """Test numerical stability at extreme values."""
        # Test very small temperature
        T_small = 1e-6  # μK
        landauer_small = STSLimits.landauer_limit(T_small)
        assert landauer_small > 0, "Landauer limit must be positive"
        assert np.isfinite(landauer_small), "Landauer limit must be finite"
        
        # Test very high temperature  
        T_large = 1e6   # MK
        landauer_large = STSLimits.landauer_limit(T_large)
        assert landauer_large > 0, "Landauer limit must be positive"
        assert np.isfinite(landauer_large), "Landauer limit must be finite"
    
    def test_debye_length_calculation_precision(self):
        """Test Debye length calculation against analytical solution."""
        # Standard physiological conditions
        ionic_strength = 0.15  # mol/L
        temperature = 310.0     # K (body temperature)
        
        # Calculate using STS function
        debye_sts = STSPhysics.debye_length(ionic_strength, temperature)
        
        # Calculate analytically
        debye_analytical = np.sqrt(
            (EPSILON_0 * K_B * temperature) / 
            (2 * E_CHARGE**2 * ionic_strength * N_A)
        )
        
        npt.assert_allclose(debye_sts, debye_analytical, rtol=1e-12,
                           err_msg="Debye length calculation imprecise")


class TestPhysicalUnitsConsistency:
    """Test physical units consistency throughout framework."""
    
    def test_energy_units_consistency(self):
        """Validate energy quantities have consistent units."""
        # Landauer limit should be in Joules
        landauer_energy = STSLimits.landauer_limit(300.0)
        
        # Should be on order of 10^-21 J at room temperature
        assert 1e-22 < landauer_energy < 1e-20, \
               f"Landauer energy magnitude unrealistic: {landauer_energy}"
        
        # ATP hydrolysis energy should be in J/mol
        atp_energy = abs(DELTA_G_ATP_HYDROLYSIS)
        assert 50e3 < atp_energy < 70e3, \
               f"ATP energy magnitude unrealistic: {atp_energy}"
    
    def test_time_units_consistency(self):
        """Validate time quantities have consistent units."""
        # Quantum coherence time should be in seconds
        coherence_time = STSPhysics.quantum_coherence_time(300.0)
        
        # Should be on order of femtoseconds at room temperature
        assert 1e-16 < coherence_time < 1e-13, \
               f"Coherence time magnitude unrealistic: {coherence_time}"
    
    def test_concentration_units_consistency(self):
        """Validate concentration quantities have consistent units."""
        # Typical tracer concentrations should be in mol/L
        max_tracer = ImplementationLimits.Biocompatible.MAX_TRACER_CONCENTRATION
        
        # Should be micromolar range
        assert 1e-8 < max_tracer < 1e-4, \
               f"Tracer concentration range unrealistic: {max_tracer}"


class TestMathematicalDerivations:
    """Test mathematical derivations for correctness."""
    
    def test_nernst_potential_derivation(self):
        """Test Nernst potential calculation against analytical result."""
        # Standard conditions
        c_in = 100e-9   # 100 nM
        c_out = 2e-3    # 2 mM  
        valence = 2     # Ca²⁺
        temperature = 310.0  # K
        
        # Calculate using STS function
        nernst_sts = STSPhysics.nernst_potential(c_in, c_out, valence, temperature)
        
        # Calculate analytically: V = (RT/zF) * ln(c_out/c_in)
        nernst_analytical = (R_GAS * temperature) / (valence * F_FARADAY) * \
                           np.log(c_out / c_in)
        
        npt.assert_allclose(nernst_sts, nernst_analytical, rtol=1e-12,
                           err_msg="Nernst potential derivation incorrect")
    
    def test_osmotic_pressure_derivation(self):
        """Test osmotic pressure calculation against van 't Hoff equation."""
        concentration_diff = 1e-6  # mol/L
        temperature = 310.0        # K
        
        # Calculate using STS function  
        osmotic_sts = STSPhysics.osmotic_pressure(concentration_diff, temperature)
        
        # Van 't Hoff equation: Π = RT * Δc
        osmotic_analytical = R_GAS * temperature * concentration_diff
        
        npt.assert_allclose(osmotic_sts, osmotic_analytical, rtol=1e-15,
                           err_msg="Osmotic pressure derivation incorrect")


class TestValidationResultStructure:
    """Test ValidationResult data structure compliance."""
    
    def test_validation_result_attributes(self):
        """Test that ValidationResult has all required attributes."""
        result = ValidationResult(
            audit_type="TEST",
            passed=True,
            measured_value=1.0,
            expected_value=1.0, 
            tolerance=0.1,
            error_magnitude=0.0,
            error_message=None
        )
        
        # Check all required attributes exist
        required_attrs = [
            'audit_type', 'passed', 'measured_value', 
            'expected_value', 'tolerance', 'error_magnitude', 'error_message'
        ]
        
        for attr in required_attrs:
            assert hasattr(result, attr), f"ValidationResult missing attribute: {attr}"
    
    def test_validation_result_types(self):
        """Test ValidationResult attribute types.""" 
        result = ValidationResult(
            audit_type="TEST",
            passed=True,
            measured_value=1.0,
            expected_value=1.0,
            tolerance=0.1, 
            error_magnitude=0.0,
            error_message=None
        )
        
        assert isinstance(result.audit_type, str)
        assert isinstance(result.passed, bool)
        assert isinstance(result.measured_value, (int, float))
        assert isinstance(result.expected_value, (int, float))
        assert isinstance(result.tolerance, (int, float))
        assert isinstance(result.error_magnitude, (int, float))
        assert result.error_message is None or isinstance(result.error_message, str)


@pytest.mark.integration
class TestFrameworkIntegration:
    """Integration tests for complete framework."""
    
    def test_complete_validation_pipeline(self):
        """Test complete validation pipeline integration."""
        from sensory_tracer_science.validation.sts_validator import STSValidator
        
        validator = STSValidator()
        
        # Create test data that should pass all audits
        test_data = {
            'E_in': 1e-9,           # 1 nJ input
            'E_out': 0.99e-9,       # 0.99 nJ output  
            'E_dissipated': 0.01e-9, # 0.01 nJ dissipated
            'I_injected': 100,       # 100 bits injected
            'I_detected': 99,        # 99 bits detected
            'I_lost': 1,            # 1 bit lost
            'signal_speed': 2e8,     # 200,000 km/s
            'medium_speed': 3e8      # 300,000 km/s (vacuum)
        }
        
        # Run full validation
        results = validator.full_validation(test_data)
        is_valid, status = validator.system_status(results)
        
        assert is_valid, f"Complete validation pipeline failed: {status}"
        
        # Check individual audit results
        assert results['energy_audit'].passed, "Energy audit should pass"
        assert results['information_balance'].passed, "Information balance should pass"  
        assert results['causality_check'].passed, "Causality check should pass"