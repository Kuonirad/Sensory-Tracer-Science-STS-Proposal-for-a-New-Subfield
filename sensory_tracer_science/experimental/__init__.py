"""
Sensory Tracer Science (STS) - Experimental Protocols Module

Advanced experimental protocols for real-world STS applications.
This module contains production-ready experimental designs and protocols.
"""

__version__ = "1.0.0"
__author__ = "STS Development Team"

from .real_world_protocols import *
from .advanced_experiments import *
from .clinical_trials import *

__all__ = [
    'RealWorldProtocolManager',
    'AdvancedExperimentSuite', 
    'ClinicalTrialProtocol',
    'ProductionValidator',
    'ExperimentalMetrics'
]