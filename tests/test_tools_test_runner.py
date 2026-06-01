"""
Comprehensive test suite for STS tools test_runner module.

These tests exercise the shipped test-runner API: each ``run_*`` helper
returns a dict shaped as ``{"test_type", "parameters", "execution_time",
"results"}`` and propagates errors to the caller, while ``main`` returns a
process exit code (0 success, 1 failed test, 2 exception).
"""

import pytest
from io import StringIO
from unittest.mock import patch, MagicMock

from sensory_tracer_science.tools.test_runner import (
    run_biocompatible_test,
    run_brillouin_test,
    run_quantum_test,
    run_performance_benchmark,
    main,
)


class TestBiocompatibleTestRunner:
    """Test biocompatible tracer test runner."""

    def test_run_biocompatible_test_default(self):
        """Test biocompatible test with default parameters."""
        result = run_biocompatible_test(duration=1.0)

        assert isinstance(result, dict)
        assert result["test_type"] == "biocompatible_neural"
        assert "execution_time" in result
        assert "results" in result
        assert result["parameters"]["tissue_size"] == "standard"
        assert result["parameters"]["duration"] == 1.0

    def test_run_biocompatible_test_micro_tissue(self):
        """Test biocompatible test with micro tissue size."""
        result = run_biocompatible_test(tissue_size="micro", duration=0.5)

        assert result["test_type"] == "biocompatible_neural"
        assert result["parameters"]["tissue_size"] == "micro"

    def test_run_biocompatible_test_large_tissue(self):
        """Test biocompatible test with large tissue size."""
        result = run_biocompatible_test(tissue_size="large", duration=0.5)

        assert result["parameters"]["tissue_size"] == "large"
        assert "results" in result

    def test_run_biocompatible_test_invalid_tissue_size(self):
        """An invalid tissue size raises ValueError (no silent default)."""
        with pytest.raises(ValueError, match="Invalid tissue size"):
            run_biocompatible_test(tissue_size="invalid", duration=0.5)

    @patch("sensory_tracer_science.tools.test_runner.NeuralTracerExperiment")
    def test_run_biocompatible_test_with_mock_experiment(self, mock_experiment_class):
        """The runner delegates to NeuralTracerExperiment and wraps its output."""
        mock_experiment = MagicMock()
        mock_experiment.run_neural_tracer_test.return_value = {"test_status": "PASSED"}
        mock_experiment_class.return_value = mock_experiment

        result = run_biocompatible_test(duration=0.5)

        mock_experiment_class.assert_called_once()
        mock_experiment.run_neural_tracer_test.assert_called_once()
        assert result["results"] == {"test_status": "PASSED"}


class TestBrillouinTestRunner:
    """Test Brillouin tracer test runner."""

    def test_run_brillouin_test_default(self):
        """Test Brillouin test with default parameters."""
        result = run_brillouin_test()

        assert isinstance(result, dict)
        assert result["test_type"] == "fiber_optic_brillouin"
        assert "execution_time" in result
        assert "results" in result

    def test_run_brillouin_test_custom_parameters(self):
        """Test Brillouin test with custom (real) parameters."""
        result = run_brillouin_test(fiber_length=10.0, input_energy=5e-10)

        assert result["test_type"] == "fiber_optic_brillouin"
        assert result["parameters"]["fiber_length"] == 10.0
        assert result["parameters"]["input_energy"] == 5e-10

    @patch("sensory_tracer_science.tools.test_runner.BrillouinTracerExperiment")
    def test_run_brillouin_test_with_mock(self, mock_experiment_class):
        """The runner delegates to BrillouinTracerExperiment."""
        mock_experiment = MagicMock()
        mock_experiment.run_brillouin_test.return_value = {"test_status": "PASSED"}
        mock_experiment_class.return_value = mock_experiment

        result = run_brillouin_test()

        mock_experiment_class.assert_called_once()
        assert result["results"] == {"test_status": "PASSED"}


class TestQuantumTestRunner:
    """Test quantum tracer test runner."""

    def test_run_quantum_test_default(self):
        """Test quantum test with default parameters."""
        result = run_quantum_test()

        assert isinstance(result, dict)
        assert result["test_type"] == "quantum_enhanced"
        assert "execution_time" in result
        assert "results" in result

    def test_run_quantum_test_custom_parameters(self):
        """Test quantum test with custom (real) parameters."""
        result = run_quantum_test(measurement_type="entanglement", precision="high")

        assert result["test_type"] == "quantum_enhanced"
        assert result["parameters"]["measurement_type"] == "entanglement"
        assert result["parameters"]["precision"] == "high"

    @patch("sensory_tracer_science.tools.test_runner.QuantumTracerExperiment")
    def test_run_quantum_test_with_mock(self, mock_experiment_class):
        """The runner delegates to QuantumTracerExperiment."""
        mock_experiment = MagicMock()
        mock_experiment.run_quantum_sensing_experiment.return_value = {
            "test_status": "PASSED"
        }
        mock_experiment_class.return_value = mock_experiment

        result = run_quantum_test()

        mock_experiment_class.assert_called_once()
        assert result["results"] == {"test_status": "PASSED"}


class TestPerformanceBenchmark:
    """Test performance benchmark runner."""

    def test_run_performance_benchmark_default(self):
        """Test performance benchmark with default parameters."""
        result = run_performance_benchmark(iterations=1)

        assert isinstance(result, dict)
        assert len(result) > 0

    def test_run_performance_benchmark_biocompatible(self):
        """Test performance benchmark for biocompatible tests."""
        result = run_performance_benchmark(test_type="biocompatible", iterations=1)

        assert isinstance(result, dict)
        assert "biocompatible" in result
        benchmark_data = result["biocompatible"]
        assert "mean_time" in benchmark_data
        assert "min_time" in benchmark_data
        assert "max_time" in benchmark_data

    def test_run_performance_benchmark_all_types(self):
        """Test performance benchmark for all test types."""
        result = run_performance_benchmark(test_type="all", iterations=1)

        assert isinstance(result, dict)
        for test_type in ("biocompatible", "quantum", "brillouin"):
            assert test_type in result
            assert "mean_time" in result[test_type]


class TestMainFunction:
    """Test main function execution (returns a process exit code)."""

    @patch("sensory_tracer_science.tools.test_runner.run_biocompatible_test")
    @patch("sys.argv", ["test_runner.py", "--biocompatible", "--verbose"])
    def test_main_biocompatible(self, mock_test):
        """A passing biocompatible run yields exit code 0."""
        mock_test.return_value = {
            "results": {"test_status": "PASSED"},
            "execution_time": 1.5,
        }

        with patch("sys.stdout", StringIO()):
            exit_code = main()

        mock_test.assert_called_once()
        assert exit_code == 0

    @patch("sensory_tracer_science.tools.test_runner.run_biocompatible_test")
    @patch("sys.argv", ["test_runner.py", "--biocompatible"])
    def test_main_biocompatible_failed_status(self, mock_test):
        """A non-PASSED test status yields exit code 1."""
        mock_test.return_value = {
            "results": {"test_status": "FAILED"},
            "execution_time": 1.5,
        }

        with patch("sys.stdout", StringIO()):
            exit_code = main()

        assert exit_code == 1

    @patch("sensory_tracer_science.tools.test_runner.run_performance_benchmark")
    @patch("sys.argv", ["test_runner.py", "--benchmark"])
    def test_main_benchmark(self, mock_benchmark):
        """A benchmark run yields exit code 0."""
        mock_benchmark.return_value = {
            "biocompatible": {"mean_time": 1.5, "min_time": 1.2, "max_time": 1.8}
        }

        with patch("sys.stdout", StringIO()):
            exit_code = main()

        mock_benchmark.assert_called_once()
        assert exit_code == 0

    @patch("sys.argv", ["test_runner.py"])
    def test_main_no_arguments(self):
        """With no test selected argparse exits (mutually-exclusive required)."""
        with patch("sys.stdout", StringIO()), patch("sys.stderr", StringIO()):
            with pytest.raises(SystemExit):
                main()

    @patch("sensory_tracer_science.tools.test_runner.run_biocompatible_test")
    @patch("sys.argv", ["test_runner.py", "--biocompatible"])
    def test_main_with_exception(self, mock_test):
        """An exception during execution yields exit code 2."""
        mock_test.side_effect = Exception("Unexpected error")

        with patch("sys.stdout", StringIO()), patch("sys.stderr", StringIO()):
            exit_code = main()

        assert exit_code == 2


class TestErrorHandling:
    """Errors from the underlying experiments propagate to the caller."""

    @patch("sensory_tracer_science.tools.test_runner.NeuralTracerExperiment")
    def test_biocompatible_test_experiment_failure(self, mock_experiment_class):
        """Test biocompatible test when experiment construction fails."""
        mock_experiment_class.side_effect = Exception("Experiment init failed")

        with pytest.raises(Exception, match="Experiment init failed"):
            run_biocompatible_test(duration=0.5)

    @patch("sensory_tracer_science.tools.test_runner.BrillouinTracerExperiment")
    def test_brillouin_test_experiment_failure(self, mock_experiment_class):
        """Test Brillouin test when experiment construction fails."""
        mock_experiment_class.side_effect = Exception("Brillouin init failed")

        with pytest.raises(Exception, match="Brillouin init failed"):
            run_brillouin_test()

    @patch("sensory_tracer_science.tools.test_runner.QuantumTracerExperiment")
    def test_quantum_test_experiment_failure(self, mock_experiment_class):
        """Test quantum test when experiment construction fails."""
        mock_experiment_class.side_effect = Exception("Quantum init failed")

        with pytest.raises(Exception, match="Quantum init failed"):
            run_quantum_test()


class TestResultStructure:
    """All runners return the documented top-level schema."""

    def test_biocompatible_result_structure(self):
        """Test biocompatible test result structure."""
        result = run_biocompatible_test(duration=0.1)
        for key in ("test_type", "parameters", "execution_time", "results"):
            assert key in result

    def test_brillouin_result_structure(self):
        """Test brillouin test result structure."""
        result = run_brillouin_test()
        for key in ("test_type", "parameters", "execution_time", "results"):
            assert key in result

    def test_quantum_result_structure(self):
        """Test quantum test result structure."""
        result = run_quantum_test()
        for key in ("test_type", "parameters", "execution_time", "results"):
            assert key in result
