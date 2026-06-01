"""
Tests for the quantum-enhanced sensory tracer implementation.

These tests exercise the real public API exported from
``sensory_tracer_science.tracers.quantum_enhanced`` and verify the physics
behaviour (energy conservation, Heisenberg scaling, HOM interference,
antibunching, STS validation).
"""

import math

import numpy as np
import pytest

from sensory_tracer_science.core.sts_constants import C_VACUUM, HBAR
from sensory_tracer_science.tracers.quantum_enhanced import (
    HongOuMandelInterferometer,
    QuantumEnhancedSensoryTracer,
    QuantumEntangledPhotonSource,
    QuantumPhotonPair,
    QuantumSensorParameters,
    QuantumTracerExperiment,
    run_quantum_tracer_tests,
)
from sensory_tracer_science.validation.sts_validator import ValidationResult


def make_pair(fidelity=0.95, wavelength=1064e-9):
    """Helper to build a representative entangled photon pair."""
    return QuantumPhotonPair(
        wavelength=wavelength,
        frequency=C_VACUUM / wavelength,
        entanglement_fidelity=fidelity,
        polarization_state=complex(1 / math.sqrt(2), 0),
        creation_time=0.0,
    )


class TestQuantumPhotonPair:
    def test_energy_per_photon_matches_planck_relation(self):
        pair = make_pair(wavelength=1064e-9)
        expected = HBAR * 2 * np.pi * pair.frequency
        assert pair.energy_per_photon == pytest.approx(expected)

    def test_total_pair_energy_is_twice_single_photon(self):
        pair = make_pair()
        assert pair.total_pair_energy == pytest.approx(2 * pair.energy_per_photon)

    def test_energy_is_positive(self):
        pair = make_pair()
        assert pair.energy_per_photon > 0
        assert pair.total_pair_energy > 0


class TestQuantumSensorParameters:
    def test_default_parameters(self):
        params = QuantumSensorParameters()
        assert params.pump_wavelength == pytest.approx(532e-9)
        assert 0.0 < params.detector_efficiency <= 1.0
        assert params.pair_generation_rate > 0
        assert 0.0 < params.interference_visibility <= 1.0

    def test_parameters_are_mutable(self):
        params = QuantumSensorParameters()
        params.pair_generation_rate = 5e6
        assert params.pair_generation_rate == 5e6


class TestQuantumEntangledPhotonSource:
    def setup_method(self):
        self.params = QuantumSensorParameters()
        self.source = QuantumEntangledPhotonSource(self.params)

    def test_derived_frequencies(self):
        assert self.source.pump_frequency == pytest.approx(
            C_VACUUM / self.params.pump_wavelength
        )
        # Type-I SPDC: signal/idler at half the pump frequency
        assert self.source.signal_frequency == pytest.approx(
            self.source.pump_frequency / 2
        )

    def test_generate_entangled_pair_returns_valid_pair(self):
        pair = self.source.generate_entangled_pair(
            pump_power=1e-3, interaction_time=1e-12
        )
        assert isinstance(pair, QuantumPhotonPair)
        assert 0.0 <= pair.entanglement_fidelity <= 1.0
        # Energy conservation: signal wavelength is twice the pump wavelength
        assert pair.wavelength == pytest.approx(2 * self.params.pump_wavelength)

    def test_longer_interaction_reduces_fidelity_via_decoherence(self):
        pair_early = self.source.generate_entangled_pair(1e-3, 1e-15)
        pair_late = self.source.generate_entangled_pair(1e-3, 1e-3)
        assert pair_late.entanglement_fidelity < pair_early.entanglement_fidelity

    def test_flux_above_detector_limit_is_rejected(self):
        params = QuantumSensorParameters()
        params.pair_generation_rate = 1e12  # well above MAX_PHOTON_FLUX
        with pytest.raises(ValueError, match="exceeds detector limit"):
            QuantumEntangledPhotonSource(params)

    def test_heisenberg_limit_beats_shot_noise(self):
        params = QuantumSensorParameters()
        source = QuantumEntangledPhotonSource(params)
        n_photons = params.pair_generation_rate * params.measurement_time
        heisenberg = source.calculate_heisenberg_limit()
        shot_noise = 1.0 / math.sqrt(n_photons)
        assert heisenberg == pytest.approx(1.0 / n_photons)
        # Heisenberg (1/N) scaling is tighter than shot-noise (1/sqrt(N))
        assert heisenberg < shot_noise


class TestHongOuMandelInterferometer:
    def setup_method(self):
        self.params = QuantumSensorParameters()
        self.interferometer = HongOuMandelInterferometer(self.params)

    def test_hom_dip_minimum_at_zero_delay(self):
        pair = make_pair(fidelity=1.0)
        p_zero = self.interferometer.hong_ou_mandel_probability(0.0, pair)
        p_offset = self.interferometer.hong_ou_mandel_probability(
            10 * self.params.coherence_time, pair
        )
        # Coincidence probability is minimised at zero delay (the HOM dip)
        assert p_zero < p_offset
        assert 0.0 <= p_zero <= 1.0
        assert 0.0 <= p_offset <= 1.0

    def test_hom_probability_approaches_half_at_large_delay(self):
        pair = make_pair(fidelity=1.0)
        p_large = self.interferometer.hong_ou_mandel_probability(
            100 * self.params.coherence_time, pair
        )
        assert p_large == pytest.approx(0.5, abs=1e-3)

    def test_measure_coincidences_structure(self):
        pair = make_pair()
        result = self.interferometer.measure_coincidences(
            photon_pair=pair, path_delay=0.0, measurement_duration=1e-3
        )
        for key in (
            "coincidences",
            "dark_counts",
            "shot_noise",
            "snr",
            "hom_probability",
            "total_detected_pairs",
        ):
            assert key in result
        assert result["coincidences"] >= 0.0
        assert result["total_detected_pairs"] > 0.0

    def test_g2_correlation_function_shape_and_range(self):
        pair = make_pair(fidelity=1.0)
        delays = np.linspace(-1e-3, 1e-3, 11)
        g2 = self.interferometer.g2_correlation_function(pair, delays)
        assert g2.shape == delays.shape
        assert np.all(g2 >= 0.0)


class TestQuantumEnhancedSensoryTracer:
    def setup_method(self):
        self.tracer = QuantumEnhancedSensoryTracer()

    def test_quantum_phase_sensing_returns_metrics(self):
        results = self.tracer.quantum_phase_sensing(sensing_parameter=0.5)
        for key in (
            "measured_parameter",
            "phase_shift",
            "snr",
            "heisenberg_limit",
            "quantum_advantage",
            "fisher_information",
            "entanglement_fidelity",
            "photon_pair_energy",
        ):
            assert key in results
        assert results["measured_parameter"] == 0.5
        assert results["photon_pair_energy"] > 0

    def test_phase_shift_scales_with_sensing_parameter(self):
        low = self.tracer.quantum_phase_sensing(sensing_parameter=0.1)
        high = self.tracer.quantum_phase_sensing(sensing_parameter=1.0)
        assert high["phase_shift"] > low["phase_shift"]

    def test_quantum_state_tomography(self):
        np.random.seed(0)
        pair = make_pair(fidelity=0.95)
        tomo = self.tracer.quantum_state_tomography(pair, num_measurements=10000)
        assert "measurement_results" in tomo
        assert tomo["entanglement_fidelity"] == pytest.approx(0.95)
        assert tomo["quantum_state_validity"] is True
        assert 0.0 <= tomo["concurrence"] <= 1.0

    def test_validate_quantum_tracer_passes_for_good_parameters(self):
        np.random.seed(0)
        sensing = self.tracer.quantum_phase_sensing(sensing_parameter=0.5)
        pair = make_pair(fidelity=0.95)
        tomo = self.tracer.quantum_state_tomography(pair, num_measurements=10000)
        validation = self.tracer.validate_quantum_tracer(sensing, tomo)
        for key in (
            "energy_audit",
            "information_balance",
            "causality_check",
            "quantum_antibunching",
            "entanglement_fidelity",
            "quantum_advantage",
        ):
            assert key in validation
            assert isinstance(validation[key], ValidationResult)
        assert validation["entanglement_fidelity"].passed is True

    def test_validate_quantum_tracer_flags_low_fidelity(self):
        np.random.seed(0)
        sensing = self.tracer.quantum_phase_sensing(sensing_parameter=0.5)
        pair = make_pair(fidelity=0.5)
        tomo = self.tracer.quantum_state_tomography(pair, num_measurements=10000)
        validation = self.tracer.validate_quantum_tracer(sensing, tomo)
        assert validation["entanglement_fidelity"].passed is False


class TestQuantumTracerExperiment:
    def test_run_experiment_reports_status(self):
        np.random.seed(0)
        experiment = QuantumTracerExperiment()
        result = experiment.run_quantum_sensing_experiment(
            sensing_parameters=[0.0, 0.5, 1.0], measurement_duration=1e-3
        )
        assert result["test_status"] in ("PASSED", "FAILED")
        assert len(result["sensing_data"]) == 3
        assert "performance_metrics" in result

    def test_generate_report_contains_status(self):
        np.random.seed(0)
        experiment = QuantumTracerExperiment()
        result = experiment.run_quantum_sensing_experiment(
            sensing_parameters=[0.0, 0.5], measurement_duration=1e-3
        )
        report = experiment.generate_quantum_report(result)
        assert "QUANTUM-ENHANCED SENSORY TRACER" in report
        assert result["test_status"] in report


class TestRunQuantumTracerTests:
    def test_run_quantum_tracer_tests_overall_summary(self):
        np.random.seed(0)
        results = run_quantum_tracer_tests()
        assert "overall_summary" in results
        summary = results["overall_summary"]
        assert summary["total_tests"] >= 1
        assert 0.0 <= summary["pass_rate"] <= 1.0
