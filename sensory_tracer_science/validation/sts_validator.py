"""
Sensory Tracer Science (STS) - Validation Protocol Implementation

This module implements the fail-safe triple audit validation protocol for STS systems.
Any system that fails any of the three audits is immediately deemed invalid.

The three audits are:
1. Energy Audit: Verify energy conservation within 1 femtojoule tolerance
2. Information Balance: Verify information conservation within 1% tolerance  
3. Causality Check: Verify signal speed ≤ medium speed (zero tolerance)
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
import math
from ..core.sts_constants import ValidationTolerances, STSLimits, C_VACUUM


@dataclass
class ValidationResult:
    """
    Result of a validation audit with pass/fail status and detailed metrics.
    """
    audit_type: str
    passed: bool
    measured_value: float
    expected_value: float
    tolerance: float
    error_magnitude: float
    error_message: Optional[str] = None


class EnergyAuditor:
    """
    Implements the energy conservation audit for STS systems.
    
    Validates: E_in = E_out + E_dissipated within 1 femtojoule tolerance
    """
    
    def __init__(self):
        self.tolerance = ValidationTolerances.ENERGY_AUDIT_TOLERANCE
    
    def energy_audit(self, E_in: float, E_out: float, E_dissipated: float) -> ValidationResult:
        """
        Perform energy conservation audit.
        
        Args:
            E_in: Total energy input to system (J)
            E_out: Total energy output from system (J)  
            E_dissipated: Energy dissipated as heat/noise (J)
            
        Returns:
            ValidationResult with audit outcome
        """
        # Validate inputs are physical
        if E_in < 0 or E_out < 0 or E_dissipated < 0:
            return ValidationResult(
                audit_type="ENERGY_AUDIT",
                passed=False,
                measured_value=E_in,
                expected_value=E_out + E_dissipated,
                tolerance=self.tolerance,
                error_magnitude=float('inf'),
                error_message="Negative energy values are unphysical"
            )
        
        # Calculate energy balance error
        total_output = E_out + E_dissipated
        energy_error = abs(E_in - total_output)
        relative_error = energy_error / E_in if E_in > 0 else float('inf')
        
        # Check if error is within tolerance
        max_allowed_error = self.tolerance * E_in
        passed = energy_error < max_allowed_error
        
        return ValidationResult(
            audit_type="ENERGY_AUDIT",
            passed=passed,
            measured_value=E_in,
            expected_value=total_output,
            tolerance=self.tolerance,
            error_magnitude=relative_error,
            error_message=None if passed else f"Energy not conserved: error {energy_error:.2e} J exceeds tolerance {max_allowed_error:.2e} J"
        )
    
    def continuous_energy_audit(self, energy_trace: np.ndarray, 
                               dissipation_trace: np.ndarray,
                               source_trace: np.ndarray,
                               dt: float) -> ValidationResult:
        """
        Perform energy audit on time-series data using energy continuity equation.
        
        Args:
            energy_trace: Time series of total system energy (J)
            dissipation_trace: Time series of dissipation rates (W)
            source_trace: Time series of source power (W)
            dt: Time step (s)
            
        Returns:
            ValidationResult for time-integrated energy balance
        """
        # Integrate power over time to get energy
        total_dissipated = np.trapz(dissipation_trace, dx=dt)
        total_sourced = np.trapz(source_trace, dx=dt)
        
        # Energy change should equal net energy flow
        initial_energy = energy_trace[0]
        final_energy = energy_trace[-1]
        energy_change = final_energy - initial_energy
        
        expected_change = total_sourced - total_dissipated
        
        # Perform audit on integrated quantities
        return self.energy_audit(
            E_in=initial_energy + total_sourced,
            E_out=final_energy,
            E_dissipated=total_dissipated
        )


class InformationAuditor:
    """
    Implements the information balance audit for STS systems.
    
    Validates: I_injected = I_detected + I_lost within 1% tolerance
    """
    
    def __init__(self):
        self.tolerance = ValidationTolerances.INFORMATION_BALANCE_TOLERANCE
    
    def information_balance(self, I_injected: float, I_detected: float, I_lost: float) -> ValidationResult:
        """
        Perform information conservation audit.
        
        Args:
            I_injected: Information injected into system (bits)
            I_detected: Information successfully detected (bits)
            I_lost: Information lost to noise/irreversible processes (bits)
            
        Returns:
            ValidationResult with audit outcome
        """
        # Validate inputs are physical
        if I_injected < 0 or I_detected < 0 or I_lost < 0:
            return ValidationResult(
                audit_type="INFORMATION_BALANCE",
                passed=False,
                measured_value=I_injected,
                expected_value=I_detected + I_lost,
                tolerance=self.tolerance,
                error_magnitude=float('inf'),
                error_message="Negative information values are unphysical"
            )
        
        # Information conservation: injected = detected + lost
        total_accounted = I_detected + I_lost
        info_error = abs(I_injected - total_accounted)
        relative_error = info_error / I_injected if I_injected > 0 else float('inf')
        
        # Check if error is within tolerance
        max_allowed_error = self.tolerance * I_injected
        passed = info_error < max_allowed_error
        
        return ValidationResult(
            audit_type="INFORMATION_BALANCE", 
            passed=passed,
            measured_value=I_injected,
            expected_value=total_accounted,
            tolerance=self.tolerance,
            error_magnitude=relative_error,
            error_message=None if passed else f"Information not conserved: error {info_error:.2e} bits exceeds tolerance {max_allowed_error:.2e} bits"
        )
    
    def shannon_information_content(self, signal: np.ndarray, noise_floor: float) -> float:
        """
        Calculate Shannon information content of a signal.
        
        Args:
            signal: Signal amplitude array
            noise_floor: Noise floor level
            
        Returns:
            Information content in bits
        """
        # Signal-to-noise ratio based information capacity
        signal_power = np.mean(np.abs(signal)**2)
        snr = signal_power / (noise_floor**2) if noise_floor > 0 else float('inf')
        
        # Shannon-Hartley theorem: C = log₂(1 + SNR)
        if snr <= 0:
            return 0.0
        return math.log2(1 + snr)
    
    def mutual_information(self, input_signal: np.ndarray, output_signal: np.ndarray) -> float:
        """
        Estimate mutual information between input and output signals.
        
        Args:
            input_signal: Input signal array
            output_signal: Output signal array
            
        Returns:
            Mutual information in bits
        """
        # Simple correlation-based estimate (placeholder for more sophisticated methods)
        correlation = np.corrcoef(input_signal.flatten(), output_signal.flatten())[0,1]
        correlation = np.clip(abs(correlation), 0, 0.999)  # Avoid log(0)
        
        # Convert correlation to mutual information estimate
        return -0.5 * math.log2(1 - correlation**2)


class CausalityAuditor:
    """
    Implements the causality check for STS systems.
    
    Validates: signal_speed ≤ medium_speed with zero tolerance
    """
    
    def __init__(self):
        self.tolerance = ValidationTolerances.CAUSALITY_TOLERANCE  # Zero tolerance
    
    def causality_check(self, signal_speed: float, medium_speed: float) -> ValidationResult:
        """
        Perform causality audit - check signal speed against medium speed limit.
        
        Args:
            signal_speed: Measured signal propagation speed (m/s)
            medium_speed: Maximum allowed speed in medium (m/s)
            
        Returns:
            ValidationResult with audit outcome
        """
        # Validate inputs are physical
        if signal_speed < 0 or medium_speed < 0:
            return ValidationResult(
                audit_type="CAUSALITY_CHECK",
                passed=False,
                measured_value=signal_speed,
                expected_value=medium_speed,
                tolerance=self.tolerance,
                error_magnitude=float('inf'),
                error_message="Negative speeds are unphysical"
            )
        
        # Check causality: signal speed must not exceed medium speed
        speed_violation = signal_speed - medium_speed
        passed = signal_speed <= medium_speed
        
        return ValidationResult(
            audit_type="CAUSALITY_CHECK",
            passed=passed,
            measured_value=signal_speed,
            expected_value=medium_speed,
            tolerance=self.tolerance,
            error_magnitude=speed_violation / medium_speed if medium_speed > 0 else float('inf'),
            error_message=None if passed else f"Causality violated: signal speed {signal_speed:.2e} m/s exceeds medium limit {medium_speed:.2e} m/s"
        )
    
    def time_of_flight_check(self, distance: float, time_delay: float, 
                           refractive_index: float = 1.0) -> ValidationResult:
        """
        Check causality based on time-of-flight measurements.
        
        Args:
            distance: Propagation distance (m)
            time_delay: Measured time delay (s)
            refractive_index: Medium refractive index
            
        Returns:
            ValidationResult for causality check
        """
        # Calculate signal speed from time-of-flight
        if time_delay <= 0:
            return ValidationResult(
                audit_type="CAUSALITY_CHECK",
                passed=False,
                measured_value=float('inf'),
                expected_value=STSLimits.max_speed_in_medium(refractive_index),
                tolerance=self.tolerance,
                error_magnitude=float('inf'),
                error_message="Non-positive time delay is unphysical"
            )
        
        signal_speed = distance / time_delay
        medium_speed = STSLimits.max_speed_in_medium(refractive_index)
        
        return self.causality_check(signal_speed, medium_speed)


class STSValidator:
    """
    Main STS validation system implementing the fail-safe triple audit protocol.
    
    Any failure in any audit immediately invalidates the entire system.
    """
    
    def __init__(self):
        """Initialize all audit subsystems."""
        self.energy_auditor = EnergyAuditor()
        self.information_auditor = InformationAuditor()
        self.causality_auditor = CausalityAuditor()
    
    def full_validation(self, system_data: Dict[str, Any]) -> Dict[str, ValidationResult]:
        """
        Perform complete STS validation protocol - all three audits.
        
        Args:
            system_data: Dictionary containing all required measurements:
                - Energy data: 'E_in', 'E_out', 'E_dissipated'
                - Information data: 'I_injected', 'I_detected', 'I_lost'  
                - Causality data: 'signal_speed', 'medium_speed'
                
        Returns:
            Dictionary of ValidationResult objects for each audit
        """
        results = {}
        
        # Audit 1: Energy Conservation
        try:
            results['energy_audit'] = self.energy_auditor.energy_audit(
                E_in=system_data['E_in'],
                E_out=system_data['E_out'], 
                E_dissipated=system_data['E_dissipated']
            )
        except KeyError as e:
            results['energy_audit'] = ValidationResult(
                audit_type="ENERGY_AUDIT",
                passed=False,
                measured_value=0.0,
                expected_value=0.0,
                tolerance=0.0,
                error_magnitude=float('inf'),
                error_message=f"Missing required energy data: {e}"
            )
        
        # Audit 2: Information Balance
        try:
            results['information_balance'] = self.information_auditor.information_balance(
                I_injected=system_data['I_injected'],
                I_detected=system_data['I_detected'],
                I_lost=system_data['I_lost']
            )
        except KeyError as e:
            results['information_balance'] = ValidationResult(
                audit_type="INFORMATION_BALANCE",
                passed=False,
                measured_value=0.0,
                expected_value=0.0,
                tolerance=0.0,
                error_magnitude=float('inf'),
                error_message=f"Missing required information data: {e}"
            )
        
        # Audit 3: Causality Check
        try:
            results['causality_check'] = self.causality_auditor.causality_check(
                signal_speed=system_data['signal_speed'],
                medium_speed=system_data['medium_speed']
            )
        except KeyError as e:
            results['causality_check'] = ValidationResult(
                audit_type="CAUSALITY_CHECK",
                passed=False,
                measured_value=0.0,
                expected_value=0.0,
                tolerance=0.0,
                error_magnitude=float('inf'),
                error_message=f"Missing required causality data: {e}"
            )
        
        return results
    
    def system_status(self, validation_results: Dict[str, ValidationResult]) -> Tuple[bool, str]:
        """
        Determine overall system validity based on all audit results.
        
        Args:
            validation_results: Dictionary of ValidationResult objects
            
        Returns:
            (is_valid, status_message)
        """
        all_passed = all(result.passed for result in validation_results.values())
        
        if all_passed:
            return True, "SYSTEM VALID: All audits passed"
        else:
            failed_audits = [name for name, result in validation_results.items() if not result.passed]
            failure_messages = [f"{name}: {result.error_message}" 
                              for name, result in validation_results.items() 
                              if not result.passed and result.error_message]
            
            status_message = f"SYSTEM INVALID: Failed audits: {', '.join(failed_audits)}\n"
            status_message += "\n".join(failure_messages)
            
            return False, status_message
    
    def generate_validation_report(self, system_data: Dict[str, Any]) -> str:
        """
        Generate comprehensive validation report for STS system.
        
        Args:
            system_data: System measurement data
            
        Returns:
            Formatted validation report string
        """
        validation_results = self.full_validation(system_data)
        is_valid, status_message = self.system_status(validation_results)
        
        report = "=" * 70 + "\n"
        report += "SENSORY TRACER SCIENCE (STS) VALIDATION REPORT\n"
        report += "=" * 70 + "\n\n"
        
        # Overall status
        report += f"OVERALL STATUS: {'✅ VALID' if is_valid else '❌ INVALID'}\n"
        report += f"STATUS MESSAGE: {status_message}\n\n"
        
        # Detailed audit results
        for audit_name, result in validation_results.items():
            report += f"{audit_name.upper().replace('_', ' ')}:\n"
            report += f"  Result: {'✅ PASS' if result.passed else '❌ FAIL'}\n"
            report += f"  Measured: {result.measured_value:.6e}\n"
            report += f"  Expected: {result.expected_value:.6e}\n"
            report += f"  Tolerance: {result.tolerance:.6e}\n"
            report += f"  Error: {result.error_magnitude:.6e}\n"
            if result.error_message:
                report += f"  Message: {result.error_message}\n"
            report += "\n"
        
        # System parameters used
        report += "SYSTEM PARAMETERS:\n"
        for key, value in system_data.items():
            if isinstance(value, (int, float)):
                report += f"  {key}: {value:.6e}\n"
            else:
                report += f"  {key}: {value}\n"
        
        report += "\n" + "=" * 70
        
        return report


# ============================================================================
# VALIDATION TESTING AND EXAMPLES
# ============================================================================

def create_test_system_data(valid: bool = True) -> Dict[str, Any]:
    """
    Create test system data for validation testing.
    
    Args:
        valid: Whether to create valid (True) or invalid (False) test data
        
    Returns:
        Dictionary of test system parameters
    """
    if valid:
        # Valid system that should pass all audits
        return {
            'E_in': 1e-9,      # 1 nJ input
            'E_out': 0.99e-9,   # 0.99 nJ output (1% loss)
            'E_dissipated': 0.01e-9,  # 0.01 nJ dissipated
            'I_injected': 1000.0,     # 1000 bits injected
            'I_detected': 995.0,      # 995 bits detected (0.5% loss)
            'I_lost': 5.0,            # 5 bits lost
            'signal_speed': 2.05e8,   # Speed in silica fiber (n=1.46)
            'medium_speed': 2.05e8,   # Maximum speed in silica
        }
    else:
        # Invalid system that should fail audits
        return {
            'E_in': 1e-9,      # 1 nJ input
            'E_out': 1.1e-9,   # 1.1 nJ output (violates energy conservation!)
            'E_dissipated': 0.01e-9,  # 0.01 nJ dissipated
            'I_injected': 1000.0,     # 1000 bits injected  
            'I_detected': 900.0,      # 900 bits detected (15% loss - too high!)
            'I_lost': 50.0,           # 50 bits lost
            'signal_speed': 3.5e8,    # Faster than light!
            'medium_speed': 2.05e8,   # Maximum speed in silica
        }


def run_validation_tests() -> Dict[str, Any]:
    """
    Run comprehensive validation tests on the STS validation system.
    
    Returns:
        Dictionary with test results
    """
    validator = STSValidator()
    results = {}
    
    # Test 1: Valid system should pass
    valid_data = create_test_system_data(valid=True)
    valid_results = validator.full_validation(valid_data)
    valid_status, valid_message = validator.system_status(valid_results)
    results['valid_system_test'] = {
        'passed': valid_status,
        'message': valid_message,
        'individual_results': {k: v.passed for k, v in valid_results.items()}
    }
    
    # Test 2: Invalid system should fail
    invalid_data = create_test_system_data(valid=False)
    invalid_results = validator.full_validation(invalid_data)
    invalid_status, invalid_message = validator.system_status(invalid_results)
    results['invalid_system_test'] = {
        'passed': not invalid_status,  # Should fail, so passing test means it failed
        'message': invalid_message,
        'individual_results': {k: v.passed for k, v in invalid_results.items()}
    }
    
    # Test 3: Individual auditor tests
    results['energy_auditor_test'] = validator.energy_auditor.energy_audit(1.0, 0.99, 0.01).passed
    results['info_auditor_test'] = validator.information_auditor.information_balance(100.0, 99.0, 1.0).passed
    results['causality_auditor_test'] = validator.causality_auditor.causality_check(2e8, 3e8).passed
    
    # Test 4: Causality violation detection
    causality_violation = validator.causality_auditor.causality_check(4e8, 3e8)
    results['causality_violation_test'] = not causality_violation.passed  # Should fail
    
    results['overall_validator_status'] = 'PASSED' if all(
        isinstance(v, bool) and v for v in results.values() if isinstance(v, bool)
    ) else 'FAILED'
    
    return results


if __name__ == "__main__":
    # Run validation tests when module is executed directly
    test_results = run_validation_tests()
    print("STS Validator Test Results:")
    for key, value in test_results.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for subkey, subvalue in value.items():
                print(f"    {subkey}: {subvalue}")
        else:
            print(f"  {key}: {value}")
    
    # Generate example validation reports
    print("\n" + "="*50)
    print("EXAMPLE VALIDATION REPORTS")
    print("="*50)
    
    validator = STSValidator()
    
    # Valid system report
    print("\n1. VALID SYSTEM:")
    valid_data = create_test_system_data(valid=True)
    valid_report = validator.generate_validation_report(valid_data)
    print(valid_report)
    
    # Invalid system report
    print("\n2. INVALID SYSTEM:")
    invalid_data = create_test_system_data(valid=False)
    invalid_report = validator.generate_validation_report(invalid_data)
    print(invalid_report)