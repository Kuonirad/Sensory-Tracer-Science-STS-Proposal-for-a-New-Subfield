"""
README Quality Platform Core Module

This module provides the foundational classes and utilities for comprehensive
README quality assessment across multiple analytical dimensions.
"""

from .models import (
    ReadmeAnalysis,
    ReadabilityMetrics,
    StructuralMetrics,
    ComplexityMetrics,
    ConsistencyMetrics,
    QualityScore,
)
from .analyzer import ReadmeAnalyzer
from .config import Config

__all__ = [
    "ReadmeAnalysis",
    "ReadabilityMetrics", 
    "StructuralMetrics",
    "ComplexityMetrics",
    "ConsistencyMetrics",
    "QualityScore",
    "ReadmeAnalyzer",
    "Config",
]

__version__ = "1.0.0"