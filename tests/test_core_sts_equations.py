"""
Comprehensive test suite for STS core equations module.
This test suite aims for 95%+ code coverage of sts_equations.py.
"""

import math
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from sensory_tracer_science.core.sts_equations import (
    STSState,
    ConservationOfSensoryInformation,
    TracerEnergyContinuity,
    WavePropagationWithAttenuation,
    STSSystemSolver,
    validate_equations
)
from sensory_tracer_science.core.sts_constants import K_B, STSPhysics, STSLimits


class TestSTSState:
    """Test the STSState dataclass functionality."""
    
    def test_sts_state_creation(self):
        """Test basic STSState creation and attribute access."""
        position = np.array([1.0, 2.0, 3.0])
        state = STSState(
            position=position,
            time=100.0,
            energy=1e-19,  # ~kT at 300K
            information_content=10.5,
            wave_amplitude=1.0 + 2.0j,
            entropy=1e-23,
            temperature=300.0
        )
        
        assert np.array_equal(state.position, position)
        assert state.time == 100.0
        assert state.energy == 1e-19
        assert state.information_content == 10.5
        assert state.wave_amplitude == 1.0 + 2.0j
        assert state.entropy == 1e-23
        assert state.temperature == 300.0
    
    def test_sts_state_numpy_arrays(self):
        """Test STSState with various numpy array configurations."""
        # 2D position
        state_2d = STSState(
            position=np.array([1.0, 2.0]),
            time=0.0,
            energy=0.0,
            information_content=0.0,
            wave_amplitude=0.0 + 0.0j,
            entropy=0.0,
            temperature=273.15
        )
        assert len(state_2d.position) == 2
        
        # Higher dimensional position (edge case)
        state_4d = STSState(
            position=np.array([1.0, 2.0, 3.0, 4.0]),
            time=0.0,
            energy=0.0,
            information_content=0.0,
            wave_amplitude=0.0 + 0.0j,
            entropy=0.0,
            temperature=273.15
        )
        assert len(state_4d.position) == 4


class TestConservationOfSensoryInformation:
    """Test the information conservation physics implementation."""
    
    def test_initialization_default_temperature(self):
        """Test default initialization with 300K temperature."""
        info_conservation = ConservationOfSensoryInformation()
        assert info_conservation.temperature == 300.0
        assert info_conservation.thermal_energy == K_B * 300.0
    
    def test_initialization_custom_temperature(self):
        """Test initialization with custom temperature."""
        custom_temp = 77.0  # Liquid nitrogen temperature
        info_conservation = ConservationOfSensoryInformation(temperature=custom_temp)
        assert info_conservation.temperature == custom_temp
        assert info_conservation.thermal_energy == K_B * custom_temp
    
    def test_information_density_basic(self):
        """Test information density calculation with normal values."""
        info_conservation = ConservationOfSensoryInformation(temperature=300.0)
        
        sensor_density = 1e20  # sensors per m³
        tracer_energy = K_B * 300.0  # kT
        
        density = info_conservation.information_density(sensor_density, tracer_energy)
        
        # Should be sensor_density * log2(1 + kT / kT) = sensor_density * log2(2) = sensor_density * 1
        expected = sensor_density * math.log2(2.0)
        assert abs(density - expected) < 1e-6
    
    def test_information_density_negative_energy_error(self):
        """Test that negative tracer energy raises ValueError."""
        info_conservation = ConservationOfSensoryInformation()
        
        with pytest.raises(ValueError, match="Tracer energy cannot be negative"):
            info_conservation.information_density(1.0, -1e-20)
    
    def test_information_density_very_small_energy(self):
        """Test information density with very small tracer energy."""
        info_conservation = ConservationOfSensoryInformation(temperature=300.0)
        
        # Energy much smaller than thermal energy
        tiny_energy = 1e-9 * info_conservation.thermal_energy
        density = info_conservation.information_density(1.0, tiny_energy)
        
        # Should return 0.0 to avoid numerical issues
        assert density == 0.0
    
    def test_information_density_zero_energy(self):
        """Test information density with exactly zero energy."""
        info_conservation = ConservationOfSensoryInformation()
        
        density = info_conservation.information_density(1.0, 0.0)
        assert density == 0.0
    
    def test_information_density_high_energy(self):
        """Test information density with high tracer energy."""
        info_conservation = ConservationOfSensoryInformation(temperature=300.0)
        
        high_energy = 1000 * info_conservation.thermal_energy
        density = info_conservation.information_density(1.0, high_energy)
        
        # Should be log2(1 + 1000) ≈ log2(1001)
        expected = math.log2(1 + 1000)
        assert abs(density - expected) < 1e-6
    
    def test_total_information_simple_case(self):
        """Test total information calculation with simple uniform fields."""
        info_conservation = ConservationOfSensoryInformation(temperature=300.0)
        
        # Create simple 2x2x2 grid
        sensor_field = np.ones((2, 2, 2)) * 1e20  # uniform sensor density
        energy_field = np.ones((2, 2, 2)) * K_B * 300.0  # uniform kT energy
        
        # Simple spatial grid with unit spacing
        x = np.linspace(0, 1, 2)
        y = np.linspace(0, 1, 2) 
        z = np.linspace(0, 1, 2)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        total_info = info_conservation.total_information(sensor_field, energy_field, spatial_grid)
        
        # Each voxel has volume 1*1*1 = 1, info density = 1e20 * log2(2) = 1e20
        # Total = 8 voxels * 1e20 = 8e20
        expected = 8 * 1e20 * math.log2(2.0)
        assert abs(total_info - expected) / expected < 1e-3
    
    def test_total_information_single_voxel(self):
        """Test total information with single voxel (edge case)."""
        info_conservation = ConservationOfSensoryInformation()
        
        sensor_field = np.array([[[1e20]]])
        energy_field = np.array([[[K_B * 300.0]]])
        
        # Single point grid
        spatial_grid = np.array([[[[0.0, 0.0, 0.0]]]])
        
        total_info = info_conservation.total_information(sensor_field, energy_field, spatial_grid)
        
        # Should use default volume element of 1.0
        expected = 1e20 * math.log2(2.0) * 1.0
        assert abs(total_info - expected) < 1e-6
    
    def test_total_information_varying_fields(self):
        """Test total information with spatially varying fields."""
        info_conservation = ConservationOfSensoryInformation(temperature=300.0)
        
        # Create 3x3x3 grid with varying values
        sensor_field = np.random.rand(3, 3, 3) * 1e20
        energy_field = np.random.rand(3, 3, 3) * K_B * 300.0
        
        x = np.linspace(0, 2, 3)
        y = np.linspace(0, 2, 3)
        z = np.linspace(0, 2, 3)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        total_info = info_conservation.total_information(sensor_field, energy_field, spatial_grid)
        
        # Should be finite and positive
        assert total_info > 0
        assert np.isfinite(total_info)


class TestTracerEnergyContinuity:
    """Test the tracer energy continuity equation implementation."""
    
    def test_initialization_default_models(self):
        """Test initialization with default dissipation and source models."""
        energy_continuity = TracerEnergyContinuity()
        
        assert hasattr(energy_continuity, 'dissipation_model')
        assert hasattr(energy_continuity, 'source_model')
        
        # Test default models
        test_pos = np.array([1.0, 2.0, 3.0])
        dissipation = energy_continuity.dissipation_model(1e-19, test_pos, 100.0)
        source = energy_continuity.source_model(test_pos, 100.0)
        
        assert dissipation > 0  # Default should have exponential decay
        assert source == 0.0  # Default should have no sources
    
    def test_initialization_custom_models(self):
        """Test initialization with custom models."""
        def custom_dissipation(energy, pos, time):
            return 0.5 * energy
        
        def custom_source(pos, time):
            return 1e-20 * math.sin(time)
        
        energy_continuity = TracerEnergyContinuity(
            dissipation_model=custom_dissipation,
            source_model=custom_source
        )
        
        test_pos = np.array([0.0, 0.0, 0.0])
        
        dissipation = energy_continuity.dissipation_model(1e-19, test_pos, 0.0)
        source = energy_continuity.source_model(test_pos, math.pi/2)
        
        assert abs(dissipation - 0.5e-19) < 1e-30
        assert abs(source - 1e-20) < 1e-30
    
    def test_default_dissipation_model(self):
        """Test the default exponential dissipation model."""
        energy_continuity = TracerEnergyContinuity()
        
        test_energy = 1e-19
        test_pos = np.array([0.0, 0.0, 0.0])
        test_time = 0.0
        
        dissipation = energy_continuity._default_dissipation(test_energy, test_pos, test_time)
        
        # Should be energy / tau where tau = 1e-6
        expected = test_energy / 1e-6
        assert abs(dissipation - expected) < 1e-30
    
    def test_default_source_model(self):
        """Test the default source model (zero sources)."""
        energy_continuity = TracerEnergyContinuity()
        
        test_pos = np.array([1.0, 1.0, 1.0])
        test_time = 123.456
        
        source = energy_continuity._default_source(test_pos, test_time)
        assert source == 0.0
    
    def test_energy_flux_divergence_uniform_flow(self):
        """Test flux divergence calculation with uniform velocity field."""
        energy_continuity = TracerEnergyContinuity()
        
        # Create 3x3x3 grid
        energy_field = np.ones((3, 3, 3)) * 1e-19
        
        # Uniform velocity in x-direction
        velocity_field = np.zeros((3, 3, 3, 3))
        velocity_field[:, :, :, 0] = 1.0  # vx = 1 m/s
        
        # Simple spatial grid
        x = np.linspace(0, 2, 3)
        y = np.linspace(0, 2, 3) 
        z = np.linspace(0, 2, 3)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        div_flux = energy_continuity.energy_flux_divergence(
            energy_field, velocity_field, spatial_grid
        )
        
        # For uniform energy and velocity, divergence should be zero
        # (except at boundaries where finite differences fail)
        center_div = div_flux[1, 1, 1]
        assert abs(center_div) < 1e-20
    
    def test_energy_flux_divergence_converging_flow(self):
        """Test flux divergence with converging velocity field."""
        energy_continuity = TracerEnergyContinuity()
        
        # Create 3x3x3 grid
        energy_field = np.ones((3, 3, 3)) * 1e-19
        
        # Converging velocity field: v_x = -x, v_y = -y, v_z = -z
        velocity_field = np.zeros((3, 3, 3, 3))
        
        x = np.linspace(-1, 1, 3)
        y = np.linspace(-1, 1, 3)
        z = np.linspace(-1, 1, 3)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        
        velocity_field[:, :, :, 0] = -xx  # vx = -x
        velocity_field[:, :, :, 1] = -yy  # vy = -y  
        velocity_field[:, :, :, 2] = -zz  # vz = -z
        
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        div_flux = energy_continuity.energy_flux_divergence(
            energy_field, velocity_field, spatial_grid
        )
        
        # For converging flow, divergence should be negative at center
        # ∇·v = -1 - 1 - 1 = -3, so ∇·(E*v) = E * ∇·v = -3E (approximately)
        center_div = div_flux[1, 1, 1]
        assert center_div < 0  # Should be negative (converging)
    
    def test_energy_flux_divergence_single_point(self):
        """Test flux divergence with single point (edge case)."""
        energy_continuity = TracerEnergyContinuity()
        
        energy_field = np.array([[[1e-19]]])
        velocity_field = np.array([[[[1.0, 0.0, 0.0]]]])
        spatial_grid = np.array([[[[0.0, 0.0, 0.0]]]])
        
        div_flux = energy_continuity.energy_flux_divergence(
            energy_field, velocity_field, spatial_grid
        )
        
        # Single point should have zero divergence
        assert div_flux[0, 0, 0] == 0.0
    
    def test_time_evolution_simple(self):
        """Test time evolution with simple energy field."""
        energy_continuity = TracerEnergyContinuity()
        
        # Initial energy field
        initial_energy = np.ones((3, 3, 3)) * 1e-19
        
        # Zero velocity field (no advection)
        velocity_field = np.zeros((3, 3, 3, 3))
        
        # Simple spatial grid
        x = np.linspace(0, 2, 3)
        y = np.linspace(0, 2, 3)
        z = np.linspace(0, 2, 3)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        dt = 1e-9  # 1 nanosecond
        time = 0.0
        
        new_energy = energy_continuity.time_evolution(
            initial_energy, velocity_field, spatial_grid, time, dt
        )
        
        # With default dissipation (tau = 1e-6), energy should decay
        # E(t+dt) ≈ E(t) * (1 - dt/tau)
        decay_factor = 1 - dt / 1e-6
        expected = initial_energy * decay_factor
        
        np.testing.assert_allclose(new_energy, expected, rtol=1e-3)
    
    def test_time_evolution_with_source(self):
        """Test time evolution with custom source term."""
        def constant_source(pos, time):
            return 1e-25  # Constant source power
        
        energy_continuity = TracerEnergyContinuity(source_model=constant_source)
        
        initial_energy = np.ones((2, 2, 2)) * 1e-19
        velocity_field = np.zeros((2, 2, 2, 3))
        
        x = np.linspace(0, 1, 2)
        y = np.linspace(0, 1, 2)
        z = np.linspace(0, 1, 2)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        dt = 1e-9
        time = 0.0
        
        new_energy = energy_continuity.time_evolution(
            initial_energy, velocity_field, spatial_grid, time, dt
        )
        
        # Energy should change due to both dissipation and source
        assert not np.allclose(new_energy, initial_energy)
        assert np.all(new_energy >= 0.0)  # Energy should remain non-negative
    
    def test_time_evolution_energy_conservation(self):
        """Test that energy remains non-negative."""
        # Create scenario that might lead to negative energy
        def high_dissipation(energy, pos, time):
            return 1e20 * energy  # Very high dissipation
        
        energy_continuity = TracerEnergyContinuity(dissipation_model=high_dissipation)
        
        initial_energy = np.ones((2, 2, 2)) * 1e-19
        velocity_field = np.zeros((2, 2, 2, 3))
        
        x = np.linspace(0, 1, 2)
        y = np.linspace(0, 1, 2)
        z = np.linspace(0, 1, 2)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        dt = 1e-6  # Large time step
        time = 0.0
        
        new_energy = energy_continuity.time_evolution(
            initial_energy, velocity_field, spatial_grid, time, dt
        )
        
        # Energy should be clipped to non-negative values
        assert np.all(new_energy >= 0.0)


class TestWavePropagationWithAttenuation:
    """Test the wave propagation equation implementation."""
    
    def test_initialization_valid_parameters(self):
        """Test initialization with valid wave parameters."""
        velocity = 2.0e8  # 200,000 km/s (less than c)
        attenuation = 1e-3
        refractive_index = 1.5
        
        wave_prop = WavePropagationWithAttenuation(velocity, attenuation, refractive_index)
        
        assert wave_prop.velocity == velocity
        assert wave_prop.attenuation == attenuation
        assert wave_prop.refractive_index == refractive_index
    
    def test_initialization_causality_violation(self):
        """Test that faster-than-light velocities are rejected."""
        with pytest.raises(ValueError, match="exceeds causality limit"):
            WavePropagationWithAttenuation(
                velocity=4e8,  # Faster than light in vacuum
                attenuation=1e-3,
                refractive_index=1.0
            )
    
    def test_initialization_vacuum_speed_of_light(self):
        """Test initialization with exactly the speed of light."""
        # Should work with speed slightly less than c
        wave_prop = WavePropagationWithAttenuation(
            velocity=2.99792457e8,  # Slightly less than exact c
            attenuation=1e-3,
            refractive_index=1.0
        )
        assert wave_prop.velocity == 2.99792457e8
    
    def test_initialization_medium_with_refractive_index(self):
        """Test initialization in medium with refractive index > 1."""
        # In medium with n=2, max speed should be c/2
        wave_prop = WavePropagationWithAttenuation(
            velocity=1.5e8,  # c/2 
            attenuation=1e-3,
            refractive_index=2.0
        )
        assert wave_prop.refractive_index == 2.0
    
    def test_laplacian_uniform_field(self):
        """Test Laplacian calculation for uniform field."""
        wave_prop = WavePropagationWithAttenuation(1e8, 1e-3)
        
        # Uniform field
        field = np.ones((3, 3, 3), dtype=complex) * (1.0 + 1.0j)
        
        x = np.linspace(0, 2, 3)
        y = np.linspace(0, 2, 3)
        z = np.linspace(0, 2, 3)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        laplacian = wave_prop.laplacian(field, spatial_grid)
        
        # Laplacian of uniform field should be zero (except at boundaries)
        center_laplacian = laplacian[1, 1, 1]
        assert abs(center_laplacian) < 1e-10
    
    def test_laplacian_quadratic_field(self):
        """Test Laplacian calculation for quadratic field."""
        wave_prop = WavePropagationWithAttenuation(1e8, 1e-3)
        
        # Create quadratic field: f(x,y,z) = x² + y² + z²
        x = np.linspace(-1, 1, 3)
        y = np.linspace(-1, 1, 3)
        z = np.linspace(-1, 1, 3)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        
        field = (xx**2 + yy**2 + zz**2).astype(complex)
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        laplacian = wave_prop.laplacian(field, spatial_grid)
        
        # Laplacian of (x² + y² + z²) should be 6 everywhere
        center_laplacian = laplacian[1, 1, 1]
        assert abs(center_laplacian - 6.0) < 0.1  # Allow for numerical error
    
    def test_laplacian_single_point(self):
        """Test Laplacian with single point field."""
        wave_prop = WavePropagationWithAttenuation(1e8, 1e-3)
        
        field = np.array([[[1.0 + 2.0j]]])
        spatial_grid = np.array([[[[0.0, 0.0, 0.0]]]])
        
        laplacian = wave_prop.laplacian(field, spatial_grid)
        
        # Single point should have zero Laplacian
        assert laplacian[0, 0, 0] == 0.0
    
    def test_time_evolution_free_wave(self):
        """Test time evolution of free wave without sources."""
        wave_prop = WavePropagationWithAttenuation(
            velocity=1e8,
            attenuation=1e-6  # Very small attenuation
        )
        
        # Initial Gaussian pulse
        x = np.linspace(-1, 1, 5)
        y = np.array([0])
        z = np.array([0])
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        
        # Gaussian profile
        sigma = 0.3
        psi = np.exp(-(xx**2) / (2 * sigma**2)).astype(complex)
        psi = psi.reshape((5, 1, 1))
        psi_dot = np.zeros_like(psi)
        
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        source_field = np.zeros_like(psi)
        
        dt = 1e-12  # Very small time step
        
        new_psi, new_psi_dot = wave_prop.time_evolution(
            psi, psi_dot, spatial_grid, source_field, dt
        )
        
        # Wave should evolve (not remain static)
        assert not np.allclose(new_psi, psi)
        assert not np.allclose(new_psi_dot, psi_dot)
    
    def test_time_evolution_with_source(self):
        """Test time evolution with source term."""
        wave_prop = WavePropagationWithAttenuation(1e8, 1e-3)
        
        # Simple 2x2x2 grid
        psi = np.zeros((2, 2, 2), dtype=complex)
        psi_dot = np.zeros_like(psi)
        
        x = np.linspace(0, 1, 2)
        y = np.linspace(0, 1, 2)
        z = np.linspace(0, 1, 2)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        # Constant source at center
        source_field = np.zeros_like(psi)
        source_field[0, 0, 0] = 1e20  # Strong source
        
        dt = 1e-12
        
        new_psi, new_psi_dot = wave_prop.time_evolution(
            psi, psi_dot, spatial_grid, source_field, dt
        )
        
        # Source should cause wave field to evolve
        assert np.any(new_psi != 0)
        assert np.any(new_psi_dot != 0)
    
    def test_time_evolution_damping(self):
        """Test wave damping due to attenuation."""
        wave_prop = WavePropagationWithAttenuation(
            velocity=1e8,
            attenuation=1e6  # Strong attenuation
        )
        
        # Initial wave with some energy
        psi = np.ones((3, 3, 3), dtype=complex) * (1.0 + 0.5j)
        psi_dot = np.ones((3, 3, 3), dtype=complex) * 0.1j
        
        x = np.linspace(0, 2, 3)
        y = np.linspace(0, 2, 3)
        z = np.linspace(0, 2, 3)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        source_field = np.zeros_like(psi)
        dt = 1e-9
        
        new_psi, new_psi_dot = wave_prop.time_evolution(
            psi, psi_dot, spatial_grid, source_field, dt
        )
        
        # Strong attenuation should reduce wave amplitude
        initial_amplitude = np.abs(psi_dot).max()
        final_amplitude = np.abs(new_psi_dot).max()
        assert final_amplitude < initial_amplitude
    
    def test_energy_density_calculation(self):
        """Test wave energy density calculation."""
        wave_prop = WavePropagationWithAttenuation(
            velocity=2e8,
            attenuation=1e-3
        )
        
        # Simple wave field
        psi = np.ones((2, 2, 2), dtype=complex) * (1.0 + 1.0j)
        psi_dot = np.ones((2, 2, 2), dtype=complex) * (0.5 - 0.3j)
        
        energy_density = wave_prop.energy_density(psi, psi_dot)
        
        # Energy density should be positive
        assert np.all(energy_density >= 0)
        
        # Check formula: (1/2) * (|∂ψ/∂t|² + v²|ψ|²)
        expected_kinetic = 0.5 * np.abs(psi_dot)**2
        expected_potential = 0.5 * (2e8)**2 * np.abs(psi)**2
        expected_total = expected_kinetic + expected_potential
        
        np.testing.assert_allclose(energy_density, expected_total, rtol=1e-10)
    
    def test_energy_density_zero_field(self):
        """Test energy density for zero field."""
        wave_prop = WavePropagationWithAttenuation(1e8, 1e-3)
        
        psi = np.zeros((2, 2, 2), dtype=complex)
        psi_dot = np.zeros((2, 2, 2), dtype=complex)
        
        energy_density = wave_prop.energy_density(psi, psi_dot)
        
        assert np.all(energy_density == 0.0)


class TestSTSSystemSolver:
    """Test the unified STS system solver."""
    
    def test_initialization_basic_parameters(self):
        """Test initialization with basic system parameters."""
        params = {
            "velocity": 1e8,
            "attenuation": 1e-3,
            "temperature": 300.0
        }
        
        solver = STSSystemSolver(params)
        
        assert solver.params == params
        assert hasattr(solver, 'info_conservation')
        assert hasattr(solver, 'energy_continuity')
        assert hasattr(solver, 'wave_propagation')
    
    def test_initialization_full_parameters(self):
        """Test initialization with complete parameter set."""
        def custom_dissipation(energy, pos, time):
            return 0.1 * energy
        
        def custom_source(pos, time):
            return 1e-22
        
        params = {
            "velocity": 2e8,
            "attenuation": 1e-4,
            "temperature": 273.15,
            "refractive_index": 1.33,
            "dissipation_model": custom_dissipation,
            "source_model": custom_source
        }
        
        solver = STSSystemSolver(params)
        
        assert solver.wave_propagation.velocity == 2e8
        assert solver.wave_propagation.refractive_index == 1.33
        assert solver.info_conservation.temperature == 273.15
    
    def test_evolve_system_basic(self):
        """Test basic system evolution."""
        params = {
            "velocity": 1e8,
            "attenuation": 1e-3,
            "temperature": 300.0
        }
        
        solver = STSSystemSolver(params)
        
        # Initial state
        initial_state = STSState(
            position=np.array([0.0, 0.0, 0.0]),
            time=0.0,
            energy=1e-19,
            information_content=10.0,
            wave_amplitude=1.0 + 0.0j,
            entropy=1e-23,
            temperature=300.0
        )
        
        # Simple 2x2x2 spatial grid
        x = np.linspace(0, 1, 2)
        y = np.linspace(0, 1, 2)
        z = np.linspace(0, 1, 2)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        time_steps = 3
        dt = 1e-9
        
        states = solver.evolve_system(initial_state, spatial_grid, time_steps, dt)
        
        # Should return initial state plus evolved states
        assert len(states) == time_steps + 1
        assert states[0] is initial_state
        
        # Later states should have different properties
        final_state = states[-1]
        assert final_state.time > initial_state.time
        assert final_state.position is not initial_state.position  # Different array
    
    def test_evolve_system_energy_evolution(self):
        """Test that energy evolves according to physics."""
        params = {
            "velocity": 1e8,
            "attenuation": 1e-3,
            "temperature": 300.0
        }
        
        solver = STSSystemSolver(params)
        
        initial_state = STSState(
            position=np.array([0.0, 0.0, 0.0]),
            time=0.0,
            energy=1e-18,  # Higher initial energy
            information_content=5.0,
            wave_amplitude=2.0 + 1.0j,
            entropy=1e-23,
            temperature=300.0
        )
        
        # Larger spatial grid for more realistic evolution
        x = np.linspace(-1, 1, 3)
        y = np.linspace(-1, 1, 3)
        z = np.linspace(-1, 1, 3)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        time_steps = 5
        dt = 1e-9
        
        states = solver.evolve_system(initial_state, spatial_grid, time_steps, dt)
        
        # Check that energy, information, and wave amplitude evolve
        energies = [state.energy for state in states]
        infos = [state.information_content for state in states]
        amplitudes = [abs(state.wave_amplitude) for state in states]
        
        # Should have some variation (not all identical)
        assert len(set(f"{e:.2e}" for e in energies)) > 1 or len(set(f"{i:.2e}" for i in infos)) > 1
    
    def test_evolve_system_single_step(self):
        """Test single-step evolution."""
        params = {
            "velocity": 5e7,
            "attenuation": 1e-4,
            "temperature": 200.0
        }
        
        solver = STSSystemSolver(params)
        
        initial_state = STSState(
            position=np.array([1.0, 2.0, 3.0]),
            time=100.0,
            energy=5e-20,
            information_content=1.0,
            wave_amplitude=0.5 + 0.8j,
            entropy=2e-24,
            temperature=200.0
        )
        
        # Single voxel
        spatial_grid = np.array([[[[0.0, 0.0, 0.0]]]])
        
        states = solver.evolve_system(initial_state, spatial_grid, time_steps=1, dt=1e-10)
        
        assert len(states) == 2
        assert states[1].time == initial_state.time + 1e-10


class TestValidationFunction:
    """Test the validation function."""
    
    def test_validate_equations_success(self):
        """Test that validation passes with correct physics."""
        results = validate_equations()
        
        assert "validation_status" in results
        assert results["validation_status"] == "PASSED"
        
        assert "info_density_test" in results
        assert results["info_density_test"] > 0
        
        assert "causality_check" in results
        assert results["causality_check"] == "PASSED"
        
        assert "ftl_rejection" in results
        assert results["ftl_rejection"] == "PASSED"
    
    def test_validate_equations_components(self):
        """Test individual components of validation."""
        results = validate_equations()
        
        # Information density should be positive
        info_density = results["info_density_test"]
        thermal_energy = STSPhysics.thermal_energy(300.0)
        expected_density = math.log2(1 + thermal_energy / thermal_energy)  # log2(2) = 1
        assert abs(info_density - expected_density) < 1e-6
        
        # Causality checks should pass
        assert results["causality_check"] == "PASSED"
        assert results["ftl_rejection"] == "PASSED"
    
    @patch('sensory_tracer_science.core.sts_equations.WavePropagationWithAttenuation')
    def test_validate_equations_causality_failure(self, mock_wave_prop):
        """Test validation when causality check fails."""
        # Mock the constructor to raise ValueError on first call (causality check)
        # but succeed on second call (FTL rejection test)
        mock_wave_prop.side_effect = [ValueError("velocity exceeds causality limit"), ValueError("FTL")]
        
        results = validate_equations()
        
        assert results["causality_check"] == "FAILED - velocity exceeds causality limit"
        assert results["ftl_rejection"] == "PASSED - correctly rejected FTL velocity"


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling throughout the module."""
    
    def test_information_density_extreme_values(self):
        """Test information density with extreme input values."""
        info_conservation = ConservationOfSensoryInformation(temperature=1.0)  # Very low temp
        
        # Very high sensor density
        huge_density = 1e50
        normal_energy = K_B * 1.0
        
        density = info_conservation.information_density(huge_density, normal_energy)
        assert np.isfinite(density)
        assert density > 0
        
        # Very small sensor density
        tiny_density = 1e-50
        density_small = info_conservation.information_density(tiny_density, normal_energy)
        assert density_small >= 0
        assert density_small < density  # Should be smaller
    
    def test_energy_continuity_zero_velocity(self):
        """Test energy continuity with zero velocity field."""
        energy_continuity = TracerEnergyContinuity()
        
        energy_field = np.ones((2, 2, 2)) * 1e-20
        velocity_field = np.zeros((2, 2, 2, 3))  # All zero velocities
        
        x = np.linspace(0, 1, 2)
        y = np.linspace(0, 1, 2)
        z = np.linspace(0, 1, 2)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        # Should work without errors
        div_flux = energy_continuity.energy_flux_divergence(
            energy_field, velocity_field, spatial_grid
        )
        assert np.all(div_flux == 0.0)  # Zero velocity → zero flux divergence
    
    def test_wave_propagation_complex_arithmetic(self):
        """Test wave propagation with complex wave fields."""
        wave_prop = WavePropagationWithAttenuation(1e8, 1e-3)
        
        # Complex wave with random phase
        psi = np.random.rand(3, 3, 3) * np.exp(1j * np.random.rand(3, 3, 3) * 2 * np.pi)
        psi_dot = np.random.rand(3, 3, 3) * np.exp(1j * np.random.rand(3, 3, 3) * 2 * np.pi)
        
        x = np.linspace(0, 2, 3)
        y = np.linspace(0, 2, 3)
        z = np.linspace(0, 2, 3)
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        spatial_grid = np.stack([xx, yy, zz], axis=-1)
        
        source_field = np.zeros_like(psi)
        dt = 1e-12
        
        # Should handle complex arithmetic correctly
        new_psi, new_psi_dot = wave_prop.time_evolution(
            psi, psi_dot, spatial_grid, source_field, dt
        )
        
        assert new_psi.dtype == complex
        assert new_psi_dot.dtype == complex
        assert np.all(np.isfinite(new_psi))
        assert np.all(np.isfinite(new_psi_dot))
    
    def test_sts_system_solver_missing_parameters(self):
        """Test system solver behavior with missing parameters."""
        # Missing required velocity parameter should cause error
        params = {
            "attenuation": 1e-3,
            "temperature": 300.0
        }
        
        with pytest.raises(KeyError):
            STSSystemSolver(params)
    
    def test_numerical_stability_small_time_steps(self):
        """Test numerical stability with very small time steps."""
        params = {
            "velocity": 1e8,
            "attenuation": 1e-3,
            "temperature": 300.0
        }
        
        solver = STSSystemSolver(params)
        
        initial_state = STSState(
            position=np.array([0.0, 0.0, 0.0]),
            time=0.0,
            energy=1e-20,
            information_content=1.0,
            wave_amplitude=1.0 + 0.0j,
            entropy=1e-24,
            temperature=300.0
        )
        
        spatial_grid = np.array([[[[0.0, 0.0, 0.0]]]])
        
        # Very small time step
        dt = 1e-15
        time_steps = 10
        
        states = solver.evolve_system(initial_state, spatial_grid, time_steps, dt)
        
        # Should complete without numerical errors
        assert len(states) == time_steps + 1
        for state in states:
            assert np.all(np.isfinite([state.energy, state.information_content]))
            assert np.isfinite(state.wave_amplitude)


if __name__ == "__main__":
    pytest.main([__file__])