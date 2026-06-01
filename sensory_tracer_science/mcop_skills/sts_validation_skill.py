'''STS Validation Skill for M-COP

A dedicated skill that integrates Sensory Tracer Science validation into M-COP reasoning loops.
Uses the existing SensoryTracerAttributor for end-to-end STS audits (energy, information, causality).
''' 

import numpy as np
from typing import Any, Dict, List, Optional, Union
from ..sts_mcop_adapter import SensoryTracerAttributor, STSEnrichedTrace, MCOPKernel

class STSValidationSkill:
    '''M-COP compatible skill for real-time STS validation and attribution.'''''

    def __init__(
        self,
        strict: bool = False,
        analyze_tissue: bool = True,
        temperature: float = 300.0,
        **attributor_kwargs
    ) -> None:
        self.strict = strict
        self.attributor = SensoryTracerAttributor(
            temperature=temperature,
            analyze_tissue=analyze_tissue,
            **attributor_kwargs
        )

    def execute(self, kernels: Union[MCOPKernel, List[MCOPKernel]], initial_activation: np.ndarray, **kwargs) -> Dict[str, Any]:
        '''Run STS validation on a reasoning stack of kernels.'''
        trace: STSEnrichedTrace = self.attributor.attribute(kernels, initial_activation, **kwargs)
        
        result = {
            'valid': trace.valid,
            'trace': trace,
            'summary': trace.summary(),
            'report': trace.report(),
            'enriched_state': None  # Could return final state if needed
        }
        
        if self.strict and not trace.valid:
            raise RuntimeError(f'STS validation failed:\n{trace.report()}')
        
        return result

    def __call__(self, *args, **kwargs):
        return self.execute(*args, **kwargs)

    def forward(self, state: np.ndarray, **kwargs) -> np.ndarray:
        '''Pass-through for use as a kernel with side-effect validation.'''
        # In full M-COP, this could trigger step-wise validation
        return state

__all__ = ['STSValidationSkill']
