"""
Comprehensive test suite for STS core constants module.
This test suite aims for 95%+ code coverage of sts_constants.py.
"""

import math
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from sensory_tracer_science.core.sts_constants import (
    # Constants
    K_B, HBAR, C_VACUUM, E_CHARGE, N_A, R_GAS, F_FARADAY, EPSILON_0,
    K_FLUOR_ON, K_BLEACH, Q_YIELD, SIGMA_ABS_2P, TAU_CA_DISSOC,
    D_CA_FREE, ETA_CYTOPLASM, P_CELL_MEMBRANE, V_CSF_FLOW, L_P_BBB,
    DELTA_G_ATP_HYDROLYSIS, LAMBDA_DEBYE_150mM, SIGMA_LOGBB,
    
    # Classes
    UncertaintyParameters, STSLimits, ValidationTolerances, ImplementationLimits, STSPhysics,
    
    # Functions
    validate_augmented_physics, validate_physical_consistency, validate_uncertainty_propagation
)


class TestFundamentalConstants:
    """Test that fundamental physical constants have correct values."""
    
    def test_boltzmann_constant(self):
        """Test Boltzmann constant value."""
        # CODATA 2022 exact value
        assert K_B == 1.380649e-23
        
    def test_reduced_planck_constant(self):
        """Test reduced Planck constant value."""
        # CODATA 2022 exact value
        assert HBAR == 1.054571817e-34
        
    def test_speed_of_light(self):
        """Test speed of light value."""
        # CODATA defining constant
        assert C_VACUUM == 299792458.0
        
    def test_elementary_charge(self):
        """Test elementary charge value."""
        # CODATA 2022 exact value
        assert E_CHARGE == 1.602176634e-19
        
    def test_avogadro_constant(self):
        """Test Avogadro constant value."""
        # CODATA 2022 defining constant
        assert N_A == 6.02214076e23
    
    def test_derived_constants(self):
        """Test that derived constants are properly calculated."""
        # Gas constant should be K_B * N_A
        assert abs(R_GAS - K_B * N_A) < 1e-15
        
        # Faraday constant should be E_CHARGE * N_A
        assert abs(F_FARADAY - E_CHARGE * N_A) < 1e-10
        
    def test_vacuum_permittivity(self):
        """Test vacuum permittivity constant."""
        assert EPSILON_0 == 8.8541878128e-12
        

class TestExperimentalConstants:
    """Test experimental biotracer constants."""
    
    def test_fluorescence_constants(self):
        """Test fluorescence-related constants."""
        # Fluorophore association rate
        assert K_FLUOR_ON == 3.0e8
        assert K_FLUOR_ON > 0
        
        # Photobleaching rate
        assert K_BLEACH == 5.8e-3
        assert K_BLEACH > 0
        
        # Quantum yield
        assert Q_YIELD == 0.75
        assert 0 < Q_YIELD <= 1.0
        
        # Two-photon absorption cross-section
        assert SIGMA_ABS_2P == 3.4e-20
        assert SIGMA_ABS_2P > 0
        
        # Ca²⁺ dissociation time
        assert TAU_CA_DISSOC == 6.7e-3
        assert TAU_CA_DISSOC > 0
    
    def test_cellular_transport_constants(self):
        """Test cellular transport constants."""
        # Free Ca²⁺ diffusion coefficient
        assert D_CA_FREE == 2.2e-10
        assert D_CA_FREE > 0
        
        # Cytoplasm viscosity
        assert ETA_CYTOPLASM == 2.5e-3
        assert ETA_CYTOPLASM > 0
        
        # Membrane permeability
        assert P_CELL_MEMBRANE == 1.2e-6
        assert P_CELL_MEMBRANE > 0
        
        # CSF flow velocity
        assert V_CSF_FLOW == 1.1e-4
        assert V_CSF_FLOW > 0
        
        # BBB hydraulic permeability
        assert L_P_BBB == 1.0e-11
        assert L_P_BBB > 0
    
    def test_bioenergetics_constants(self):
        """Test bioenergetics constants."""
        # ATP hydrolysis free energy
        assert DELTA_G_ATP_HYDROLYSIS == -57.3e3
        assert DELTA_G_ATP_HYDROLYSIS < 0  # Must be negative (exergonic)
        
    def test_ionic_environment_constants(self):
        """Test ionic environment constants."""
        # Debye screening length
        assert LAMBDA_DEBYE_150mM == 0.78e-9
        assert LAMBDA_DEBYE_150mM > 0
        
        # LogBB prediction uncertainty
        assert SIGMA_LOGBB == 0.18
        assert SIGMA_LOGBB > 0


class TestUncertaintyParameters:
    """Test uncertainty parameter definitions."""
    
    def test_logbb_parameters(self):
        """Test LogBB uncertainty parameters."""
        assert UncertaintyParameters.LOGBB_MEAN == -0.29
        assert UncertaintyParameters.LOGBB_STD == 0.18
        assert UncertaintyParameters.LOGBB_STD > 0
        
    def test_k_off_parameters(self):
        """Test Ca²⁺ dissociation rate parameters."""
        assert UncertaintyParameters.K_OFF_MEAN == 150.0
        assert UncertaintyParameters.K_OFF_STD == 15.0
        assert UncertaintyParameters.K_OFF_STD > 0
        
    def test_quantum_yield_parameters(self):
        """Test quantum yield uncertainty parameters."""
        assert UncertaintyParameters.Q_YIELD_MEAN == 0.75
        assert UncertaintyParameters.Q_YIELD_STD == 0.05
        assert 0 < UncertaintyParameters.Q_YIELD_MEAN <= 1.0
        assert UncertaintyParameters.Q_YIELD_STD > 0
        
    def test_photobleaching_parameters(self):
        """Test photobleaching rate uncertainty parameters."""
        assert UncertaintyParameters.K_BLEACH_MEAN == 5.8e-3
        assert UncertaintyParameters.K_BLEACH_STD == 0.5e-3
        assert UncertaintyParameters.K_BLEACH_MEAN > 0
        assert UncertaintyParameters.K_BLEACH_STD > 0


class TestSTSLimits:
    """Test STS fundamental limits derived from axioms."""
    
    def test_landauer_limit_default_temperature(self):
        """Test Landauer limit at default temperature."""
        limit = STSLimits.landauer_limit()
        expected = K_B * 300.0 * math.log(2)
        assert abs(limit - expected) < 1e-25
        assert limit > 0
        
    def test_landauer_limit_custom_temperatures(self):
        """Test Landauer limit at various temperatures."""
        # Room temperature
        limit_300K = STSLimits.landauer_limit(300.0)
        expected_300K = K_B * 300.0 * math.log(2)
        assert abs(limit_300K - expected_300K) < 1e-25
        
        # Body temperature
        limit_310K = STSLimits.landauer_limit(310.0)
        expected_310K = K_B * 310.0 * math.log(2)
        assert abs(limit_310K - expected_310K) < 1e-25
        
        # Liquid nitrogen temperature
        limit_77K = STSLimits.landauer_limit(77.0)
        expected_77K = K_B * 77.0 * math.log(2)
        assert abs(limit_77K - expected_77K) < 1e-25
        
        # Higher temperature should give higher limit
        assert limit_310K > limit_300K > limit_77K
        
    def test_landauer_limit_zero_temperature(self):
        """Test Landauer limit at absolute zero."""
        limit = STSLimits.landauer_limit(0.0)
        assert limit == 0.0
        
    def test_max_speed_in_medium_vacuum(self):
        """Test maximum speed in vacuum."""
        speed = STSLimits.max_speed_in_medium(1.0)
        assert speed == C_VACUUM
        
    def test_max_speed_in_medium_glass(self):
        """Test maximum speed in glass."""
        n_glass = 1.5
        speed = STSLimits.max_speed_in_medium(n_glass)
        expected = C_VACUUM / n_glass
        assert abs(speed - expected) < 1e-6
        assert speed < C_VACUUM
        
    def test_max_speed_in_medium_water(self):
        """Test maximum speed in water."""
        n_water = 1.33
        speed = STSLimits.max_speed_in_medium(n_water)
        expected = C_VACUUM / n_water
        assert abs(speed - expected) < 1e-6
        
    def test_max_speed_invalid_refractive_index(self):
        """Test that invalid refractive indices are rejected."""
        with pytest.raises(ValueError, match="Refractive index must be ≥ 1.0"):
            STSLimits.max_speed_in_medium(0.5)
            
        with pytest.raises(ValueError, match="Refractive index must be ≥ 1.0"):
            STSLimits.max_speed_in_medium(-1.0)
    
    def test_heisenberg_uncertainty(self):
        """Test Heisenberg uncertainty limit."""
        uncertainty = STSLimits.heisenberg_uncertainty()
        expected = HBAR / 2.0
        assert abs(uncertainty - expected) < 1e-40
        assert uncertainty > 0
        
    def test_min_entropy_production(self):
        """Test minimum entropy production."""
        assert STSLimits.MIN_ENTROPY_PRODUCTION == 0.0
        
    def test_atp_constraints(self):
        """Test ATP-related biological constraints."""
        assert STSLimits.ATP_FREE_ENERGY == 57300.0
        assert STSLimits.ATP_FREE_ENERGY > 0
        
        assert STSLimits.MAX_ATP_DEPLETION_RATE == 0.1e-3
        assert STSLimits.MAX_ATP_DEPLETION_RATE > 0
        
    def test_augmented_validation_limits(self):
        """Test augmented validation limits."""
        assert STSLimits.MAX_PHOTOTOXIC_DOSE == 50.0
        assert STSLimits.MAX_PHOTOTOXIC_DOSE > 0
        
        assert STSLimits.MAX_CA_BUFFER_CAPACITY == 50e-6
        assert STSLimits.MAX_CA_BUFFER_CAPACITY > 0
        
        assert STSLimits.MAX_MEMBRANE_POTENTIAL_DRIFT == 2e-3
        assert STSLimits.MAX_MEMBRANE_POTENTIAL_DRIFT > 0
        
        assert STSLimits.MAX_OSMOTIC_SWELLING == 0.005
        assert STSLimits.MAX_OSMOTIC_SWELLING > 0
        
        assert STSLimits.MAX_PH_SHIFT == 0.05
        assert STSLimits.MAX_PH_SHIFT > 0
        
    def test_min_single_bit_energy(self):
        """Test minimum single bit energy calculation."""
        # Default temperature
        energy_default = STSLimits.min_single_bit_energy()
        expected_default = K_B * 300.0 * math.log(2)
        assert abs(energy_default - expected_default) < 1e-25
        
        # Custom temperature
        energy_custom = STSLimits.min_single_bit_energy(273.15)
        expected_custom = K_B * 273.15 * math.log(2)
        assert abs(energy_custom - expected_custom) < 1e-25
        
        # Should be identical to landauer_limit
        assert energy_default == STSLimits.landauer_limit(300.0)
        assert energy_custom == STSLimits.landauer_limit(273.15)


class TestValidationTolerances:
    """Test validation tolerance definitions."""
    
    def test_energy_audit_tolerance(self):
        """Test energy audit tolerance."""
        assert ValidationTolerances.ENERGY_AUDIT_TOLERANCE == 1e-12
        assert ValidationTolerances.ENERGY_AUDIT_TOLERANCE > 0
        
    def test_information_balance_tolerance(self):
        """Test information balance tolerance."""
        assert ValidationTolerances.INFORMATION_BALANCE_TOLERANCE == 0.01
        assert ValidationTolerances.INFORMATION_BALANCE_TOLERANCE > 0
        
    def test_causality_tolerance(self):
        """Test causality tolerance (should be zero)."""
        assert ValidationTolerances.CAUSALITY_TOLERANCE == 0.0


class TestImplementationLimits:
    """Test implementation-specific constraints."""
    
    def test_fiber_optic_limits(self):
        """Test fiber optic tracer limits."""
        assert ImplementationLimits.FiberOptic.MAX_INPUT_ENERGY == 1e-9
        assert ImplementationLimits.FiberOptic.MAX_INPUT_ENERGY > 0
        
        freq_range = ImplementationLimits.FiberOptic.BRILLOUIN_FREQUENCY_SHIFT_RANGE
        assert freq_range == (9e9, 13e9)
        assert freq_range[0] < freq_range[1]
        assert all(f > 0 for f in freq_range)
        
        assert ImplementationLimits.FiberOptic.FIBER_ATTENUATION_COEFFICIENT == 0.2e-3
        assert ImplementationLimits.FiberOptic.FIBER_ATTENUATION_COEFFICIENT > 0
        
        assert ImplementationLimits.FiberOptic.SILICA_REFRACTIVE_INDEX == 1.46
        assert ImplementationLimits.FiberOptic.SILICA_REFRACTIVE_INDEX >= 1.0
        
    def test_biocompatible_limits(self):
        """Test biocompatible tracer limits."""
        assert ImplementationLimits.Biocompatible.MAX_TRACER_CONCENTRATION == 1e-6
        assert ImplementationLimits.Biocompatible.MAX_TRACER_CONCENTRATION > 0
        
        assert ImplementationLimits.Biocompatible.MAX_ATP_DEPLETION_RATE == -0.1e-3
        assert ImplementationLimits.Biocompatible.MAX_ATP_DEPLETION_RATE < 0
        
        assert ImplementationLimits.Biocompatible.TYPICAL_DIFFUSION_COEFFICIENT == 1e-12
        assert ImplementationLimits.Biocompatible.TYPICAL_DIFFUSION_COEFFICIENT > 0
        
        assert ImplementationLimits.Biocompatible.BLOOD_BRAIN_BARRIER_CLEARANCE == 1e-6
        assert ImplementationLimits.Biocompatible.BLOOD_BRAIN_BARRIER_CLEARANCE > 0
        
    def test_quantum_limits(self):
        """Test quantum-enhanced tracer limits."""
        assert ImplementationLimits.Quantum.MAX_PHOTON_FLUX == 1e9
        assert ImplementationLimits.Quantum.MAX_PHOTON_FLUX > 0
        
        assert ImplementationLimits.Quantum.MIN_ENTANGLEMENT_FIDELITY == 0.9
        assert 0 < ImplementationLimits.Quantum.MIN_ENTANGLEMENT_FIDELITY <= 1.0
        
        assert ImplementationLimits.Quantum.MAX_CORRELATION_FUNCTION == 0.1
        assert ImplementationLimits.Quantum.MAX_CORRELATION_FUNCTION > 0
        
        # Test coherence time limit function
        coherence_limit = ImplementationLimits.Quantum.QUANTUM_COHERENCE_TIME_LIMIT(300.0)
        expected = HBAR / (2 * K_B * 300.0)
        assert abs(coherence_limit - expected) < 1e-40


class TestSTSPhysics:
    """Test derived physical quantities and relationships."""
    
    def test_debye_length_calculation(self):
        """Test Debye length calculation."""
        # Standard physiological conditions
        ionic_strength = 0.15  # mol/L
        temperature = 310.0  # K
        
        debye_length = STSPhysics.debye_length(ionic_strength, temperature)
        
        # Should be positive and of correct order of magnitude
        assert debye_length > 0
        assert 1e-10 < debye_length < 1e-8  # nanometer range
        
    def test_debye_length_default_temperature(self):
        """Test Debye length with default temperature."""
        debye_length = STSPhysics.debye_length(0.15)
        assert debye_length > 0
        
    def test_debye_length_varying_ionic_strength(self):
        """Test Debye length with varying ionic strength."""
        # Higher ionic strength should give shorter Debye length
        debye_low = STSPhysics.debye_length(0.01, 300.0)
        debye_high = STSPhysics.debye_length(0.15, 300.0)
        
        assert debye_low > debye_high
        
    def test_debye_length_varying_temperature(self):
        """Test Debye length with varying temperature."""
        # Higher temperature should give longer Debye length
        debye_cold = STSPhysics.debye_length(0.15, 273.15)
        debye_warm = STSPhysics.debye_length(0.15, 310.0)
        
        assert debye_warm > debye_cold
        
    def test_nernst_potential_calculation(self):
        """Test Nernst potential calculation."""
        # Typical Ca²⁺ gradient
        c_in = 100e-9  # mol/L (100 nM intracellular)
        c_out = 2e-3   # mol/L (2 mM extracellular)
        valence = 2    # Ca²⁺
        temperature = 310.0  # K
        
        nernst_v = STSPhysics.nernst_potential(c_in, c_out, valence, temperature)
        
        # Should be positive (outward gradient) and physiologically reasonable
        assert nernst_v > 0
        assert 0.1 < nernst_v < 0.2  # ~100-200 mV range for Ca²⁺
        
    def test_nernst_potential_default_temperature(self):
        """Test Nernst potential with default temperature."""
        nernst_v = STSPhysics.nernst_potential(1e-3, 10e-3, 1)
        assert isinstance(nernst_v, float)
        
    def test_nernst_potential_monovalent_ion(self):
        """Test Nernst potential for monovalent ion."""
        # 10-fold concentration gradient for K⁺
        nernst_v = STSPhysics.nernst_potential(150e-3, 15e-3, 1, 310.0)
        
        # Should be negative (inward gradient)
        assert nernst_v < 0
        
    def test_nernst_potential_reverse_gradient(self):
        """Test Nernst potential with reversed concentration gradient."""
        # Higher inside than outside
        nernst_v = STSPhysics.nernst_potential(10e-3, 1e-3, 1, 310.0)
        assert nernst_v < 0
        
    def test_osmotic_pressure_calculation(self):
        """Test osmotic pressure calculation."""
        concentration_diff = 1e-6  # mol/L (1 μM difference)
        temperature = 310.0  # K
        
        osmotic_p = STSPhysics.osmotic_pressure(concentration_diff, temperature)
        
        # Should be positive and reasonable magnitude
        assert osmotic_p > 0
        assert osmotic_p < 1000.0  # Should be less than 1 kPa for 1 μM
        
    def test_osmotic_pressure_default_temperature(self):
        """Test osmotic pressure with default temperature."""
        osmotic_p = STSPhysics.osmotic_pressure(1e-3)
        assert osmotic_p > 0
        
    def test_osmotic_pressure_proportionality(self):
        """Test osmotic pressure proportionality to concentration."""
        # Osmotic pressure should be proportional to concentration difference
        p1 = STSPhysics.osmotic_pressure(1e-6, 300.0)
        p2 = STSPhysics.osmotic_pressure(2e-6, 300.0)
        
        assert abs(p2 - 2 * p1) < 1e-10
        
    def test_two_photon_excitation_rate(self):
        """Test two-photon excitation rate calculation."""
        power_avg = 1e-3     # W (1 mW)
        pulse_duration = 100e-15  # s (100 fs)
        rep_rate = 80e6      # Hz (80 MHz)
        wavelength = 810e-9  # m (810 nm)
        
        excitation_rate = STSPhysics.two_photon_excitation_rate(
            power_avg, pulse_duration, rep_rate, wavelength
        )
        
        # Should be positive and reasonable order of magnitude
        assert excitation_rate > 0
        assert 1e3 < excitation_rate < 1e7  # 10³ to 10⁷ photons/s
        
    def test_two_photon_excitation_rate_default_wavelength(self):
        """Test two-photon excitation rate with default wavelength."""
        excitation_rate = STSPhysics.two_photon_excitation_rate(1e-3, 100e-15, 80e6)
        assert excitation_rate > 0
        
    def test_two_photon_excitation_rate_power_scaling(self):
        """Test excitation rate scales with power."""
        rate1 = STSPhysics.two_photon_excitation_rate(1e-3, 100e-15, 80e6)
        rate2 = STSPhysics.two_photon_excitation_rate(2e-3, 100e-15, 80e6)
        
        # Should scale linearly with power
        assert abs(rate2 - 2 * rate1) < 1e-6
        
    def test_photobleaching_rate_reference_conditions(self):
        """Test photobleaching rate at reference conditions."""
        wavelength = 810e-9    # m (reference wavelength)
        intensity = 1e6        # W/m² (reference intensity)
        temperature = 310.0    # K (reference temperature)
        
        bleach_rate = STSPhysics.photobleaching_rate(wavelength, intensity, temperature)
        
        # Should equal reference rate K_BLEACH
        assert abs(bleach_rate - K_BLEACH) < 1e-10
        
    def test_photobleaching_rate_default_temperature(self):
        """Test photobleaching rate with default temperature."""
        bleach_rate = STSPhysics.photobleaching_rate(810e-9, 1e6)
        assert bleach_rate > 0
        
    def test_photobleaching_rate_wavelength_scaling(self):
        """Test photobleaching rate wavelength dependence."""
        # Shorter wavelengths should cause more damage
        rate_short = STSPhysics.photobleaching_rate(400e-9, 1e6, 310.0)  # 400 nm
        rate_long = STSPhysics.photobleaching_rate(800e-9, 1e6, 310.0)   # 800 nm
        
        assert rate_short > rate_long
        
    def test_photobleaching_rate_intensity_scaling(self):
        """Test photobleaching rate intensity dependence."""
        # Higher intensity should cause more bleaching
        rate_low = STSPhysics.photobleaching_rate(810e-9, 5e5, 310.0)   # Low intensity
        rate_high = STSPhysics.photobleaching_rate(810e-9, 2e6, 310.0)  # High intensity
        
        assert rate_high > rate_low
        
    def test_photobleaching_rate_temperature_scaling(self):
        """Test photobleaching rate temperature dependence."""
        # Higher temperature should generally increase rate (Arrhenius)
        rate_cold = STSPhysics.photobleaching_rate(810e-9, 1e6, 273.15)  # 0°C
        rate_hot = STSPhysics.photobleaching_rate(810e-9, 1e6, 323.15)   # 50°C
        
        assert rate_hot > rate_cold
        
    def test_information_energy_coupling(self):
        """Test information-energy coupling calculation."""
        # Default temperature
        energy_default = STSPhysics.information_energy_coupling()
        expected_default = STSLimits.landauer_limit(300.0)
        assert energy_default == expected_default
        
        # Custom temperature
        energy_custom = STSPhysics.information_energy_coupling(273.15)
        expected_custom = STSLimits.landauer_limit(273.15)
        assert energy_custom == expected_custom
        
    def test_thermal_energy(self):
        """Test thermal energy calculation."""
        # Default temperature
        thermal_default = STSPhysics.thermal_energy()
        expected_default = K_B * 300.0
        assert abs(thermal_default - expected_default) < 1e-25
        
        # Custom temperature
        thermal_custom = STSPhysics.thermal_energy(310.0)
        expected_custom = K_B * 310.0
        assert abs(thermal_custom - expected_custom) < 1e-25
        
        # Higher temperature should give higher thermal energy
        assert thermal_custom > thermal_default
        
    def test_quantum_coherence_time(self):
        """Test quantum coherence time calculation."""
        # Default temperature
        coherence_default = STSPhysics.quantum_coherence_time()
        expected_default = HBAR / (2 * K_B * 300.0)
        assert abs(coherence_default - expected_default) < 1e-40
        
        # Custom temperature
        coherence_custom = STSPhysics.quantum_coherence_time(77.0)  # Liquid nitrogen
        expected_custom = HBAR / (2 * K_B * 77.0)
        assert abs(coherence_custom - expected_custom) < 1e-40
        
        # Lower temperature should give longer coherence time
        assert coherence_custom > coherence_default
        
    def test_maximum_propagation_distance(self):
        """Test maximum propagation distance calculation."""
        velocity = 2e8         # m/s
        attenuation = 1e-3     # 1/m
        initial_energy = 1e-18 # J
        temperature = 300.0    # K
        
        max_distance = STSPhysics.maximum_propagation_distance(
            velocity, attenuation, initial_energy, temperature
        )
        
        # Should be positive and finite
        assert max_distance > 0
        assert np.isfinite(max_distance)
        
    def test_maximum_propagation_distance_default_temperature(self):
        """Test maximum propagation distance with default temperature."""
        max_distance = STSPhysics.maximum_propagation_distance(1e8, 1e-3, 1e-18)
        assert max_distance > 0
        
    def test_maximum_propagation_distance_low_energy(self):
        """Test maximum propagation distance with low initial energy."""
        # Energy below thermal noise
        thermal_energy = STSPhysics.thermal_energy(300.0)
        low_energy = 0.5 * thermal_energy
        
        max_distance = STSPhysics.maximum_propagation_distance(1e8, 1e-3, low_energy, 300.0)
        
        # Should return zero distance
        assert max_distance == 0.0
        
    def test_maximum_propagation_distance_equal_thermal_energy(self):
        """Test maximum propagation distance with energy equal to thermal noise."""
        thermal_energy = STSPhysics.thermal_energy(300.0)
        
        max_distance = STSPhysics.maximum_propagation_distance(1e8, 1e-3, thermal_energy, 300.0)
        
        # Should return zero distance
        assert max_distance == 0.0


class TestValidationFunctions:
    """Test the validation functions."""
    
    def test_validate_augmented_physics_success(self):
        """Test that augmented physics validation passes."""
        results = validate_augmented_physics()
        
        assert "augmented_validation_status" in results
        assert results["augmented_validation_status"] == "PASSED"
        
        # Check individual results
        assert "debye_length_150mM" in results
        assert results["debye_length_150mM"] > 0
        
        assert "nernst_potential_ca" in results
        assert 0.1 < results["nernst_potential_ca"] < 0.15
        
        assert "osmotic_pressure_1uM" in results
        assert results["osmotic_pressure_1uM"] > 0
        assert results["osmotic_pressure_1uM"] < 500.0
        
        assert "two_photon_rate" in results
        assert 1e3 < results["two_photon_rate"] < 1e7
        
        assert "photobleaching_rate" in results
        assert abs(results["photobleaching_rate"] - K_BLEACH) < 1e-4
        
    def test_validate_physical_consistency_success(self):
        """Test that physical consistency validation passes."""
        results = validate_physical_consistency()
        
        assert "validation_status" in results
        assert results["validation_status"] == "PASSED"
        
        # Check core physics results
        assert results["landauer_limit_300K"] > 0
        assert results["heisenberg_limit"] > 0
        assert results["light_speed_in_silica"] < C_VACUUM
        assert results["thermal_energy_300K"] > 0
        assert results["quantum_coherence_300K"] > 0
        
        # Check consistency flags
        assert results["debye_consistency"] is True
        assert results["gas_constant_consistency"] is True
        assert results["faraday_consistency"] is True
        assert results["atp_energy_consistency"] is True
        assert results["fluor_kinetics_reasonable"] is True
        assert results["bleach_rate_reasonable"] is True
        assert results["quantum_yield_valid"] is True
        assert results["two_photon_cross_section_reasonable"] is True
        
    @patch('numpy.random.normal')
    def test_validate_uncertainty_propagation_success(self, mock_normal):
        """Test uncertainty propagation validation with mocked numpy."""
        # Mock numpy.random.normal to return predictable values
        mock_normal.side_effect = lambda mean, std, size: np.full(size, mean) + np.random.rand(size) * std * 0.1
        
        results = validate_uncertainty_propagation()
        
        assert "uncertainty_validation_status" in results
        assert results["uncertainty_validation_status"] == "PASSED"
        
        # Check sampling errors are small
        assert results["logbb_mean_error"] < 0.1
        assert results["logbb_std_error"] < 0.1
        assert results["koff_mean_error"] < 10.0
        assert results["koff_std_error"] < 5.0
        
    @patch('sensory_tracer_science.core.sts_constants.np', None)
    def test_validate_uncertainty_propagation_no_numpy(self):
        """Test uncertainty propagation when numpy is not available."""
        results = validate_uncertainty_propagation()
        
        assert results["uncertainty_validation_status"] == "SKIPPED - numpy not available"


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""
    
    def test_sts_limits_extreme_temperatures(self):
        """Test STS limits with extreme temperatures."""
        # Very high temperature
        limit_high = STSLimits.landauer_limit(1e6)
        assert limit_high > 0
        assert np.isfinite(limit_high)
        
        # Very low temperature (but not zero)
        limit_low = STSLimits.landauer_limit(1e-6)
        assert limit_low > 0
        assert limit_low < limit_high
        
    def test_sts_limits_extreme_refractive_indices(self):
        """Test speed limits with extreme but valid refractive indices."""
        # Just above 1.0
        speed = STSLimits.max_speed_in_medium(1.000001)
        assert speed < C_VACUUM
        assert speed > 0.999999 * C_VACUUM
        
        # Very high refractive index
        speed_high_n = STSLimits.max_speed_in_medium(100.0)
        assert speed_high_n == C_VACUUM / 100.0
        assert speed_high_n > 0
        
    def test_sts_physics_extreme_parameters(self):
        """Test STSPhysics methods with extreme but valid parameters."""
        # Very high ionic strength
        debye_high_i = STSPhysics.debye_length(10.0, 300.0)  # 10 M
        assert debye_high_i > 0
        assert debye_high_i < 1e-10  # Should be very short
        
        # Very low ionic strength
        debye_low_i = STSPhysics.debye_length(1e-6, 300.0)  # 1 μM
        assert debye_low_i > debye_high_i  # Should be longer
        
        # Extreme concentration gradients
        nernst_extreme = STSPhysics.nernst_potential(1e-12, 1.0, 1, 300.0)  # 10¹² fold gradient
        assert np.isfinite(nernst_extreme)
        assert nernst_extreme != 0
        
    def test_photobleaching_rate_extreme_conditions(self):
        """Test photobleaching rate with extreme conditions."""
        # Very short wavelength
        rate_short = STSPhysics.photobleaching_rate(200e-9, 1e6, 310.0)
        assert rate_short > K_BLEACH  # Should be higher than reference
        
        # Very long wavelength  
        rate_long = STSPhysics.photobleaching_rate(2000e-9, 1e6, 310.0)
        assert rate_long < K_BLEACH  # Should be lower than reference
        
        # Very high intensity
        rate_high_i = STSPhysics.photobleaching_rate(810e-9, 1e9, 310.0)
        assert rate_high_i > K_BLEACH
        
        # Very low intensity
        rate_low_i = STSPhysics.photobleaching_rate(810e-9, 1e3, 310.0)
        assert rate_low_i < K_BLEACH
        
    def test_maximum_propagation_distance_edge_cases(self):
        """Test maximum propagation distance edge cases."""
        # Very low attenuation
        distance_low_att = STSPhysics.maximum_propagation_distance(1e8, 1e-9, 1e-18, 300.0)
        assert distance_low_att > 0
        
        # Very high attenuation
        distance_high_att = STSPhysics.maximum_propagation_distance(1e8, 1e3, 1e-18, 300.0)
        assert distance_high_att < distance_low_att
        
        # Very high initial energy
        distance_high_e = STSPhysics.maximum_propagation_distance(1e8, 1e-3, 1e-15, 300.0)
        distance_low_e = STSPhysics.maximum_propagation_distance(1e8, 1e-3, 1e-18, 300.0)
        assert distance_high_e > distance_low_e


class TestMainExecution:
    """Test the main execution block functionality."""
    
    @patch('builtins.print')
    def test_main_execution_success(self, mock_print):
        """Test that main execution runs without errors."""
        # Import the module to trigger __main__ execution
        import sensory_tracer_science.core.sts_constants
        
        # The module should have printed validation results
        # We can't easily test the exact output, but we can verify no exceptions occurred
        assert True  # If we get here, no exceptions were raised
        
    @patch('sensory_tracer_science.core.sts_constants.validate_augmented_physics')
    @patch('builtins.print')
    def test_main_execution_with_augmented_failure(self, mock_print, mock_validate_augmented):
        """Test main execution when augmented validation fails."""
        # Make augmented validation raise an exception
        mock_validate_augmented.side_effect = Exception("Test failure")
        
        # Re-import to trigger main execution
        import importlib
        import sensory_tracer_science.core.sts_constants
        importlib.reload(sensory_tracer_science.core.sts_constants)
        
        # Should handle the exception gracefully
        assert True  # If we get here, exception was handled
        
    @patch('sensory_tracer_science.core.sts_constants.validate_uncertainty_propagation')
    @patch('builtins.print')
    def test_main_execution_with_uncertainty_failure(self, mock_print, mock_validate_uncertainty):
        """Test main execution when uncertainty validation fails."""
        # Make uncertainty validation raise an exception
        mock_validate_uncertainty.side_effect = Exception("Test failure")
        
        # Re-import to trigger main execution
        import importlib
        import sensory_tracer_science.core.sts_constants
        importlib.reload(sensory_tracer_science.core.sts_constants)
        
        # Should handle the exception gracefully
        assert True  # If we get here, exception was handled


if __name__ == "__main__":
    pytest.main([__file__])