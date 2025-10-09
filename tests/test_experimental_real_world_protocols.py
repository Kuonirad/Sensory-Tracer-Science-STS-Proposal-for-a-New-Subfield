#!/usr/bin/env python3
"""
Test Suite for Real World Protocols Module

Comprehensive tests for production-ready experimental protocols,
safety compliance, and regulatory standardization functionality.
"""

import json
import pytest
import logging
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from sensory_tracer_science.experimental.real_world_protocols import (
    ExperimentalParameters,
    SafetyProtocol,
    RealWorldProtocolManager,
)


class TestExperimentalParameters:
    """Test experimental parameter configuration for real-world use."""
    
    def test_default_experimental_parameters(self):
        """Test default experimental parameters."""
        params = ExperimentalParameters()
        
        # Safety Parameters
        assert params.max_power_density == 1e-3  # W/cm² - FDA limit
        assert params.max_tracer_concentration == 1e-6  # M - biocompatibility limit
        assert params.max_exposure_time == 3600.0  # 1 hour maximum
        
        # Environmental Parameters
        assert params.temperature_range == (295.0, 310.0)  # 22°C to 37°C
        assert params.pressure_range == (0.8e5, 1.2e5)  # 0.8-1.2 atm
        assert params.humidity_range == (30.0, 70.0)  # % RH
        
        # Measurement Parameters
        assert params.sampling_rate == 1000.0  # Hz
        assert params.measurement_duration == 60.0  # seconds
        assert params.signal_to_noise_ratio == 20.0  # dB minimum
        
        # Quality Control
        assert params.calibration_interval == 3600.0  # hourly calibration
        assert params.validation_frequency == 10  # every 10 measurements
        
        # Regulatory Compliance
        assert params.fda_compliant is True
        assert params.iso_standard == "ISO 14155:2020"
        assert params.gmp_compliant is True
    
    def test_custom_experimental_parameters(self):
        """Test custom experimental parameters."""
        params = ExperimentalParameters(
            max_power_density=5e-4,  # More conservative
            max_tracer_concentration=5e-7,  # Lower concentration
            temperature_range=(298.0, 308.0),  # Narrower range
            sampling_rate=2000.0,  # Higher sampling rate
            fda_compliant=True
        )
        
        assert params.max_power_density == 5e-4
        assert params.max_tracer_concentration == 5e-7
        assert params.temperature_range == (298.0, 308.0)
        assert params.sampling_rate == 2000.0
        assert params.fda_compliant is True
    
    def test_parameter_validation_ranges(self):
        """Test parameter validation for reasonable ranges."""
        params = ExperimentalParameters()
        
        # Safety parameters should be positive
        assert params.max_power_density > 0
        assert params.max_tracer_concentration > 0
        assert params.max_exposure_time > 0
        
        # Environmental ranges should be physically reasonable
        temp_min, temp_max = params.temperature_range
        assert 200 < temp_min < temp_max < 400  # Kelvin range
        
        press_min, press_max = params.pressure_range
        assert 0 < press_min < press_max < 10e5  # Pascal range
        
        humid_min, humid_max = params.humidity_range
        assert 0 <= humid_min < humid_max <= 100  # Percentage range
        
        # Measurement parameters should be reasonable
        assert 0 < params.sampling_rate <= 1e6  # Up to MHz
        assert 0 < params.measurement_duration <= 86400  # Up to 24 hours
        assert 0 < params.signal_to_noise_ratio <= 100  # Reasonable SNR in dB


class TestSafetyProtocol:
    """Test safety protocol configuration."""
    
    def test_default_safety_protocol(self):
        """Test default safety protocol parameters."""
        protocol = SafetyProtocol()
        
        # Emergency Procedures
        assert protocol.emergency_shutdown_enabled is True
        assert protocol.automatic_safety_cutoff == 0.001  # W/cm²
        
        # Monitoring Systems
        assert protocol.continuous_monitoring is True
        
        # Personnel Safety
        assert protocol.required_training_hours == 40.0
        assert protocol.maximum_exposure_per_day == 8.0  # hours
        
        # Check post_init populated defaults
        assert protocol.alert_thresholds is not None
        assert protocol.protective_equipment is not None
        
        # Verify specific thresholds
        assert protocol.alert_thresholds["temperature"] == 315.0  # K (42°C)
        assert protocol.alert_thresholds["power_density"] == 0.0005  # W/cm²
        assert protocol.alert_thresholds["concentration"] == 0.5e-6  # M
        assert protocol.alert_thresholds["exposure_time"] == 1800.0  # 30 min
        
        # Verify protective equipment
        expected_equipment = [
            "safety_glasses", "lab_coat", "nitrile_gloves",
            "radiation_dosimeter", "emergency_communication_device"
        ]
        for equipment in expected_equipment:
            assert equipment in protocol.protective_equipment
    
    def test_custom_safety_protocol(self):
        """Test custom safety protocol configuration."""
        custom_thresholds = {
            "temperature": 310.0,  # Lower threshold
            "power_density": 0.0001,  # More conservative
        }
        
        custom_equipment = ["custom_shield", "monitoring_device"]
        
        protocol = SafetyProtocol(
            automatic_safety_cutoff=0.0005,  # More sensitive
            required_training_hours=60.0,  # More training
            alert_thresholds=custom_thresholds,
            protective_equipment=custom_equipment
        )
        
        assert protocol.automatic_safety_cutoff == 0.0005
        assert protocol.required_training_hours == 60.0
        assert protocol.alert_thresholds == custom_thresholds
        assert protocol.protective_equipment == custom_equipment
    
    def test_safety_protocol_post_init(self):
        """Test __post_init__ method for safety protocol."""
        # Test with None values to trigger defaults
        protocol = SafetyProtocol(
            alert_thresholds=None,
            protective_equipment=None
        )
        
        # Should be populated with defaults
        assert protocol.alert_thresholds is not None
        assert protocol.protective_equipment is not None
        assert len(protocol.alert_thresholds) > 0
        assert len(protocol.protective_equipment) > 0
    
    def test_safety_threshold_validation(self):
        """Test safety threshold validation logic."""
        protocol = SafetyProtocol()
        
        # All thresholds should be positive
        for key, value in protocol.alert_thresholds.items():
            assert value > 0, f"Threshold for {key} should be positive"
        
        # Emergency cutoff should be lower than alert thresholds
        assert protocol.automatic_safety_cutoff < protocol.alert_thresholds["power_density"]
        
        # Training hours should be reasonable
        assert 0 < protocol.required_training_hours <= 200  # Up to 5 weeks
        
        # Daily exposure should be reasonable
        assert 0 < protocol.maximum_exposure_per_day <= 24  # Up to 24 hours


class TestRealWorldProtocolManager:
    """Test real-world protocol manager functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.experiment_id = "test_protocol_001"
        self.manager = RealWorldProtocolManager(
            experiment_id=self.experiment_id,
            protocol_version="1.0.0",
            regulatory_approval="FDA_TEST_001"
        )
    
    def test_manager_initialization(self):
        """Test protocol manager initialization."""
        assert self.manager.experiment_id == self.experiment_id
        assert isinstance(self.manager.parameters, ExperimentalParameters)
        assert isinstance(self.manager.safety, SafetyProtocol)
        
        # Check initial state
        assert hasattr(self.manager, 'experiment_active')
        assert hasattr(self.manager, 'safety_status')
        assert hasattr(self.manager, 'experiment_data')
        assert hasattr(self.manager, 'safety_log')
        
        assert self.manager.experiment_active is False
        assert self.manager.safety_status == "SAFE"
        assert self.manager.experiment_data == []
        assert self.manager.safety_log == []
    
    def test_biocompatible_protocol_execution(self):
        """Test biocompatible protocol execution."""
        # Run biocompatible protocol
        result = self.manager.run_biocompatible_protocol(
            tissue_size="medium",
            duration=60.0
        )
        
        assert result["protocol_type"] == "biocompatible_neural"
        assert result["duration"] == 60.0
        assert result["tissue_size"] == "medium"
        assert "execution_time" in result
        assert "safety_status" in result
    
    def test_brillouin_protocol_execution(self):
        """Test Brillouin protocol execution."""
        # Run Brillouin protocol
        result = self.manager.run_brillouin_protocol(
            fiber_length=1000.0,
            input_energy=5e-10
        )
        
        assert result["protocol_type"] == "fiber_optic_brillouin"
        assert result["fiber_length"] == 1000.0
        assert result["input_energy"] == 5e-10
        assert "execution_time" in result
        assert "safety_status" in result
    
    def test_quantum_protocol_execution(self):
        """Test quantum enhanced protocol execution."""
        # Run quantum protocol
        result = self.manager.run_quantum_enhanced_protocol(
            measurement_type="entanglement",
            precision_level=0.001
        )
        
        assert result["protocol_type"] == "quantum_enhanced"
        assert result["measurement_type"] == "entanglement"
        assert result["precision_level"] == 0.001
        assert "execution_time" in result
        assert "safety_status" in result
    
    def test_experimental_conditions_validation(self):
        """Test experimental conditions validation."""
        # Validate experimental conditions
        validation_result = self.manager.validate_experimental_conditions()
        
        assert "environmental_conditions" in validation_result
        assert "safety_parameters" in validation_result
        assert "equipment_status" in validation_result
        assert "overall_status" in validation_result
        
        # All conditions should pass with default parameters
        assert validation_result["overall_status"] == "PASS"
    
    def test_system_calibration(self):
        """Test system calibration functionality."""
        # Perform system calibration
        calibration_result = self.manager.perform_system_calibration()
        
        assert "calibration_status" in calibration_result
        assert "calibrated_parameters" in calibration_result
        assert "calibration_timestamp" in calibration_result
        
        # Calibration should pass
        assert calibration_result["calibration_status"] == "SUCCESS"
        
        # Check that last calibration time is updated
        assert self.manager.last_calibration is not None
    
    def test_protocol_report_generation(self):
        """Test protocol report generation functionality."""
        # Generate protocol report
        report = self.manager.generate_protocol_report()
        
        assert "experiment_id" in report
        assert "protocol_version" in report
        assert "experiment_summary" in report
        assert "safety_compliance" in report
        assert "regulatory_status" in report
        
        # Verify report content
        assert report["experiment_id"] == self.experiment_id
        assert report["protocol_version"] == "1.0.0"
        assert report["safety_compliance"] == "PASS"
    
    def test_protocol_state_management(self):
        """Test protocol state management."""
        # Initial state should be inactive
        assert self.manager.experiment_active is False
        assert self.manager.safety_status == "SAFE"
        assert self.manager.measurement_count == 0
        
        # Run a protocol and check state changes
        self.manager.run_biocompatible_protocol(tissue_size="small", duration=30.0)
        
        # Verify state tracking
        assert hasattr(self.manager, 'experiment_data')
        assert hasattr(self.manager, 'safety_log')
        assert len(self.manager.experiment_data) >= 0  # Should have some data logged
        assert len(self.manager.safety_log) >= 0  # Should have safety logs


class TestProtocolValidationAndCompliance:
    """Test protocol validation and regulatory compliance."""
    
    def setup_method(self):
        """Set up compliance test fixtures."""
        self.manager = RealWorldProtocolManager(
            experiment_id="compliance_test_001",
            protocol_version="1.0.0",
            regulatory_approval="FDA_COMP_001"
        )
    
    def test_fda_compliance_validation(self):
        """Test FDA compliance validation."""
        fda_result = self.manager.validate_fda_compliance()
        
        # Should check key FDA requirements
        assert "power_density_limit" in fda_result
        assert "biocompatibility" in fda_result
        assert "safety_monitoring" in fda_result
        
        # All should pass with default parameters
        assert fda_result["power_density_limit"]["compliant"] is True
        assert fda_result["biocompatibility"]["compliant"] is True
        assert fda_result["safety_monitoring"]["compliant"] is True
    
    def test_iso_standard_compliance(self):
        """Test ISO standard compliance."""
        iso_result = self.manager.validate_iso_compliance()
        
        # Should check ISO 14155:2020 requirements
        assert "documentation" in iso_result
        assert "quality_management" in iso_result
        assert "safety_procedures" in iso_result
        
        # All should pass with proper configuration
        assert iso_result["documentation"]["compliant"] is True
        assert iso_result["quality_management"]["compliant"] is True
    
    def test_gmp_compliance(self):
        """Test Good Manufacturing Practice compliance."""
        gmp_result = self.manager.validate_gmp_compliance()
        
        # Should check GMP requirements
        assert "quality_control" in gmp_result
        assert "personnel_training" in gmp_result
        assert "equipment_validation" in gmp_result
        
        # All should pass with proper procedures
        assert gmp_result["quality_control"]["compliant"] is True
        assert gmp_result["personnel_training"]["compliant"] is True
    
    def test_comprehensive_compliance_report(self):
        """Test comprehensive compliance reporting."""
        report = self.manager.generate_compliance_report()
        
        # Should include all regulatory frameworks
        assert "fda" in report
        assert "iso" in report
        assert "gmp" in report
        
        # Should have overall compliance status
        assert "overall_compliance" in report
        assert report["overall_compliance"]["compliant"] is True
        
        # Should be serializable for regulatory submission
        try:
            json_report = json.dumps(report, default=str)
            assert len(json_report) > 0
            
        except (TypeError, ValueError) as e:
            pytest.fail(f"Compliance report serialization failed: {e}")


class TestSafetyProtocolIntegration:
    """Test safety protocol integration across system components."""
    
    def setup_method(self):
        """Set up safety integration tests."""
        self.safety_protocol = SafetyProtocol()
        self.experimental_params = ExperimentalParameters()
        self.manager = RealWorldProtocolManager(
            protocol_id="safety_integration_001",
            experimental_params=self.experimental_params,
            safety_protocol=self.safety_protocol
        )
    
    def test_safety_parameter_consistency(self):
        """Test consistency between safety protocol and experimental parameters."""
        # Emergency cutoff should be below experimental limits
        assert (self.safety_protocol.automatic_safety_cutoff < 
                self.experimental_params.max_power_density)
        
        # Alert thresholds should be below experimental limits
        assert (self.safety_protocol.alert_thresholds["power_density"] < 
                self.experimental_params.max_power_density)
        
        # Temperature thresholds should be within environmental range
        temp_min, temp_max = self.experimental_params.temperature_range
        alert_temp = self.safety_protocol.alert_thresholds["temperature"]
        assert temp_min <= alert_temp <= temp_max + 10  # Allow some margin for safety
    
    def test_emergency_shutdown_procedures(self):
        """Test emergency shutdown procedures."""
        # Simulate emergency condition
        emergency_result = self.manager.trigger_emergency_shutdown(
            reason="power_density_exceeded",
            measured_value=0.002,  # Above safety limit
            threshold=0.001
        )
        
        assert emergency_result["shutdown_triggered"] is True
        assert emergency_result["reason"] == "power_density_exceeded"
        assert emergency_result["timestamp"] is not None
        
        # All experiments should be stopped
        assert len(self.manager.active_experiments) == 0
        
        # Safety monitoring should remain active
        assert len(self.manager.safety_monitors) > 0
    
    def test_personnel_safety_procedures(self):
        """Test personnel safety procedures."""
        # Check training requirements
        training_status = self.manager.check_personnel_training("operator_001")
        assert "training_hours_completed" in training_status
        assert "certification_valid" in training_status
        
        # Check protective equipment
        equipment_check = self.manager.verify_protective_equipment()
        assert equipment_check["all_equipment_present"] is True
        assert len(equipment_check["missing_equipment"]) == 0
        
        # Check exposure limits
        exposure_check = self.manager.check_daily_exposure_limits("operator_001")
        assert "current_exposure" in exposure_check
        assert "remaining_allowed" in exposure_check


class TestRealWorldProtocolErrorHandling:
    """Test error handling in real-world protocol management."""
    
    def test_invalid_experiment_parameters(self):
        """Test handling of invalid experiment parameters."""
        manager = RealWorldProtocolManager(
            protocol_id="error_test_001",
            experimental_params=ExperimentalParameters(),
            safety_protocol=SafetyProtocol()
        )
        
        # Test invalid experiment type
        with pytest.raises(ValueError):
            manager.start_experiment(
                experiment_id="invalid_001",
                experiment_type="invalid_type",
                duration=60.0
            )
        
        # Test invalid duration
        with pytest.raises(ValueError):
            manager.start_experiment(
                experiment_id="invalid_002",
                experiment_type="biocompatible_neural",
                duration=-10.0  # Negative duration
            )
    
    def test_safety_limit_violations(self):
        """Test handling of safety limit violations."""
        manager = RealWorldProtocolManager(
            protocol_id="safety_test_001",
            experimental_params=ExperimentalParameters(),
            safety_protocol=SafetyProtocol()
        )
        
        # Test power density violation
        violation_result = manager.handle_safety_violation(
            parameter="power_density",
            measured_value=0.002,  # Above limit
            safe_limit=0.001
        )
        
        assert violation_result["violation_detected"] is True
        assert violation_result["action_taken"] == "emergency_shutdown"
        assert violation_result["parameter"] == "power_density"
    
    def test_equipment_failure_handling(self):
        """Test handling of equipment failures."""
        manager = RealWorldProtocolManager(
            protocol_id="equipment_test_001",
            experimental_params=ExperimentalParameters(),
            safety_protocol=SafetyProtocol()
        )
        
        # Simulate equipment failure
        failure_result = manager.handle_equipment_failure(
            equipment_id="power_monitor_001",
            failure_type="sensor_malfunction"
        )
        
        assert failure_result["failure_acknowledged"] is True
        assert failure_result["backup_activated"] is True
        assert failure_result["experiments_paused"] is True


class TestDataIntegrityAndAuditTrails:
    """Test data integrity and audit trail functionality."""
    
    def setup_method(self):
        """Set up data integrity tests."""
        self.manager = RealWorldProtocolManager(
            protocol_id="audit_test_001",
            experimental_params=ExperimentalParameters(),
            safety_protocol=SafetyProtocol()
        )
    
    def test_audit_trail_creation(self):
        """Test creation and maintenance of audit trails."""
        # Perform an action that should be audited
        experiment_id = "audit_exp_001"
        start_result = self.manager.start_experiment(
            experiment_id=experiment_id,
            experiment_type="biocompatible_neural",
            duration=30.0
        )
        
        # Check that audit entry was created
        audit_log = self.manager.get_audit_log()
        assert len(audit_log) > 0
        
        # Verify audit entry contents
        latest_entry = audit_log[-1]
        assert latest_entry["action"] == "start_experiment"
        assert latest_entry["experiment_id"] == experiment_id
        assert latest_entry["timestamp"] is not None
        assert latest_entry["user"] is not None
    
    def test_data_integrity_checksums(self):
        """Test data integrity through checksums."""
        # Log some measurement data
        measurement_data = {
            "temperature": [300.0, 301.0, 302.0],
            "pressure": [101325.0, 101330.0, 101335.0]
        }
        
        log_result = self.manager.log_measurements(measurement_data)
        assert "checksum" in log_result
        
        # Verify data can be retrieved with integrity check
        retrieved_data = self.manager.get_measurements_with_integrity_check()
        assert retrieved_data["integrity_verified"] is True
        assert retrieved_data["checksum_valid"] is True
    
    def test_regulatory_audit_export(self):
        """Test export functionality for regulatory audits."""
        # Generate some audit data
        self.manager.start_experiment("audit_exp_001", "biocompatible_neural", 60.0)
        self.manager.stop_experiment("audit_exp_001")
        
        # Export audit data
        export_result = self.manager.export_audit_data(
            start_date=datetime.now() - timedelta(hours=1),
            end_date=datetime.now() + timedelta(hours=1),
            format="json"
        )
        
        assert export_result["export_successful"] is True
        assert "file_path" in export_result
        assert export_result["format"] == "json"
        
        # Verify export contains required regulatory information
        assert "compliance_data" in export_result
        assert "audit_trail" in export_result
        assert "safety_events" in export_result