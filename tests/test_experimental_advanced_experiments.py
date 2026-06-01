"""
Tests for the advanced experiments module.

These tests exercise the real public API of
``sensory_tracer_science.experimental.advanced_experiments``. The heavy
end-to-end experiment methods (multi-modal/distributed/AI runs and the
demo) allocate large arrays and are intentionally not executed here; we
verify construction, parameter defaults and the cheap input-validation
paths instead.
"""

from dataclasses import asdict

import pytest

from sensory_tracer_science.experimental.advanced_experiments import (
    AdaptiveProtocolParameters,
    AdvancedExperimentSuite,
    MultiModalParameters,
    run_advanced_experiment_demo,
)


class TestMultiModalParameters:
    def test_default_initialization(self):
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

    def test_custom_initialization(self):
        params = MultiModalParameters(
            temporal_synchronization_accuracy=1e-9,
            data_fusion_algorithm="kalman_filter",
            real_time_processing=False,
        )
        assert params.temporal_synchronization_accuracy == 1e-9
        assert params.data_fusion_algorithm == "kalman_filter"
        assert params.real_time_processing is False
        # Untouched fields keep their defaults
        assert params.cross_modal_correlation_threshold == 0.85
        assert params.confidence_weighting is True

    def test_algorithm_variants(self):
        for algorithm in ("bayesian_inference", "kalman_filter", "neural_network"):
            params = MultiModalParameters(data_fusion_algorithm=algorithm)
            assert params.data_fusion_algorithm == algorithm


class TestAdaptiveProtocolParameters:
    def test_default_initialization(self):
        params = AdaptiveProtocolParameters()
        assert params.learning_rate == 0.01
        assert params.adaptation_window == 100
        assert params.convergence_threshold == 0.001
        assert params.optimization_algorithm == "particle_swarm"
        assert params.population_size == 50
        assert params.generations == 100
        assert params.safety_constraints_enabled is True

    def test_post_init_populates_default_constraints(self):
        params = AdaptiveProtocolParameters()
        assert isinstance(params.performance_constraints, dict)
        assert params.performance_constraints["signal_to_noise_ratio"] == 20.0
        assert "measurement_accuracy" in params.performance_constraints

    def test_custom_constraints_preserved(self):
        custom = {"signal_to_noise_ratio": 40.0}
        params = AdaptiveProtocolParameters(performance_constraints=custom)
        assert params.performance_constraints == custom


class TestAdvancedExperimentSuite:
    def test_initialization_requires_suite_id(self):
        suite = AdvancedExperimentSuite("suite-001")
        assert suite.suite_id == "suite-001"
        assert isinstance(suite.multi_modal_params, MultiModalParameters)
        assert isinstance(suite.adaptive_params, AdaptiveProtocolParameters)

    def test_initial_state_containers(self):
        suite = AdvancedExperimentSuite("suite-002")
        assert suite.active_experiments == {}
        assert suite.data_streams == {}
        assert suite.performance_metrics == {}

    def test_exposes_experiment_methods(self):
        suite = AdvancedExperimentSuite("suite-003")
        for method in (
            "run_multi_modal_sensing_experiment",
            "run_adaptive_optimization_experiment",
            "run_distributed_sensing_network",
            "run_ai_enhanced_discovery_experiment",
        ):
            assert callable(getattr(suite, method))

    def test_multiple_instances_are_independent(self):
        suite1 = AdvancedExperimentSuite("a")
        suite2 = AdvancedExperimentSuite("b")
        assert suite1 is not suite2
        assert suite1.suite_id != suite2.suite_id

    def test_multi_modal_rejects_unsupported_modality(self):
        suite = AdvancedExperimentSuite("suite-004")
        # Validation happens before any heavy allocation, so this is cheap.
        with pytest.raises(ValueError, match="Unsupported modality"):
            suite.run_multi_modal_sensing_experiment(
                modalities=["not_a_real_modality"],
                target_object="phantom",
                duration=1.0,
            )


class TestParameterSerialization:
    def test_parameters_are_dataclasses(self):
        multi = asdict(MultiModalParameters())
        adaptive = asdict(AdaptiveProtocolParameters())
        assert isinstance(multi, dict) and len(multi) > 0
        assert isinstance(adaptive, dict) and len(adaptive) > 0


def test_demo_function_is_importable_and_callable():
    # The demo runs the full heavy experiment pipeline (high memory / slow),
    # so we only assert it is importable and callable rather than executing it.
    assert callable(run_advanced_experiment_demo)
