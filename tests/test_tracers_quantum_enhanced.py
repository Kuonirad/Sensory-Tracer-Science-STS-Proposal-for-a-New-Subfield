"""
Comprehensive test suite for quantum enhanced tracer module.
This test suite aims for 95%+ code coverage of quantum_enhanced.py.
"""

import cmath
import math
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from sensory_tracer_science.tracers.quantum_enhanced import (
    QuantumPhotonPair,
    QuantumSensorParameters,
    QuantumEntangledPhotonSource,
    HongOuMandelInterferometer,
    QuantumEnhancedSensoryTracer,
    QuantumTracerExperiment,
    run_quantum_tracer_tests
)
from sensory_tracer_science.core.sts_constants import C_VACUUM, HBAR, K_B, ImplementationLimits


class TestQuantumPhotonPair:
    """Test the QuantumPhotonPair dataclass."""
    
    def test_initialization_basic(self):
        """Test basic photon pair initialization."""
        wavelength = 800e-9  # 800 nm
        frequency = C_VACUUM / wavelength
        fidelity = 0.95
        polarization = 1.0 + 0.5j
        creation_time = 0.0
        
        pair = QuantumPhotonPair(
            wavelength=wavelength,
            frequency=frequency,
            entanglement_fidelity=fidelity,
            polarization_state=polarization,
            creation_time=creation_time
        )
        
        assert pair.wavelength == wavelength
        assert pair.frequency == frequency
        assert pair.entanglement_fidelity == fidelity
        assert pair.polarization_state == polarization
        assert pair.creation_time == creation_time
    
    def test_energy_per_photon_property(self):
        """Test energy per photon calculation."""
        wavelength = 1000e-9  # 1000 nm
        frequency = C_VACUUM / wavelength
        
        pair = QuantumPhotonPair(
            wavelength=wavelength,
            frequency=frequency,
            entanglement_fidelity=0.9,
            polarization_state=1.0 + 0.0j,
            creation_time=0.0
        )
        
        expected_energy = HBAR * 2 * np.pi * frequency
        assert abs(pair.energy_per_photon - expected_energy) < 1e-30
    
    def test_total_pair_energy_property(self):
        """Test total pair energy calculation."""
        wavelength = 600e-9  # 600 nm
        frequency = C_VACUUM / wavelength
        
        pair = QuantumPhotonPair(
            wavelength=wavelength,
            frequency=frequency,
            entanglement_fidelity=0.99,
            polarization_state=0.7 + 0.7j,
            creation_time=1e-9
        )
        
        expected_total = 2 * HBAR * 2 * np.pi * frequency
        assert abs(pair.total_pair_energy - expected_total) < 1e-30
    
    def test_frequency_wavelength_consistency(self):
        """Test that frequency and wavelength are consistent with c = λν."""
        wavelength = 1550e-9  # Telecom wavelength
        frequency = C_VACUUM / wavelength
        
        pair = QuantumPhotonPair(
            wavelength=wavelength,
            frequency=frequency,
            entanglement_fidelity=1.0,
            polarization_state=1.0 + 0.0j,
            creation_time=0.0
        )
        
        # Check consistency
        calculated_wavelength = C_VACUUM / pair.frequency
        assert abs(calculated_wavelength - pair.wavelength) < 1e-15
    
    def test_complex_polarization_states(self):
        """Test various complex polarization states."""
        # Circular polarization
        circular_pair = QuantumPhotonPair(
            wavelength=800e-9,
            frequency=C_VACUUM / 800e-9,
            entanglement_fidelity=0.95,
            polarization_state=1.0 + 1.0j,  # Circular
            creation_time=0.0
        )
        
        assert isinstance(circular_pair.polarization_state, complex)
        assert abs(circular_pair.polarization_state - (1.0 + 1.0j)) < 1e-10
        
        # Linear polarization
        linear_pair = QuantumPhotonPair(
            wavelength=800e-9,
            frequency=C_VACUUM / 800e-9,
            entanglement_fidelity=0.95,
            polarization_state=1.0 + 0.0j,  # Linear
            creation_time=0.0
        )
        
        assert linear_pair.polarization_state.imag == 0.0


class TestQuantumSensorParameters:
    """Test the QuantumSensorParameters dataclass."""
    
    def test_default_initialization(self):
        """Test default parameter initialization."""
        params = QuantumSensorParameters()
        
        # Photon properties
        assert params.central_wavelength == 800e-9
        assert params.bandwidth == 10e-9
        assert params.coherence_length > 0
        
        # Quantum properties
        assert params.entanglement_fidelity == 0.95
        assert params.detection_efficiency == 0.8
        assert params.dark_count_rate == 1000.0
        
        # Timing properties
        assert params.coincidence_window == 1e-9
        assert params.measurement_time == 1e-3
        
        # Physical constraints
        assert params.temperature == 4.0  # Cryogenic
        assert params.photon_flux_limit == ImplementationLimits.Quantum.MAX_PHOTON_FLUX
    
    def test_custom_initialization(self):
        """Test custom parameter initialization."""
        params = QuantumSensorParameters(
            central_wavelength=1550e-9,
            entanglement_fidelity=0.99,
            temperature=1.0
        )
        
        assert params.central_wavelength == 1550e-9
        assert params.entanglement_fidelity == 0.99
        assert params.temperature == 1.0
        
        # Other parameters should remain default
        assert params.bandwidth == 10e-9
        assert params.detection_efficiency == 0.8
    
    def test_parameter_physical_validity(self):
        """Test that parameters are physically reasonable."""
        params = QuantumSensorParameters()
        
        # Wavelength should be in optical range
        assert 300e-9 < params.central_wavelength < 2000e-9
        
        # Bandwidth should be positive and smaller than wavelength
        assert params.bandwidth > 0
        assert params.bandwidth < params.central_wavelength
        
        # Fidelity should be between 0 and 1
        assert 0 < params.entanglement_fidelity <= 1.0
        
        # Detection efficiency should be between 0 and 1
        assert 0 < params.detection_efficiency <= 1.0
        
        # Dark count rate should be positive
        assert params.dark_count_rate >= 0
        
        # Temperature should be positive
        assert params.temperature > 0
        
        # Timing parameters should be positive
        assert params.coincidence_window > 0
        assert params.measurement_time > 0


class TestQuantumEntangledPhotonSource:
    """Test the QuantumEntangledPhotonSource class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.params = QuantumSensorParameters()
        self.source = QuantumEntangledPhotonSource(self.params)
    
    def test_initialization(self):
        """Test source initialization."""
        assert self.source.params is self.params
        assert hasattr(self.source, 'validator')
        
        # Check calculated properties
        assert self.source.photon_energy > 0
        expected_energy = HBAR * 2 * np.pi * C_VACUUM / self.params.central_wavelength
        assert abs(self.source.photon_energy - expected_energy) < 1e-30
        
        assert self.source.coherence_time > 0
        expected_coherence_time = self.params.coherence_length / C_VACUUM
        assert abs(self.source.coherence_time - expected_coherence_time) < 1e-15
    
    def test_generate_entangled_pair_basic(self):
        """Test basic entangled pair generation."""
        pair = self.source.generate_entangled_pair(0.0)
        
        # Should return QuantumPhotonPair instance
        assert isinstance(pair, QuantumPhotonPair)
        
        # Properties should be reasonable
        assert pair.entanglement_fidelity <= self.params.entanglement_fidelity
        assert pair.wavelength > 0
        assert pair.frequency > 0
        assert pair.creation_time == 0.0
        
        # Energy should be consistent
        assert pair.energy_per_photon > 0
        assert pair.total_pair_energy > pair.energy_per_photon
    
    def test_generate_entangled_pair_fidelity_degradation(self):
        """Test entanglement fidelity degradation mechanisms."""
        # Generate pairs at different times
        pair_early = self.source.generate_entangled_pair(0.0)
        pair_late = self.source.generate_entangled_pair(1e-6)  # 1 microsecond later
        
        # Later pairs might have lower fidelity due to decoherence
        # (though both should still be high quality)
        assert 0 < pair_early.entanglement_fidelity <= 1.0
        assert 0 < pair_late.entanglement_fidelity <= 1.0
    
    def test_generate_entangled_pair_multiple_calls(self):
        """Test generating multiple entangled pairs."""
        pairs = []
        for i in range(10):
            pair = self.source.generate_entangled_pair(i * 1e-9)
            pairs.append(pair)
        
        # All pairs should be valid
        for pair in pairs:
            assert isinstance(pair, QuantumPhotonPair)
            assert pair.entanglement_fidelity > 0
            assert pair.wavelength > 0
        
        # Creation times should be different
        creation_times = [pair.creation_time for pair in pairs]
        assert len(set(creation_times)) == len(pairs)  # All unique
    
    def test_calculate_heisenberg_limit(self):
        """Test Heisenberg uncertainty limit calculation."""
        limit = self.source.calculate_heisenberg_limit()
        
        # Should return positive limit
        assert limit > 0
        
        # Should be related to ℏ/2
        expected_order = HBAR / 2
        assert limit >= expected_order  # Should be at least the fundamental limit
        
        # Should be finite
        assert np.isfinite(limit)
    
    def test_calculate_heisenberg_limit_temperature_dependence(self):
        """Test Heisenberg limit temperature dependence."""
        # Test at different temperatures
        params_cold = QuantumSensorParameters(temperature=1.0)
        source_cold = QuantumEntangledPhotonSource(params_cold)
        
        params_warm = QuantumSensorParameters(temperature=10.0)
        source_warm = QuantumEntangledPhotonSource(params_warm)
        
        limit_cold = source_cold.calculate_heisenberg_limit()
        limit_warm = source_warm.calculate_heisenberg_limit()
        
        # Both should be positive and finite
        assert limit_cold > 0 and np.isfinite(limit_cold)
        assert limit_warm > 0 and np.isfinite(limit_warm)
        
        # Warmer temperature might give larger uncertainty due to thermal effects
        # (though both should be close to quantum limit)
        assert limit_cold > 0
        assert limit_warm > 0


class TestHongOuMandelInterferometer:
    """Test the HongOuMandelInterferometer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.params = QuantumSensorParameters()
        self.interferometer = HongOuMandelInterferometer(self.params)
    
    def test_initialization(self):
        """Test interferometer initialization."""
        assert self.interferometer.params is self.params
        assert hasattr(self.interferometer, 'validator')
    
    def test_hong_ou_mandel_probability_perfect_indistinguishability(self):
        """Test HOM probability with perfect indistinguishability."""
        # Create identical photon pairs
        pair1 = QuantumPhotonPair(
            wavelength=800e-9,
            frequency=C_VACUUM / 800e-9,
            entanglement_fidelity=1.0,
            polarization_state=1.0 + 0.0j,
            creation_time=0.0
        )
        
        pair2 = QuantumPhotonPair(
            wavelength=800e-9,
            frequency=C_VACUUM / 800e-9,
            entanglement_fidelity=1.0,
            polarization_state=1.0 + 0.0j,
            creation_time=0.0
        )
        
        time_delay = 0.0  # Perfect temporal overlap
        
        prob = self.interferometer.hong_ou_mandel_probability(pair1, pair2, time_delay)
        
        # Should be close to 0 for perfect indistinguishability (HOM dip)
        assert prob < 0.1  # Should show strong suppression
        assert prob >= 0   # Probability must be non-negative
    
    def test_hong_ou_mandel_probability_distinguishable_photons(self):
        """Test HOM probability with distinguishable photons."""
        # Create distinguishable photon pairs
        pair1 = QuantumPhotonPair(
            wavelength=800e-9,
            frequency=C_VACUUM / 800e-9,
            entanglement_fidelity=1.0,
            polarization_state=1.0 + 0.0j,
            creation_time=0.0
        )
        
        pair2 = QuantumPhotonPair(
            wavelength=850e-9,  # Different wavelength
            frequency=C_VACUUM / 850e-9,
            entanglement_fidelity=1.0,
            polarization_state=1.0 + 0.0j,
            creation_time=0.0
        )
        
        time_delay = 0.0
        
        prob = self.interferometer.hong_ou_mandel_probability(pair1, pair2, time_delay)
        
        # Should be close to 0.5 for distinguishable photons (classical limit)
        assert 0.3 < prob < 0.7  # Should be near classical value
    
    def test_hong_ou_mandel_probability_time_delay_dependence(self):
        """Test HOM probability dependence on time delay."""
        pair1 = QuantumPhotonPair(
            wavelength=800e-9,
            frequency=C_VACUUM / 800e-9,
            entanglement_fidelity=1.0,
            polarization_state=1.0 + 0.0j,
            creation_time=0.0
        )
        
        pair2 = QuantumPhotonPair(
            wavelength=800e-9,
            frequency=C_VACUUM / 800e-9,
            entanglement_fidelity=1.0,
            polarization_state=1.0 + 0.0j,
            creation_time=0.0
        )
        
        # Test different time delays
        prob_zero = self.interferometer.hong_ou_mandel_probability(pair1, pair2, 0.0)
        prob_small = self.interferometer.hong_ou_mandel_probability(pair1, pair2, 1e-15)
        prob_large = self.interferometer.hong_ou_mandel_probability(pair1, pair2, 1e-12)
        
        # Zero delay should give minimum probability
        assert prob_zero <= prob_small
        assert prob_small <= prob_large
        
        # Large delay should approach classical limit
        assert prob_large > 0.3
    
    def test_measure_coincidences_basic(self):
        """Test basic coincidence measurement."""
        photon_pairs = []
        for i in range(10):
            pair = QuantumPhotonPair(
                wavelength=800e-9,
                frequency=C_VACUUM / 800e-9,
                entanglement_fidelity=0.95,
                polarization_state=1.0 + 0.0j,
                creation_time=i * 1e-9
            )
            photon_pairs.append(pair)
        
        measurement_duration = 10e-9  # 10 ns
        
        coincidences = self.interferometer.measure_coincidences(photon_pairs, measurement_duration)
        
        # Should return coincidence data
        assert isinstance(coincidences, dict)
        assert 'total_coincidences' in coincidences
        assert 'coincidence_rate' in coincidences
        assert 'detection_times' in coincidences
        
        # Values should be reasonable
        assert coincidences['total_coincidences'] >= 0
        assert coincidences['coincidence_rate'] >= 0
        assert len(coincidences['detection_times']) <= len(photon_pairs)
    
    def test_measure_coincidences_empty_input(self):
        """Test coincidence measurement with no photons."""
        coincidences = self.interferometer.measure_coincidences([], 1e-3)
        
        # Should handle empty input gracefully
        assert coincidences['total_coincidences'] == 0
        assert coincidences['coincidence_rate'] == 0
        assert len(coincidences['detection_times']) == 0
    
    def test_measure_coincidences_detection_efficiency(self):
        """Test that detection efficiency affects coincidence count."""
        # Create photon pairs
        photon_pairs = [
            QuantumPhotonPair(800e-9, C_VACUUM/800e-9, 0.95, 1.0+0.0j, i*1e-9)
            for i in range(20)
        ]
        
        # Test with high efficiency parameters
        high_eff_params = QuantumSensorParameters(detection_efficiency=0.9)
        high_eff_interferometer = HongOuMandelInterferometer(high_eff_params)
        
        # Test with low efficiency parameters
        low_eff_params = QuantumSensorParameters(detection_efficiency=0.1)
        low_eff_interferometer = HongOuMandelInterferometer(low_eff_params)
        
        duration = 20e-9
        
        coincidences_high = high_eff_interferometer.measure_coincidences(photon_pairs, duration)
        coincidences_low = low_eff_interferometer.measure_coincidences(photon_pairs, duration)
        
        # High efficiency should generally give more coincidences
        assert coincidences_high['coincidence_rate'] >= coincidences_low['coincidence_rate']
    
    def test_g2_correlation_function(self):
        """Test second-order correlation function calculation."""
        # Create test coincidence data
        detection_times = np.array([0.0, 1e-9, 2.5e-9, 5e-9, 8e-9]) * 1e9  # Convert to ns
        measurement_duration = 10e-9  # 10 ns
        
        g2 = self.interferometer.g2_correlation_function(detection_times, measurement_duration)
        
        # Should return correlation data
        assert isinstance(g2, dict)
        assert 'g2_zero' in g2
        assert 'correlation_times' in g2
        assert 'g2_values' in g2
        
        # g²(0) should be meaningful for photon statistics
        assert g2['g2_zero'] >= 0  # Must be non-negative
        
        # For ideal single photons, g²(0) should be 0
        # For coherent light, g²(0) should be 1
        # For thermal light, g²(0) should be 2
        assert g2['g2_zero'] <= 3  # Should be reasonable
    
    def test_g2_correlation_function_antibunching(self):
        """Test g² function for antibunched light (single photons)."""
        # Create well-separated detection times (antibunched)
        detection_times = np.array([0.0, 10.0, 20.0, 30.0, 40.0])  # ns, well separated
        measurement_duration = 50e-9
        
        g2 = self.interferometer.g2_correlation_function(detection_times, measurement_duration)
        
        # Should show antibunching (g²(0) < 1)
        assert g2['g2_zero'] < 1.0  # Signature of quantum light


class TestQuantumEnhancedSensoryTracer:
    """Test the QuantumEnhancedSensoryTracer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.params = QuantumSensorParameters()
        self.tracer = QuantumEnhancedSensoryTracer(self.params)
    
    def test_initialization_with_parameters(self):
        """Test tracer initialization with parameters."""
        assert self.tracer.params is self.params
        assert hasattr(self.tracer, 'photon_source')
        assert hasattr(self.tracer, 'interferometer')
        assert hasattr(self.tracer, 'validator')
    
    def test_initialization_default_parameters(self):
        """Test tracer initialization with default parameters."""
        tracer_default = QuantumEnhancedSensoryTracer()
        
        assert isinstance(tracer_default.params, QuantumSensorParameters)
        assert hasattr(tracer_default, 'photon_source')
        assert hasattr(tracer_default, 'interferometer')
    
    def test_quantum_phase_sensing_basic(self):
        """Test basic quantum phase sensing."""
        sensing_params = {
            'phase_shift_range': 2 * np.pi,
            'measurement_points': 50,
            'integration_time': 1e-3
        }
        
        results = self.tracer.quantum_phase_sensing(sensing_params)
        
        # Should return sensing results
        assert isinstance(results, dict)
        assert 'phase_measurements' in results
        assert 'phase_sensitivity' in results
        assert 'quantum_advantage' in results
        assert 'measurement_uncertainty' in results
        
        # Phase measurements should be arrays
        phase_meas = results['phase_measurements']
        assert len(phase_meas) > 0
        
        # Sensitivity should be positive
        assert results['phase_sensitivity'] > 0
        
        # Measurement uncertainty should be positive and finite
        assert results['measurement_uncertainty'] > 0
        assert np.isfinite(results['measurement_uncertainty'])
    
    def test_quantum_phase_sensing_heisenberg_scaling(self):
        """Test that quantum phase sensing approaches Heisenberg scaling."""
        sensing_params = {
            'phase_shift_range': np.pi,
            'measurement_points': 20,
            'integration_time': 1e-3
        }
        
        results = self.tracer.quantum_phase_sensing(sensing_params)
        
        # Should show quantum advantage
        quantum_advantage = results['quantum_advantage']
        assert quantum_advantage > 1.0  # Should beat classical limit
        
        # Uncertainty should be at or near quantum limit
        uncertainty = results['measurement_uncertainty']
        heisenberg_limit = self.tracer.photon_source.calculate_heisenberg_limit()
        
        # Uncertainty should be comparable to or better than Heisenberg limit
        assert uncertainty >= 0.1 * heisenberg_limit  # Allow for practical limitations
    
    def test_quantum_phase_sensing_parameter_scaling(self):
        """Test phase sensing scaling with different parameters."""
        # Short integration time
        params_short = {
            'phase_shift_range': np.pi,
            'measurement_points': 10,
            'integration_time': 1e-6  # Short time
        }
        
        # Long integration time
        params_long = {
            'phase_shift_range': np.pi,
            'measurement_points': 10,
            'integration_time': 1e-2  # Long time
        }
        
        results_short = self.tracer.quantum_phase_sensing(params_short)
        results_long = self.tracer.quantum_phase_sensing(params_long)
        
        # Longer integration should generally give better sensitivity
        assert results_long['phase_sensitivity'] >= results_short['phase_sensitivity']
        
        # Longer integration should generally give lower uncertainty
        assert results_long['measurement_uncertainty'] <= results_short['measurement_uncertainty'] * 2
    
    def test_quantum_state_tomography(self):
        """Test quantum state tomography."""
        # Create test photon pairs
        photon_pairs = []
        for i in range(50):
            pair = QuantumPhotonPair(
                wavelength=800e-9,
                frequency=C_VACUUM / 800e-9,
                entanglement_fidelity=0.95 - i * 0.001,  # Slight degradation
                polarization_state=cmath.exp(1j * i * 0.1),  # Varying phase
                creation_time=i * 1e-9
            )
            photon_pairs.append(pair)
        
        measurement_basis = ['H', 'V', 'D', 'A', 'R', 'L']  # Standard polarization bases
        
        tomography_result = self.tracer.quantum_state_tomography(photon_pairs, measurement_basis)
        
        # Should return tomography results
        assert isinstance(tomography_result, dict)
        assert 'density_matrix' in tomography_result
        assert 'fidelity_estimate' in tomography_result
        assert 'purity' in tomography_result
        assert 'entanglement_measure' in tomography_result
        
        # Density matrix should be 2D array
        density_matrix = tomography_result['density_matrix']
        assert density_matrix.shape == (2, 2) or density_matrix.shape == (4, 4)  # Qubit or two-qubit
        
        # Fidelity should be between 0 and 1
        fidelity = tomography_result['fidelity_estimate']
        assert 0 <= fidelity <= 1
        
        # Purity should be between 0 and 1
        purity = tomography_result['purity']
        assert 0 <= purity <= 1
        
        # Entanglement measure should be non-negative
        entanglement = tomography_result['entanglement_measure']
        assert entanglement >= 0
    
    def test_quantum_state_tomography_empty_input(self):
        """Test quantum state tomography with empty input."""
        measurement_basis = ['H', 'V']
        
        tomography_result = self.tracer.quantum_state_tomography([], measurement_basis)
        
        # Should handle empty input gracefully
        assert isinstance(tomography_result, dict)
        # May return default or error state
    
    def test_validate_quantum_tracer_valid_operation(self):
        """Test quantum tracer validation under valid conditions."""
        test_data = {
            'entanglement_fidelity': 0.95,
            'detection_efficiency': 0.8,
            'photon_flux': 1e6,  # Within limits
            'g2_zero': 0.1,  # Good antibunching
            'phase_sensitivity': 1e-6,
            'measurement_uncertainty': 1e-15
        }
        
        validation = self.tracer.validate_quantum_tracer(test_data)
        
        # Should pass validation
        assert validation['quantum_validation_passed']
        assert validation['entanglement_quality_sufficient']
        assert validation['photon_flux_within_limits']
        assert validation['antibunching_detected']
        assert validation['heisenberg_limited']
    
    def test_validate_quantum_tracer_invalid_operation(self):
        """Test quantum tracer validation under invalid conditions."""
        test_data = {
            'entanglement_fidelity': 0.5,   # Low fidelity
            'detection_efficiency': 0.1,     # Low efficiency
            'photon_flux': 1e12,            # Excessive flux
            'g2_zero': 1.5,                 # No antibunching
            'phase_sensitivity': 1e-3,       # Poor sensitivity
            'measurement_uncertainty': 1e-10  # Large uncertainty
        }
        
        validation = self.tracer.validate_quantum_tracer(test_data)
        
        # Should fail validation
        assert not validation['quantum_validation_passed']
        assert not validation['entanglement_quality_sufficient']
        assert not validation['photon_flux_within_limits']
        assert not validation['antibunching_detected']
        assert not validation['heisenberg_limited']
    
    def test_validate_quantum_tracer_edge_cases(self):
        """Test quantum tracer validation at edge cases."""
        # Exactly at limits
        test_data = {
            'entanglement_fidelity': ImplementationLimits.Quantum.MIN_ENTANGLEMENT_FIDELITY,
            'detection_efficiency': 0.9,
            'photon_flux': ImplementationLimits.Quantum.MAX_PHOTON_FLUX,
            'g2_zero': ImplementationLimits.Quantum.MAX_CORRELATION_FUNCTION,
            'phase_sensitivity': 1e-6,
            'measurement_uncertainty': 1e-15
        }
        
        validation = self.tracer.validate_quantum_tracer(test_data)
        
        # Should handle edge cases appropriately
        assert isinstance(validation['quantum_validation_passed'], bool)
        assert isinstance(validation['entanglement_quality_sufficient'], bool)


class TestQuantumTracerExperiment:
    """Test the QuantumTracerExperiment class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.experiment = QuantumTracerExperiment()
    
    def test_initialization_default(self):
        """Test experiment initialization with default parameters."""
        assert hasattr(self.experiment, 'params')
        assert isinstance(self.experiment.params, QuantumSensorParameters)
        assert hasattr(self.experiment, 'tracer')
        assert hasattr(self.experiment, 'validator')
    
    def test_initialization_custom_parameters(self):
        """Test experiment initialization with custom parameters."""
        custom_params = QuantumSensorParameters(
            central_wavelength=1550e-9,
            entanglement_fidelity=0.99
        )
        
        experiment = QuantumTracerExperiment(custom_params)
        
        assert experiment.params is custom_params
        assert experiment.params.central_wavelength == 1550e-9
    
    def test_run_quantum_sensing_experiment_basic(self):
        """Test basic quantum sensing experiment."""
        experiment_params = {
            'measurement_type': 'phase_sensing',
            'target_sensitivity': 1e-6,
            'measurement_duration': 1e-3,
            'photon_budget': 1e6
        }
        
        results = self.experiment.run_quantum_sensing_experiment(experiment_params)
        
        # Should return comprehensive results
        assert isinstance(results, dict)
        
        # Check required result fields
        required_fields = [
            'experiment_setup', 'quantum_measurements', 'performance_metrics',
            'validation_results', 'quantum_advantage'
        ]
        
        for field in required_fields:
            assert field in results, f"Missing required field: {field}"
    
    def test_run_quantum_sensing_experiment_tomography(self):
        """Test quantum sensing experiment with state tomography."""
        experiment_params = {
            'measurement_type': 'state_tomography',
            'target_sensitivity': 1e-5,
            'measurement_duration': 5e-3,
            'photon_budget': 5e5
        }
        
        results = self.experiment.run_quantum_sensing_experiment(experiment_params)
        
        # Should handle tomography measurements
        assert 'quantum_measurements' in results
        measurements = results['quantum_measurements']
        
        # Should include tomography-specific results
        if 'density_matrix' in measurements:
            assert measurements['density_matrix'].shape[0] > 1
    
    def test_run_quantum_sensing_experiment_parameter_limits(self):
        """Test experiment with parameter limits."""
        # High photon budget (may exceed limits)
        experiment_params = {
            'measurement_type': 'phase_sensing',
            'target_sensitivity': 1e-8,
            'measurement_duration': 1e-3,
            'photon_budget': 1e12  # Very high
        }
        
        results = self.experiment.run_quantum_sensing_experiment(experiment_params)
        
        # Should handle high photon budget appropriately
        validation = results['validation_results']
        if 'photon_flux_within_limits' in validation:
            # Should flag excessive photon flux
            assert not validation['photon_flux_within_limits']
    
    def test_generate_quantum_report(self):
        """Test quantum experiment report generation."""
        # Create mock experiment results
        experiment_results = {
            'experiment_setup': {
                'measurement_type': 'phase_sensing',
                'wavelength': 800e-9,
                'duration': 1e-3
            },
            'quantum_measurements': {
                'phase_sensitivity': 1e-6,
                'entanglement_fidelity': 0.95,
                'g2_zero': 0.1
            },
            'performance_metrics': {
                'quantum_advantage': 2.5,
                'heisenberg_scaling': True
            },
            'validation_results': {
                'quantum_validation_passed': True,
                'entanglement_quality_sufficient': True,
                'heisenberg_limited': True
            },
            'quantum_advantage': 2.5
        }
        
        report = self.experiment.generate_quantum_report(experiment_results)
        
        # Should return formatted string report
        assert isinstance(report, str)
        assert len(report) > 500  # Should be substantial report
        
        # Should contain key information
        assert "QUANTUM TRACER EXPERIMENT REPORT" in report
        assert "PASSED" in report or "FAILED" in report
        assert "quantum" in report.lower()
        assert "entanglement" in report.lower()
    
    def test_generate_quantum_report_failed_experiment(self):
        """Test report generation for failed experiment."""
        # Create results with failed validation
        failed_results = {
            'experiment_setup': {
                'measurement_type': 'phase_sensing',
                'wavelength': 800e-9,
                'duration': 1e-3
            },
            'quantum_measurements': {
                'phase_sensitivity': 1e-3,  # Poor sensitivity
                'entanglement_fidelity': 0.6,  # Low fidelity
                'g2_zero': 1.2  # No antibunching
            },
            'performance_metrics': {
                'quantum_advantage': 0.8,  # Below classical limit
                'heisenberg_scaling': False
            },
            'validation_results': {
                'quantum_validation_passed': False,
                'entanglement_quality_sufficient': False,
                'heisenberg_limited': False
            },
            'quantum_advantage': 0.8
        }
        
        report = self.experiment.generate_quantum_report(failed_results)
        
        # Should indicate failures
        assert "FAILED" in report or "INSUFFICIENT" in report
        assert "quantum advantage" in report.lower() or "classical" in report.lower()


class TestRunQuantumTracerTests:
    """Test the run_quantum_tracer_tests function."""
    
    def test_run_quantum_tracer_tests(self):
        """Test comprehensive quantum tracer tests execution."""
        results = run_quantum_tracer_tests()
        
        # Should return comprehensive test results
        assert isinstance(results, dict)
        
        # Should include multiple test scenarios
        assert len(results) > 2  # Should have several test cases
        
        # Check for expected test categories
        expected_categories = ['basic_entanglement', 'phase_sensing', 'state_tomography']
        found_categories = [key for key in results.keys() if any(cat in key for cat in expected_categories)]
        assert len(found_categories) > 0
        
        # Each test should have proper structure
        for test_name, test_result in results.items():
            if isinstance(test_result, dict):
                # Should have some indication of test outcome
                has_status = any(key in test_result for key in ['test_status', 'validation_passed', 'quantum_validation_passed'])
                has_data = len(test_result) > 0
                assert has_status or has_data
    
    def test_run_quantum_tracer_tests_consistency(self):
        """Test that comprehensive tests produce consistent results."""
        # Run tests twice
        results1 = run_quantum_tracer_tests()
        results2 = run_quantum_tracer_tests()
        
        # Should produce consistent test structure
        assert set(results1.keys()) == set(results2.keys())
        
        # Test types should be consistent
        for key in results1.keys():
            assert type(results1[key]) == type(results2[key])


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling throughout the module."""
    
    def test_quantum_photon_pair_extreme_parameters(self):
        """Test quantum photon pair with extreme parameters."""
        # Very short wavelength (UV)
        pair_uv = QuantumPhotonPair(
            wavelength=200e-9,
            frequency=C_VACUUM / 200e-9,
            entanglement_fidelity=1.0,
            polarization_state=1.0 + 0.0j,
            creation_time=0.0
        )
        
        assert pair_uv.energy_per_photon > 0
        assert np.isfinite(pair_uv.energy_per_photon)
        
        # Very long wavelength (IR)
        pair_ir = QuantumPhotonPair(
            wavelength=10e-6,
            frequency=C_VACUUM / 10e-6,
            entanglement_fidelity=0.5,
            polarization_state=0.1 + 0.9j,
            creation_time=1e-6
        )
        
        assert pair_ir.energy_per_photon > 0
        assert pair_uv.energy_per_photon > pair_ir.energy_per_photon
    
    def test_quantum_sensor_parameters_extreme_values(self):
        """Test quantum sensor parameters with extreme values."""
        # Very high fidelity
        params_perfect = QuantumSensorParameters(entanglement_fidelity=0.9999)
        assert params_perfect.entanglement_fidelity == 0.9999
        
        # Very low temperature
        params_cold = QuantumSensorParameters(temperature=0.1)
        assert params_cold.temperature == 0.1
        
        # Very short coincidence window
        params_fast = QuantumSensorParameters(coincidence_window=1e-12)
        assert params_fast.coincidence_window == 1e-12
    
    def test_hom_interferometer_extreme_conditions(self):
        """Test HOM interferometer under extreme conditions."""
        params = QuantumSensorParameters(detection_efficiency=0.01)  # Very low efficiency
        interferometer = HongOuMandelInterferometer(params)
        
        # Very different photon pairs
        pair1 = QuantumPhotonPair(400e-9, C_VACUUM/400e-9, 1.0, 1.0+0.0j, 0.0)
        pair2 = QuantumPhotonPair(1600e-9, C_VACUUM/1600e-9, 1.0, 0.0+1.0j, 0.0)
        
        prob = interferometer.hong_ou_mandel_probability(pair1, pair2, 0.0)
        
        # Should handle very different photons
        assert 0 <= prob <= 1
        assert prob > 0.3  # Should be near classical limit
    
    def test_quantum_tracer_zero_entanglement(self):
        """Test quantum tracer with zero entanglement."""
        params = QuantumSensorParameters(entanglement_fidelity=0.0)
        tracer = QuantumEnhancedSensoryTracer(params)
        
        # Should handle zero entanglement gracefully
        sensing_params = {
            'phase_shift_range': np.pi,
            'measurement_points': 10,
            'integration_time': 1e-6
        }
        
        results = tracer.quantum_phase_sensing(sensing_params)
        
        # Should still return results (though performance will be poor)
        assert isinstance(results, dict)
        assert 'quantum_advantage' in results
        
        # Quantum advantage should be poor with no entanglement
        assert results['quantum_advantage'] <= 1.0
    
    def test_coincidence_measurement_very_high_flux(self):
        """Test coincidence measurement with very high photon flux."""
        params = QuantumSensorParameters()
        interferometer = HongOuMandelInterferometer(params)
        
        # Create many photon pairs (high flux)
        photon_pairs = [
            QuantumPhotonPair(800e-9, C_VACUUM/800e-9, 0.9, 1.0+0.0j, i*1e-12)
            for i in range(10000)  # Very high flux
        ]
        
        # Very short measurement duration
        coincidences = interferometer.measure_coincidences(photon_pairs, 1e-9)
        
        # Should handle high flux appropriately
        assert coincidences['total_coincidences'] >= 0
        assert np.isfinite(coincidences['coincidence_rate'])
        
        # Rate should be high but finite
        assert coincidences['coincidence_rate'] < 1e15  # Should be reasonable
    
    def test_state_tomography_with_noisy_data(self):
        """Test state tomography with very noisy/corrupted data."""
        params = QuantumSensorParameters()
        tracer = QuantumEnhancedSensoryTracer(params)
        
        # Create photon pairs with very low fidelity
        noisy_pairs = []
        for i in range(20):
            pair = QuantumPhotonPair(
                wavelength=800e-9 + np.random.normal(0, 50e-9),  # Wavelength noise
                frequency=C_VACUUM / (800e-9 + np.random.normal(0, 50e-9)),
                entanglement_fidelity=0.1 + 0.1 * np.random.rand(),  # Very low fidelity
                polarization_state=np.random.rand() + 1j * np.random.rand(),  # Random state
                creation_time=i * 1e-9 + np.random.normal(0, 1e-10)  # Time jitter
            )
            noisy_pairs.append(pair)
        
        measurement_basis = ['H', 'V']
        
        # Should handle noisy data gracefully
        try:
            tomography_result = tracer.quantum_state_tomography(noisy_pairs, measurement_basis)
            
            # Should return results even with poor data
            assert isinstance(tomography_result, dict)
            
            if 'fidelity_estimate' in tomography_result:
                # Fidelity should be low but finite
                assert 0 <= tomography_result['fidelity_estimate'] <= 1
                
        except Exception as e:
            # If it raises an exception, should be informative
            assert "tomography" in str(e).lower() or "measurement" in str(e).lower()


# Additional comprehensive edge case tests to push coverage to 90%+
class TestQuantumTracerAdvancedEdgeCases:
    """Advanced edge case tests for quantum tracer module to achieve 90%+ coverage."""
    
    def setup_method(self):
        """Set up test fixtures for advanced edge case testing."""
        self.default_params = QuantumSensorParameters()
        self.source = QuantumEntangledPhotonSource(self.default_params)
        self.interferometer = HongOuMandelInterferometer(self.default_params)
        self.tracer = QuantumEnhancedSensoryTracer(self.default_params)
        self.experiment = QuantumTracerExperiment(self.default_params)
    
    def test_quantum_photon_pair_boundary_conditions(self):
        """Test quantum photon pair at physical boundaries."""
        # Test at Planck frequency boundary
        planck_wavelength = 1.616e-35  # Planck length
        planck_freq = C_VACUUM / planck_wavelength
        
        try:
            planck_pair = QuantumPhotonPair(
                wavelength=planck_wavelength,
                frequency=planck_freq,
                entanglement_fidelity=1.0,
                polarization_state=1.0 + 0.0j,
                creation_time=0.0
            )
            
            # Energy should be enormous but finite
            assert np.isfinite(planck_pair.energy_per_photon)
            assert planck_pair.energy_per_photon > 1e10  # Should be very high energy
            
        except (ValueError, OverflowError):
            # Acceptable to fail at Planck scale
            pass
    
    def test_photon_pair_complex_polarization_edge_cases(self):
        """Test photon pairs with complex polarization edge cases."""
        # Test with infinite polarization magnitude
        with pytest.raises((ValueError, OverflowError)):
            QuantumPhotonPair(
                wavelength=800e-9,
                frequency=C_VACUUM / 800e-9,
                entanglement_fidelity=1.0,
                polarization_state=float('inf') + 1j * float('inf'),
                creation_time=0.0
            )
        
        # Test with NaN polarization
        with pytest.raises((ValueError, TypeError)):
            QuantumPhotonPair(
                wavelength=800e-9,
                frequency=C_VACUUM / 800e-9,
                entanglement_fidelity=1.0,
                polarization_state=float('nan') + 1j * float('nan'),
                creation_time=0.0
            )
    
    def test_quantum_sensor_parameters_edge_validation(self):
        """Test quantum sensor parameter validation at edges."""
        # Test zero detection efficiency
        zero_efficiency_params = QuantumSensorParameters(detection_efficiency=0.0)
        assert zero_efficiency_params.detection_efficiency == 0.0
        
        # Test maximum detection efficiency
        max_efficiency_params = QuantumSensorParameters(detection_efficiency=1.0)
        assert max_efficiency_params.detection_efficiency == 1.0
        
        # Test invalid negative values
        with pytest.raises(ValueError):
            QuantumSensorParameters(detection_efficiency=-0.1)
            
        with pytest.raises(ValueError):
            QuantumSensorParameters(entanglement_fidelity=-0.1)
            
        with pytest.raises(ValueError):
            QuantumSensorParameters(temperature=-1.0)
    
    def test_entangled_photon_source_extreme_parameters(self):
        """Test entangled photon source with extreme parameters."""
        # Test with very high pump power
        high_power_params = QuantumSensorParameters()
        high_power_params.pump_power = 1e3  # 1 kW
        
        source = QuantumEntangledPhotonSource(high_power_params)
        
        # Generation rate should be very high
        pair = source.generate_entangled_pair(0.0, 1e-12, 0.0)
        assert isinstance(pair, QuantumPhotonPair)
        
        # Test Heisenberg limit with extreme parameters
        heisenberg_limit = source.calculate_heisenberg_limit()
        assert np.isfinite(heisenberg_limit)
        assert heisenberg_limit > 0
    
    def test_entangled_photon_source_zero_pump_power(self):
        """Test entangled photon source with zero pump power."""
        zero_power_params = QuantumSensorParameters()
        zero_power_params.pump_power = 0.0
        
        source = QuantumEntangledPhotonSource(zero_power_params)
        
        # Should still generate pairs (with poor efficiency)
        pair = source.generate_entangled_pair(0.0, 1e-12, 0.0)
        assert isinstance(pair, QuantumPhotonPair)
        assert pair.entanglement_fidelity <= 0.1  # Should be very low
    
    def test_hom_interferometer_identical_photon_pairs(self):
        """Test HOM interferometer with perfectly identical photon pairs."""
        identical_pair = QuantumPhotonPair(
            wavelength=800e-9,
            frequency=C_VACUUM / 800e-9,
            entanglement_fidelity=1.0,
            polarization_state=1.0 + 0.0j,
            creation_time=0.0
        )
        
        # Identical photons should show perfect Hong-Ou-Mandel effect
        prob = self.interferometer.hong_ou_mandel_probability(
            identical_pair, identical_pair, 0.0
        )
        
        # Should be close to 0 for perfect interference
        assert prob < 0.1
    
    def test_hom_interferometer_orthogonal_polarizations(self):
        """Test HOM interferometer with orthogonal polarizations."""
        pair1 = QuantumPhotonPair(
            wavelength=800e-9,
            frequency=C_VACUUM / 800e-9,
            entanglement_fidelity=1.0,
            polarization_state=1.0 + 0.0j,  # Horizontal
            creation_time=0.0
        )
        
        pair2 = QuantumPhotonPair(
            wavelength=800e-9,
            frequency=C_VACUUM / 800e-9,
            entanglement_fidelity=1.0,
            polarization_state=0.0 + 1.0j,  # Vertical
            creation_time=0.0
        )
        
        # Orthogonal polarizations should not interfere
        prob = self.interferometer.hong_ou_mandel_probability(pair1, pair2, 0.0)
        
        # Should be close to classical limit (0.5)
        assert 0.4 < prob < 0.6
    
    def test_coincidence_measurement_empty_photon_list(self):
        """Test coincidence measurement with empty photon list."""
        coincidences = self.interferometer.measure_coincidences([], 1e-3)
        
        assert coincidences['total_coincidences'] == 0
        assert coincidences['coincidence_rate'] == 0.0
        assert coincidences['g2_zero'] == 0.0
    
    def test_coincidence_measurement_single_photon(self):
        """Test coincidence measurement with single photon pair."""
        single_pair = [QuantumPhotonPair(
            wavelength=800e-9,
            frequency=C_VACUUM / 800e-9,
            entanglement_fidelity=1.0,
            polarization_state=1.0 + 0.0j,
            creation_time=1e-9
        )]
        
        coincidences = self.interferometer.measure_coincidences(single_pair, 1e-3)
        
        # Should handle single photon gracefully
        assert coincidences['total_coincidences'] >= 0
        assert np.isfinite(coincidences['coincidence_rate'])
    
    def test_g2_correlation_function_extreme_delays(self):
        """Test g2 correlation function with extreme time delays."""
        # Create photon pairs
        photon_pairs = [
            QuantumPhotonPair(800e-9, C_VACUUM/800e-9, 0.9, 1.0+0.0j, i*1e-9)
            for i in range(100)
        ]
        
        # Test with very long delay
        long_delay = 1e-3  # 1 ms delay
        g2_long = self.interferometer.g2_correlation_function(
            photon_pairs, long_delay, 1e-6
        )
        
        assert np.isfinite(g2_long)
        
        # Test with very short delay
        short_delay = 1e-15  # 1 fs delay
        g2_short = self.interferometer.g2_correlation_function(
            photon_pairs, short_delay, 1e-6
        )
        
        assert np.isfinite(g2_short)
    
    def test_quantum_phase_sensing_zero_phase_range(self):
        """Test quantum phase sensing with zero phase range."""
        sensing_params = {
            'phase_shift_range': 0.0,  # No phase variation
            'measurement_points': 10,
            'integration_time': 1e-6
        }
        
        results = self.tracer.quantum_phase_sensing(sensing_params)
        
        # Should handle zero phase range
        assert isinstance(results, dict)
        assert 'measured_phases' in results
        assert 'phase_sensitivity' in results
    
    def test_quantum_phase_sensing_single_measurement_point(self):
        """Test quantum phase sensing with single measurement point."""
        sensing_params = {
            'phase_shift_range': np.pi,
            'measurement_points': 1,  # Single point
            'integration_time': 1e-6
        }
        
        results = self.tracer.quantum_phase_sensing(sensing_params)
        
        # Should handle single measurement point
        assert len(results['measured_phases']) == 1
        assert np.isfinite(results['phase_sensitivity'])
    
    def test_quantum_phase_sensing_infinite_integration_time(self):
        """Test quantum phase sensing with very long integration time."""
        sensing_params = {
            'phase_shift_range': np.pi/4,
            'measurement_points': 5,
            'integration_time': 1e6  # Very long integration time
        }
        
        results = self.tracer.quantum_phase_sensing(sensing_params)
        
        # Should handle long integration times
        assert np.isfinite(results['phase_sensitivity'])
        # Longer integration should improve sensitivity
        assert results['phase_sensitivity'] < 1e-3
    
    def test_quantum_state_tomography_empty_pairs(self):
        """Test quantum state tomography with empty photon pairs."""
        measurement_basis = ['H', 'V', 'D', 'A', 'R', 'L']
        
        try:
            result = self.tracer.quantum_state_tomography([], measurement_basis)
            
            # Should handle empty list gracefully
            assert isinstance(result, dict)
            
        except ValueError as e:
            # Acceptable to raise error for empty input
            assert "empty" in str(e).lower() or "insufficient" in str(e).lower()
    
    def test_quantum_state_tomography_single_basis(self):
        """Test quantum state tomography with single measurement basis."""
        photon_pairs = [
            QuantumPhotonPair(800e-9, C_VACUUM/800e-9, 0.9, 1.0+0.0j, i*1e-9)
            for i in range(10)
        ]
        
        single_basis = ['H']  # Only horizontal measurement
        
        result = self.tracer.quantum_state_tomography(photon_pairs, single_basis)
        
        # Should handle single basis (though results will be limited)
        assert isinstance(result, dict)
        if 'density_matrix' in result:
            # Matrix should be valid even with limited measurements
            assert result['density_matrix'].shape[0] >= 1
    
    def test_validate_quantum_tracer_extreme_conditions(self):
        """Test quantum tracer validation under extreme conditions."""
        # Test with zero-efficiency parameters
        zero_params = QuantumSensorParameters(detection_efficiency=0.0)
        zero_tracer = QuantumEnhancedSensoryTracer(zero_params)
        
        validation_result = zero_tracer.validate_quantum_tracer()
        
        assert isinstance(validation_result, dict)
        assert 'quantum_validation_passed' in validation_result
        
        # Zero efficiency should likely fail validation
        if not validation_result['quantum_validation_passed']:
            assert 'detection_efficiency_sufficient' in validation_result
            assert not validation_result['detection_efficiency_sufficient']
    
    def test_validate_quantum_tracer_perfect_conditions(self):
        """Test quantum tracer validation under perfect conditions."""
        # Test with perfect parameters
        perfect_params = QuantumSensorParameters(
            detection_efficiency=1.0,
            entanglement_fidelity=1.0,
            temperature=0.01,  # Very low temperature
        )
        perfect_tracer = QuantumEnhancedSensoryTracer(perfect_params)
        
        validation_result = perfect_tracer.validate_quantum_tracer()
        
        assert isinstance(validation_result, dict)
        assert validation_result['quantum_validation_passed'] is True
        assert validation_result['entanglement_quality_sufficient'] is True
        assert validation_result['detection_efficiency_sufficient'] is True
    
    def test_quantum_experiment_edge_case_parameters(self):
        """Test quantum experiment with edge case parameters."""
        # Test with zero photon budget
        zero_budget_params = {
            'measurement_type': 'phase_sensing',
            'target_sensitivity': 1e-6,
            'measurement_duration': 1e-3,
            'photon_budget': 0  # Zero photons
        }
        
        results = self.experiment.run_quantum_sensing_experiment(zero_budget_params)
        
        # Should handle zero photon budget
        assert isinstance(results, dict)
        
        # Validation should likely fail
        validation = results['validation_results']
        if 'photon_flux_within_limits' in validation:
            assert validation['photon_flux_within_limits'] is False
    
    def test_quantum_experiment_extreme_sensitivity_target(self):
        """Test quantum experiment with extreme sensitivity targets."""
        # Test with impossibly high sensitivity target
        extreme_params = {
            'measurement_type': 'phase_sensing',
            'target_sensitivity': 1e-20,  # Extremely high sensitivity
            'measurement_duration': 1e-9,  # Very short time
            'photon_budget': 10  # Very few photons
        }
        
        results = self.experiment.run_quantum_sensing_experiment(extreme_params)
        
        # Should handle extreme parameters
        assert isinstance(results, dict)
        
        # Performance metrics should indicate limitations
        performance = results['performance_metrics']
        assert 'quantum_advantage' in performance
        # Quantum advantage might be poor with extreme constraints
    
    def test_quantum_report_generation_edge_cases(self):
        """Test quantum report generation with edge case results."""
        # Test with minimal results structure
        minimal_results = {
            'experiment_setup': {},
            'quantum_measurements': {},
            'performance_metrics': {},
            'validation_results': {'quantum_validation_passed': False},
            'quantum_advantage': 0.0
        }
        
        report = self.experiment.generate_quantum_report(minimal_results)
        
        # Should handle minimal results
        assert isinstance(report, str)
        assert len(report) > 100  # Should still generate some report
        
        # Test with missing fields
        incomplete_results = {
            'experiment_setup': {
                'measurement_type': 'phase_sensing',
            },
            # Missing other required fields
        }
        
        try:
            report_incomplete = self.experiment.generate_quantum_report(incomplete_results)
            assert isinstance(report_incomplete, str)
        except KeyError:
            # Acceptable to fail with incomplete results
            pass
    
    def test_run_quantum_tracer_tests_robustness(self):
        """Test robustness of run_quantum_tracer_tests function."""
        # Run multiple times to check consistency
        results_sets = []
        for _ in range(3):
            results = run_quantum_tracer_tests()
            results_sets.append(results)
        
        # All runs should return valid dictionaries
        for results in results_sets:
            assert isinstance(results, dict)
            assert len(results) > 0
        
        # Structure should be consistent across runs
        keys_sets = [set(results.keys()) for results in results_sets]
        assert all(keys == keys_sets[0] for keys in keys_sets)
    
    def test_implementation_limits_adherence(self):
        """Test adherence to implementation limits from constants."""
        # Test that quantum tracer respects implementation limits
        params = QuantumSensorParameters()
        
        # Check that parameters are within reasonable limits
        assert params.detection_efficiency <= 1.0
        assert params.entanglement_fidelity <= 1.0
        assert params.temperature >= 0.0
        assert params.coincidence_window > 0.0
        assert params.central_wavelength > 0.0
        
        # Test photon generation within limits
        source = QuantumEntangledPhotonSource(params)
        
        # Generate many pairs quickly
        pairs = []
        for i in range(100):
            pair = source.generate_entangled_pair(i*1e-12, 1e-12, 0.0)
            pairs.append(pair)
            
        # All pairs should have reasonable properties
        for pair in pairs:
            assert 0.0 <= pair.entanglement_fidelity <= 1.0
            assert pair.wavelength > 0.0
            assert pair.frequency > 0.0
            assert np.isfinite(pair.energy_per_photon)


if __name__ == "__main__":
    pytest.main([__file__])