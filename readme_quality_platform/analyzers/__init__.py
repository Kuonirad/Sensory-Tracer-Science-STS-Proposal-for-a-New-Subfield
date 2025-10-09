"""
Analyzers Package for README Quality Platform

Specialized analyzers for different sources and integration points including
GitHub repositories, local directories, and web-based README files.
"""

from .github import GitHubAnalyzer
from .directory import DirectoryAnalyzer
from .web import WebAnalyzer

__all__ = [
    "GitHubAnalyzer",
    "DirectoryAnalyzer", 
    "WebAnalyzer",
]