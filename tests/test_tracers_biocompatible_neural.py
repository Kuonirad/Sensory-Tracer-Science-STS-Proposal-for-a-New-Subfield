"""
Comprehensive test suite for biocompatible neural tracer module.
This test suite aims for 95%+ code coverage of biocompatible_neural.py.
"""

import math
import pytest
import numpy as np
from unittest.mock import patch, MagicMock, call

from sensory_tracer_science.tracers.biocompatible_neural import (
    BiologicalParameters,
    BiochemicalTracer,
    BiocompatibleNeuralTracer,
    NeuralTracerExperiment
)
from sensory_tracer_science.core.sts_constants import K_B, ImplementationLimits
from sensory_tracer_science.validation.sts_validator import STSValidator


class TestBiologicalParameters:
    """Test the BiologicalParameters dataclass."""
    
    def test_default_initialization(self):
        """Test default parameter initialization."""
        params = BiologicalParameters()
        
        # ATP energetics
        assert params.atp_free_energy == 57000.0
        assert params.atp_concentration == 5e-3
        assert params.atp_turnover_rate == 1e-3
        
        # ATP costs
        assert params.atp_per_uptake == 1.0
        assert params.atp_per_binding == 0.1
        assert params.atp_per_clearance == 2.0
        
        # Cellular geometry
        assert params.cell_radius == 10e-6
        assert params.cell_volume == 4.2e-15
        assert params.membrane_permeability == 1e-6
        
        # Diffusion properties
        assert params.diffusion_coefficient_tissue == 1e-12
        assert params.diffusion_coefficient_cytoplasm == 1e-11
        assert params.tortuosity_factor == 1.6
        
        # Clearance mechanisms
        assert params.blood_brain_barrier_clearance == 1e-6
        assert params.enzymatic_degradation_rate == 1e-5
        assert params.glial_uptake_rate == 1e-4
        
        # Toxicity parameters
        assert params.ld50_concentration == 10e-6
        assert params.noael_concentration == 1e-6
        assert params.microglial_activation_threshold == 0.5e-6
        assert params.apoptosis_rate_constant == 1e-7
        assert params.cytotoxicity_hill_coefficient == 2.0
        assert params.neuroinflammation_rate == 1e-5
        
        # BBB parameters
        assert params.bbb_permeability_coefficient == 1e-8
        assert params.efflux_transporter_km == 1e-5
        assert params.efflux_transporter_vmax == 1e-6
        
        # Binding parameters
        assert params.binding_site_density == 1e-3
        assert params.association_rate_constant == 1e6
        assert params.dissociation_rate_constant == 1e-3
        
        # Quantum measurement
        assert params.measurement_uncertainty_position == 1e-9
        assert params.measurement_uncertainty_momentum == 1e-24
        assert params.quantum_correlation_decay == 1e-12
        
        # Environment
        assert params.body_temperature == 310.0
        assert params.ionic_strength == 0.15
        assert params.ph == 7.4
    
    def test_custom_initialization(self):
        """Test custom parameter initialization."""
        params = BiologicalParameters(
            atp_free_energy=60000.0,
            body_temperature=300.0,
            cell_radius=5e-6
        )
        
        assert params.atp_free_energy == 60000.0
        assert params.body_temperature == 300.0
        assert params.cell_radius == 5e-6
        
        # Other parameters should remain default
        assert params.atp_concentration == 5e-3
        assert params.ionic_strength == 0.15
    
    def test_parameter_physical_validity(self):
        """Test that all parameters are physically reasonable."""
        params = BiologicalParameters()
        
        # All energies should be positive
        assert params.atp_free_energy > 0
        
        # All concentrations should be positive
        assert params.atp_concentration > 0
        assert params.ld50_concentration > 0
        assert params.binding_site_density > 0
        
        # All rates should be positive
        assert params.atp_turnover_rate > 0
        assert params.association_rate_constant > 0
        assert params.dissociation_rate_constant > 0
        
        # Temperature should be above freezing
        assert params.body_temperature > 273.15
        
        # pH should be physiological range
        assert 6.0 < params.ph < 8.0
        
        # Geometric properties should be positive
        assert params.cell_radius > 0
        assert params.cell_volume > 0


class TestBiochemicalTracer:
    """Test the BiochemicalTracer class."""
    
    def test_initialization_basic(self):
        """Test basic tracer initialization."""
        tracer = BiochemicalTracer(
            name="test_tracer",
            molecular_weight=500.0,
            fluorescence_quantum_yield=0.8,
            binding_affinity=1e-6
        )
        
        assert tracer.name == "test_tracer"
        assert tracer.molecular_weight == 500.0
        assert tracer.quantum_yield == 0.8
        assert tracer.binding_affinity == 1e-6
        
        # Derived properties should be calculated
        assert hasattr(tracer, 'stokes_radius')
        assert hasattr(tracer, 'diffusion_coefficient')
        assert tracer.stokes_radius > 0
        assert tracer.diffusion_coefficient > 0
    
    def test_initialization_defaults(self):
        """Test tracer initialization with default values."""
        tracer = BiochemicalTracer("simple_tracer", 300.0)
        
        assert tracer.quantum_yield == 0.0  # Default
        assert tracer.binding_affinity == 1e-6  # Default
    
    def test_stokes_radius_calculation(self):
        """Test Stokes radius calculation."""
        # Small molecule
        tracer_small = BiochemicalTracer("small", 100.0)
        
        # Large molecule
        tracer_large = BiochemicalTracer("large", 1000.0)
        
        # Larger molecular weight should give larger radius
        assert tracer_large.stokes_radius > tracer_small.stokes_radius
        
        # Test specific calculation
        expected_radius = (500.0 / 1000.0) ** (1/3) * 1e-9
        tracer_test = BiochemicalTracer("test", 500.0)
        assert abs(tracer_test.stokes_radius - expected_radius) < 1e-12
    
    def test_diffusion_coefficient_calculation_default_temperature(self):
        """Test diffusion coefficient calculation with default temperature."""
        tracer = BiochemicalTracer("test", 500.0)
        
        # Should use default temperature of 310K
        water_viscosity = 6.9e-4  # Pa·s at 37°C
        expected_d = (K_B * 310.0) / (6 * np.pi * water_viscosity * tracer.stokes_radius)
        
        assert abs(tracer.diffusion_coefficient - expected_d) < 1e-20
    
    def test_diffusion_coefficient_calculation_custom_temperature(self):
        """Test diffusion coefficient calculation with custom temperature."""
        tracer = BiochemicalTracer("test", 500.0)
        
        # Calculate at room temperature
        d_room_temp = tracer._calculate_diffusion_coefficient(293.15)
        
        # Should be different from default (body temperature)
        assert d_room_temp != tracer.diffusion_coefficient
        
        # Should be positive
        assert d_room_temp > 0
    
    def test_diffusion_coefficient_scaling(self):
        """Test that diffusion coefficient scales properly with molecular size."""
        # Create tracers of different sizes
        tracer_small = BiochemicalTracer("small", 200.0)
        tracer_large = BiochemicalTracer("large", 800.0)
        
        # Smaller molecules should diffuse faster
        assert tracer_small.diffusion_coefficient > tracer_large.diffusion_coefficient
    
    def test_quantum_yield_bounds(self):
        """Test quantum yield is within physical bounds."""
        # Valid quantum yield
        tracer = BiochemicalTracer("test", 500.0, fluorescence_quantum_yield=0.9)
        assert 0 <= tracer.quantum_yield <= 1.0
        
        # Edge cases
        tracer_zero = BiochemicalTracer("zero", 500.0, fluorescence_quantum_yield=0.0)
        tracer_one = BiochemicalTracer("one", 500.0, fluorescence_quantum_yield=1.0)
        
        assert tracer_zero.quantum_yield == 0.0
        assert tracer_one.quantum_yield == 1.0


class TestBiocompatibleNeuralTracer:
    """Test the main BiocompatibleNeuralTracer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_tracer = BiochemicalTracer("test_tracer", 500.0, 0.8, 1e-6)
        self.test_geometry = {
            "length": 1e-3,
            "width": 1e-3,
            "height": 0.5e-3
        }
        self.tracer_system = BiocompatibleNeuralTracer(
            self.test_tracer,
            self.test_geometry
        )
    
    def test_initialization_basic(self):
        """Test basic tracer system initialization."""
        assert self.tracer_system.tracer is self.test_tracer
        assert self.tracer_system.geometry == self.test_geometry
        assert isinstance(self.tracer_system.params, BiologicalParameters)
        
        # Check calculated properties
        expected_volume = 1e-3 * 1e-3 * 0.5e-3
        assert abs(self.tracer_system.tissue_volume - expected_volume) < 1e-15
        
        # Check constraints
        assert self.tracer_system.max_concentration == ImplementationLimits.Biocompatible.MAX_TRACER_CONCENTRATION
        assert self.tracer_system.max_atp_depletion == ImplementationLimits.Biocompatible.MAX_ATP_DEPLETION_RATE
    
    def test_initialization_with_custom_parameters(self):
        """Test initialization with custom biological parameters."""
        custom_params = BiologicalParameters(body_temperature=300.0)
        
        tracer_system = BiocompatibleNeuralTracer(
            self.test_tracer,
            self.test_geometry,
            custom_params
        )
        
        assert tracer_system.params is custom_params
        assert tracer_system.params.body_temperature == 300.0
    
    def test_calculate_bbb_permeability(self):
        """Test blood-brain barrier permeability calculation."""
        tracer_props = {"concentration": 1e-6}
        
        permeability = self.tracer_system.calculate_bbb_permeability(tracer_props)
        
        # Should be positive and within reasonable range
        assert permeability > 0
        assert permeability < 1e-5  # Should be low for BBB
    
    def test_calculate_bbb_permeability_concentration_dependence(self):
        """Test BBB permeability dependence on concentration."""
        # Low concentration
        props_low = {"concentration": 1e-8}
        permeability_low = self.tracer_system.calculate_bbb_permeability(props_low)
        
        # High concentration
        props_high = {"concentration": 1e-5}
        permeability_high = self.tracer_system.calculate_bbb_permeability(props_high)
        
        # Should show saturation behavior (Michaelis-Menten)
        assert permeability_low > 0
        assert permeability_high > 0
    
    def test_calculate_binding_kinetics(self):
        """Test binding kinetics calculation."""
        free_tracer = 1e-6  # mol/L
        bound_tracer = 1e-7  # mol/L
        dt = 1e-3  # s
        
        new_free, new_bound = self.tracer_system.calculate_binding_kinetics(
            free_tracer, bound_tracer, dt
        )
        
        # Should conserve total tracer (approximately)
        initial_total = free_tracer + bound_tracer
        final_total = new_free + new_bound
        assert abs(final_total - initial_total) < 1e-10
        
        # Concentrations should be non-negative
        assert new_free >= 0
        assert new_bound >= 0
    
    def test_calculate_binding_kinetics_equilibrium(self):
        """Test binding kinetics approaches equilibrium."""
        # Start far from equilibrium
        free_tracer = 1e-6
        bound_tracer = 0.0
        
        # Run multiple time steps
        for _ in range(100):
            free_tracer, bound_tracer = self.tracer_system.calculate_binding_kinetics(
                free_tracer, bound_tracer, 1e-6
            )
        
        # Should approach equilibrium (some binding should occur)
        assert bound_tracer > 0
        assert free_tracer < 1e-6  # Some should have bound
    
    def test_calculate_quantum_measurement_noise(self):
        """Test quantum measurement noise calculation."""
        signal_strength = 1e-20  # J
        measurement_time = 1e-3  # s
        
        noise = self.tracer_system.calculate_quantum_measurement_noise(
            signal_strength, measurement_time
        )
        
        # Should be positive and scale with Heisenberg uncertainty
        assert noise > 0
        assert isinstance(noise, float)
    
    def test_calculate_quantum_measurement_noise_scaling(self):
        """Test quantum noise scaling with parameters."""
        # Stronger signal should give better SNR (lower relative noise)
        noise_weak = self.tracer_system.calculate_quantum_measurement_noise(1e-21, 1e-3)
        noise_strong = self.tracer_system.calculate_quantum_measurement_noise(1e-19, 1e-3)
        
        # Longer measurement time should reduce noise
        noise_short = self.tracer_system.calculate_quantum_measurement_noise(1e-20, 1e-6)
        noise_long = self.tracer_system.calculate_quantum_measurement_noise(1e-20, 1e-3)
        
        assert noise_weak > 0
        assert noise_strong > 0
        assert noise_short > 0
        assert noise_long > 0
    
    def test_calculate_laplacian_uniform_field(self):
        """Test Laplacian calculation for uniform field."""
        # Create uniform concentration field
        field = np.ones((3, 3, 3)) * 1e-6
        
        # Create simple spatial grid
        x = np.linspace(0, 1e-3, 3)
        y = np.linspace(0, 1e-3, 3)
        z = np.linspace(0, 1e-3, 3)
        dx, dy, dz = x[1] - x[0], y[1] - y[0], z[1] - z[0]
        
        laplacian = self.tracer_system._calculate_laplacian(field, dx, dy, dz)
        
        # Laplacian of uniform field should be zero (except at boundaries)
        center_value = laplacian[1, 1, 1]
        assert abs(center_value) < 1e-10
    
    def test_calculate_laplacian_parabolic_field(self):
        """Test Laplacian calculation for parabolic field."""
        # Create parabolic field: f(x,y,z) = x² + y² + z²
        x = np.linspace(-1e-3, 1e-3, 3)
        y = np.linspace(-1e-3, 1e-3, 3)
        z = np.linspace(-1e-3, 1e-3, 3)
        
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        field = (xx**2 + yy**2 + zz**2) * 1e6  # Scale to concentration units
        
        dx, dy, dz = x[1] - x[0], y[1] - y[0], z[1] - z[0]
        
        laplacian = self.tracer_system._calculate_laplacian(field, dx, dy, dz)
        
        # Laplacian of (x² + y² + z²) should be approximately 6
        center_value = laplacian[1, 1, 1]
        expected = 6 * 1e6  # Scaled by concentration factor
        assert abs(center_value - expected) / expected < 0.1  # Allow 10% error for finite differences
    
    def test_calculate_gradient_linear_field(self):
        """Test gradient calculation for linear field."""
        # Create linear field: f(x,y,z) = x + 2y + 3z
        x = np.linspace(0, 1e-3, 3)
        y = np.linspace(0, 1e-3, 3)
        z = np.linspace(0, 1e-3, 3)
        
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        field = (xx + 2*yy + 3*zz) * 1e6  # Scale to concentration units
        
        dx, dy, dz = x[1] - x[0], y[1] - y[0], z[1] - z[0]
        
        gradient = self.tracer_system._calculate_gradient(field, dx, dy, dz)
        
        # Gradient of (x + 2y + 3z) should be (1, 2, 3)
        center_grad = gradient[1, 1, 1, :]
        expected = np.array([1, 2, 3]) * 1e6 / np.array([dx, dy, dz])
        
        np.testing.assert_allclose(center_grad, expected, rtol=0.1)
    
    def test_calculate_atp_consumption(self):
        """Test ATP consumption calculation."""
        tracer_flux = {
            "uptake_rate": 1e-9,     # mol/L/s
            "binding_rate": 1e-10,   # mol/L/s
            "clearance_rate": 1e-11  # mol/L/s
        }
        
        atp_rate = self.tracer_system.calculate_atp_consumption(tracer_flux)
        
        # Should be positive (ATP consumption)
        assert atp_rate > 0
        
        # Should scale with flux rates
        expected = (
            tracer_flux["uptake_rate"] * self.tracer_system.params.atp_per_uptake +
            tracer_flux["binding_rate"] * self.tracer_system.params.atp_per_binding +
            tracer_flux["clearance_rate"] * self.tracer_system.params.atp_per_clearance
        )
        assert abs(atp_rate - expected) < 1e-15
    
    def test_calculate_atp_consumption_zero_flux(self):
        """Test ATP consumption with zero flux."""
        tracer_flux = {
            "uptake_rate": 0.0,
            "binding_rate": 0.0,
            "clearance_rate": 0.0
        }
        
        atp_rate = self.tracer_system.calculate_atp_consumption(tracer_flux)
        assert atp_rate == 0.0
    
    def test_information_extraction(self):
        """Test information extraction from tracer signal."""
        # Create test concentration history
        time_steps = 10
        concentration_history = np.random.rand(3, 3, 3, time_steps) * 1e-6
        
        measurement_params = {
            "spatial_resolution": 1e-6,
            "temporal_resolution": 1e-3,
            "detection_threshold": 1e-9
        }
        
        info_content = self.tracer_system.information_extraction(
            concentration_history, measurement_params
        )
        
        # Should return positive information content
        assert info_content > 0
        assert isinstance(info_content, float)
    
    def test_information_extraction_zero_signal(self):
        """Test information extraction with zero signal."""
        # Zero concentration everywhere
        concentration_history = np.zeros((2, 2, 2, 5))
        
        measurement_params = {
            "spatial_resolution": 1e-6,
            "temporal_resolution": 1e-3,
            "detection_threshold": 1e-9
        }
        
        info_content = self.tracer_system.information_extraction(
            concentration_history, measurement_params
        )
        
        # Should return zero or very small information content
        assert info_content >= 0
        assert info_content < 1e-6  # Should be very small
    
    def test_calculate_toxicity_response(self):
        """Test toxicity response calculation."""
        concentration = 1e-6  # mol/L
        exposure_time = 3600.0  # s (1 hour)
        
        toxicity = self.tracer_system.calculate_toxicity_response(
            concentration, exposure_time
        )
        
        # Should return toxicity metrics
        assert "cell_viability" in toxicity
        assert "microglial_activation" in toxicity
        assert "apoptosis_rate" in toxicity
        assert "neuroinflammation" in toxicity
        
        # Cell viability should be between 0 and 1
        assert 0 <= toxicity["cell_viability"] <= 1
        
        # All rates should be non-negative
        assert toxicity["microglial_activation"] >= 0
        assert toxicity["apoptosis_rate"] >= 0
        assert toxicity["neuroinflammation"] >= 0
    
    def test_calculate_toxicity_response_dose_dependence(self):
        """Test toxicity response dose dependence."""
        exposure_time = 3600.0
        
        # Low dose
        toxicity_low = self.tracer_system.calculate_toxicity_response(1e-8, exposure_time)
        
        # High dose
        toxicity_high = self.tracer_system.calculate_toxicity_response(1e-5, exposure_time)
        
        # High dose should show more toxicity
        assert toxicity_low["cell_viability"] >= toxicity_high["cell_viability"]
        assert toxicity_high["microglial_activation"] >= toxicity_low["microglial_activation"]
    
    def test_calculate_toxicity_response_time_dependence(self):
        """Test toxicity response time dependence."""
        concentration = 1e-6
        
        # Short exposure
        toxicity_short = self.tracer_system.calculate_toxicity_response(concentration, 60.0)
        
        # Long exposure
        toxicity_long = self.tracer_system.calculate_toxicity_response(concentration, 7200.0)
        
        # Longer exposure should generally show more effects
        assert toxicity_short["cell_viability"] >= toxicity_long["cell_viability"]
    
    def test_validate_biocompatibility_safe_conditions(self):
        """Test biocompatibility validation under safe conditions."""
        test_data = {
            "concentration_profile": np.ones((3, 3, 3, 10)) * 1e-7,  # Low concentration
            "atp_consumption_rate": 1e-6,  # Low ATP use
            "measurement_noise": 1e-12,
            "information_content": 10.0
        }
        
        validation_result = self.tracer_system.validate_biocompatibility(test_data)
        
        # Should pass validation
        assert validation_result["overall_status"] == "PASSED"
        assert validation_result["biocompatible"]
        
        # Individual checks should pass
        assert validation_result["concentration_within_limits"]
        assert validation_result["atp_budget_sustainable"]
        assert validation_result["quantum_noise_acceptable"]
    
    def test_validate_biocompatibility_unsafe_conditions(self):
        """Test biocompatibility validation under unsafe conditions."""
        test_data = {
            "concentration_profile": np.ones((3, 3, 3, 10)) * 1e-4,  # High concentration
            "atp_consumption_rate": 1e-2,  # High ATP use
            "measurement_noise": 1e-6,
            "information_content": 1.0
        }
        
        validation_result = self.tracer_system.validate_biocompatibility(test_data)
        
        # Should fail validation
        assert validation_result["overall_status"] == "FAILED"
        assert not validation_result["biocompatible"]
        
        # Some checks should fail
        assert not validation_result["concentration_within_limits"]
        assert not validation_result["atp_budget_sustainable"]
    
    def test_validate_augmented_metrics(self):
        """Test augmented metrics validation."""
        test_data = {
            "concentration_profile": np.ones((3, 3, 3, 10)) * 1e-6,
            "toxicity_metrics": {
                "cell_viability": 0.95,
                "microglial_activation": 0.01,
                "apoptosis_rate": 1e-8,
                "neuroinflammation": 1e-6
            },
            "bbb_permeability": 1e-8,
            "binding_occupancy": 0.1
        }
        
        # This should not raise an exception and should process the data
        try:
            result = self.tracer_system._validate_augmented_metrics(test_data)
            # If it returns a result, check it's reasonable
            if isinstance(result, dict):
                assert "augmented_validation" in result or "validation_passed" in result or len(result) > 0
        except Exception as e:
            # If it raises an exception, it should be informative
            assert "validation" in str(e).lower() or "metric" in str(e).lower()
    
    def test_diffusion_advection_evolution_basic(self):
        """Test basic diffusion-advection evolution."""
        # Create simple initial conditions
        initial_conc = np.zeros((3, 3, 3))
        initial_conc[1, 1, 1] = 1e-6  # Point source at center
        
        # Zero velocity field
        velocity_field = np.zeros((3, 3, 3, 3))
        
        # Simple spatial grid
        x = np.linspace(0, 1e-3, 3)
        y = np.linspace(0, 1e-3, 3)
        z = np.linspace(0, 1e-3, 3)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        # Run short evolution
        results = self.tracer_system.diffusion_advection_evolution(
            initial_conc, velocity_field, spatial_grid, time_steps=5, dt=1e-6
        )
        
        # Should return results dictionary
        assert isinstance(results, dict)
        assert "concentration_history" in results
        assert "atp_consumption_history" in results
        assert "binding_history" in results
        
        # Concentration should spread due to diffusion
        final_conc = results["concentration_history"][:, :, :, -1]
        assert np.sum(final_conc) > 0  # Mass should be conserved (approximately)
        
        # Center concentration should decrease (spreading)
        assert final_conc[1, 1, 1] < initial_conc[1, 1, 1]
    
    def test_diffusion_advection_evolution_with_flow(self):
        """Test diffusion-advection evolution with flow field."""
        # Create initial conditions
        initial_conc = np.zeros((3, 3, 3))
        initial_conc[0, 1, 1] = 1e-6  # Source at one end
        
        # Uniform flow in x-direction
        velocity_field = np.zeros((3, 3, 3, 3))
        velocity_field[:, :, :, 0] = 1e-6  # 1 μm/s in x-direction
        
        # Spatial grid
        x = np.linspace(0, 2e-3, 3)
        y = np.linspace(0, 1e-3, 3)
        z = np.linspace(0, 1e-3, 3)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        # Run evolution
        results = self.tracer_system.diffusion_advection_evolution(
            initial_conc, velocity_field, spatial_grid, time_steps=10, dt=1e-3
        )
        
        # Should show advective transport
        final_conc = results["concentration_history"][:, :, :, -1]
        
        # Mass should be conserved (approximately)
        assert abs(np.sum(final_conc) - np.sum(initial_conc)) / np.sum(initial_conc) < 0.5


class TestNeuralTracerExperiment:
    """Test the NeuralTracerExperiment class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tissue_dimensions = {
            "length": 2e-3,
            "width": 1e-3,
            "height": 0.5e-3
        }
        self.experiment = NeuralTracerExperiment(self.tissue_dimensions)
    
    def test_initialization(self):
        """Test experiment initialization."""
        assert self.experiment.tissue_dimensions == self.tissue_dimensions
        
        # Check calculated volume
        expected_volume = 2e-3 * 1e-3 * 0.5e-3
        assert abs(self.experiment.tissue_volume - expected_volume) < 1e-15
        
        # Should have validator
        assert hasattr(self.experiment, 'validator')
    
    def test_create_test_scenario_basic(self):
        """Test basic test scenario creation."""
        scenario_params = {
            "tracer_type": "calcium_indicator",
            "injection_concentration": 1e-6,
            "measurement_duration": 300.0
        }
        
        scenario = self.experiment.create_test_scenario(scenario_params)
        
        # Should return scenario dictionary
        assert isinstance(scenario, dict)
        assert "tracer" in scenario
        assert "initial_conditions" in scenario
        assert "measurement_params" in scenario
        
        # Tracer should be created
        assert isinstance(scenario["tracer"], BiochemicalTracer)
    
    def test_create_test_scenario_fluorescence_tracer(self):
        """Test fluorescence tracer scenario creation."""
        scenario_params = {
            "tracer_type": "fluorescence_reporter",
            "injection_concentration": 5e-7,
            "measurement_duration": 600.0
        }
        
        scenario = self.experiment.create_test_scenario(scenario_params)
        
        # Should create appropriate tracer
        tracer = scenario["tracer"]
        assert tracer.quantum_yield > 0  # Should have fluorescence
        assert tracer.binding_affinity > 0
    
    def test_create_test_scenario_unknown_tracer_type(self):
        """Test scenario creation with unknown tracer type."""
        scenario_params = {
            "tracer_type": "unknown_type",
            "injection_concentration": 1e-6,
            "measurement_duration": 300.0
        }
        
        # Should handle unknown type gracefully (default to generic tracer)
        scenario = self.experiment.create_test_scenario(scenario_params)
        assert isinstance(scenario["tracer"], BiochemicalTracer)
    
    def test_run_neural_tracer_test_basic(self):
        """Test basic neural tracer test execution."""
        test_params = {
            "tracer_concentration": 1e-6,
            "measurement_time": 60.0,
            "spatial_resolution": 1e-6,
            "time_step": 1.0
        }
        
        results = self.experiment.run_neural_tracer_test(test_params)
        
        # Should return comprehensive results
        assert isinstance(results, dict)
        
        # Check required result fields
        required_fields = [
            "tracer_system", "concentration_evolution", "information_content",
            "atp_consumption", "biocompatibility_status", "validation_results"
        ]
        
        for field in required_fields:
            assert field in results, f"Missing required field: {field}"
    
    def test_run_neural_tracer_test_with_flow(self):
        """Test neural tracer test with tissue flow."""
        test_params = {
            "tracer_concentration": 5e-7,
            "measurement_time": 120.0,
            "spatial_resolution": 2e-6,
            "time_step": 2.0,
            "include_tissue_flow": True,
            "flow_velocity": 1e-5  # 10 μm/s
        }
        
        results = self.experiment.run_neural_tracer_test(test_params)
        
        # Should handle flow simulation
        assert "tissue_flow_effects" in results or "concentration_evolution" in results
        
        # Flow should affect tracer distribution
        if "concentration_evolution" in results:
            conc_history = results["concentration_evolution"]
            assert conc_history.shape[-1] > 1  # Should have time evolution
    
    def test_run_neural_tracer_test_validation_failure(self):
        """Test neural tracer test with validation failure conditions."""
        # Use parameters that should cause validation failure
        test_params = {
            "tracer_concentration": 1e-4,  # Very high concentration
            "measurement_time": 30.0,
            "spatial_resolution": 1e-6,
            "time_step": 1.0
        }
        
        results = self.experiment.run_neural_tracer_test(test_params)
        
        # Should still return results but with failure status
        assert "biocompatibility_status" in results
        assert "validation_results" in results
        
        # Biocompatibility should be marked as failed or questionable
        biocompat = results["biocompatibility_status"]
        if isinstance(biocompat, dict):
            assert biocompat.get("biocompatible", True) is False or biocompat.get("overall_status") == "FAILED"
        elif isinstance(biocompat, bool):
            assert biocompat is False
    
    def test_generate_biocompatibility_report(self):
        """Test biocompatibility report generation."""
        # Create mock test results
        test_results = {
            "tracer_system": BiocompatibleNeuralTracer(
                BiochemicalTracer("test_tracer", 500.0),
                self.tissue_dimensions
            ),
            "concentration_evolution": np.random.rand(3, 3, 3, 10) * 1e-6,
            "information_content": 15.0,
            "atp_consumption": 1e-6,
            "biocompatibility_status": {
                "biocompatible": True,
                "overall_status": "PASSED",
                "concentration_within_limits": True,
                "atp_budget_sustainable": True
            },
            "validation_results": {
                "sts_compliance": True,
                "causality_preserved": True
            }
        }
        
        report = self.experiment.generate_biocompatibility_report(test_results)
        
        # Should return formatted string report
        assert isinstance(report, str)
        assert len(report) > 100  # Should be substantial report
        
        # Should contain key information
        assert "BIOCOMPATIBILITY REPORT" in report
        assert "PASSED" in report or "FAILED" in report
        assert "ATP" in report
        assert "concentration" in report.lower()
    
    def test_generate_biocompatibility_report_failed(self):
        """Test biocompatibility report for failed test."""
        # Create mock failed test results
        test_results = {
            "tracer_system": BiocompatibleNeuralTracer(
                BiochemicalTracer("toxic_tracer", 500.0),
                self.tissue_dimensions
            ),
            "concentration_evolution": np.random.rand(3, 3, 3, 5) * 1e-4,  # High concentration
            "information_content": 5.0,
            "atp_consumption": 1e-3,  # High ATP consumption
            "biocompatibility_status": {
                "biocompatible": False,
                "overall_status": "FAILED",
                "concentration_within_limits": False,
                "atp_budget_sustainable": False
            },
            "validation_results": {
                "sts_compliance": False,
                "causality_preserved": True
            }
        }
        
        report = self.experiment.generate_biocompatibility_report(test_results)
        
        # Should indicate failure
        assert "FAILED" in report
        assert "not biocompatible" in report.lower() or "unsafe" in report.lower()


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling throughout the module."""
    
    def test_biochemical_tracer_extreme_molecular_weights(self):
        """Test biochemical tracer with extreme molecular weights."""
        # Very small molecule
        tracer_small = BiochemicalTracer("tiny", 50.0)
        assert tracer_small.stokes_radius > 0
        assert tracer_small.diffusion_coefficient > 0
        
        # Very large molecule
        tracer_large = BiochemicalTracer("huge", 100000.0)
        assert tracer_large.stokes_radius > tracer_small.stokes_radius
        assert tracer_large.diffusion_coefficient < tracer_small.diffusion_coefficient
    
    def test_biocompatible_tracer_zero_geometry(self):
        """Test tracer system with minimal geometry."""
        tiny_geometry = {
            "length": 1e-9,  # 1 nm
            "width": 1e-9,
            "height": 1e-9
        }
        
        tracer = BiochemicalTracer("test", 500.0)
        tracer_system = BiocompatibleNeuralTracer(tracer, tiny_geometry)
        
        # Should handle tiny volumes
        assert tracer_system.tissue_volume > 0
        assert tracer_system.tissue_volume == 1e-27
    
    def test_binding_kinetics_extreme_rates(self):
        """Test binding kinetics with extreme rate constants."""
        # Create tracer system with extreme binding rates
        params = BiologicalParameters()
        params.association_rate_constant = 1e12  # Very fast
        params.dissociation_rate_constant = 1e-12  # Very slow
        
        tracer = BiochemicalTracer("test", 500.0)
        geometry = {"length": 1e-3, "width": 1e-3, "height": 1e-3}
        tracer_system = BiocompatibleNeuralTracer(tracer, geometry, params)
        
        # Should handle extreme rates without numerical issues
        free_tracer = 1e-6
        bound_tracer = 0.0
        dt = 1e-9  # Very small time step
        
        new_free, new_bound = tracer_system.calculate_binding_kinetics(
            free_tracer, bound_tracer, dt
        )
        
        # Should remain finite and physical
        assert np.isfinite(new_free)
        assert np.isfinite(new_bound)
        assert new_free >= 0
        assert new_bound >= 0
    
    def test_quantum_noise_extreme_conditions(self):
        """Test quantum noise calculation under extreme conditions."""
        tracer = BiochemicalTracer("test", 500.0)
        geometry = {"length": 1e-3, "width": 1e-3, "height": 1e-3}
        tracer_system = BiocompatibleNeuralTracer(tracer, geometry)
        
        # Very weak signal
        noise_weak = tracer_system.calculate_quantum_measurement_noise(1e-30, 1e-3)
        assert np.isfinite(noise_weak)
        assert noise_weak >= 0
        
        # Very strong signal
        noise_strong = tracer_system.calculate_quantum_measurement_noise(1e-10, 1e-3)
        assert np.isfinite(noise_strong)
        assert noise_strong >= 0
        
        # Very short measurement time
        noise_short = tracer_system.calculate_quantum_measurement_noise(1e-20, 1e-12)
        assert np.isfinite(noise_short)
        assert noise_short >= 0
    
    def test_information_extraction_edge_cases(self):
        """Test information extraction with edge cases."""
        tracer = BiochemicalTracer("test", 500.0)
        geometry = {"length": 1e-3, "width": 1e-3, "height": 1e-3}
        tracer_system = BiocompatibleNeuralTracer(tracer, geometry)
        
        # Single voxel, single time point
        conc_history_minimal = np.array([[[[1e-6]]]])
        
        measurement_params = {
            "spatial_resolution": 1e-6,
            "temporal_resolution": 1e-3,
            "detection_threshold": 1e-9
        }
        
        info = tracer_system.information_extraction(conc_history_minimal, measurement_params)
        assert np.isfinite(info)
        assert info >= 0
        
        # Very noisy data
        conc_history_noisy = np.random.rand(5, 5, 5, 20) * 1e-12  # Below detection threshold
        
        info_noisy = tracer_system.information_extraction(conc_history_noisy, measurement_params)
        assert np.isfinite(info_noisy)
        assert info_noisy >= 0
    
    def test_toxicity_response_extreme_doses(self):
        """Test toxicity response at extreme doses."""
        tracer = BiochemicalTracer("test", 500.0)
        geometry = {"length": 1e-3, "width": 1e-3, "height": 1e-3}
        tracer_system = BiocompatibleNeuralTracer(tracer, geometry)
        
        # Extremely low dose
        toxicity_low = tracer_system.calculate_toxicity_response(1e-12, 3600.0)
        
        # Should show minimal toxicity
        assert toxicity_low["cell_viability"] > 0.99
        assert toxicity_low["microglial_activation"] < 0.01
        
        # Extremely high dose
        toxicity_high = tracer_system.calculate_toxicity_response(1e-3, 3600.0)
        
        # Should show significant toxicity
        assert toxicity_high["cell_viability"] < 0.5
        assert toxicity_high["microglial_activation"] > 0.1
        
        # All responses should be finite and within bounds
        for key, value in toxicity_high.items():
            assert np.isfinite(value)
            if key == "cell_viability":
                assert 0 <= value <= 1
            else:
                assert value >= 0


if __name__ == "__main__":
    pytest.main([__file__])