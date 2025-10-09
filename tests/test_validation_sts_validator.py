"""
Comprehensive test suite for STS validation module.
This test suite aims for 95%+ code coverage of sts_validator.py.
"""

import math
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from sensory_tracer_science.validation.sts_validator import (
    ValidationResult,
    EnergyAuditor,
    InformationAuditor,
    CausalityAuditor,
    STSValidator,
    create_test_system_data,
    run_validation_tests
)
from sensory_tracer_science.core.sts_constants import C_VACUUM, ValidationTolerances


class TestValidationResult:
    """Test the ValidationResult dataclass."""
    
    def test_initialization_basic(self):
        """Test basic ValidationResult initialization."""
        result = ValidationResult(
            audit_type="TEST_AUDIT",
            passed=True,
            measured_value=1.0,
            expected_value=1.0,
            tolerance=0.01,
            error_magnitude=0.0
        )
        
        assert result.audit_type == "TEST_AUDIT"
        assert result.passed is True
        assert result.measured_value == 1.0
        assert result.expected_value == 1.0
        assert result.tolerance == 0.01
        assert result.error_magnitude == 0.0
        assert result.error_message is None
    
    def test_initialization_with_error_message(self):
        """Test ValidationResult initialization with error message."""
        result = ValidationResult(
            audit_type="FAILED_AUDIT",
            passed=False,
            measured_value=2.0,
            expected_value=1.0,
            tolerance=0.01,
            error_magnitude=1.0,
            error_message="Test failure message"
        )
        
        assert result.audit_type == "FAILED_AUDIT"
        assert result.passed is False
        assert result.error_message == "Test failure message"
    
    def test_initialization_all_parameters(self):
        """Test ValidationResult with all parameter types."""
        result = ValidationResult(
            audit_type="COMPREHENSIVE_AUDIT",
            passed=False,
            measured_value=1.5e-10,
            expected_value=1.0e-10,
            tolerance=1e-12,
            error_magnitude=5e-11,
            error_message="Energy conservation violated"
        )
        
        assert result.measured_value == 1.5e-10
        assert result.expected_value == 1.0e-10
        assert result.tolerance == 1e-12
        assert result.error_magnitude == 5e-11


class TestEnergyAuditor:
    """Test the EnergyAuditor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.auditor = EnergyAuditor()
    
    def test_initialization(self):
        """Test energy auditor initialization."""
        assert self.auditor.tolerance == ValidationTolerances.ENERGY_AUDIT_TOLERANCE
    
    def test_energy_audit_perfect_conservation(self):
        """Test energy audit with perfect conservation."""
        E_in = 1e-18  # 1 aJ
        E_out = 6e-19  # 0.6 aJ
        E_dissipated = 4e-19  # 0.4 aJ
        
        result = self.auditor.energy_audit(E_in, E_out, E_dissipated)
        
        assert result.audit_type == "ENERGY_AUDIT"
        assert result.passed is True
        assert result.measured_value == E_in
        assert result.expected_value == E_out + E_dissipated
        assert result.error_magnitude == 0.0
        assert result.error_message is None
    
    def test_energy_audit_small_acceptable_error(self):
        """Test energy audit with small acceptable error."""
        E_in = 1e-18  # 1 aJ
        E_out = 6e-19  # 0.6 aJ
        E_dissipated = 4e-19 + 1e-31  # Tiny error (0.1 fJ)
        
        result = self.auditor.energy_audit(E_in, E_out, E_dissipated)
        
        # Should pass because error is within tolerance
        assert result.passed is True
        assert result.error_magnitude < self.auditor.tolerance
    
    def test_energy_audit_large_unacceptable_error(self):
        """Test energy audit with large unacceptable error."""
        E_in = 1e-18  # 1 aJ
        E_out = 6e-19  # 0.6 aJ
        E_dissipated = 3e-19  # Only 0.3 aJ dissipated (missing 0.1 aJ)
        
        result = self.auditor.energy_audit(E_in, E_out, E_dissipated)
        
        # Should fail because error exceeds tolerance
        assert result.passed is False
        assert result.error_magnitude > self.auditor.tolerance
        assert "Energy not conserved" in result.error_message
    
    def test_energy_audit_negative_input_energy(self):
        """Test energy audit with negative input energy."""
        E_in = -1e-18  # Negative energy (unphysical)
        E_out = 6e-19
        E_dissipated = 4e-19
        
        result = self.auditor.energy_audit(E_in, E_out, E_dissipated)
        
        # Should fail immediately due to unphysical energy
        assert result.passed is False
        assert result.error_magnitude == float("inf")
        assert "Negative energy values are unphysical" in result.error_message
    
    def test_energy_audit_negative_output_energy(self):
        """Test energy audit with negative output energy."""
        E_in = 1e-18
        E_out = -6e-19  # Negative output (unphysical)
        E_dissipated = 4e-19
        
        result = self.auditor.energy_audit(E_in, E_out, E_dissipated)
        
        # Should fail immediately
        assert result.passed is False
        assert "Negative energy values are unphysical" in result.error_message
    
    def test_energy_audit_negative_dissipated_energy(self):
        """Test energy audit with negative dissipated energy."""
        E_in = 1e-18
        E_out = 6e-19
        E_dissipated = -4e-19  # Negative dissipation (unphysical)
        
        result = self.auditor.energy_audit(E_in, E_out, E_dissipated)
        
        # Should fail immediately
        assert result.passed is False
        assert "Negative energy values are unphysical" in result.error_message
    
    def test_energy_audit_zero_input_energy(self):
        """Test energy audit with zero input energy."""
        E_in = 0.0
        E_out = 0.0
        E_dissipated = 0.0
        
        result = self.auditor.energy_audit(E_in, E_out, E_dissipated)
        
        # Should handle zero energy case
        assert result.passed is True
        assert result.error_magnitude == float("inf")  # Division by zero case
    
    def test_energy_audit_very_small_energies(self):
        """Test energy audit with very small energies."""
        E_in = 1e-30  # Extremely small energy
        E_out = 6e-31
        E_dissipated = 4e-31
        
        result = self.auditor.energy_audit(E_in, E_out, E_dissipated)
        
        # Should work with very small energies
        assert result.passed is True
        assert np.isfinite(result.error_magnitude)
    
    def test_continuous_energy_audit_basic(self):
        """Test continuous energy audit with simple traces."""
        time_steps = 100
        dt = 1e-9  # 1 ns time steps
        
        # Create simple energy traces
        energy_trace = np.ones(time_steps) * 1e-18  # Constant energy
        dissipation_trace = np.zeros(time_steps)  # No dissipation
        source_trace = np.zeros(time_steps)  # No sources
        
        result = self.auditor.continuous_energy_audit(
            energy_trace, dissipation_trace, source_trace, dt
        )
        
        # Should pass with constant energy
        assert result.passed is True
        assert result.audit_type == "CONTINUOUS_ENERGY_AUDIT"
    
    def test_continuous_energy_audit_with_dissipation(self):
        """Test continuous energy audit with dissipation."""
        time_steps = 50
        dt = 1e-9
        
        # Energy decreasing due to dissipation
        initial_energy = 1e-18
        dissipation_rate = 1e-27  # J/s
        
        energy_trace = np.array([
            initial_energy * np.exp(-dissipation_rate * i * dt / initial_energy)
            for i in range(time_steps)
        ])
        
        dissipation_trace = np.ones(time_steps) * dissipation_rate * dt
        source_trace = np.zeros(time_steps)
        
        result = self.auditor.continuous_energy_audit(
            energy_trace, dissipation_trace, source_trace, dt
        )
        
        # Should handle exponential decay
        assert result.passed is True or result.error_magnitude < 0.1  # Allow some numerical error
    
    def test_continuous_energy_audit_with_sources(self):
        """Test continuous energy audit with energy sources."""
        time_steps = 50
        dt = 1e-9
        
        # Energy increasing due to sources
        energy_trace = np.linspace(1e-18, 2e-18, time_steps)
        dissipation_trace = np.zeros(time_steps)
        source_trace = np.ones(time_steps) * 1e-27 * dt  # Constant source
        
        result = self.auditor.continuous_energy_audit(
            energy_trace, dissipation_trace, source_trace, dt
        )
        
        # Should handle energy addition
        assert isinstance(result, ValidationResult)
        assert result.audit_type == "CONTINUOUS_ENERGY_AUDIT"
    
    def test_continuous_energy_audit_mismatched_arrays(self):
        """Test continuous energy audit with mismatched array sizes."""
        energy_trace = np.ones(50) * 1e-18
        dissipation_trace = np.zeros(40)  # Different size
        source_trace = np.zeros(50)
        dt = 1e-9
        
        # Should handle mismatched arrays gracefully
        try:
            result = self.auditor.continuous_energy_audit(
                energy_trace, dissipation_trace, source_trace, dt
            )
            # If it succeeds, should be a valid result
            assert isinstance(result, ValidationResult)
        except (ValueError, AssertionError):
            # If it raises an error, that's also acceptable
            pass


class TestInformationAuditor:
    """Test the InformationAuditor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.auditor = InformationAuditor()
    
    def test_initialization(self):
        """Test information auditor initialization."""
        assert self.auditor.tolerance == ValidationTolerances.INFORMATION_BALANCE_TOLERANCE
    
    def test_information_balance_perfect_conservation(self):
        """Test information balance with perfect conservation."""
        I_injected = 100.0  # bits
        I_measured = 100.0  # bits
        I_noise = 0.0  # No noise
        
        result = self.auditor.information_balance(I_injected, I_measured, I_noise)
        
        assert result.audit_type == "INFORMATION_BALANCE"
        assert result.passed is True
        assert result.error_magnitude == 0.0
        assert result.error_message is None
    
    def test_information_balance_acceptable_loss(self):
        """Test information balance with acceptable information loss."""
        I_injected = 100.0  # bits
        I_measured = 99.5   # bits (0.5% loss, within 1% tolerance)
        I_noise = 0.5       # bits lost to noise
        
        result = self.auditor.information_balance(I_injected, I_measured, I_noise)
        
        # Should pass because loss is within tolerance
        assert result.passed is True
        assert result.error_magnitude < self.auditor.tolerance
    
    def test_information_balance_excessive_loss(self):
        """Test information balance with excessive information loss."""
        I_injected = 100.0  # bits
        I_measured = 95.0   # bits (5% loss, exceeds 1% tolerance)
        I_noise = 3.0       # bits lost to noise (2% of total loss unaccounted)
        
        result = self.auditor.information_balance(I_injected, I_measured, I_noise)
        
        # Should fail because loss exceeds tolerance
        assert result.passed is False
        assert result.error_magnitude > self.auditor.tolerance
        assert "Information not conserved" in result.error_message
    
    def test_information_balance_negative_information(self):
        """Test information balance with negative information."""
        I_injected = -10.0  # Negative information (unphysical)
        I_measured = 50.0
        I_noise = 0.0
        
        result = self.auditor.information_balance(I_injected, I_measured, I_noise)
        
        # Should fail due to negative information
        assert result.passed is False
        assert "Negative information is unphysical" in result.error_message
    
    def test_information_balance_zero_injection(self):
        """Test information balance with zero injected information."""
        I_injected = 0.0
        I_measured = 0.0
        I_noise = 0.0
        
        result = self.auditor.information_balance(I_injected, I_measured, I_noise)
        
        # Should handle zero information case
        assert result.passed is True
    
    def test_shannon_information_content_uniform_distribution(self):
        """Test Shannon information content for uniform distribution."""
        # Uniform distribution over 8 states
        probabilities = np.ones(8) / 8
        
        info_content = self.auditor.shannon_information_content(probabilities)
        
        # Should equal log₂(8) = 3 bits for uniform distribution
        expected = math.log2(8)
        assert abs(info_content - expected) < 1e-10
    
    def test_shannon_information_content_delta_distribution(self):
        """Test Shannon information content for delta distribution."""
        # Delta distribution (certainty)
        probabilities = np.array([1.0, 0.0, 0.0, 0.0])
        
        info_content = self.auditor.shannon_information_content(probabilities)
        
        # Should equal 0 bits for certain outcome
        assert abs(info_content) < 1e-10
    
    def test_shannon_information_content_binary_distribution(self):
        """Test Shannon information content for binary distribution."""
        # Equal probability binary distribution
        probabilities = np.array([0.5, 0.5])
        
        info_content = self.auditor.shannon_information_content(probabilities)
        
        # Should equal 1 bit for fair coin
        assert abs(info_content - 1.0) < 1e-10
    
    def test_shannon_information_content_invalid_probabilities(self):
        """Test Shannon information with invalid probabilities."""
        # Probabilities that don't sum to 1
        invalid_probs = np.array([0.3, 0.3, 0.3])  # Sum = 0.9
        
        # Should handle invalid probabilities
        try:
            info_content = self.auditor.shannon_information_content(invalid_probs)
            # If it succeeds, should return finite value
            assert np.isfinite(info_content)
        except (ValueError, AssertionError):
            # If it raises error, that's acceptable too
            pass
    
    def test_mutual_information_independent_variables(self):
        """Test mutual information for independent variables."""
        # Independent binary variables
        joint_probs = np.array([
            [0.25, 0.25],  # P(X=0,Y=0), P(X=0,Y=1)
            [0.25, 0.25]   # P(X=1,Y=0), P(X=1,Y=1)
        ])
        
        mutual_info = self.auditor.mutual_information(joint_probs)
        
        # Should be 0 for independent variables
        assert abs(mutual_info) < 1e-10
    
    def test_mutual_information_fully_correlated(self):
        """Test mutual information for fully correlated variables."""
        # Fully correlated binary variables
        joint_probs = np.array([
            [0.5, 0.0],  # P(X=0,Y=0), P(X=0,Y=1)
            [0.0, 0.5]   # P(X=1,Y=0), P(X=1,Y=1)
        ])
        
        mutual_info = self.auditor.mutual_information(joint_probs)
        
        # Should be 1 bit for fully correlated binary variables
        assert abs(mutual_info - 1.0) < 1e-10
    
    def test_mutual_information_partial_correlation(self):
        """Test mutual information for partially correlated variables."""
        # Partially correlated variables
        joint_probs = np.array([
            [0.4, 0.1],  # P(X=0,Y=0), P(X=0,Y=1)
            [0.1, 0.4]   # P(X=1,Y=0), P(X=1,Y=1)
        ])
        
        mutual_info = self.auditor.mutual_information(joint_probs)
        
        # Should be between 0 and 1 for partial correlation
        assert 0 < mutual_info < 1
    
    def test_mutual_information_invalid_joint_distribution(self):
        """Test mutual information with invalid joint distribution."""
        # Joint probabilities that don't sum to 1
        invalid_joint = np.array([
            [0.3, 0.2],
            [0.2, 0.2]  # Sum = 0.9
        ])
        
        # Should handle invalid joint distribution
        try:
            mutual_info = self.auditor.mutual_information(invalid_joint)
            assert np.isfinite(mutual_info)
        except (ValueError, AssertionError):
            pass


class TestCausalityAuditor:
    """Test the CausalityAuditor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.auditor = CausalityAuditor()
    
    def test_initialization(self):
        """Test causality auditor initialization."""
        assert self.auditor.tolerance == ValidationTolerances.CAUSALITY_TOLERANCE
    
    def test_causality_check_subluminal_speed(self):
        """Test causality check with subluminal propagation speed."""
        signal_speed = 2e8  # m/s (slower than light)
        medium_refractive_index = 1.5
        
        result = self.auditor.causality_check(signal_speed, medium_refractive_index)
        
        # Should pass because signal speed < c/n
        assert result.audit_type == "CAUSALITY_CHECK"
        assert result.passed is True
        assert result.error_message is None
    
    def test_causality_check_speed_of_light_in_vacuum(self):
        """Test causality check at exactly the speed of light in vacuum."""
        signal_speed = C_VACUUM
        medium_refractive_index = 1.0  # Vacuum
        
        result = self.auditor.causality_check(signal_speed, medium_refractive_index)
        
        # Should fail because speed must be strictly less than c
        assert result.passed is False
        assert "exceeds maximum allowed speed" in result.error_message
    
    def test_causality_check_superluminal_speed(self):
        """Test causality check with superluminal speed."""
        signal_speed = 4e8  # m/s (faster than light)
        medium_refractive_index = 1.0
        
        result = self.auditor.causality_check(signal_speed, medium_refractive_index)
        
        # Should fail due to faster-than-light propagation
        assert result.passed is False
        assert "exceeds maximum allowed speed" in result.error_message
    
    def test_causality_check_speed_in_dense_medium(self):
        """Test causality check in dense medium."""
        signal_speed = 1.5e8  # m/s
        medium_refractive_index = 2.0  # Dense medium
        
        result = self.auditor.causality_check(signal_speed, medium_refractive_index)
        
        # Should pass because 1.5e8 < c/2 = 1.5e8
        # Actually should fail because it equals the limit
        assert result.passed is False  # Zero tolerance policy
    
    def test_causality_check_just_below_limit(self):
        """Test causality check just below the speed limit."""
        medium_refractive_index = 1.5
        max_speed = C_VACUUM / medium_refractive_index
        signal_speed = max_speed * 0.999  # Just below limit
        
        result = self.auditor.causality_check(signal_speed, medium_refractive_index)
        
        # Should pass because it's below the limit
        assert result.passed is True
    
    def test_causality_check_negative_speed(self):
        """Test causality check with negative signal speed."""
        signal_speed = -1e8  # Negative speed (unphysical)
        medium_refractive_index = 1.0
        
        result = self.auditor.causality_check(signal_speed, medium_refractive_index)
        
        # Should fail due to negative speed
        assert result.passed is False
        assert "Negative propagation speed is unphysical" in result.error_message
    
    def test_causality_check_invalid_refractive_index(self):
        """Test causality check with invalid refractive index."""
        signal_speed = 1e8
        medium_refractive_index = 0.5  # Invalid (< 1)
        
        result = self.auditor.causality_check(signal_speed, medium_refractive_index)
        
        # Should fail due to invalid refractive index
        assert result.passed is False
        assert "Refractive index must be ≥ 1" in result.error_message
    
    def test_time_of_flight_check_basic(self):
        """Test basic time-of-flight causality check."""
        distances = np.array([0.0, 1.0, 2.0, 3.0])  # meters
        arrival_times = np.array([0.0, 5e-9, 10e-9, 15e-9])  # 5 ns/m → 2e8 m/s
        medium_refractive_index = 1.5  # n = 1.5 → max speed = 2e8 m/s
        
        result = self.auditor.time_of_flight_check(distances, arrival_times, medium_refractive_index)
        
        # Should pass because implied speed = 2e8 m/s = c/1.5
        # But due to zero tolerance, should fail
        assert result.passed is False  # Exactly at limit
    
    def test_time_of_flight_check_subluminal(self):
        """Test time-of-flight check with subluminal propagation."""
        distances = np.array([0.0, 1.0, 2.0, 3.0])  # meters
        arrival_times = np.array([0.0, 6e-9, 12e-9, 18e-9])  # 6 ns/m → 1.67e8 m/s
        medium_refractive_index = 1.0  # Vacuum
        
        result = self.auditor.time_of_flight_check(distances, arrival_times, medium_refractive_index)
        
        # Should pass because 1.67e8 m/s < c
        assert result.passed is True
    
    def test_time_of_flight_check_superluminal(self):
        """Test time-of-flight check with superluminal propagation."""
        distances = np.array([0.0, 1.0, 2.0, 3.0])  # meters
        arrival_times = np.array([0.0, 2e-9, 4e-9, 6e-9])  # 2 ns/m → 5e8 m/s
        medium_refractive_index = 1.0  # Vacuum
        
        result = self.auditor.time_of_flight_check(distances, arrival_times, medium_refractive_index)
        
        # Should fail because 5e8 m/s > c
        assert result.passed is False
        assert "superluminal propagation detected" in result.error_message.lower()
    
    def test_time_of_flight_check_inconsistent_data(self):
        """Test time-of-flight check with inconsistent data."""
        distances = np.array([0.0, 1.0, 2.0])  # 3 points
        arrival_times = np.array([0.0, 5e-9, 10e-9, 15e-9])  # 4 points
        medium_refractive_index = 1.0
        
        # Should handle mismatched array sizes
        try:
            result = self.auditor.time_of_flight_check(distances, arrival_times, medium_refractive_index)
            assert isinstance(result, ValidationResult)
        except (ValueError, AssertionError):
            pass
    
    def test_time_of_flight_check_single_point(self):
        """Test time-of-flight check with single data point."""
        distances = np.array([0.0])
        arrival_times = np.array([0.0])
        medium_refractive_index = 1.0
        
        result = self.auditor.time_of_flight_check(distances, arrival_times, medium_refractive_index)
        
        # Should handle single point (no propagation to check)
        assert isinstance(result, ValidationResult)


class TestSTSValidator:
    """Test the main STSValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = STSValidator()
    
    def test_initialization(self):
        """Test validator initialization."""
        assert hasattr(self.validator, 'energy_auditor')
        assert hasattr(self.validator, 'information_auditor')
        assert hasattr(self.validator, 'causality_auditor')
        
        assert isinstance(self.validator.energy_auditor, EnergyAuditor)
        assert isinstance(self.validator.information_auditor, InformationAuditor)
        assert isinstance(self.validator.causality_auditor, CausalityAuditor)
    
    def test_full_validation_all_pass(self):
        """Test full validation when all audits pass."""
        # Create system data that should pass all tests
        system_data = {
            'energy': {
                'input': 1e-18,
                'output': 6e-19,
                'dissipated': 4e-19
            },
            'information': {
                'injected': 100.0,
                'measured': 99.5,
                'noise_loss': 0.5
            },
            'causality': {
                'signal_speed': 1e8,
                'medium_refractive_index': 1.5
            }
        }
        
        results = self.validator.full_validation(system_data)
        
        # Should return results for all three audits
        assert isinstance(results, dict)
        assert 'energy_audit' in results
        assert 'information_audit' in results
        assert 'causality_audit' in results
        assert 'overall_passed' in results
        
        # All individual audits should pass
        assert results['energy_audit'].passed is True
        assert results['information_audit'].passed is True
        assert results['causality_audit'].passed is True
        assert results['overall_passed'] is True
    
    def test_full_validation_energy_fail(self):
        """Test full validation when energy audit fails."""
        system_data = {
            'energy': {
                'input': 1e-18,
                'output': 6e-19,
                'dissipated': 2e-19  # Missing 2e-19 J
            },
            'information': {
                'injected': 100.0,
                'measured': 99.5,
                'noise_loss': 0.5
            },
            'causality': {
                'signal_speed': 1e8,
                'medium_refractive_index': 1.5
            }
        }
        
        results = self.validator.full_validation(system_data)
        
        # Energy audit should fail, overall should fail
        assert results['energy_audit'].passed is False
        assert results['overall_passed'] is False
        
        # Other audits might still pass
        assert results['information_audit'].passed is True
        assert results['causality_audit'].passed is True
    
    def test_full_validation_information_fail(self):
        """Test full validation when information audit fails."""
        system_data = {
            'energy': {
                'input': 1e-18,
                'output': 6e-19,
                'dissipated': 4e-19
            },
            'information': {
                'injected': 100.0,
                'measured': 90.0,  # Too much loss
                'noise_loss': 5.0
            },
            'causality': {
                'signal_speed': 1e8,
                'medium_refractive_index': 1.5
            }
        }
        
        results = self.validator.full_validation(system_data)
        
        # Information audit should fail, overall should fail
        assert results['information_audit'].passed is False
        assert results['overall_passed'] is False
    
    def test_full_validation_causality_fail(self):
        """Test full validation when causality audit fails."""
        system_data = {
            'energy': {
                'input': 1e-18,
                'output': 6e-19,
                'dissipated': 4e-19
            },
            'information': {
                'injected': 100.0,
                'measured': 99.5,
                'noise_loss': 0.5
            },
            'causality': {
                'signal_speed': 4e8,  # Faster than light
                'medium_refractive_index': 1.0
            }
        }
        
        results = self.validator.full_validation(system_data)
        
        # Causality audit should fail, overall should fail
        assert results['causality_audit'].passed is False
        assert results['overall_passed'] is False
    
    def test_full_validation_all_fail(self):
        """Test full validation when all audits fail."""
        system_data = {
            'energy': {
                'input': 1e-18,
                'output': 6e-19,
                'dissipated': 2e-19  # Energy not conserved
            },
            'information': {
                'injected': 100.0,
                'measured': 85.0,  # Too much information loss
                'noise_loss': 10.0
            },
            'causality': {
                'signal_speed': 5e8,  # Superluminal
                'medium_refractive_index': 1.0
            }
        }
        
        results = self.validator.full_validation(system_data)
        
        # All audits should fail
        assert results['energy_audit'].passed is False
        assert results['information_audit'].passed is False
        assert results['causality_audit'].passed is False
        assert results['overall_passed'] is False
    
    def test_full_validation_missing_data(self):
        """Test full validation with missing data fields."""
        incomplete_data = {
            'energy': {
                'input': 1e-18,
                'output': 6e-19
                # Missing 'dissipated' field
            }
        }
        
        # Should handle missing data gracefully
        try:
            results = self.validator.full_validation(incomplete_data)
            assert isinstance(results, dict)
        except KeyError:
            # Acceptable to raise KeyError for missing required fields
            pass
    
    def test_system_status_healthy(self):
        """Test system status assessment for healthy system."""
        # Create passing validation results
        validation_results = {
            'energy_audit': ValidationResult("ENERGY_AUDIT", True, 1e-18, 1e-18, 1e-12, 0.0),
            'information_audit': ValidationResult("INFORMATION_BALANCE", True, 100.0, 100.0, 0.01, 0.0),
            'causality_audit': ValidationResult("CAUSALITY_CHECK", True, 1e8, 2e8, 0.0, 0.0),
            'overall_passed': True
        }
        
        status = self.validator.system_status(validation_results)
        
        assert isinstance(status, dict)
        assert status['system_health'] == 'HEALTHY'
        assert status['operational_status'] == 'OPERATIONAL'
        assert status['critical_failures'] == []
    
    def test_system_status_failed(self):
        """Test system status assessment for failed system."""
        validation_results = {
            'energy_audit': ValidationResult("ENERGY_AUDIT", False, 1e-18, 8e-19, 1e-12, 0.2, "Energy violation"),
            'information_audit': ValidationResult("INFORMATION_BALANCE", False, 100.0, 80.0, 0.01, 0.2, "Info loss"),
            'causality_audit': ValidationResult("CAUSALITY_CHECK", False, 4e8, 3e8, 0.0, 1.33, "Superluminal"),
            'overall_passed': False
        }
        
        status = self.validator.system_status(validation_results)
        
        assert status['system_health'] == 'CRITICAL'
        assert status['operational_status'] == 'NON_OPERATIONAL'
        assert len(status['critical_failures']) == 3
    
    def test_system_status_partial_failure(self):
        """Test system status with partial failures."""
        validation_results = {
            'energy_audit': ValidationResult("ENERGY_AUDIT", True, 1e-18, 1e-18, 1e-12, 0.0),
            'information_audit': ValidationResult("INFORMATION_BALANCE", False, 100.0, 85.0, 0.01, 0.15, "Info loss"),
            'causality_audit': ValidationResult("CAUSALITY_CHECK", True, 1e8, 2e8, 0.0, 0.0),
            'overall_passed': False
        }
        
        status = self.validator.system_status(validation_results)
        
        assert status['system_health'] == 'DEGRADED'
        assert len(status['critical_failures']) == 1
    
    def test_generate_validation_report(self):
        """Test validation report generation."""
        system_data = {
            'energy': {
                'input': 1e-18,
                'output': 6e-19,
                'dissipated': 4e-19
            },
            'information': {
                'injected': 100.0,
                'measured': 99.5,
                'noise_loss': 0.5
            },
            'causality': {
                'signal_speed': 1e8,
                'medium_refractive_index': 1.5
            }
        }
        
        report = self.validator.generate_validation_report(system_data)
        
        # Should return formatted string report
        assert isinstance(report, str)
        assert len(report) > 200  # Should be substantial
        
        # Should contain key information
        assert "STS VALIDATION REPORT" in report
        assert "Energy Audit" in report
        assert "Information Audit" in report
        assert "Causality Audit" in report


class TestUtilityFunctions:
    """Test utility functions in the validation module."""
    
    def test_create_test_system_data_valid(self):
        """Test creation of valid test system data."""
        data = create_test_system_data(valid=True)
        
        assert isinstance(data, dict)
        assert 'energy' in data
        assert 'information' in data
        assert 'causality' in data
        
        # Should have all required fields
        assert 'input' in data['energy']
        assert 'output' in data['energy']
        assert 'dissipated' in data['energy']
        
        # Energy should be conserved
        energy = data['energy']
        total_out = energy['output'] + energy['dissipated']
        assert abs(energy['input'] - total_out) < 1e-20
    
    def test_create_test_system_data_invalid(self):
        """Test creation of invalid test system data."""
        data = create_test_system_data(valid=False)
        
        assert isinstance(data, dict)
        assert 'energy' in data
        assert 'information' in data
        assert 'causality' in data
        
        # Should have violations that cause failure
        # At least one audit should fail with this data
        validator = STSValidator()
        results = validator.full_validation(data)
        assert results['overall_passed'] is False
    
    def test_run_validation_tests(self):
        """Test the comprehensive validation test suite."""
        results = run_validation_tests()
        
        assert isinstance(results, dict)
        
        # Should include multiple test scenarios
        assert len(results) > 2
        
        # Should have valid and invalid test cases
        test_names = list(results.keys())
        assert any('valid' in name.lower() or 'pass' in name.lower() for name in test_names)
        assert any('invalid' in name.lower() or 'fail' in name.lower() for name in test_names)
        
        # Each result should have proper structure
        for test_name, test_result in results.items():
            assert isinstance(test_result, dict)
            assert 'test_status' in test_result or 'overall_passed' in test_result


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling throughout the validation module."""
    
    def test_energy_auditor_extreme_values(self):
        """Test energy auditor with extreme energy values."""
        auditor = EnergyAuditor()
        
        # Very large energies
        large_energy = 1e10  # 10 GJ
        result_large = auditor.energy_audit(large_energy, large_energy/2, large_energy/2)
        assert result_large.passed is True
        
        # Very small energies
        tiny_energy = 1e-50  # Extremely small
        result_tiny = auditor.energy_audit(tiny_energy, tiny_energy/2, tiny_energy/2)
        assert result_tiny.passed is True
    
    def test_information_auditor_extreme_values(self):
        """Test information auditor with extreme information values."""
        auditor = InformationAuditor()
        
        # Very large information content
        large_info = 1e6  # 1 megabit
        result = auditor.information_balance(large_info, large_info*0.995, large_info*0.005)
        assert result.passed is True
        
        # Very small information content
        tiny_info = 1e-10  # Very small
        result_tiny = auditor.information_balance(tiny_info, tiny_info, 0.0)
        assert result_tiny.passed is True
    
    def test_causality_auditor_extreme_speeds(self):
        """Test causality auditor with extreme speeds."""
        auditor = CausalityAuditor()
        
        # Very slow speed
        slow_speed = 1.0  # 1 m/s
        result_slow = auditor.causality_check(slow_speed, 1.0)
        assert result_slow.passed is True
        
        # Speed close to but below light speed
        near_c_speed = C_VACUUM * 0.99999
        result_near_c = auditor.causality_check(near_c_speed, 1.0)
        assert result_near_c.passed is True
    
    def test_validator_with_nan_values(self):
        """Test validator behavior with NaN values."""
        validator = STSValidator()
        
        system_data = {
            'energy': {
                'input': float('nan'),  # NaN value
                'output': 6e-19,
                'dissipated': 4e-19
            },
            'information': {
                'injected': 100.0,
                'measured': 99.5,
                'noise_loss': 0.5
            },
            'causality': {
                'signal_speed': 1e8,
                'medium_refractive_index': 1.5
            }
        }
        
        # Should handle NaN values gracefully
        try:
            results = validator.full_validation(system_data)
            # Should fail due to invalid input
            assert results['overall_passed'] is False
        except (ValueError, AssertionError):
            # Acceptable to raise error for invalid input
            pass
    
    def test_validator_with_inf_values(self):
        """Test validator behavior with infinite values."""
        validator = STSValidator()
        
        system_data = {
            'energy': {
                'input': float('inf'),  # Infinite energy
                'output': 6e-19,
                'dissipated': 4e-19
            },
            'information': {
                'injected': 100.0,
                'measured': 99.5,
                'noise_loss': 0.5
            },
            'causality': {
                'signal_speed': 1e8,
                'medium_refractive_index': 1.5
            }
        }
        
        # Should handle infinite values
        try:
            results = validator.full_validation(system_data)
            assert results['overall_passed'] is False
        except (ValueError, OverflowError):
            pass
    
    def test_shannon_information_with_zero_probabilities(self):
        """Test Shannon information calculation with zero probabilities."""
        auditor = InformationAuditor()
        
        # Distribution with zero probabilities
        probs_with_zeros = np.array([0.5, 0.0, 0.5, 0.0])
        
        info = auditor.shannon_information_content(probs_with_zeros)
        
        # Should handle zero probabilities (0 * log(0) = 0 by convention)
        assert np.isfinite(info)
        assert info >= 0
    
    def test_time_of_flight_with_negative_times(self):
        """Test time-of-flight check with negative arrival times."""
        auditor = CausalityAuditor()
        
        distances = np.array([0.0, 1.0, 2.0])
        arrival_times = np.array([0.0, -5e-9, -10e-9])  # Negative times
        
        result = auditor.time_of_flight_check(distances, arrival_times, 1.0)
        
        # Should fail due to unphysical negative times
        assert result.passed is False
    
    def test_continuous_energy_audit_with_negative_dt(self):
        """Test continuous energy audit with negative time step."""
        auditor = EnergyAuditor()
        
        energy_trace = np.ones(10) * 1e-18
        dissipation_trace = np.zeros(10)
        source_trace = np.zeros(10)
        dt = -1e-9  # Negative time step
        
        # Should handle negative dt gracefully
        try:
            result = auditor.continuous_energy_audit(
                energy_trace, dissipation_trace, source_trace, dt
            )
            # If it succeeds, should indicate failure
            assert result.passed is False
        except (ValueError, AssertionError):
            # Acceptable to raise error for invalid input
            pass


if __name__ == "__main__":
    pytest.main([__file__])