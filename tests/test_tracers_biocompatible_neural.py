"""
Tests for the biocompatible neural tracer implementation.

These tests exercise the real public API of
``sensory_tracer_science.tracers.biocompatible_neural`` and verify the
biological/physical behaviour (Stokes-Einstein diffusion, Hill-equation
toxicity, Langmuir binding, ATP budgeting, information extraction and STS
biocompatibility validation).
"""

import numpy as np
import pytest

from sensory_tracer_science.tracers.biocompatible_neural import (
    BiochemicalTracer,
    BiocompatibleNeuralTracer,
    BiologicalParameters,
    NeuralTracerExperiment,
)
from sensory_tracer_science.validation.sts_validator import ValidationResult

TISSUE = {"length": 1e-3, "width": 1e-3, "height": 1e-3}


def make_tracer(mw=1000.0):
    return BiochemicalTracer(
        name="Calcium Green-1",
        molecular_weight=mw,
        fluorescence_quantum_yield=0.8,
        binding_affinity=1e-6,
    )


def make_neural_tracer():
    return BiocompatibleNeuralTracer(tracer=make_tracer(), tissue_geometry=TISSUE)


class TestBiochemicalTracer:
    def test_derived_properties_positive(self):
        tracer = make_tracer()
        assert tracer.stokes_radius > 0
        assert tracer.diffusion_coefficient > 0

    def test_heavier_molecule_diffuses_slower(self):
        light = make_tracer(mw=500.0)
        heavy = make_tracer(mw=5000.0)
        # Larger molecule -> larger Stokes radius -> smaller diffusion coefficient
        assert heavy.stokes_radius > light.stokes_radius
        assert heavy.diffusion_coefficient < light.diffusion_coefficient


class TestBiologicalParameters:
    def test_physiological_defaults(self):
        params = BiologicalParameters()
        assert params.body_temperature == pytest.approx(310.0)
        assert params.ph == pytest.approx(7.4)
        assert params.ld50_concentration > params.noael_concentration


class TestBiocompatibleNeuralTracer:
    def setup_method(self):
        self.tracer = make_neural_tracer()

    def test_tissue_volume(self):
        expected = TISSUE["length"] * TISSUE["width"] * TISSUE["height"]
        assert self.tracer.tissue_volume == pytest.approx(expected)

    def test_toxicity_increases_with_concentration(self):
        low = self.tracer.calculate_toxicity_response(np.array([1e-7]))
        high = self.tracer.calculate_toxicity_response(np.array([5e-6]))
        for key in (
            "cytotoxicity_fraction",
            "microglial_activation",
            "apoptosis_rate",
            "inflammatory_response",
        ):
            assert key in low
        assert high["cytotoxicity_fraction"][0] > low["cytotoxicity_fraction"][0]

    def test_bbb_permeability_is_positive(self):
        perm = self.tracer.calculate_bbb_permeability(
            {"concentration": np.array([1e-7])}
        )
        assert perm > 0

    def test_binding_kinetics_bounded_and_increasing(self):
        conc = np.array([1e-6])
        bound = np.array([0.0])
        new_bound = self.tracer.calculate_binding_kinetics(conc, bound, dt=1.0)
        assert np.all(new_bound >= 0.0) and np.all(new_bound <= 1.0)
        assert new_bound[0] > bound[0]

    def test_quantum_measurement_noise_in_range(self):
        noise = self.tracer.calculate_quantum_measurement_noise(
            measurement_volume=1e-15, measurement_time=1e-3
        )
        assert 1e-6 <= noise <= 1e-2

    def test_atp_consumption_nonnegative_and_capped(self):
        conc = np.full((4, 4, 4), 1e-7)
        activity = np.full((4, 4, 4), 5.0)
        total_rate, spatial = self.tracer.calculate_atp_consumption(conc, activity)
        cap = self.tracer.params.atp_turnover_rate * 0.1
        assert 0.0 <= total_rate <= cap + 1e-12
        assert spatial.shape == conc.shape
        assert np.all(np.isfinite(spatial))

    def test_information_extraction_metrics(self):
        # 4D histories: (time, nx, ny, nz)
        rng = np.random.default_rng(0)
        conc_hist = np.abs(rng.normal(1e-7, 1e-8, size=(5, 3, 3, 3)))
        neural_hist = np.abs(rng.normal(5.0, 1.0, size=(5, 3, 3, 3)))
        metrics = self.tracer.information_extraction(conc_hist, neural_hist)
        for key in (
            "spatial_resolution",
            "information_entropy",
            "mutual_information",
            "total_information_bits",
            "signal_to_noise_ratio",
        ):
            assert key in metrics
            assert np.isfinite(metrics[key])
        assert metrics["information_entropy"] >= 0.0

    def test_diffusion_advection_evolution_conserves_constraints(self):
        exp = NeuralTracerExperiment(TISSUE)
        grid, conc, _ = exp.create_test_scenario(grid_size=(6, 6, 6))
        velocity = np.zeros((*grid.shape[:-1], 3))
        results = exp.neural_tracer.diffusion_advection_evolution(
            initial_concentration=conc,
            velocity_field=velocity,
            spatial_grid=grid,
            time_steps=3,
            dt=1.0,
        )
        for key in (
            "concentration_history",
            "bound_fraction_history",
            "toxicity_history",
            "quantum_noise_history",
            "final_bbb_permeability",
        ):
            assert key in results
        history = results["concentration_history"]
        assert np.all(history >= 0.0)
        # Concentration stays within the Axiom A5 safety limit
        assert np.max(history) <= exp.neural_tracer.max_concentration + 1e-12


class TestNeuralTracerExperiment:
    def setup_method(self):
        self.exp = NeuralTracerExperiment(TISSUE)

    def test_create_test_scenario_shapes(self):
        grid, conc, neural = self.exp.create_test_scenario(grid_size=(8, 8, 4))
        assert grid.shape == (8, 8, 4, 3)
        assert conc.shape == (8, 8, 4)
        assert neural.shape == (8, 8, 4)
        assert np.all(conc >= 0.0)

    def test_run_neural_tracer_test_reports_status(self):
        results = self.exp.run_neural_tracer_test(simulation_time=2.0, dt=1.0)
        assert results["test_status"] in ("PASSED", "FAILED")
        assert "validation_results" in results
        for value in results["validation_results"].values():
            assert isinstance(value, ValidationResult)
        assert results["max_concentration"] >= 0.0

    def test_generate_biocompatibility_report(self):
        results = self.exp.run_neural_tracer_test(simulation_time=2.0, dt=1.0)
        report = self.exp.generate_biocompatibility_report(results)
        assert "BIOCOMPATIBLE NEURAL TRACER" in report
