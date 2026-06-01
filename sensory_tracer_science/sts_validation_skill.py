import numpy as np
from typing import List, Optional, Dict, Any, Callable
from sensory_tracer_science.sts_mcop_adapter import SensoryTracerAttributor, STSEnrichedTrace

class STSValidationSkill:
    """M-COP compatible skill for full STS validation of reasoning chains.
    
    Applies energy-conserving, information-preserving, causality-respecting audits to any M-COP
    kernel sequence by treating it as synthetic neural tissue via the existing adapter.
    """
    
    def __init__(self, analyze_tissue: bool = True, verbose: bool = False, name: str = "sts_validation"):
        self.attributor = SensoryTracerAttributor(analyze_tissue=analyze_tissue)
        self.verbose = verbose
        self.name = name
        self.description = (
            "End-to-end STS triple-audit (energy/info/causality) on reasoning steps. "
            "Returns STSEnrichedTrace with full metrics and validation."
        )
    
    def execute(self, kernels: List[Callable], initial_activation: np.ndarray, 
                step_labels: Optional[List[str]] = None, **kwargs) -> STSEnrichedTrace:
        """Run STS validation on a sequence of reasoning kernels."""
        if step_labels is None:
            step_labels = [f"kernel_{i}" for i in range(len(kernels))]
        
        trace: STSEnrichedTrace = self.attributor.attribute(
            kernels=kernels,
            initial_activation=initial_activation,
            step_labels=step_labels,
            **kwargs
        )
        
        if self.verbose:
            print(f"[STSValidationSkill] Trace summary: {trace.summary()}")
        
        return trace
    
    def validate(self, trace: STSEnrichedTrace) -> bool:
        """Check if reasoning chain passes all STS invariants."""
        return trace.valid
    
    def get_report(self, trace: STSEnrichedTrace) -> Dict[str, Any]:
        """Comprehensive STS validation report."""
        return {
            'valid': trace.valid,
            'energy_efficiency': getattr(trace, 'energy_efficiency', None),
            'information_fidelity': getattr(trace, 'information_fidelity', None),
            'landauer_efficiency': getattr(trace, 'landauer_efficiency', None),
            'causality_preserved': getattr(trace, 'causality_preserved', None),
            'dag_acyclic': getattr(trace, 'dag_acyclic', None),
            'tissue_metrics': getattr(trace, 'tissue_metrics', None),
            'full_report': trace.report() if hasattr(trace, 'report') else str(trace),
            'skill': self.name
        }
    
    def __call__(self, kernels, initial_activation, step_labels=None, **kwargs):
        return self.execute(kernels, initial_activation, step_labels, **kwargs)

# Usage example for M-COP registry
if __name__ == "__main__":
    # Example M-COP kernels (any callable np.ndarray -> np.ndarray)
    def encoder(x): return x * 1.05
    def processor(x): return np.tanh(x)
    kernels = [encoder, processor]
    initial = np.random.randn(256).astype(float)
    
    skill = STSValidationSkill(verbose=True)
    trace = skill(kernels, initial, ["encoder", "processor"])
    report = skill.get_report(trace)
    print("STS Validation passed:", report['valid'])
    print(report)
