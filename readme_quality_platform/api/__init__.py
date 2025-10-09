"""
API Package for README Quality Platform

FastAPI-based REST API server providing comprehensive README analysis endpoints
with support for file uploads, GitHub integration, and batch processing.
"""

from .server import app, main

__all__ = ["app", "main"]