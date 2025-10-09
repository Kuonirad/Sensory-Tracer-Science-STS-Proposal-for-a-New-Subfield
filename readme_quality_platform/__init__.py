"""
README Quality Platform - Comprehensive README Analysis Toolkit

A multi-dimensional README quality assessment platform providing readability analysis,
structural evaluation, complexity assessment, and code-documentation consistency checking.
"""

__version__ = "1.0.0"
__author__ = "README Quality Platform Team"

# Core exports
try:
    from .core.analyzer import ReadmeAnalyzer
    from .core.config import Config, get_config
    from .core.models import (
        ReadmeAnalysis,
        ReadabilityMetrics,
        StructuralMetrics,
        ComplexityMetrics,
        ConsistencyMetrics,
        QualityScore,
    )
    
    # Analyzer exports
    from .analyzers.github import GitHubAnalyzer
    
    __all__ = [
        "ReadmeAnalyzer",
        "Config", 
        "get_config",
        "ReadmeAnalysis",
        "ReadabilityMetrics",
        "StructuralMetrics", 
        "ComplexityMetrics",
        "ConsistencyMetrics",
        "QualityScore",
        "GitHubAnalyzer",
    ]
    
except ImportError as e:
    # Graceful degradation if dependencies are missing
    print(f"Warning: Could not import all components: {e}")
    __all__ = []