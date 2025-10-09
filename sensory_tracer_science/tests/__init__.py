"""
STS Tests Module - Comprehensive Testing Framework

This module contains the complete test suite for validating the
Sensory Tracer Science framework against all logical, physical,
and engineering requirements.
"""

from .test_complete_sts_framework import (
    STSFrameworkTester,
    STSTestResult,
    TestSTSFramework,
)

__all__ = ["STSFrameworkTester", "STSTestResult", "TestSTSFramework"]
