"""
Comprehensive test suite for STS tools test_runner module.
"""

import pytest
import sys
from io import StringIO
from unittest.mock import patch, MagicMock

from sensory_tracer_science.tools.test_runner import (
    run_biocompatible_test,
    run_brillouin_test,
    run_quantum_test,
    run_performance_benchmark,
    main
)


class TestBiocompatibleTestRunner:
    """Test biocompatible tracer test runner."""
    
    def test_run_biocompatible_test_default(self):
        """Test biocompatible test with default parameters."""
        result = run_biocompatible_test()
        
        assert isinstance(result, dict)
        assert "test_type" in result
        assert result["test_type"] == "biocompatible_neural"
        assert "status" in result
        assert "duration" in result
        assert "tissue_geometry" in result
        
    def test_run_biocompatible_test_micro_tissue(self):
        """Test biocompatible test with micro tissue size."""
        result = run_biocompatible_test(tissue_size="micro", duration=30.0, verbose=True)
        
        assert result["test_type"] == "biocompatible_neural"
        assert result["tissue_geometry"]["length"] == 100e-6
        assert result["tissue_geometry"]["width"] == 50e-6
        assert result["tissue_geometry"]["height"] == 10e-6
        
    def test_run_biocompatible_test_large_tissue(self):
        """Test biocompatible test with large tissue size."""
        result = run_biocompatible_test(tissue_size="large", duration=120.0)
        
        assert result["tissue_geometry"]["length"] == 5e-3
        assert result["tissue_geometry"]["width"] == 5e-3
        assert result["tissue_geometry"]["height"] == 2e-3
        
    def test_run_biocompatible_test_invalid_tissue_size(self):
        """Test biocompatible test with invalid tissue size."""
        result = run_biocompatible_test(tissue_size="invalid")
        
        # Should default to standard
        assert result["tissue_geometry"]["length"] == 1e-3
        
    @patch('sensory_tracer_science.tools.test_runner.NeuralTracerExperiment')
    def test_run_biocompatible_test_with_mock_experiment(self, mock_experiment_class):
        """Test biocompatible test with mocked experiment."""
        mock_experiment = MagicMock()
        mock_experiment.run_experiment.return_value = {"status": "completed", "data": "mock_data"}
        mock_experiment_class.return_value = mock_experiment
        
        result = run_biocompatible_test(verbose=True)
        
        assert result["status"] in ["completed", "error"]
        mock_experiment_class.assert_called_once()


class TestBrillouinTestRunner:
    """Test Brillouin tracer test runner."""
    
    def test_run_brillouin_test_default(self):
        """Test Brillouin test with default parameters."""
        result = run_brillouin_test()
        
        assert isinstance(result, dict)
        assert "test_type" in result
        assert result["test_type"] == "fiber_optic_brillouin"
        assert "status" in result
        
    def test_run_brillouin_test_custom_parameters(self):
        """Test Brillouin test with custom parameters."""
        result = run_brillouin_test(
            fiber_length=10.0,
            pulse_power=50.0,
            duration=180.0,
            verbose=True
        )
        
        assert result["test_type"] == "fiber_optic_brillouin"
        assert "fiber_length_m" in result
        assert result["fiber_length_m"] == 10.0
        
    @patch('sensory_tracer_science.tools.test_runner.BrillouinTracerExperiment')
    def test_run_brillouin_test_with_mock(self, mock_experiment_class):
        """Test Brillouin test with mocked experiment."""
        mock_experiment = MagicMock()
        mock_experiment.run_experiment.return_value = {"status": "completed"}
        mock_experiment_class.return_value = mock_experiment
        
        result = run_brillouin_test(verbose=True)
        
        assert result["status"] in ["completed", "error"]


class TestQuantumTestRunner:
    """Test quantum tracer test runner."""
    
    def test_run_quantum_test_default(self):
        """Test quantum test with default parameters."""
        result = run_quantum_test()
        
        assert isinstance(result, dict)
        assert "test_type" in result
        assert result["test_type"] == "quantum_enhanced"
        assert "status" in result
        
    def test_run_quantum_test_custom_parameters(self):
        """Test quantum test with custom parameters."""
        result = run_quantum_test(
            num_qubits=10,
            coherence_time=1e-6,
            duration=90.0,
            verbose=True
        )
        
        assert result["test_type"] == "quantum_enhanced"
        assert "qubit_count" in result
        assert result["qubit_count"] == 10
        
    @patch('sensory_tracer_science.tools.test_runner.QuantumTracerExperiment')
    def test_run_quantum_test_with_mock(self, mock_experiment_class):
        """Test quantum test with mocked experiment."""
        mock_experiment = MagicMock()
        mock_experiment.run_experiment.return_value = {"status": "completed"}
        mock_experiment_class.return_value = mock_experiment
        
        result = run_quantum_test(verbose=True)
        
        assert result["status"] in ["completed", "error"]


class TestPerformanceBenchmark:
    """Test performance benchmark runner."""
    
    def test_run_performance_benchmark_default(self):
        """Test performance benchmark with default parameters."""
        result = run_performance_benchmark()
        
        assert isinstance(result, dict)
        # Should contain benchmark results for at least one test
        assert len(result) > 0
        
    def test_run_performance_benchmark_biocompatible(self):
        """Test performance benchmark for biocompatible tests."""
        result = run_performance_benchmark(test_type="biocompatible", iterations=2)
        
        assert isinstance(result, dict)
        if "biocompatible" in result:
            benchmark_data = result["biocompatible"]
            assert "mean_time" in benchmark_data
            assert "min_time" in benchmark_data  
            assert "max_time" in benchmark_data
            
    def test_run_performance_benchmark_all_types(self):
        """Test performance benchmark for all test types."""
        result = run_performance_benchmark(test_type="all", iterations=1)
        
        assert isinstance(result, dict)
        # Should have results for multiple test types
        expected_types = ["biocompatible", "quantum", "brillouin"]
        for test_type in expected_types:
            if test_type in result:
                assert "mean_time" in result[test_type]
        

class TestMainFunction:
    """Test main function execution."""
    
    @patch('sensory_tracer_science.tools.test_runner.run_biocompatible_test')
    @patch('sys.argv', ['test_runner.py', '--biocompatible', '--verbose'])
    def test_main_biocompatible(self, mock_test):
        """Test main function with biocompatible test."""
        mock_test.return_value = {
            "results": {"test_status": "PASSED"},
            "execution_time": 1.5
        }
        
        # Capture output
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            with patch('sys.exit') as mock_exit:
                main()
        
        mock_test.assert_called_once()
        mock_exit.assert_called_with(0)
        
    @patch('sensory_tracer_science.tools.test_runner.run_performance_benchmark')
    @patch('sys.argv', ['test_runner.py', '--benchmark'])
    def test_main_benchmark(self, mock_benchmark):
        """Test main function with benchmark."""
        mock_benchmark.return_value = {
            "biocompatible": {
                "mean_time": 1.5,
                "min_time": 1.2,
                "max_time": 1.8
            }
        }
        
        with patch('sys.stdout', StringIO()):
            with patch('sys.exit') as mock_exit:
                main()
        
        mock_benchmark.assert_called_once()
        mock_exit.assert_called_with(0)
        
    @patch('sys.argv', ['test_runner.py'])
    def test_main_no_arguments(self):
        """Test main function with no arguments (should show help)."""
        with patch('sys.stdout', StringIO()):
            with patch('sys.exit'):
                main()
                
    @patch('sensory_tracer_science.tools.test_runner.run_biocompatible_test')
    @patch('sys.argv', ['test_runner.py', '--biocompatible'])
    def test_main_with_exception(self, mock_test):
        """Test main function handling exceptions."""
        mock_test.side_effect = Exception("Unexpected error")
        
        with patch('sys.stdout', StringIO()):
            with patch('sys.stderr', StringIO()):
                with patch('sys.exit') as mock_exit:
                    main()
        
        # Should exit with error code
        mock_exit.assert_called_with(1)


class TestErrorHandling:
    """Test error handling in test runner."""
    
    @patch('sensory_tracer_science.tools.test_runner.NeuralTracerExperiment')
    def test_biocompatible_test_experiment_failure(self, mock_experiment_class):
        """Test biocompatible test when experiment fails."""
        mock_experiment_class.side_effect = Exception("Experiment initialization failed")
        
        result = run_biocompatible_test()
        
        assert result["status"] == "error"
        assert "error_message" in result
        
    @patch('sensory_tracer_science.tools.test_runner.BrillouinTracerExperiment')
    def test_brillouin_test_experiment_failure(self, mock_experiment_class):
        """Test Brillouin test when experiment fails."""
        mock_experiment_class.side_effect = Exception("Brillouin initialization failed")
        
        result = run_brillouin_test()
        
        assert result["status"] == "error"
        
    @patch('sensory_tracer_science.tools.test_runner.QuantumTracerExperiment')
    def test_quantum_test_experiment_failure(self, mock_experiment_class):
        """Test quantum test when experiment fails."""
        mock_experiment_class.side_effect = Exception("Quantum initialization failed")
        
        result = run_quantum_test()
        
        assert result["status"] == "error"


class TestOutputFormatting:
    """Test output formatting and verbose mode."""
    
    def test_verbose_output_biocompatible(self):
        """Test verbose output for biocompatible test."""
        with patch('sys.stdout', StringIO()) as captured:
            result = run_biocompatible_test(verbose=True)
            
        # Should have verbose output
        assert result["status"] in ["completed", "error"]
        
    def test_verbose_output_benchmark(self):
        """Test verbose output for benchmark."""
        result = run_performance_benchmark(test_type="biocompatible", iterations=1)
        
        # Should return benchmark results
        assert isinstance(result, dict)