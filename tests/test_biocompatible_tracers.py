"""
Comprehensive test suite for biocompatible neural tracer validation.
Tests the complete augmented validation framework and safety margins.
"""

import pytest
import numpy as np
import numpy.testing as npt
from sensory_tracer_science.tracers.biocompatible_neural import (
    BiocompatibleNeuralTracer, TracerParameters
)
from sensory_tracer_science.core.sts_constants import *


class TestBiocompatibleTracerValidation:
    """Test biocompatible neural tracer validation framework."""
    
    def test_optimized_tracer_parameters(self):
        """Test tracer with optimized parameters passes all validation."""
        # Create optimized tracer parameters for maximum safety
        params = TracerParameters(
            photon_energy=1.5e-19,      # J (optimized for safety)
            photons_per_second=1e3,     # Hz (low flux)
            ca_buffering_capacity=5e-7, # mol/L (enhanced buffering)
            membrane_capacitance=1e-12, # F (standard capacitance)
            temperature=310.0,          # K (body temperature)
            atp_concentration=5e-3,     # mol/L (physiological)
            atp_free_energy=-30.5e3     # J/mol (standard conditions)
        )
        
        tracer = BiocompatibleNeuralTracer(params)
        validation_results = tracer.validate_biocompatibility()
        
        # All 6 augmented validation checks must pass
        assert validation_results['phototoxic_dose_safe'], \
               "Phototoxic dose validation failed"
        assert validation_results['calcium_buffering_adequate'], \
               "Calcium buffering validation failed"
        assert validation_results['membrane_potential_stable'], \
               "Membrane potential stability validation failed"
        assert validation_results['landauer_compliant'], \
               "Landauer compliance validation failed"
        assert validation_results['thermodynamic_feasible'], \
               "Thermodynamic feasibility validation failed"
        assert validation_results['atp_energetics_valid'], \
               "ATP energetics validation failed"
    
    def test_safety_margins(self):
        """Test that safety margins are substantial (>1000x)."""
        params = TracerParameters(
            photon_energy=1.5e-19,
            photons_per_second=1e3,
            ca_buffering_capacity=5e-7,
            membrane_capacitance=1e-12,
            temperature=310.0,
            atp_concentration=5e-3,
            atp_free_energy=-30.5e3
        )
        
        tracer = BiocompatibleNeuralTracer(params)
        safety_metrics = tracer.safety_analysis()
        
        # Verify substantial safety margins
        assert safety_metrics['phototoxic_safety_margin'] > 1000, \
               f"Phototoxic safety margin insufficient: {safety_metrics['phototoxic_safety_margin']}"
        assert safety_metrics['ca_buffering_margin'] > 1000, \
               f"Ca buffering margin insufficient: {safety_metrics['ca_buffering_margin']}"
        assert safety_metrics['membrane_stability_margin'] > 10, \
               f"Membrane stability margin insufficient: {safety_metrics['membrane_stability_margin']}"
    
    def test_landauer_compliance_calculation(self):
        """Test Landauer compliance calculation with ATP energetics."""
        params = TracerParameters(
            photon_energy=1.5e-19,
            photons_per_second=1e3,
            ca_buffering_capacity=5e-7,
            membrane_capacitance=1e-12,
            temperature=310.0,
            atp_concentration=5e-3,
            atp_free_energy=-30.5e3  # Negative ΔG
        )
        
        tracer = BiocompatibleNeuralTracer(params)
        
        # Test the fixed ATP energy calculation
        total_atp = tracer.calculate_total_atp_consumed()
        atp_to_work_efficiency = 0.6  # 60% efficiency
        atp_energy_available = total_atp * abs(params.atp_free_energy) * atp_to_work_efficiency
        
        # Should be positive energy available
        assert atp_energy_available > 0, \
               "ATP energy available must be positive"
        
        # Landauer compliance check should pass
        landauer_min = STSLimits.landauer_limit(params.temperature)
        information_bits = tracer.calculate_information_content() / np.log(2)
        min_energy_required = information_bits * landauer_min
        
        assert atp_energy_available >= min_energy_required, \
               "ATP energy must exceed Landauer minimum"
    
    def test_phototoxic_dose_calculation(self):
        """Test phototoxic dose calculation and safety limits."""
        params = TracerParameters(
            photon_energy=1.5e-19,
            photons_per_second=1e3,
            ca_buffering_capacity=5e-7,
            membrane_capacitance=1e-12,
            temperature=310.0,
            atp_concentration=5e-3,
            atp_free_energy=-30.5e3
        )
        
        tracer = BiocompatibleNeuralTracer(params)
        
        # Calculate optical power
        optical_power = tracer.calculate_optical_power()
        expected_power = params.photon_energy * params.photons_per_second
        npt.assert_allclose(optical_power, expected_power, rtol=1e-15)
        
        # Phototoxic limit (1 mW/cm²)
        phototoxic_limit = 1e-3  # W/cm²
        cell_area = 1e-6  # cm² (10 μm diameter cell)
        max_safe_power = phototoxic_limit * cell_area
        
        assert optical_power < max_safe_power, \
               f"Optical power {optical_power} exceeds safety limit {max_safe_power}"
    
    def test_calcium_buffering_validation(self):
        """Test calcium buffering capacity validation."""
        params = TracerParameters(
            photon_energy=1.5e-19,
            photons_per_second=1e3,
            ca_buffering_capacity=5e-7,  # Enhanced buffering
            membrane_capacitance=1e-12,
            temperature=310.0,
            atp_concentration=5e-3,
            atp_free_energy=-30.5e3
        )
        
        tracer = BiocompatibleNeuralTracer(params)
        
        # Calculate expected Ca²⁺ release
        expected_ca_release = tracer.calculate_expected_ca_release()
        
        # Buffering capacity should exceed Ca release
        assert params.ca_buffering_capacity > expected_ca_release, \
               "Ca buffering capacity insufficient for expected release"
        
        # Safety margin should be substantial
        margin = params.ca_buffering_capacity / expected_ca_release
        assert margin > 1000, f"Ca buffering safety margin insufficient: {margin}"
    
    def test_membrane_potential_stability(self):
        """Test membrane potential stability validation."""
        params = TracerParameters(
            photon_energy=1.5e-19,
            photons_per_second=1e3,
            ca_buffering_capacity=5e-7,
            membrane_capacitance=1e-12,
            temperature=310.0,
            atp_concentration=5e-3,
            atp_free_energy=-30.5e3
        )
        
        tracer = BiocompatibleNeuralTracer(params)
        
        # Calculate membrane potential drift
        potential_drift = tracer.calculate_membrane_potential_drift()
        
        # Drift should be minimal (<1 mV)
        max_drift = 1e-3  # V
        assert abs(potential_drift) < max_drift, \
               f"Membrane potential drift too large: {potential_drift}"
    
    def test_thermodynamic_feasibility(self):
        """Test thermodynamic feasibility validation."""
        params = TracerParameters(
            photon_energy=1.5e-19,
            photons_per_second=1e3,
            ca_buffering_capacity=5e-7,
            membrane_capacitance=1e-12,
            temperature=310.0,
            atp_concentration=5e-3,
            atp_free_energy=-30.5e3
        )
        
        tracer = BiocompatibleNeuralTracer(params)
        
        # Total energy consumption
        total_energy = tracer.calculate_total_energy_consumption()
        
        # Available ATP energy
        atp_energy = tracer.calculate_total_atp_consumed() * abs(params.atp_free_energy)
        
        # Energy balance should be feasible
        assert atp_energy >= total_energy, \
               "Insufficient ATP energy for total consumption"
    
    def test_extreme_parameter_robustness(self):
        """Test tracer robustness with extreme parameters."""
        # Test with very low photon energy
        params_low = TracerParameters(
            photon_energy=1e-21,        # Very low energy
            photons_per_second=1e6,     # High flux to compensate
            ca_buffering_capacity=1e-6, # High buffering
            membrane_capacitance=1e-12,
            temperature=310.0,
            atp_concentration=5e-3,
            atp_free_energy=-30.5e3
        )
        
        tracer_low = BiocompatibleNeuralTracer(params_low)
        
        # Should not raise exceptions
        try:
            results_low = tracer_low.validate_biocompatibility()
            assert isinstance(results_low, dict)
        except Exception as e:
            pytest.fail(f"Extreme low energy parameters caused exception: {e}")
        
        # Test with high photon energy but very low flux
        params_high = TracerParameters(
            photon_energy=1e-18,        # High energy
            photons_per_second=1e2,     # Very low flux
            ca_buffering_capacity=5e-7,
            membrane_capacitance=1e-12,
            temperature=310.0,
            atp_concentration=5e-3,
            atp_free_energy=-30.5e3
        )
        
        tracer_high = BiocompatibleNeuralTracer(params_high)
        
        try:
            results_high = tracer_high.validate_biocompatibility()
            assert isinstance(results_high, dict)
        except Exception as e:
            pytest.fail(f"Extreme high energy parameters caused exception: {e}")


class TestTracerParametersValidation:
    """Test TracerParameters data structure validation."""
    
    def test_default_parameters_valid(self):
        """Test that default parameters are physiologically valid."""
        params = TracerParameters()
        
        # Check parameter ranges
        assert 1e-21 <= params.photon_energy <= 1e-17, \
               "Default photon energy outside valid range"
        assert 1e1 <= params.photons_per_second <= 1e12, \
               "Default photon flux outside valid range"
        assert 1e-9 <= params.ca_buffering_capacity <= 1e-3, \
               "Default Ca buffering outside valid range"
        assert 1e-15 <= params.membrane_capacitance <= 1e-9, \
               "Default membrane capacitance outside valid range"
        assert 273.15 <= params.temperature <= 373.15, \
               "Default temperature outside valid range"
        assert 1e-6 <= params.atp_concentration <= 1e-1, \
               "Default ATP concentration outside valid range"
        assert -50e3 <= params.atp_free_energy <= -20e3, \
               "Default ATP free energy outside valid range"
    
    def test_parameter_type_validation(self):
        """Test parameter type validation."""
        # All parameters should be numeric
        params = TracerParameters()
        
        assert isinstance(params.photon_energy, (int, float))
        assert isinstance(params.photons_per_second, (int, float))
        assert isinstance(params.ca_buffering_capacity, (int, float))
        assert isinstance(params.membrane_capacitance, (int, float))
        assert isinstance(params.temperature, (int, float))
        assert isinstance(params.atp_concentration, (int, float))
        assert isinstance(params.atp_free_energy, (int, float))
    
    def test_parameter_physical_constraints(self):
        """Test that parameters satisfy physical constraints."""
        params = TracerParameters()
        
        # All energies and rates should be positive
        assert params.photon_energy > 0, "Photon energy must be positive"
        assert params.photons_per_second > 0, "Photon flux must be positive"
        assert params.ca_buffering_capacity > 0, "Ca buffering must be positive"
        assert params.membrane_capacitance > 0, "Membrane capacitance must be positive"
        assert params.temperature > 0, "Temperature must be positive"
        assert params.atp_concentration > 0, "ATP concentration must be positive"
        
        # ATP free energy should be negative (exothermic)
        assert params.atp_free_energy < 0, "ATP free energy should be negative"


class TestTracerMethods:
    """Test individual tracer calculation methods."""
    
    def test_information_content_calculation(self):
        """Test information content calculation."""
        params = TracerParameters()
        tracer = BiocompatibleNeuralTracer(params)
        
        info_content = tracer.calculate_information_content()
        
        # Information content should be positive
        assert info_content > 0, "Information content must be positive"
        
        # Should be proportional to photon energy and flux
        expected_info = params.photon_energy * params.photons_per_second
        # Information includes logarithmic terms, so approximate check
        assert 0.1 * expected_info <= info_content <= 10 * expected_info, \
               "Information content magnitude unrealistic"
    
    def test_energy_per_bit_calculation(self):
        """Test energy per bit calculation."""
        params = TracerParameters()
        tracer = BiocompatibleNeuralTracer(params)
        
        energy_per_bit = tracer.calculate_energy_per_bit()
        
        # Should exceed Landauer limit
        landauer_min = STSLimits.landauer_limit(params.temperature)
        assert energy_per_bit >= landauer_min, \
               "Energy per bit below Landauer limit"
        
        # Should be realistic (not too far above minimum)
        assert energy_per_bit <= 1e6 * landauer_min, \
               "Energy per bit unrealistically high"
    
    def test_measurement_uncertainty_calculation(self):
        """Test quantum measurement uncertainty calculation."""
        params = TracerParameters()
        tracer = BiocompatibleNeuralTracer(params)
        
        uncertainty = tracer.calculate_measurement_uncertainty()
        
        # Should respect Heisenberg uncertainty principle
        hbar = HBAR
        assert uncertainty >= hbar / 2, \
               "Measurement uncertainty violates Heisenberg principle"
    
    def test_causal_structure_validation(self):
        """Test causal structure validation."""
        params = TracerParameters()
        tracer = BiocompatibleNeuralTracer(params)
        
        causal_valid = tracer.validate_causal_structure()
        
        # Should always be True for properly constructed tracer
        assert causal_valid, "Causal structure validation failed"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])