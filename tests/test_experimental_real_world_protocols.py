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
        
        # The power-density warning threshold fires before the hard cutoff.
        assert protocol.alert_thresholds["power_density"] < protocol.automatic_safety_cutoff
        
        # Training hours should be reasonable
        assert 0 < protocol.required_training_hours <= 200  # Up to 5 weeks
        
        # Daily exposure should be reasonable
        assert 0 < protocol.maximum_exposure_per_day <= 24  # Up to 24 hours


class TestRealWorldProtocolManager:
    """Test the real-world protocol manager against the shipped API."""

    def setup_method(self):
        """Set up test fixtures."""
        self.experiment_id = "test_protocol_001"
        self.manager = RealWorldProtocolManager(
            experiment_id=self.experiment_id,
            protocol_version="1.0.0",
            regulatory_approval="FDA_TEST_001",
        )

    def test_manager_initialization(self):
        """Test protocol manager initialization."""
        assert self.manager.experiment_id == self.experiment_id
        assert self.manager.protocol_version == "1.0.0"
        assert self.manager.regulatory_approval == "FDA_TEST_001"
        assert isinstance(self.manager.parameters, ExperimentalParameters)
        assert isinstance(self.manager.safety, SafetyProtocol)

        # Initial state
        assert self.manager.experiment_active is False
        assert self.manager.safety_status == "SAFE"
        assert self.manager.experiment_data == []
        assert self.manager.safety_log == []
        assert self.manager.measurement_count == 0
        assert self.manager.last_calibration is None

    def test_validate_experimental_conditions_structure(self):
        """validate_experimental_conditions returns the documented checks."""
        result = self.manager.validate_experimental_conditions()

        for key in (
            "temperature_safe",
            "pressure_safe",
            "humidity_safe",
            "power_density_safe",
            "concentration_safe",
            "equipment_calibrated",
            "personnel_certified",
            "regulatory_approved",
        ):
            assert key in result
            assert isinstance(result[key], bool)

        # Regulatory approval was supplied at construction.
        assert result["regulatory_approved"] is True
        # Equipment is not calibrated until calibration runs.
        assert result["equipment_calibrated"] is False

    def test_validate_without_regulatory_approval(self):
        """Without a regulatory approval the corresponding check is False."""
        manager = RealWorldProtocolManager(experiment_id="no_approval")
        result = manager.validate_experimental_conditions()
        assert result["regulatory_approved"] is False

    def test_perform_system_calibration(self):
        """perform_system_calibration returns precision/offset values."""
        result = self.manager.perform_system_calibration()

        for key in (
            "power_offset",
            "power_precision",
            "concentration_offset",
            "concentration_precision",
            "timing_precision",
            "temperature_precision",
            "pressure_precision",
            "humidity_precision",
        ):
            assert key in result
            assert isinstance(result[key], float)

        # Calibration timestamp is recorded.
        assert self.manager.last_calibration is not None

    def test_calibration_marks_equipment_calibrated(self):
        """Calibration flips the equipment_calibrated validation check."""
        before = self.manager.validate_experimental_conditions()
        assert before["equipment_calibrated"] is False

        self.manager.perform_system_calibration()

        after = self.manager.validate_experimental_conditions()
        assert after["equipment_calibrated"] is True

    def test_biocompatible_protocol_requires_validation(self):
        """Biocompatible protocol refuses to run on uncalibrated equipment."""
        with pytest.raises(RuntimeError):
            self.manager.run_biocompatible_protocol(
                tissue_type="neural", duration=30.0
            )

    def test_biocompatible_protocol_rejects_unknown_tissue(self):
        """An unsupported tissue type raises ValueError after validation."""
        # Calibrate so the condition validation passes.
        self.manager.perform_system_calibration()
        with pytest.raises(ValueError):
            self.manager.run_biocompatible_protocol(
                tissue_type="bone", duration=30.0
            )

    def test_brillouin_protocol_rejects_unknown_fiber(self):
        """An unsupported fiber type raises ValueError before execution."""
        with pytest.raises(ValueError):
            self.manager.run_brillouin_protocol(
                fiber_type="unobtainium", measurement_range=100.0
            )

    def test_generate_protocol_report_is_string(self):
        """generate_protocol_report returns a human-readable report string."""
        report = self.manager.generate_protocol_report()

        assert isinstance(report, str)
        assert self.experiment_id in report
        assert "PROTOCOL EXECUTION REPORT" in report
        assert self.manager.protocol_version in report
        assert self.manager.parameters.iso_standard in report


class TestSafetyProtocolIntegration:
    """Test consistency between safety protocol and experimental parameters."""

    def setup_method(self):
        """Set up safety integration fixtures."""
        self.safety_protocol = SafetyProtocol()
        self.experimental_params = ExperimentalParameters()
        self.manager = RealWorldProtocolManager(experiment_id="safety_integration_001")

    def test_safety_parameter_consistency(self):
        """Emergency/alert thresholds sit below the experimental limits."""
        # Emergency cutoff should be at/below the experimental power limit.
        assert (
            self.safety_protocol.automatic_safety_cutoff
            <= self.experimental_params.max_power_density
        )

        # Alert threshold should be below the experimental power limit.
        assert (
            self.safety_protocol.alert_thresholds["power_density"]
            < self.experimental_params.max_power_density
        )

        # Temperature alert threshold should be near the environmental range.
        temp_min, temp_max = self.experimental_params.temperature_range
        alert_temp = self.safety_protocol.alert_thresholds["temperature"]
        assert temp_min <= alert_temp <= temp_max + 10  # safety margin

    def test_manager_uses_default_safety_and_parameters(self):
        """The manager wires up default safety and experimental parameters."""
        assert isinstance(self.manager.safety, SafetyProtocol)
        assert isinstance(self.manager.parameters, ExperimentalParameters)
        assert self.manager.safety.emergency_shutdown_enabled is True
        assert self.manager.parameters.fda_compliant is True
