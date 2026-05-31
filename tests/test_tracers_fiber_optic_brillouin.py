"""
Tests for the fiber-optic Brillouin sensory tracer implementation.

These tests exercise the real public API of
``sensory_tracer_science.tracers.fiber_optic_brillouin`` and verify the
physics behaviour (Brillouin frequency shift vs temperature/strain,
three-wave power coupling, propagation energy constraints, sensing
information extraction and STS validation).
"""

import numpy as np
import pytest

from sensory_tracer_science.core.sts_constants import C_VACUUM
from sensory_tracer_science.tracers.fiber_optic_brillouin import (
    BrillouinScatteringParameters,
    BrillouinTracerExperiment,
    FiberOpticBrillouinTracer,
    run_comprehensive_brillouin_tests,
)
from sensory_tracer_science.validation.sts_validator import ValidationResult


def make_tracer(length=1000.0):
    return FiberOpticBrillouinTracer(fiber_length=length)


class TestBrillouinScatteringParameters:
    def test_silica_defaults(self):
        params = BrillouinScatteringParameters()
        assert params.refractive_index == pytest.approx(1.46)
        assert params.acoustic_velocity == pytest.approx(5960.0)
        assert params.frequency == pytest.approx(C_VACUUM / 1.55e-6)


class TestFiberOpticBrillouinTracer:
    def setup_method(self):
        self.tracer = make_tracer()

    def test_light_speed_in_fiber(self):
        assert self.tracer.light_speed_fiber == pytest.approx(
            C_VACUUM / self.tracer.params.refractive_index
        )

    def test_frequency_shift_baseline_and_temperature_dependence(self):
        base = self.tracer.brillouin_frequency_shift(temperature=300.0, strain=0.0)
        assert base == pytest.approx(self.tracer.params.brillouin_frequency_shift)
        hotter = self.tracer.brillouin_frequency_shift(temperature=350.0, strain=0.0)
        # Positive temperature coefficient (~1 MHz/K)
        assert hotter > base

    def test_frequency_shift_strain_dependence(self):
        no_strain = self.tracer.brillouin_frequency_shift(strain=0.0)
        with_strain = self.tracer.brillouin_frequency_shift(strain=100.0)
        assert with_strain > no_strain

    def test_power_coupling_nonnegative(self):
        stokes, acoustic = self.tracer.brillouin_power_coupling(
            pump_power=1e-3, distance=1.0
        )
        assert stokes >= 0.0
        assert acoustic >= 0.0
        # Acoustic (phonon) power is a small fraction of the Stokes power
        assert acoustic <= stokes

    def test_propagation_simulation_structure(self):
        temp = np.full(1000, 300.0)
        strain = np.zeros(1000)
        results = self.tracer.propagation_simulation(
            input_energy=1e-9,
            pulse_width=1e-9,
            temperature_profile=temp,
            strain_profile=strain,
            num_points=1000,
        )
        for key in (
            "position",
            "pump_power",
            "stokes_power",
            "acoustic_power",
            "brillouin_shift",
            "total_energy",
            "information_content",
        ):
            assert key in results
            assert len(results[key]) == 1000
        assert np.all(results["pump_power"] >= 0.0)

    def test_propagation_rejects_excess_energy(self):
        temp = np.full(10, 300.0)
        strain = np.zeros(10)
        with pytest.raises(ValueError, match="exceeds safe limit"):
            self.tracer.propagation_simulation(
                input_energy=1e-6,  # far above MAX_INPUT_ENERGY (1 nJ)
                pulse_width=1e-9,
                temperature_profile=temp,
                strain_profile=strain,
                num_points=10,
            )

    def test_extract_sensing_information(self):
        temp = 300.0 + 5.0 * np.sin(np.linspace(0, 6, 1000))
        strain = np.zeros(1000)
        results = self.tracer.propagation_simulation(
            input_energy=1e-9,
            pulse_width=1e-9,
            temperature_profile=temp,
            strain_profile=strain,
        )
        sensing = self.tracer.extract_sensing_information(results)
        for key in (
            "extracted_temperature",
            "spatial_resolution",
            "channel_capacity_per_point",
            "total_information_capacity",
            "number_of_sensing_points",
        ):
            assert key in sensing
        assert sensing["spatial_resolution"] > 0
        assert sensing["number_of_sensing_points"] > 0

    def test_validate_tracer_operation_returns_validation_results(self):
        temp = np.full(1000, 300.0)
        strain = np.zeros(1000)
        results = self.tracer.propagation_simulation(
            input_energy=1e-9,
            pulse_width=1e-9,
            temperature_profile=temp,
            strain_profile=strain,
        )
        sensing = self.tracer.extract_sensing_information(results)
        validation = self.tracer.validate_tracer_operation(1e-9, results, sensing)
        for key in ("energy_audit", "information_balance", "causality_check"):
            assert key in validation
            assert isinstance(validation[key], ValidationResult)
        # Light in fiber must respect the causality limit
        assert validation["causality_check"].passed is True


class TestBrillouinTracerExperiment:
    def test_create_test_environment_shapes(self):
        exp = BrillouinTracerExperiment(fiber_length=1000.0)
        temp, strain = exp.create_test_environment()
        assert temp.shape == (1000,)
        assert strain.shape == (1000,)
        assert np.all(temp > 0)

    def test_run_brillouin_test_reports_status(self):
        exp = BrillouinTracerExperiment(fiber_length=1000.0)
        results = exp.run_brillouin_test(input_energy=1e-9)
        assert results["test_status"] in ("PASSED", "FAILED")
        assert results["causality_check_passed"] is True
        assert "sensing_information" in results

    def test_generate_test_report(self):
        exp = BrillouinTracerExperiment(fiber_length=1000.0)
        results = exp.run_brillouin_test(input_energy=1e-9)
        report = exp.generate_test_report(results)
        assert "FIBER-OPTIC BRILLOUIN TRACER" in report
        assert results["test_status"] in report


class TestRunComprehensiveBrillouinTests:
    def test_overall_summary_and_energy_limit_enforcement(self):
        results = run_comprehensive_brillouin_tests()
        assert "overall_summary" in results
        # The over-limit case must be rejected by the energy constraint
        assert "energy_limit_enforcement" in results
        assert "PASSED" in results["energy_limit_enforcement"]
