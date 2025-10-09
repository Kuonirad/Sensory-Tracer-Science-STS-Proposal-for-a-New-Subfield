"""
Comprehensive test suite for fiber optic Brillouin tracer module.
This test suite aims for 95%+ code coverage of fiber_optic_brillouin.py.
"""

import math
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from sensory_tracer_science.tracers.fiber_optic_brillouin import (
    BrillouinScatteringParameters,
    FiberOpticBrillouinTracer,
    BrillouinTracerExperiment,
    run_comprehensive_brillouin_tests
)
from sensory_tracer_science.core.sts_constants import C_VACUUM, HBAR, K_B, ImplementationLimits


class TestBrillouinScatteringParameters:
    """Test the BrillouinScatteringParameters dataclass."""
    
    def test_default_initialization(self):
        """Test default parameter initialization."""
        params = BrillouinScatteringParameters()
        
        # Fiber material properties
        assert params.refractive_index == 1.46
        assert params.density == 2200.0
        assert params.acoustic_velocity == 5960.0
        
        # Optical properties
        assert params.wavelength == 1.55e-6
        assert params.frequency == C_VACUUM / (1.55e-6)
        
        # Brillouin scattering coefficients
        assert params.brillouin_gain_coefficient == 2e-11
        assert params.brillouin_frequency_shift == 11e9
        assert params.brillouin_linewidth == 30e6
        
        # Fiber geometry
        assert params.core_radius == 4.1e-6
    
    def test_custom_initialization(self):
        """Test custom parameter initialization."""
        params = BrillouinScatteringParameters(
            refractive_index=1.5,
            wavelength=1.3e-6,
            density=2500.0
        )
        
        assert params.refractive_index == 1.5
        assert params.wavelength == 1.3e-6
        assert params.density == 2500.0
        
        # Other parameters should remain default
        assert params.acoustic_velocity == 5960.0
        assert params.brillouin_gain_coefficient == 2e-11
    
    def test_frequency_wavelength_consistency(self):
        """Test that frequency and wavelength are consistent."""
        params = BrillouinScatteringParameters()
        
        expected_frequency = C_VACUUM / params.wavelength
        assert abs(params.frequency - expected_frequency) / expected_frequency < 1e-10
    
    def test_parameter_physical_validity(self):
        """Test that all parameters are physically reasonable."""
        params = BrillouinScatteringParameters()
        
        # Refractive index should be > 1
        assert params.refractive_index > 1.0
        
        # All positive quantities
        assert params.density > 0
        assert params.acoustic_velocity > 0
        assert params.wavelength > 0
        assert params.frequency > 0
        assert params.brillouin_gain_coefficient > 0
        assert params.brillouin_frequency_shift > 0
        assert params.brillouin_linewidth > 0
        assert params.core_radius > 0
        
        # Acoustic velocity should be reasonable for solids
        assert 1000 < params.acoustic_velocity < 10000  # m/s
        
        # Optical wavelength should be in reasonable range
        assert 1e-6 < params.wavelength < 2e-6  # Near-infrared range


class TestFiberOpticBrillouinTracer:
    """Test the FiberOpticBrillouinTracer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.params = BrillouinScatteringParameters()
        self.fiber_length = 100.0  # meters
        self.tracer = FiberOpticBrillouinTracer(self.params, self.fiber_length)
    
    def test_initialization_basic(self):
        """Test basic tracer initialization."""
        assert self.tracer.params is self.params
        assert self.tracer.fiber_length == self.fiber_length
        assert hasattr(self.tracer, 'validator')
        
        # Check energy limits
        assert self.tracer.max_input_energy == ImplementationLimits.FiberOptic.MAX_INPUT_ENERGY
        
        # Check effective area calculation
        assert self.tracer.effective_area > 0
        expected_area = math.pi * (self.params.core_radius ** 2)
        assert abs(self.tracer.effective_area - expected_area) / expected_area < 1e-10
    
    def test_initialization_custom_parameters(self):
        """Test initialization with custom parameters."""
        custom_params = BrillouinScatteringParameters(
            refractive_index=1.5,
            core_radius=5e-6
        )
        tracer = FiberOpticBrillouinTracer(custom_params, 200.0)
        
        assert tracer.params is custom_params
        assert tracer.fiber_length == 200.0
        
        # Effective area should reflect custom core radius
        expected_area = math.pi * (5e-6) ** 2
        assert abs(tracer.effective_area - expected_area) < 1e-20
    
    def test_brillouin_frequency_shift_calculation(self):
        """Test Brillouin frequency shift calculation."""
        # Test with typical parameters
        temperature = 300.0  # K
        strain = 1e-6      # microstrain
        
        freq_shift = self.tracer.brillouin_frequency_shift(temperature, strain)
        
        # Should return a frequency shift close to the nominal value
        assert isinstance(freq_shift, float)
        assert freq_shift > 0
        assert abs(freq_shift - self.params.brillouin_frequency_shift) / self.params.brillouin_frequency_shift < 0.1
    
    def test_brillouin_frequency_shift_temperature_dependence(self):
        """Test temperature dependence of Brillouin frequency shift."""
        strain = 0.0  # No strain
        
        freq_300K = self.tracer.brillouin_frequency_shift(300.0, strain)
        freq_350K = self.tracer.brillouin_frequency_shift(350.0, strain)
        
        # Higher temperature should generally decrease frequency shift
        assert freq_350K != freq_300K
        assert abs(freq_350K - freq_300K) > 1e6  # Should be measurable difference (MHz)
    
    def test_brillouin_frequency_shift_strain_dependence(self):
        """Test strain dependence of Brillouin frequency shift."""
        temperature = 300.0  # Constant temperature
        
        freq_no_strain = self.tracer.brillouin_frequency_shift(temperature, 0.0)
        freq_with_strain = self.tracer.brillouin_frequency_shift(temperature, 1e-3)  # 1000 microstrain
        
        # Strain should change frequency shift
        assert freq_with_strain != freq_no_strain
        assert abs(freq_with_strain - freq_no_strain) > 1e6  # Should be measurable
    
    def test_brillouin_power_coupling_basic(self):
        """Test basic Brillouin power coupling calculation."""
        pump_power = 1e-6    # W (1 mW)
        probe_power = 1e-9   # W (1 μW)
        interaction_length = 10.0  # m
        
        coupling = self.tracer.brillouin_power_coupling(
            pump_power, probe_power, interaction_length
        )
        
        # Should return coupling coefficient
        assert isinstance(coupling, float)
        assert coupling >= 0  # Power coupling should be non-negative
    
    def test_brillouin_power_coupling_scaling(self):
        """Test power coupling scaling with parameters."""
        base_pump = 1e-6
        base_probe = 1e-9
        base_length = 10.0
        
        # Test power scaling
        coupling_1x = self.tracer.brillouin_power_coupling(base_pump, base_probe, base_length)
        coupling_2x_pump = self.tracer.brillouin_power_coupling(2*base_pump, base_probe, base_length)
        coupling_2x_probe = self.tracer.brillouin_power_coupling(base_pump, 2*base_probe, base_length)
        
        # Should scale with pump and probe powers
        assert coupling_2x_pump > coupling_1x
        assert coupling_2x_probe > coupling_1x
        
        # Test length scaling
        coupling_2x_length = self.tracer.brillouin_power_coupling(base_pump, base_probe, 2*base_length)
        assert coupling_2x_length > coupling_1x
    
    def test_brillouin_power_coupling_energy_limits(self):
        """Test that power coupling respects energy limits."""
        # Test with maximum allowed power
        max_power = ImplementationLimits.FiberOptic.MAX_INPUT_ENERGY  # This is energy, convert to power
        max_power_watts = max_power / 1e-3  # Assume 1 ms pulse duration
        
        coupling = self.tracer.brillouin_power_coupling(
            max_power_watts, 1e-9, 10.0
        )
        
        # Should handle maximum power without issues
        assert np.isfinite(coupling)
        assert coupling >= 0
    
    def test_propagation_simulation_basic(self):
        """Test basic light propagation simulation."""
        input_energy = 1e-9  # J (1 nJ)
        fiber_positions = np.linspace(0, self.fiber_length, 100)
        
        # Simple environment (no external perturbations)
        environment = {
            'temperature': np.ones_like(fiber_positions) * 300.0,
            'strain': np.zeros_like(fiber_positions),
            'pressure': np.ones_like(fiber_positions) * 101325.0  # 1 atm
        }
        
        results = self.tracer.propagation_simulation(input_energy, fiber_positions, environment)
        
        # Should return simulation results
        assert isinstance(results, dict)
        assert 'power_profile' in results
        assert 'brillouin_spectrum' in results
        assert 'sensing_data' in results
        
        # Power profile should be positive and decay with distance
        power_profile = results['power_profile']
        assert np.all(power_profile >= 0)
        assert power_profile[0] >= power_profile[-1]  # Should decay due to losses
    
    def test_propagation_simulation_energy_conservation(self):
        """Test energy conservation in propagation simulation."""
        input_energy = 5e-10  # J
        fiber_positions = np.linspace(0, 50.0, 50)
        
        environment = {
            'temperature': np.ones_like(fiber_positions) * 300.0,
            'strain': np.zeros_like(fiber_positions),
            'pressure': np.ones_like(fiber_positions) * 101325.0
        }
        
        results = self.tracer.propagation_simulation(input_energy, fiber_positions, environment)
        
        # Total energy should be conserved (accounting for losses)
        power_profile = results['power_profile']
        
        # Input energy should be greater than or equal to output energy
        output_energy = power_profile[-1] * 1e-3  # Assume 1 ms duration
        assert input_energy >= output_energy
        
        # Energy loss should be reasonable (not more than 90% for reasonable fiber length)
        energy_loss_fraction = 1 - (output_energy / input_energy)
        assert 0 <= energy_loss_fraction <= 0.9
    
    def test_propagation_simulation_environmental_effects(self):
        """Test propagation simulation with environmental variations."""
        input_energy = 1e-9
        fiber_positions = np.linspace(0, 100.0, 50)
        
        # Environment with variations
        environment = {
            'temperature': 300.0 + 10.0 * np.sin(fiber_positions / 10.0),  # Temperature gradient
            'strain': 1e-6 * np.cos(fiber_positions / 20.0),  # Strain variation
            'pressure': np.ones_like(fiber_positions) * 101325.0
        }
        
        results = self.tracer.propagation_simulation(input_energy, fiber_positions, environment)
        
        # Should handle environmental variations
        sensing_data = results['sensing_data']
        assert 'temperature_profile' in sensing_data
        assert 'strain_profile' in sensing_data
        
        # Reconstructed profiles should show variations
        temp_profile = sensing_data['temperature_profile']
        strain_profile = sensing_data['strain_profile']
        
        assert np.std(temp_profile) > 0.1  # Should detect temperature variations
        assert np.std(strain_profile) > 1e-7  # Should detect strain variations
    
    def test_extract_sensing_information(self):
        """Test sensing information extraction."""
        # Mock Brillouin spectrum data
        frequency_axis = np.linspace(10.5e9, 11.5e9, 1000)  # Around Brillouin frequency
        spectrum_data = np.exp(-((frequency_axis - 11.0e9) / 20e6)**2)  # Gaussian peak
        
        fiber_positions = np.linspace(0, 100.0, 50)
        
        sensing_info = self.tracer.extract_sensing_information(
            spectrum_data, frequency_axis, fiber_positions
        )
        
        # Should return sensing information
        assert isinstance(sensing_info, dict)
        assert 'brillouin_frequency' in sensing_info
        assert 'linewidth' in sensing_info
        assert 'temperature_estimate' in sensing_info
        assert 'strain_estimate' in sensing_info
        
        # Frequency should be near the expected Brillouin frequency
        freq = sensing_info['brillouin_frequency']
        assert abs(freq - 11.0e9) < 100e6  # Within 100 MHz
        
        # Estimates should be reasonable
        temp_est = sensing_info['temperature_estimate']
        strain_est = sensing_info['strain_estimate']
        assert 200 < temp_est < 400  # Reasonable temperature range (K)
        assert abs(strain_est) < 1e-3  # Reasonable strain range
    
    def test_extract_sensing_information_noisy_spectrum(self):
        """Test sensing information extraction with noisy spectrum."""
        frequency_axis = np.linspace(10.5e9, 11.5e9, 1000)
        
        # Noisy spectrum
        clean_spectrum = np.exp(-((frequency_axis - 11.05e9) / 25e6)**2)
        noise = np.random.normal(0, 0.1, len(frequency_axis))
        noisy_spectrum = clean_spectrum + noise
        noisy_spectrum = np.maximum(noisy_spectrum, 0)  # Ensure non-negative
        
        fiber_positions = np.linspace(0, 50.0, 25)
        
        sensing_info = self.tracer.extract_sensing_information(
            noisy_spectrum, frequency_axis, fiber_positions
        )
        
        # Should handle noise reasonably
        assert np.isfinite(sensing_info['brillouin_frequency'])
        assert np.isfinite(sensing_info['temperature_estimate'])
        assert np.isfinite(sensing_info['strain_estimate'])
        
        # Frequency should still be in reasonable range despite noise
        freq = sensing_info['brillouin_frequency']
        assert 10.0e9 < freq < 12.0e9
    
    def test_validate_tracer_operation_valid_conditions(self):
        """Test tracer operation validation under valid conditions."""
        test_data = {
            'input_energy': 5e-10,  # Well below limit
            'power_levels': np.array([1e-6, 8e-7, 6e-7, 4e-7, 2e-7]),  # Reasonable decay
            'brillouin_frequency': 11.0e9,  # Within expected range
            'measurement_snr': 20.0,  # Good SNR
            'sensing_accuracy': 0.05  # 5% accuracy
        }
        
        validation = self.tracer.validate_tracer_operation(test_data)
        
        # Should pass validation
        assert validation['validation_passed']
        assert validation['energy_within_limits']
        assert validation['snr_adequate']
        assert validation['sensing_accuracy_acceptable']
    
    def test_validate_tracer_operation_invalid_conditions(self):
        """Test tracer operation validation under invalid conditions."""
        test_data = {
            'input_energy': 1e-8,  # Above safety limit
            'power_levels': np.array([1e-3, 1e-3, 1e-3]),  # Too high power
            'brillouin_frequency': 15.0e9,  # Outside expected range
            'measurement_snr': 2.0,  # Poor SNR
            'sensing_accuracy': 0.5  # Poor accuracy
        }
        
        validation = self.tracer.validate_tracer_operation(test_data)
        
        # Should fail validation
        assert not validation['validation_passed']
        assert not validation['energy_within_limits']
        assert not validation['snr_adequate']
        assert not validation['sensing_accuracy_acceptable']
    
    def test_validate_tracer_operation_edge_cases(self):
        """Test validation with edge case values."""
        # Exactly at limits
        test_data = {
            'input_energy': ImplementationLimits.FiberOptic.MAX_INPUT_ENERGY,
            'power_levels': np.array([1e-9, 5e-10, 1e-10]),
            'brillouin_frequency': 11.0e9,
            'measurement_snr': 10.0,  # Exactly at threshold
            'sensing_accuracy': 0.1
        }
        
        validation = self.tracer.validate_tracer_operation(test_data)
        
        # Should handle edge cases appropriately
        assert isinstance(validation['validation_passed'], bool)
        assert isinstance(validation['energy_within_limits'], bool)


class TestBrillouinTracerExperiment:
    """Test the BrillouinTracerExperiment class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fiber_length = 500.0  # meters
        self.experiment = BrillouinTracerExperiment(self.fiber_length)
    
    def test_initialization(self):
        """Test experiment initialization."""
        assert self.experiment.fiber_length == self.fiber_length
        assert hasattr(self.experiment, 'params')
        assert isinstance(self.experiment.params, BrillouinScatteringParameters)
        assert hasattr(self.experiment, 'validator')
    
    def test_initialization_default_fiber_length(self):
        """Test initialization with default fiber length."""
        experiment = BrillouinTracerExperiment()
        assert experiment.fiber_length == 1000.0  # Default value
    
    def test_create_test_environment(self):
        """Test test environment creation."""
        positions, environment = self.experiment.create_test_environment()
        
        # Should return position array and environment dict
        assert isinstance(positions, np.ndarray)
        assert isinstance(environment, dict)
        
        # Positions should span the fiber length
        assert positions[0] == 0.0
        assert positions[-1] <= self.fiber_length
        assert len(positions) > 10  # Should have reasonable resolution
        
        # Environment should have required fields
        required_fields = ['temperature', 'strain', 'pressure']
        for field in required_fields:
            assert field in environment
            assert len(environment[field]) == len(positions)
            assert np.all(np.isfinite(environment[field]))
    
    def test_create_test_environment_variations(self):
        """Test that test environment includes realistic variations."""
        positions, environment = self.experiment.create_test_environment()
        
        # Temperature should have some variation
        temp = environment['temperature']
        assert np.std(temp) > 0.1  # Should have at least 0.1 K variation
        assert np.all(temp > 200)  # Should be above absolute zero
        assert np.all(temp < 400)  # Should be below extreme temperatures
        
        # Strain should include some variations
        strain = environment['strain']
        assert np.std(strain) > 1e-7  # Should have measurable strain variation
        assert np.all(np.abs(strain) < 1e-3)  # Should be within reasonable limits
        
        # Pressure should be reasonable
        pressure = environment['pressure']
        assert np.all(pressure > 50000)   # Above 0.5 atm
        assert np.all(pressure < 200000)  # Below 2 atm
    
    def test_run_brillouin_test_basic(self):
        """Test basic Brillouin test execution."""
        input_energy = 1e-9  # 1 nJ
        
        results = self.experiment.run_brillouin_test(input_energy)
        
        # Should return comprehensive results
        assert isinstance(results, dict)
        
        # Check required result fields
        required_fields = [
            'tracer_system', 'propagation_results', 'sensing_information',
            'validation_results', 'energy_budget'
        ]
        
        for field in required_fields:
            assert field in results, f"Missing required field: {field}"
    
    def test_run_brillouin_test_default_energy(self):
        """Test Brillouin test with default energy."""
        results = self.experiment.run_brillouin_test()  # Use default energy
        
        # Should complete successfully
        assert 'tracer_system' in results
        assert 'energy_budget' in results
        
        # Energy budget should show reasonable values
        energy_budget = results['energy_budget']
        assert energy_budget['input_energy'] > 0
        assert energy_budget['total_loss'] >= 0
    
    def test_run_brillouin_test_high_energy(self):
        """Test Brillouin test with high energy input."""
        # Use energy near the safety limit
        high_energy = 0.9 * ImplementationLimits.FiberOptic.MAX_INPUT_ENERGY
        
        results = self.experiment.run_brillouin_test(high_energy)
        
        # Should handle high energy appropriately
        validation = results['validation_results']
        
        # Should validate energy limits
        assert 'energy_within_limits' in validation
        
        # Energy budget should reflect high input
        energy_budget = results['energy_budget']
        assert energy_budget['input_energy'] == high_energy
    
    def test_run_brillouin_test_excessive_energy(self):
        """Test Brillouin test with excessive energy input."""
        # Use energy above safety limits
        excessive_energy = 2 * ImplementationLimits.FiberOptic.MAX_INPUT_ENERGY
        
        results = self.experiment.run_brillouin_test(excessive_energy)
        
        # Should flag safety concerns
        validation = results['validation_results']
        assert not validation.get('energy_within_limits', True)
        assert not validation.get('validation_passed', True)
    
    def test_generate_test_report(self):
        """Test test report generation."""
        # Run a test to get results
        results = self.experiment.run_brillouin_test(1e-9)
        
        # Generate report
        report = self.experiment.generate_test_report(results)
        
        # Should return formatted string report
        assert isinstance(report, str)
        assert len(report) > 500  # Should be substantial report
        
        # Should contain key information
        assert "BRILLOUIN TRACER TEST REPORT" in report
        assert "Validation Status" in report
        assert "Energy Budget" in report
        assert "Sensing Performance" in report
    
    def test_generate_test_report_failed_validation(self):
        """Test report generation for failed validation."""
        # Create results with failed validation
        results = {
            'tracer_system': FiberOpticBrillouinTracer(BrillouinScatteringParameters(), 100.0),
            'propagation_results': {
                'power_profile': np.array([1e-6, 5e-7, 2e-7]),
                'brillouin_spectrum': np.random.rand(1000),
                'sensing_data': {'temperature_profile': [300, 305, 310]}
            },
            'sensing_information': {
                'brillouin_frequency': 11.0e9,
                'temperature_estimate': 305.0,
                'strain_estimate': 1e-6
            },
            'validation_results': {
                'validation_passed': False,
                'energy_within_limits': False,
                'snr_adequate': False
            },
            'energy_budget': {
                'input_energy': 1e-8,  # Excessive
                'total_loss': 5e-9
            }
        }
        
        report = self.experiment.generate_test_report(results)
        
        # Should indicate failures
        assert "FAILED" in report or "UNSAFE" in report
        assert "exceeded" in report.lower() or "insufficient" in report.lower()


class TestComprehensiveBrillouinTests:
    """Test the comprehensive test function."""
    
    def test_run_comprehensive_brillouin_tests(self):
        """Test comprehensive Brillouin tests execution."""
        results = run_comprehensive_brillouin_tests()
        
        # Should return comprehensive test results
        assert isinstance(results, dict)
        
        # Should include multiple test scenarios
        assert len(results) > 3  # Should have several test cases
        
        # Check for expected test categories
        expected_categories = ['basic_operation', 'sensitivity_test', 'range_test']
        found_categories = [key for key in results.keys() if any(cat in key for cat in expected_categories)]
        assert len(found_categories) > 0
        
        # Each test should have proper structure
        for test_name, test_result in results.items():
            if isinstance(test_result, dict):
                assert 'test_status' in test_result or 'validation_passed' in test_result or len(test_result) > 0
    
    def test_run_comprehensive_brillouin_tests_consistency(self):
        """Test that comprehensive tests produce consistent results."""
        # Run tests twice
        results1 = run_comprehensive_brillouin_tests()
        results2 = run_comprehensive_brillouin_tests()
        
        # Should produce consistent results (same test structure)
        assert set(results1.keys()) == set(results2.keys())
        
        # Numerical results should be similar (allowing for randomness in test conditions)
        for key in results1.keys():
            assert type(results1[key]) == type(results2[key])


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling throughout the module."""
    
    def test_brillouin_parameters_extreme_values(self):
        """Test Brillouin parameters with extreme but valid values."""
        # Very high refractive index
        params_high_n = BrillouinScatteringParameters(refractive_index=2.0)
        assert params_high_n.refractive_index == 2.0
        
        # Very low wavelength (but still reasonable)
        params_short_wave = BrillouinScatteringParameters(wavelength=1.0e-6)
        assert params_short_wave.wavelength == 1.0e-6
        
        # Very high density
        params_high_density = BrillouinScatteringParameters(density=5000.0)
        assert params_high_density.density == 5000.0
    
    def test_fiber_tracer_very_short_fiber(self):
        """Test fiber tracer with very short fiber length."""
        params = BrillouinScatteringParameters()
        short_fiber = FiberOpticBrillouinTracer(params, 0.1)  # 10 cm fiber
        
        assert short_fiber.fiber_length == 0.1
        
        # Should still be able to perform basic calculations
        freq_shift = short_fiber.brillouin_frequency_shift(300.0, 0.0)
        assert np.isfinite(freq_shift)
        assert freq_shift > 0
    
    def test_fiber_tracer_very_long_fiber(self):
        """Test fiber tracer with very long fiber length."""
        params = BrillouinScatteringParameters()
        long_fiber = FiberOpticBrillouinTracer(params, 100000.0)  # 100 km fiber
        
        assert long_fiber.fiber_length == 100000.0
        
        # Should handle long fiber without issues
        coupling = long_fiber.brillouin_power_coupling(1e-6, 1e-9, 1000.0)
        assert np.isfinite(coupling)
        assert coupling >= 0
    
    def test_propagation_simulation_extreme_conditions(self):
        """Test propagation simulation under extreme conditions."""
        params = BrillouinScatteringParameters()
        tracer = FiberOpticBrillouinTracer(params, 100.0)
        
        fiber_positions = np.linspace(0, 100.0, 50)
        
        # Extreme temperature variation
        extreme_environment = {
            'temperature': np.linspace(200.0, 400.0, 50),  # Large temperature gradient
            'strain': np.linspace(-1e-3, 1e-3, 50),  # Large strain variation
            'pressure': np.ones(50) * 101325.0
        }
        
        results = tracer.propagation_simulation(1e-9, fiber_positions, extreme_environment)
        
        # Should handle extreme conditions without crashing
        assert 'power_profile' in results
        assert np.all(np.isfinite(results['power_profile']))
        assert np.all(results['power_profile'] >= 0)
    
    def test_sensing_information_extraction_edge_cases(self):
        """Test sensing information extraction with edge cases."""
        params = BrillouinScatteringParameters()
        tracer = FiberOpticBrillouinTracer(params, 100.0)
        
        # Very narrow frequency range
        narrow_freq = np.linspace(10.99e9, 11.01e9, 100)  # Only 20 MHz range
        narrow_spectrum = np.exp(-((narrow_freq - 11.0e9) / 5e6)**2)
        
        fiber_positions = np.linspace(0, 100.0, 10)
        
        info = tracer.extract_sensing_information(narrow_spectrum, narrow_freq, fiber_positions)
        
        # Should handle narrow spectrum
        assert np.isfinite(info['brillouin_frequency'])
        assert np.isfinite(info['temperature_estimate'])
        
        # Very flat spectrum (no clear peak)
        flat_spectrum = np.ones_like(narrow_freq) + np.random.normal(0, 0.01, len(narrow_freq))
        
        info_flat = tracer.extract_sensing_information(flat_spectrum, narrow_freq, fiber_positions)
        
        # Should handle flat spectrum gracefully
        assert np.isfinite(info_flat['brillouin_frequency'])
        # Temperature estimate might be less reliable but should be finite
        assert np.isfinite(info_flat['temperature_estimate'])
    
    def test_validation_with_missing_data(self):
        """Test validation with incomplete data."""
        params = BrillouinScatteringParameters()
        tracer = FiberOpticBrillouinTracer(params, 100.0)
        
        # Minimal test data
        minimal_data = {
            'input_energy': 1e-9,
            'brillouin_frequency': 11.0e9
        }
        
        # Should handle missing fields gracefully
        try:
            validation = tracer.validate_tracer_operation(minimal_data)
            # If it succeeds, should return reasonable results
            assert isinstance(validation, dict)
        except KeyError:
            # If it raises KeyError, that's also acceptable behavior
            pass
    
    def test_zero_energy_propagation(self):
        """Test propagation simulation with zero input energy."""
        params = BrillouinScatteringParameters()
        tracer = FiberOpticBrillouinTracer(params, 50.0)
        
        fiber_positions = np.linspace(0, 50.0, 25)
        environment = {
            'temperature': np.ones(25) * 300.0,
            'strain': np.zeros(25),
            'pressure': np.ones(25) * 101325.0
        }
        
        results = tracer.propagation_simulation(0.0, fiber_positions, environment)
        
        # Should handle zero energy input
        power_profile = results['power_profile']
        assert np.all(power_profile == 0.0)  # All powers should be zero
    
    def test_negative_energy_handling(self):
        """Test handling of negative energy inputs."""
        params = BrillouinScatteringParameters()
        tracer = FiberOpticBrillouinTracer(params, 50.0)
        
        # Should either reject negative energy or handle it gracefully
        try:
            coupling = tracer.brillouin_power_coupling(-1e-6, 1e-9, 10.0)
            # If it allows negative energy, result should be reasonable
            assert np.isfinite(coupling)
        except (ValueError, AssertionError):
            # If it rejects negative energy, that's also acceptable
            pass


if __name__ == "__main__":
    pytest.main([__file__])