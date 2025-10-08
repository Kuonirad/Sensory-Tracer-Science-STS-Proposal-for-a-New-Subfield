"""
Test fixtures for STS framework testing.
Provides standardized test data and mock objects.
"""

import pytest
import numpy as np
from typing import Dict, Any
from sensory_tracer_science.tracers.biocompatible_neural import TracerParameters


@pytest.fixture
def standard_tracer_params():
    """Standard optimized tracer parameters for testing."""
    return TracerParameters(
        photon_energy=1.5e-19,      # J (optimized for safety)
        photons_per_second=1e3,     # Hz (low flux)
        ca_buffering_capacity=5e-7, # mol/L (enhanced buffering)
        membrane_capacitance=1e-12, # F (standard capacitance)
        temperature=310.0,          # K (body temperature)
        atp_concentration=5e-3,     # mol/L (physiological)
        atp_free_energy=-30.5e3     # J/mol (standard conditions)
    )


@pytest.fixture
def validation_test_data():
    """Standard validation test data."""
    return {
        'E_in': 1e-9,           # 1 nJ input
        'E_out': 0.99e-9,       # 0.99 nJ output  
        'E_dissipated': 0.01e-9, # 0.01 nJ dissipated
        'I_injected': 100,       # 100 bits injected
        'I_detected': 99,        # 99 bits detected
        'I_lost': 1,            # 1 bit lost
        'signal_speed': 2e8,     # 200,000 km/s
        'medium_speed': 3e8      # 300,000 km/s (vacuum)
    }


@pytest.fixture
def codata_constants():
    """CODATA 2022 fundamental constants for validation."""
    return {
        'boltzmann_constant': 1.380649e-23,      # J/K (exact)
        'planck_constant': 6.62607015e-34,       # J⋅Hz⁻¹ (exact)
        'reduced_planck': 1.054571817e-34,       # J⋅s (exact)
        'speed_of_light': 299792458.0,           # m/s (exact)
        'elementary_charge': 1.602176634e-19,    # C (exact)
        'avogadro_constant': 6.02214076e23,      # mol⁻¹ (exact)
        'gas_constant': 8.314462618,             # J/(mol⋅K)
        'faraday_constant': 96485.33212,         # C/mol
    }


@pytest.fixture
def extreme_test_parameters():
    """Extreme parameter values for robustness testing."""
    return {
        'very_low_energy': TracerParameters(
            photon_energy=1e-21,
            photons_per_second=1e6,
            ca_buffering_capacity=1e-6,
            membrane_capacitance=1e-12,
            temperature=310.0,
            atp_concentration=5e-3,
            atp_free_energy=-30.5e3
        ),
        'very_high_flux': TracerParameters(
            photon_energy=1e-19,
            photons_per_second=1e15,
            ca_buffering_capacity=1e-4,
            membrane_capacitance=1e-9,
            temperature=310.0,
            atp_concentration=1e-2,
            atp_free_energy=-50e3
        ),
        'minimal_buffering': TracerParameters(
            photon_energy=1e-20,
            photons_per_second=1e3,
            ca_buffering_capacity=1e-9,
            membrane_capacitance=1e-15,
            temperature=273.15,
            atp_concentration=1e-6,
            atp_free_energy=-25e3
        )
    }