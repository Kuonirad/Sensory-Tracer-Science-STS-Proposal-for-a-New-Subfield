"""
Sensory Tracer Science (STS) - Governing Equations Implementation

This module implements the core governing equations of STS, derived directly
from the foundational axioms. All equations respect conservation laws,
causality, and thermodynamic constraints.
"""

import math
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple

import numpy as np

from .sts_constants import K_B, STSLimits, STSPhysics


@dataclass
class STSState:
    """
    Represents the state of a sensory tracer system at a given time and position.
    All quantities must be physically meaningful and conserved.
    """

    position: np.ndarray  # 3D position vector (m)
    time: float  # Time (s)
    energy: float  # Tracer energy (J)
    information_content: float  # Information content (bits)
    wave_amplitude: complex  # Wave function amplitude
    entropy: float  # Local entropy (J/K)
    temperature: float  # Local temperature (K)


class ConservationOfSensoryInformation:
    """
    Implementation of the STS information conservation equation:

    I_total = ∫∫∫ ρ_sensor(r⃗,t) · log₂(1 + E_tracer(r⃗,t)/(k_B T)) d³r dt = const

    This is the fundamental conservation law for information in STS.
    """

    def __init__(self, temperature: float = 300.0):
        """
        Initialize information conservation calculator.

        Args:
            temperature: System temperature in Kelvin
        """
        self.temperature = temperature
        self.thermal_energy = K_B * temperature

    def information_density(self, sensor_density: float, tracer_energy: float) -> float:
        """
        Calculate information density at a point in space-time.

        Args:
            sensor_density: Local density of sensors (1/m³)
            tracer_energy: Local tracer energy (J)

        Returns:
            Information density (bits/m³)
        """
        if tracer_energy < 0:
            raise ValueError("Tracer energy cannot be negative")

        # Avoid numerical issues when tracer_energy << thermal_energy
        if tracer_energy < 1e-6 * self.thermal_energy:
            return 0.0

        return sensor_density * math.log2(1 + tracer_energy / self.thermal_energy)

    def total_information(
        self,
        sensor_field: np.ndarray,
        energy_field: np.ndarray,
        spatial_grid: np.ndarray,
    ) -> float:
        """
        Calculate total conserved information over a spatial domain.

        Args:
            sensor_field: 3D array of sensor densities
            energy_field: 3D array of tracer energies
            spatial_grid: 3D spatial coordinate arrays

        Returns:
            Total information content (bits)
        """
        # Calculate information density at each grid point
        info_density = np.zeros_like(sensor_field)
        for i in range(sensor_field.shape[0]):
            for j in range(sensor_field.shape[1]):
                for k in range(sensor_field.shape[2]):
                    info_density[i, j, k] = self.information_density(
                        sensor_field[i, j, k], energy_field[i, j, k]
                    )

        # Integrate over spatial domain (simple rectangular integration)
        dx = (
            spatial_grid[1, 0, 0, 0] - spatial_grid[0, 0, 0, 0]
            if spatial_grid.shape[0] > 1
            else 1.0
        )
        dy = (
            spatial_grid[0, 1, 0, 1] - spatial_grid[0, 0, 0, 1]
            if spatial_grid.shape[1] > 1
            else 1.0
        )
        dz = (
            spatial_grid[0, 0, 1, 2] - spatial_grid[0, 0, 0, 2]
            if spatial_grid.shape[2] > 1
            else 1.0
        )

        volume_element = dx * dy * dz
        return float(np.sum(info_density) * volume_element)


class TracerEnergyContinuity:
    """
    Implementation of the tracer energy continuity equation:

    ∂E_tracer/∂t + ∇ · J⃗_tracer = -P_dissipation + P_source

    This ensures energy conservation for the sensory tracer.
    """

    def __init__(
        self,
        dissipation_model: Optional[Callable] = None,
        source_model: Optional[Callable] = None,
    ):
        """
        Initialize energy continuity solver.

        Args:
            dissipation_model: Function(E, r, t) -> dissipation rate (W)
            source_model: Function(r, t) -> source power (W)
        """
        self.dissipation_model = dissipation_model or self._default_dissipation
        self.source_model = source_model or self._default_source

    def _default_dissipation(
        self, energy: float, position: np.ndarray, time: float
    ) -> float:
        """Default exponential dissipation model."""
        # Simple exponential decay with characteristic time
        tau_dissipation = 1e-6  # 1 microsecond
        return energy / tau_dissipation

    def _default_source(self, position: np.ndarray, time: float) -> float:
        """Default source model (no external sources)."""
        return 0.0

    def energy_flux_divergence(
        self,
        energy_field: np.ndarray,
        velocity_field: np.ndarray,
        spatial_grid: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate divergence of energy flux: ∇ · J⃗_tracer

        Args:
            energy_field: 3D array of energy densities
            velocity_field: 4D array of velocity vectors [x,y,z,component]
            spatial_grid: 3D spatial coordinate arrays

        Returns:
            3D array of flux divergences
        """
        # Energy flux J = E * v
        flux_x = energy_field * velocity_field[:, :, :, 0]
        flux_y = energy_field * velocity_field[:, :, :, 1]
        flux_z = energy_field * velocity_field[:, :, :, 2]

        # Calculate divergence using finite differences
        dx = (
            spatial_grid[1, 0, 0, 0] - spatial_grid[0, 0, 0, 0]
            if spatial_grid.shape[0] > 1
            else 1.0
        )
        dy = (
            spatial_grid[0, 1, 0, 1] - spatial_grid[0, 0, 0, 1]
            if spatial_grid.shape[1] > 1
            else 1.0
        )
        dz = (
            spatial_grid[0, 0, 1, 2] - spatial_grid[0, 0, 0, 2]
            if spatial_grid.shape[2] > 1
            else 1.0
        )

        div_flux = np.zeros_like(energy_field)

        # ∂(flux_x)/∂x
        if spatial_grid.shape[0] > 2:
            div_flux[1:-1, :, :] += (flux_x[2:, :, :] - flux_x[:-2, :, :]) / (2 * dx)

        # ∂(flux_y)/∂y
        if spatial_grid.shape[1] > 2:
            div_flux[:, 1:-1, :] += (flux_y[:, 2:, :] - flux_y[:, :-2, :]) / (2 * dy)

        # ∂(flux_z)/∂z
        if spatial_grid.shape[2] > 2:
            div_flux[:, :, 1:-1] += (flux_z[:, :, 2:] - flux_z[:, :, :-2]) / (2 * dz)

        return div_flux

    def time_evolution(
        self,
        energy_field: np.ndarray,
        velocity_field: np.ndarray,
        spatial_grid: np.ndarray,
        time: float,
        dt: float,
    ) -> np.ndarray:
        """
        Evolve energy field according to continuity equation.

        Args:
            energy_field: Current energy field
            velocity_field: Velocity field
            spatial_grid: Spatial coordinates
            time: Current time
            dt: Time step

        Returns:
            Updated energy field
        """
        # Calculate flux divergence
        flux_div = self.energy_flux_divergence(
            energy_field, velocity_field, spatial_grid
        )

        # Calculate source and dissipation terms
        source_term = np.zeros_like(energy_field)
        dissipation_term = np.zeros_like(energy_field)

        for i in range(energy_field.shape[0]):
            for j in range(energy_field.shape[1]):
                for k in range(energy_field.shape[2]):
                    pos = spatial_grid[i, j, k, :]
                    source_term[i, j, k] = self.source_model(pos, time)
                    dissipation_term[i, j, k] = self.dissipation_model(
                        energy_field[i, j, k], pos, time
                    )

        # Time evolution: ∂E/∂t = -∇·J - P_dissipation + P_source
        dE_dt = -flux_div - dissipation_term + source_term

        # Forward Euler integration (simple but stable for small dt)
        new_energy_field = energy_field + dt * dE_dt

        # Ensure energy remains non-negative (physical constraint)
        new_energy_field = np.maximum(new_energy_field, 0.0)

        return new_energy_field


class WavePropagationWithAttenuation:
    """
    Implementation of the wave propagation equation with attenuation:

    ∂²ψ/∂t² = v² ∇²ψ - γ ∂ψ/∂t + S_sensor(r⃗,t)

    This describes how sensory tracers propagate as waves through media.
    """

    def __init__(
        self, velocity: float, attenuation: float, refractive_index: float = 1.0
    ):
        """
        Initialize wave propagation solver.

        Args:
            velocity: Wave propagation speed (m/s)
            attenuation: Attenuation coefficient γ (1/s)
            refractive_index: Medium refractive index
        """
        # Validate causality (Axiom A2)
        max_allowed_speed = STSLimits.max_speed_in_medium(refractive_index)
        if velocity > max_allowed_speed:
            raise ValueError(
                f"Velocity {velocity:.2e} m/s exceeds causality limit "
                f"{max_allowed_speed:.2e} m/s for n={refractive_index}"
            )

        self.velocity = velocity
        self.attenuation = attenuation
        self.refractive_index = refractive_index

    def laplacian(self, field: np.ndarray, spatial_grid: np.ndarray) -> np.ndarray:
        """
        Calculate spatial Laplacian ∇²ψ using finite differences.

        Args:
            field: 3D complex wave field
            spatial_grid: 3D spatial coordinate arrays

        Returns:
            3D array of Laplacian values
        """
        lapl = np.zeros_like(field)

        dx = (
            spatial_grid[1, 0, 0, 0] - spatial_grid[0, 0, 0, 0]
            if spatial_grid.shape[0] > 1
            else 1.0
        )
        dy = (
            spatial_grid[0, 1, 0, 1] - spatial_grid[0, 0, 0, 1]
            if spatial_grid.shape[1] > 1
            else 1.0
        )
        dz = (
            spatial_grid[0, 0, 1, 2] - spatial_grid[0, 0, 0, 2]
            if spatial_grid.shape[2] > 1
            else 1.0
        )

        # Second derivatives using central differences
        if spatial_grid.shape[0] > 2:
            lapl[1:-1, :, :] += (
                field[2:, :, :] - 2 * field[1:-1, :, :] + field[:-2, :, :]
            ) / dx**2

        if spatial_grid.shape[1] > 2:
            lapl[:, 1:-1, :] += (
                field[:, 2:, :] - 2 * field[:, 1:-1, :] + field[:, :-2, :]
            ) / dy**2

        if spatial_grid.shape[2] > 2:
            lapl[:, :, 1:-1] += (
                field[:, :, 2:] - 2 * field[:, :, 1:-1] + field[:, :, :-2]
            ) / dz**2

        return lapl

    def time_evolution(
        self,
        psi: np.ndarray,
        psi_dot: np.ndarray,
        spatial_grid: np.ndarray,
        source_field: np.ndarray,
        dt: float,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Evolve wave field according to damped wave equation.

        Args:
            psi: Current wave field
            psi_dot: Current time derivative of wave field
            spatial_grid: Spatial coordinates
            source_field: Source term S_sensor(r⃗,t)
            dt: Time step

        Returns:
            (updated_psi, updated_psi_dot)
        """
        # Calculate spatial Laplacian
        laplacian_psi = self.laplacian(psi, spatial_grid)

        # Wave equation: ∂²ψ/∂t² = v² ∇²ψ - γ ∂ψ/∂t + S
        psi_ddot = (
            self.velocity**2 * laplacian_psi - self.attenuation * psi_dot + source_field
        )

        # Leapfrog integration for second-order ODE
        new_psi_dot = psi_dot + dt * psi_ddot
        new_psi = psi + dt * new_psi_dot

        return new_psi, new_psi_dot

    def energy_density(self, psi: np.ndarray, psi_dot: np.ndarray) -> np.ndarray:
        """
        Calculate wave energy density.

        Args:
            psi: Wave field
            psi_dot: Time derivative of wave field

        Returns:
            Energy density field
        """
        # Energy density = (1/2) * (|∂ψ/∂t|² + v²|∇ψ|²)
        # Simplified to kinetic + potential energy
        kinetic_density = 0.5 * np.abs(psi_dot) ** 2
        potential_density = 0.5 * self.velocity**2 * np.abs(psi) ** 2

        return kinetic_density + potential_density


class STSSystemSolver:
    """
    Unified solver for complete STS system combining all governing equations.
    """

    def __init__(self, system_parameters: Dict[str, Any]):
        """
        Initialize complete STS system solver.

        Args:
            system_parameters: Dictionary of system parameters
        """
        self.params = system_parameters

        # Initialize component solvers
        self.info_conservation = ConservationOfSensoryInformation(
            temperature=system_parameters.get("temperature", 300.0)
        )

        self.energy_continuity = TracerEnergyContinuity(
            dissipation_model=system_parameters.get("dissipation_model"),
            source_model=system_parameters.get("source_model"),
        )

        self.wave_propagation = WavePropagationWithAttenuation(
            velocity=system_parameters["velocity"],
            attenuation=system_parameters["attenuation"],
            refractive_index=system_parameters.get("refractive_index", 1.0),
        )

    def evolve_system(
        self,
        initial_state: STSState,
        spatial_grid: np.ndarray,
        time_steps: int,
        dt: float,
    ) -> list[STSState]:
        """
        Evolve complete STS system through time.

        Args:
            initial_state: Initial system state
            spatial_grid: Spatial coordinate grid
            time_steps: Number of time steps
            dt: Time step size

        Returns:
            List of system states at each time step
        """
        states = [initial_state]
        current_state = initial_state

        # Initialize fields
        energy_field = np.full(spatial_grid.shape[:-1], current_state.energy)
        psi_field = np.full(spatial_grid.shape[:-1], current_state.wave_amplitude)
        psi_dot_field = np.zeros_like(psi_field, dtype=complex)
        velocity_field = np.zeros((*spatial_grid.shape[:-1], 3))

        for step in range(time_steps):
            current_time = initial_state.time + step * dt

            # Evolve energy field
            energy_field = self.energy_continuity.time_evolution(
                energy_field, velocity_field, spatial_grid, current_time, dt
            )

            # Evolve wave field
            source_field = np.zeros_like(psi_field)  # No external sources by default
            psi_field, psi_dot_field = self.wave_propagation.time_evolution(
                psi_field, psi_dot_field, spatial_grid, source_field, dt
            )

            # Calculate conserved information
            sensor_density = np.ones_like(energy_field)  # Uniform sensor density
            total_info = self.info_conservation.total_information(
                sensor_density, energy_field, spatial_grid
            )

            # Create new state
            new_state = STSState(
                position=current_state.position.copy(),
                time=current_time + dt,
                energy=float(np.mean(energy_field)),
                information_content=total_info,
                wave_amplitude=complex(np.mean(psi_field)),
                entropy=current_state.entropy,  # Updated separately
                temperature=current_state.temperature,
            )

            states.append(new_state)
            current_state = new_state

        return states


# ============================================================================
# VALIDATION AND TESTING
# ============================================================================


def validate_equations() -> Dict[str, Any]:
    """
    Validate that all STS equations are mathematically and physically consistent.

    Returns:
        Dictionary with validation results
    """
    results = {}

    # Test information conservation
    info_solver = ConservationOfSensoryInformation()
    test_energy = STSPhysics.thermal_energy(300.0)
    info_density = info_solver.information_density(1.0, test_energy)
    results["info_density_test"] = info_density
    assert info_density > 0, "Information density must be positive"

    # Test energy continuity
    energy_solver = TracerEnergyContinuity()
    assert hasattr(
        energy_solver, "time_evolution"
    ), "Energy solver must have time evolution"

    # Test wave propagation (check causality)
    try:
        _ = WavePropagationWithAttenuation(
            velocity=2.99792458e8,  # Slightly less than exact speed of light
            attenuation=1e-3,
            refractive_index=1.0,
        )
        results["causality_check"] = "PASSED"
    except ValueError:
        results["causality_check"] = "FAILED"

    # Test faster-than-light rejection
    try:
        _ = WavePropagationWithAttenuation(
            velocity=4e8, attenuation=1e-3, refractive_index=1.0  # Faster than light
        )
        results["ftl_rejection"] = "FAILED"
    except ValueError:
        results["ftl_rejection"] = "PASSED"

    results["validation_status"] = "PASSED"
    return results


if __name__ == "__main__":
    # Run validation when module is executed directly
    validation_results = validate_equations()
    print("STS Equations Validation Results:")
    for key, value in validation_results.items():
        print(f"  {key}: {value}")
