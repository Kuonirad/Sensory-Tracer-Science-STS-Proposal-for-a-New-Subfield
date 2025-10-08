"""
Comprehensive Test Suite for Sensory Tracer Science (STS)

This test suite implements scientific-grade testing standards including:
- Unit tests with >95% coverage
- Integration tests for complex systems  
- Performance benchmarks and regression tests
- Statistical validation and Monte Carlo analysis
- Physical constants validation against CODATA 2022
- Numerical precision and error propagation tests

Test Categories:
- Core physics validation (constants, equations, limits)
- Tracer implementation tests (optical, biological, quantum)
- Validation framework tests (energy, information, causality audits)
- Integration tests (complete workflow validation)
- Performance tests (computational efficiency)
- Regression tests (prevent breaking changes)

All tests follow scientific computing best practices with:
- Rigorous numerical tolerances
- Statistical significance testing
- Comprehensive edge case coverage
- Reproducible test environments
- Continuous integration validation
"""

__version__ = "1.0.0"
__author__ = "STS Development Team"

# Test configuration
TEST_CONFIG = {
    'numerical_tolerance': 1e-12,
    'statistical_confidence': 0.95,
    'monte_carlo_samples': 10000,
    'performance_benchmark_runs': 100,
    'codata_precision_threshold': 1e-15,
    'landauer_compliance_threshold': 1e-21,
}

# Test fixtures and utilities
try:
    from .fixtures import *
except ImportError:
    pass

__all__ = [
    'TEST_CONFIG',
]