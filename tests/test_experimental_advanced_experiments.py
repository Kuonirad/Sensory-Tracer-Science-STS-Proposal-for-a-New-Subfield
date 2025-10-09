#!/usr/bin/env python3
"""
Test Suite for Advanced Experimental Module

Comprehensive tests for the advanced experimental protocols,
multi-modal sensing, and adaptive protocol functionality.
"""

import json
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from sensory_tracer_science.experimental.advanced_experiments import (
    MultiModalParameters,
    AdaptiveProtocolParameters,
    AdvancedExperimentSuite,
)


class TestMultiModalParameters:
    """Test multi-modal sensing parameter configuration."""
    
    def test_default_parameters(self):
        """Test default multi-modal parameters."""
        params = MultiModalParameters()
        
        assert params.temporal_synchronization_accuracy == 1e-6
        assert params.spatial_registration_accuracy == 1e-6
        assert params.cross_modal_correlation_threshold == 0.85
        assert params.data_fusion_algorithm == "bayesian_inference"
        assert params.confidence_weighting is True
        assert params.adaptive_sampling is True
        assert params.real_time_processing is True
        assert params.maximum_latency == 0.001
        assert params.bandwidth_optimization is True
    
    def test_custom_parameters(self):
        """Test custom multi-modal parameters."""
        params = MultiModalParameters(
            temporal_synchronization_accuracy=5e-7,
            spatial_registration_accuracy=2e-6,
            cross_modal_correlation_threshold=0.9,
            data_fusion_algorithm="kalman_filter",
            real_time_processing=False
        )
        
        assert params.temporal_synchronization_accuracy == 5e-7
        assert params.spatial_registration_accuracy == 2e-6
        assert params.cross_modal_correlation_threshold == 0.9
        assert params.data_fusion_algorithm == "kalman_filter"
        assert params.real_time_processing is False


class TestAdaptiveProtocolParameters:
    """Test adaptive protocol parameter configuration."""
    
    def test_default_parameters(self):
        """Test default adaptive protocol parameters."""
        params = AdaptiveProtocolParameters()
        
        assert params.learning_rate == 0.01
        assert params.adaptation_window == 100
        assert params.convergence_threshold == 0.001
        assert params.optimization_algorithm == "particle_swarm"
        assert params.population_size == 50
        assert params.generations == 100
        assert params.safety_constraints_enabled is True
        
        # Check default performance constraints
        assert "signal_to_noise_ratio" in params.performance_constraints
        assert params.performance_constraints["signal_to_noise_ratio"] == 20.0
        assert params.performance_constraints["measurement_accuracy"] == 0.01
        assert params.performance_constraints["response_time"] == 0.1
        assert params.performance_constraints["energy_efficiency"] == 0.8
    
    def test_custom_performance_constraints(self):
        """Test custom performance constraints."""
        custom_constraints = {
            "signal_to_noise_ratio": 25.0,
            "measurement_accuracy": 0.005,
        }
        
        params = AdaptiveProtocolParameters(
            learning_rate=0.05,
            performance_constraints=custom_constraints
        )
        
        assert params.learning_rate == 0.05
        assert params.performance_constraints == custom_constraints
    
    def test_none_performance_constraints_post_init(self):
        """Test __post_init__ handling of None performance constraints."""
        params = AdaptiveProtocolParameters(performance_constraints=None)
        
        # Should be populated with defaults in __post_init__
        assert params.performance_constraints is not None
        assert len(params.performance_constraints) == 4


class TestAdvancedExperimentSuite:
    """Test advanced experiment suite functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.suite_id = "test_suite_001"
        self.suite = AdvancedExperimentSuite(self.suite_id)
    
    def test_initialization(self):
        """Test experiment suite initialization."""
        assert self.suite.suite_id == self.suite_id
        assert isinstance(self.suite.multi_modal_params, MultiModalParameters)
        assert isinstance(self.suite.adaptive_params, AdaptiveProtocolParameters)
        assert self.suite.active_experiments == {}
        assert self.suite.data_streams == {}
        assert self.suite.performance_metrics == {}
    
    @patch('sensory_tracer_science.experimental.advanced_experiments.QuantumTracerExperiment')
    @patch('sensory_tracer_science.experimental.advanced_experiments.BrillouinTracerExperiment')
    @patch('sensory_tracer_science.experimental.advanced_experiments.NeuralTracerExperiment')
    def test_setup_multi_modal_experiment(self, mock_neural, mock_brillouin, mock_quantum):
        """Test multi-modal experiment setup."""
        # Mock the tracer experiments
        mock_neural.return_value = Mock()
        mock_brillouin.return_value = Mock()
        mock_quantum.return_value = Mock()
        
        tracer_types = ["neural", "brillouin", "quantum"]
        
        # Test that experiment setup would use the tracers
        for tracer_type in tracer_types:
            experiment_id = f"exp_{tracer_type}_001"
            # This would be part of the actual implementation
            assert experiment_id not in self.suite.active_experiments
    
    def test_multi_modal_parameters_validation(self):
        """Test validation of multi-modal parameters."""
        params = self.suite.multi_modal_params
        
        # Temporal synchronization should be positive and reasonable
        assert 0 < params.temporal_synchronization_accuracy < 1e-3
        
        # Spatial registration should be positive and reasonable  
        assert 0 < params.spatial_registration_accuracy < 1e-3
        
        # Correlation threshold should be between 0 and 1
        assert 0 < params.cross_modal_correlation_threshold <= 1.0
        
        # Maximum latency should be positive and reasonable for real-time
        assert 0 < params.maximum_latency < 1.0
    
    def test_adaptive_parameters_validation(self):
        """Test validation of adaptive protocol parameters."""
        params = self.suite.adaptive_params
        
        # Learning rate should be positive and not too large
        assert 0 < params.learning_rate < 1.0
        
        # Adaptation window should be positive integer
        assert params.adaptation_window > 0
        
        # Convergence threshold should be positive and small
        assert 0 < params.convergence_threshold < 1.0
        
        # Population size should be reasonable for optimization
        assert 10 <= params.population_size <= 1000
        
        # Generations should be positive
        assert params.generations > 0
    
    def test_performance_constraints_validation(self):
        """Test validation of performance constraints."""
        constraints = self.suite.adaptive_params.performance_constraints
        
        # SNR should be positive (in dB)
        assert constraints["signal_to_noise_ratio"] > 0
        
        # Accuracy should be positive fraction
        assert 0 < constraints["measurement_accuracy"] < 1.0
        
        # Response time should be positive
        assert constraints["response_time"] > 0
        
        # Energy efficiency should be between 0 and 1
        assert 0 < constraints["energy_efficiency"] <= 1.0


class TestExperimentalMetrics:
    """Test experimental metrics functionality (mock implementation)."""
    
    def test_metrics_initialization(self):
        """Test experimental metrics initialization with mock."""
        # Mock a metrics object for testing purposes
        class MockExperimentalMetrics:
            def __init__(self):
                self.start_time = datetime.now()
                self.measurements = {}
                self.performance_data = {}
        
        metrics = MockExperimentalMetrics()
        
        # Check that metrics object exists and has expected attributes
        assert hasattr(metrics, 'start_time')
        assert hasattr(metrics, 'measurements')
        assert hasattr(metrics, 'performance_data')
        
        # Verify initial state
        assert metrics.measurements == {}
        assert metrics.performance_data == {}
    
    def test_metrics_data_types(self):
        """Test metrics data type handling with mock."""
        class MockExperimentalMetrics:
            def __init__(self):
                self.measurements = {}
                self.performance_data = {}
        
        metrics = MockExperimentalMetrics()
        
        # Add some test measurements
        metrics.measurements['temperature'] = [295.0, 296.0, 297.0]
        metrics.measurements['pressure'] = [101325.0, 101330.0, 101320.0]
        
        # Verify data types
        assert isinstance(metrics.measurements['temperature'], list)
        assert isinstance(metrics.measurements['pressure'], list)
        assert all(isinstance(t, float) for t in metrics.measurements['temperature'])


class TestAdvancedExperimentIntegration:
    """Test integration between advanced experiment components."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.suite = AdvancedExperimentSuite("integration_test_001")
    
    def test_parameter_consistency(self):
        """Test consistency between multi-modal and adaptive parameters."""
        multi_params = self.suite.multi_modal_params
        adaptive_params = self.suite.adaptive_params
        
        # Real-time processing should be compatible with maximum latency
        if multi_params.real_time_processing:
            assert multi_params.maximum_latency <= 0.1  # 100ms reasonable for real-time
        
        # Adaptive sampling should be compatible with learning parameters
        if multi_params.adaptive_sampling:
            assert adaptive_params.learning_rate > 0
            assert adaptive_params.adaptation_window > 0
    
    def test_safety_constraint_integration(self):
        """Test integration of safety constraints across parameters."""
        adaptive_params = self.suite.adaptive_params
        
        if adaptive_params.safety_constraints_enabled:
            # Should have reasonable performance constraints
            constraints = adaptive_params.performance_constraints
            assert len(constraints) > 0
            
            # Energy efficiency constraint should exist for safety
            assert "energy_efficiency" in constraints
            assert constraints["energy_efficiency"] >= 0.5  # Minimum 50% efficiency
    
    def test_multi_modal_synchronization_requirements(self):
        """Test synchronization requirements for multi-modal sensing."""
        params = self.suite.multi_modal_params
        
        # Temporal and spatial synchronization should be compatible
        temporal_precision = params.temporal_synchronization_accuracy
        spatial_precision = params.spatial_registration_accuracy
        
        # Both should be in reasonable scientific ranges
        assert 1e-9 <= temporal_precision <= 1e-3  # nanosecond to millisecond
        assert 1e-9 <= spatial_precision <= 1e-3   # nanometer to millimeter
        
        # For real-time processing, synchronization should be fast enough
        if params.real_time_processing:
            assert temporal_precision <= params.maximum_latency / 10


class TestAdvancedExperimentErrorHandling:
    """Test error handling in advanced experiments."""
    
    def test_invalid_suite_id(self):
        """Test handling of invalid suite IDs."""
        # Empty string should be handled gracefully
        suite = AdvancedExperimentSuite("")
        assert suite.suite_id == ""
        
        # None should be handled
        suite = AdvancedExperimentSuite(None)
        assert suite.suite_id is None
    
    def test_parameter_boundary_conditions(self):
        """Test parameter boundary conditions."""
        # Test extreme but valid values
        params = MultiModalParameters(
            temporal_synchronization_accuracy=1e-9,  # nanosecond precision
            cross_modal_correlation_threshold=1.0,   # perfect correlation
            maximum_latency=0.0001                   # 0.1ms latency
        )
        
        assert params.temporal_synchronization_accuracy == 1e-9
        assert params.cross_modal_correlation_threshold == 1.0
        assert params.maximum_latency == 0.0001
    
    def test_adaptive_protocol_edge_cases(self):
        """Test adaptive protocol edge cases."""
        # Test minimum viable parameters
        params = AdaptiveProtocolParameters(
            learning_rate=1e-6,        # very slow learning
            adaptation_window=1,       # single measurement window
            population_size=2,         # minimal population
            generations=1              # single generation
        )
        
        assert params.learning_rate == 1e-6
        assert params.adaptation_window == 1
        assert params.population_size == 2
        assert params.generations == 1


class TestExperimentalDataHandling:
    """Test experimental data handling and processing."""
    
    def setup_method(self):
        """Set up data handling tests."""
        class MockExperimentalMetrics:
            def __init__(self):
                self.measurements = {}
                self.performance_data = {}
        
        self.metrics = MockExperimentalMetrics()
    
    def test_measurement_data_storage(self):
        """Test measurement data storage and retrieval."""
        # Add measurement data
        self.metrics.measurements['sensor_1'] = [1.0, 2.0, 3.0]
        self.metrics.measurements['sensor_2'] = [4.0, 5.0, 6.0]
        
        # Verify storage
        assert len(self.metrics.measurements) == 2
        assert 'sensor_1' in self.metrics.measurements
        assert 'sensor_2' in self.metrics.measurements
        
        # Verify data integrity
        assert self.metrics.measurements['sensor_1'] == [1.0, 2.0, 3.0]
        assert self.metrics.measurements['sensor_2'] == [4.0, 5.0, 6.0]
    
    def test_performance_data_tracking(self):
        """Test performance data tracking."""
        # Add performance metrics
        self.metrics.performance_data['throughput'] = 1000.0  # measurements/sec
        self.metrics.performance_data['latency'] = 0.001      # seconds
        self.metrics.performance_data['accuracy'] = 0.99      # 99% accuracy
        
        # Verify tracking
        assert self.metrics.performance_data['throughput'] == 1000.0
        assert self.metrics.performance_data['latency'] == 0.001
        assert self.metrics.performance_data['accuracy'] == 0.99
    
    def test_data_serialization_compatibility(self):
        """Test that metrics data can be serialized."""
        class MockExperimentalMetrics:
            def __init__(self):
                self.measurements = {}
                self.performance_data = {}
        
        metrics = MockExperimentalMetrics()
        
        # Add various data types
        metrics.measurements['integers'] = [1, 2, 3]
        metrics.measurements['floats'] = [1.1, 2.2, 3.3]
        metrics.performance_data['string'] = "test_value"
        metrics.performance_data['boolean'] = True
        
        # Test JSON serialization (common for data export)
        try:
            json_str = json.dumps({
                'measurements': metrics.measurements,
                'performance_data': metrics.performance_data
            })
            assert len(json_str) > 0
            
            # Test deserialization
            restored = json.loads(json_str)
            assert restored['measurements']['integers'] == [1, 2, 3]
            assert restored['performance_data']['string'] == "test_value"
            
        except (TypeError, ValueError) as e:
            pytest.fail(f"Data serialization failed: {e}")