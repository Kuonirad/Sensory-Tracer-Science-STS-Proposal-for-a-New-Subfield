"""
STS Validation Module - Fail-Safe Validation Protocol Implementation

This module implements the triple audit validation protocol that ensures
all STS systems comply with fundamental physical principles.
"""

from .sts_validator import (
    CausalityAuditor,
    EnergyAuditor,
    InformationAuditor,
    STSValidator,
    ValidationResult,
)

__all__ = [
    "STSValidator",
    "ValidationResult",
    "EnergyAuditor",
    "InformationAuditor",
    "CausalityAuditor",
]
