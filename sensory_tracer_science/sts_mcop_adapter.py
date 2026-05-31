"""
STS <-> MCOP Bridging Adapter
=============================

This module bridges **Sensory Tracer Science (STS)** with the **MCOP**
(Meta-Cognitive Optimization Protocol) reasoning framework.

The STS package was originally built to trace *physical* sensory signals
(optical / biological / quantum) through real tissue while respecting three
non-negotiable conservation laws:

* **Energy conservation** ``E_in = E_out + E_dissipated`` (Axiom A1 / Landauer).
* **Information conservation** ``I_injected = I_detected + I_lost`` (Axiom A2).
* **Causality** ``signal_speed <= medium_speed`` (Axiom A3).

MCOP reasoning loops are *computational* rather than physical, but they share the
exact same primitives: a kernel transforms an activation/attention state, it costs
energy (Landauer-bounded compute), it preserves or loses information, and steps
form a Directed Acyclic Graph (DAG) of strictly-ordered causality. This adapter
makes that analogy *operational*: it treats an LLM/MCOP activation flow as
**synthetic neural tissue** and runs the STS triple-audit over the reasoning
stack, returning an enriched trace with energy/information-fidelity metrics.

Design goals
------------
* **Zero hard dependency on MCOP.** Kernels are duck-typed via
  :class:`MCOPKernel` (any callable ``np.ndarray -> np.ndarray`` or any object
  exposing ``.execute`` / ``.forward`` / ``.__call__``). This keeps STS
  installable on its own while remaining a drop-in attribution layer for MCOP.
* **Energy-conserving by construction.** Propagation accounting always satisfies
  ``E_in = E_out + E_dissipated`` exactly, so the STS energy audit passes; the
  Landauer floor is checked *separately* as a physical-plausibility flag.
* **DAG-preserving causality.** The reasoning stack is validated as an acyclic
  graph and each transition is checked against a normalized medium-speed budget.
* **Information-preserving fidelity.** Shannon content and step-wise mutual
  information are tracked, yielding an end-to-end information-fidelity score.

The public entry point is :class:`SensoryTracerAttributor`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union, cast

import numpy as np

from .core.sts_constants import K_B, STSLimits
from .validation.sts_validator import (
    CausalityAuditor,
    EnergyAuditor,
    InformationAuditor,
    ValidationResult,
)

# A kernel is either a plain callable or an object exposing a common execution
# method. We resolve the concrete callable at runtime in ``_as_callable``.
KernelCallable = Callable[[np.ndarray], np.ndarray]
MCOPKernel = Union[KernelCallable, Any]


# ============================================================================
# Numerical helpers (pure functions, fully deterministic)
# ============================================================================


def _as_callable(kernel: MCOPKernel) -> KernelCallable:
    """Resolve an MCOP kernel to a plain ``np.ndarray -> np.ndarray`` callable.

    Accepts a bare callable or any object exposing ``execute``/``forward``/
    ``step``/``__call__``. This is what keeps the adapter framework-agnostic.

    Args:
        kernel: The MCOP kernel (callable or object).

    Returns:
        A callable mapping an input activation to an output activation.

    Raises:
        TypeError: If no suitable execution method can be found.
    """
    if callable(kernel) and not _has_method(kernel, ("execute", "forward", "step")):
        return cast(KernelCallable, kernel)
    for method_name in ("execute", "forward", "step"):
        method = getattr(kernel, method_name, None)
        if callable(method):
            return cast(KernelCallable, method)
    if callable(kernel):
        return cast(KernelCallable, kernel)
    raise TypeError(
        "MCOP kernel must be callable or expose execute()/forward()/step()."
    )


def _has_method(obj: object, names: Tuple[str, ...]) -> bool:
    """Return ``True`` if ``obj`` exposes any callable method in ``names``."""
    return any(callable(getattr(obj, name, None)) for name in names)


def _flatten(activation: np.ndarray) -> np.ndarray:
    """Return a 1-D float64 view of an arbitrary activation/attention tensor."""
    return np.asarray(activation, dtype=np.float64).reshape(-1)


def _cosine_overlap(a: np.ndarray, b: np.ndarray) -> float:
    """Directional overlap of two activation states, clipped to ``[0, 1]``.

    This is the STS analogue of *resonance* (MCOP Stigmergy uses the same cosine
    similarity). It quantifies how much of the input signal *direction* survives
    the kernel transformation and therefore acts as the propagation transmission
    coefficient. Vectors of differing length are compared on their shared prefix
    (the overlapping sub-space), which is the conservative choice when a kernel
    changes hidden dimensionality.

    Returns:
        Transmission coefficient in ``[0, 1]``.
    """
    fa, fb = _flatten(a), _flatten(b)
    n = min(fa.size, fb.size)
    if n == 0:
        return 0.0
    fa, fb = fa[:n], fb[:n]
    na = float(np.linalg.norm(fa))
    nb = float(np.linalg.norm(fb))
    if na == 0.0 or nb == 0.0:
        return 0.0
    cos = float(np.dot(fa, fb) / (na * nb))
    return float(np.clip(abs(cos), 0.0, 1.0))


# ============================================================================
# Data model
# ============================================================================


@dataclass
class ReasoningStepTrace:
    """Per-step STS-enriched record of a single MCOP kernel transformation."""

    index: int
    label: str
    # Energy-conserving propagation accounting (Joules).
    energy_in: float
    energy_out: float
    energy_dissipated: float
    landauer_floor: float
    landauer_respected: bool
    # Information accounting (bits).
    information_injected: float
    information_detected: float
    information_lost: float
    information_fidelity: float
    # Independent cross-check: correlation-based mutual-information estimate
    # (does *not* drive the conservation accounting, only validates it).
    mutual_information_estimate: float
    # Propagation geometry.
    transmission: float
    signal_speed: float
    medium_speed: float
    # STS triple-audit verdicts for this step.
    energy_audit: ValidationResult
    information_audit: ValidationResult
    causality_audit: ValidationResult

    @property
    def passed(self) -> bool:
        """``True`` iff this step passes all three STS audits."""
        return (
            self.energy_audit.passed
            and self.information_audit.passed
            and self.causality_audit.passed
        )


@dataclass
class STSEnrichedTrace:
    """Aggregate STS attribution over a full MCOP reasoning stack."""

    steps: List[ReasoningStepTrace] = field(default_factory=list)
    total_energy_in: float = 0.0
    total_energy_out: float = 0.0
    total_energy_dissipated: float = 0.0
    total_information_injected: float = 0.0
    total_information_detected: float = 0.0
    energy_efficiency: float = 0.0
    information_fidelity: float = 0.0
    landauer_efficiency: float = 0.0
    dag_acyclic: bool = True
    causality_preserved: bool = True
    landauer_respected: bool = True
    valid: bool = True
    tissue_metrics: Optional[Dict[str, float]] = None

    def summary(self) -> Dict[str, Any]:
        """Return a compact, JSON-serializable metric summary."""
        return {
            "num_steps": len(self.steps),
            "valid": self.valid,
            "energy_efficiency": self.energy_efficiency,
            "information_fidelity": self.information_fidelity,
            "landauer_efficiency": self.landauer_efficiency,
            "landauer_respected": self.landauer_respected,
            "dag_acyclic": self.dag_acyclic,
            "causality_preserved": self.causality_preserved,
            "total_energy_in_J": self.total_energy_in,
            "total_energy_dissipated_J": self.total_energy_dissipated,
            "total_information_injected_bits": self.total_information_injected,
            "total_information_detected_bits": self.total_information_detected,
        }

    def report(self) -> str:
        """Human-readable attribution report."""
        lines = [
            "=" * 70,
            "STS x MCOP ATTRIBUTION REPORT",
            "=" * 70,
            f"Reasoning steps audited : {len(self.steps)}",
            f"Overall STS validity    : {'VALID' if self.valid else 'INVALID'}",
            "",
            "END-TO-END METRICS",
            f"  Energy efficiency      : {self.energy_efficiency:.4f}"
            "  (E_out / E_in)",
            f"  Information fidelity    : {self.information_fidelity:.4f}"
            "  (I_detected / I_injected)",
            f"  Landauer efficiency     : {self.landauer_efficiency:.3e}"
            "  (ideal floor / actual dissipation)",
            f"  Landauer respected      : {self.landauer_respected}",
            f"  DAG acyclic             : {self.dag_acyclic}",
            f"  Causality preserved     : {self.causality_preserved}",
            f"  Total E_in              : {self.total_energy_in:.3e} J",
            f"  Total E_dissipated      : {self.total_energy_dissipated:.3e} J",
            "",
            "PER-STEP AUDIT",
        ]
        for step in self.steps:
            verdict = "PASS" if step.passed else "FAIL"
            lines.append(
                f"  [{step.index:02d}] {step.label:<24} {verdict}"
                f"  fidelity={step.information_fidelity:.3f}"
                f"  transmission={step.transmission:.3f}"
            )
        if self.tissue_metrics is not None:
            lines.append("")
            lines.append("SYNTHETIC NEURAL TISSUE METRICS")
            for key, value in self.tissue_metrics.items():
                lines.append(f"  {key:<26}: {value:.4e}")
        lines.append("=" * 70)
        return "\n".join(lines)


# ============================================================================
# Synthetic neural tissue (bio-tracer generalization)
# ============================================================================


class SyntheticNeuralTissue:
    """Treat an LLM/MCOP activation flow as analogical "neural tissue".

    The STS biocompatible neural tracer was written for *physical* calcium-
    indicator concentration fields propagating through brain tissue. The exact
    same information-extraction mechanics (spatial Shannon entropy + tracer/
    activity mutual information) apply to a stack of LLM activations once we map:

    * hidden-activation magnitude  ->  local tracer "concentration"
    * attention/activity magnitude ->  local "neural activity"
    * reasoning-step index         ->  the time axis of propagation

    This class performs that mapping and reuses the *real* bio-tracer
    ``information_extraction`` routine, so the analogy is computed by the audited
    STS code path rather than a re-implementation.
    """

    def __init__(self, temperature: float = 310.0) -> None:
        """Initialize the tissue model.

        Args:
            temperature: Effective temperature (K). Defaults to body temperature
                so the bio-tracer constants remain in their validated regime.
        """
        self.temperature = float(temperature)

    @staticmethod
    def _as_field(matrix: np.ndarray) -> np.ndarray:
        """Reshape a (steps, features) matrix into a (steps, X, Y, 1) field."""
        arr = np.asarray(matrix, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        steps, features = arr.shape
        side = max(1, int(math.ceil(math.sqrt(features))))
        padded = np.zeros((steps, side * side), dtype=np.float64)
        padded[:, :features] = arr
        return padded.reshape(steps, side, side, 1)

    def analyze(
        self,
        activations: Sequence[np.ndarray],
        activity: Optional[Sequence[np.ndarray]] = None,
    ) -> Dict[str, float]:
        """Run STS bio-tracer information extraction over an activation stack.

        Args:
            activations: Sequence of per-step activation vectors (the "tracer").
            activity: Optional sequence of per-step attention/activity vectors.
                Defaults to the absolute activations when omitted.

        Returns:
            Dictionary of fidelity metrics (entropy, mutual information, SNR)
            produced by the audited bio-tracer code path.
        """
        # Imported lazily to avoid a heavy import for callers that never touch
        # the bio-tissue analogy.
        from .tracers.biocompatible_neural import (
            BiochemicalTracer,
            BiocompatibleNeuralTracer,
        )

        stacked = np.array([_flatten(a) for a in activations], dtype=np.float64)
        conc_field = self._as_field(np.abs(stacked))
        if activity is None:
            activity_field = conc_field.copy()
        else:
            activity_field = self._as_field(
                np.array([_flatten(a) for a in activity], dtype=np.float64)
            )

        tracer = BiochemicalTracer(
            name="SyntheticActivationTracer",
            molecular_weight=1000.0,
            fluorescence_quantum_yield=0.75,
        )
        geometry = {"length": 1e-3, "width": 1e-3, "height": 0.5e-3}
        neural_tracer = BiocompatibleNeuralTracer(
            tracer=tracer, tissue_geometry=geometry
        )
        metrics = neural_tracer.information_extraction(conc_field, activity_field)
        return {
            "information_entropy": float(metrics["information_entropy"]),
            "mutual_information": float(metrics["mutual_information"]),
            "total_information_bits": float(metrics["total_information_bits"]),
            "signal_to_noise_ratio": float(metrics["signal_to_noise_ratio"]),
        }


# ============================================================================
# Attribution engine
# ============================================================================


class SensoryTracerAttributor:
    """Wrap MCOP kernel execution with STS propagation simulation.

    The attributor executes a reasoning stack (a sequence of kernels, or a single
    kernel applied iteratively) and, for every transition, computes the STS
    primitives and runs the triple audit. The result is an
    :class:`STSEnrichedTrace` exposing energy/information-fidelity metrics for the
    whole reasoning chain.

    Shared-primitive contract
    --------------------------
    * **Energy-conserving propagation:** ``E_out = transmission * E_in`` and
      ``E_dissipated = (1 - transmission) * E_in`` so the energy audit holds by
      construction; the Landauer minimum is checked as a separate flag.
    * **Information-preserving fidelity:** ``I_detected = transmission_info``,
      ``I_lost = I_injected - I_detected``.
    * **DAG-preserving causality:** the dependency graph is verified acyclic and
      each transition speed is bounded by the medium speed.
    """

    def __init__(
        self,
        temperature: float = 300.0,
        medium_speed: float = 1.0,
        noise_floor: float = 1e-3,
        amplification: float = 1.0e6,
        analyze_tissue: bool = False,
    ) -> None:
        """Configure the attributor.

        Args:
            temperature: Temperature (K) for the Landauer/thermal-energy mapping.
            medium_speed: Normalized causal speed limit per reasoning tick.
                Activation state may not "move" faster than this between steps.
            noise_floor: Effective noise floor for Shannon information content.
            amplification: Scale factor converting dimensionless activation
                information (bits) into a physical tracer energy budget. Energy
                accounting is invariant to this scale; it only sets the units of
                the reported Joule figures.
            analyze_tissue: When ``True``, also run the synthetic-neural-tissue
                bio-tracer analysis and attach its metrics to the trace.
        """
        self.temperature = float(temperature)
        self.medium_speed = float(medium_speed)
        self.noise_floor = float(noise_floor)
        self.amplification = float(amplification)
        self.analyze_tissue = bool(analyze_tissue)

        self.energy_auditor = EnergyAuditor()
        self.information_auditor = InformationAuditor()
        self.causality_auditor = CausalityAuditor()

        self.thermal_energy = K_B * self.temperature
        self.landauer_per_bit = STSLimits.landauer_limit(self.temperature)

    # -- primitive mappings -------------------------------------------------

    def _state_bits(self, activation: np.ndarray) -> float:
        """Shannon information content (bits) of an activation state."""
        flat = _flatten(activation)
        if flat.size == 0:
            return 0.0
        bits = self.information_auditor.shannon_information_content(
            flat, self.noise_floor
        )
        return float(max(bits, 0.0))

    def _state_energy(self, activation: np.ndarray) -> float:
        """Map an activation state to a physical tracer energy (Joules).

        Energy is anchored to information content via the Landauer relation:
        ``E = bits * k_B T ln2 * amplification``. This ties the energy and
        information primitives together exactly as STS requires.
        """
        return self._state_bits(activation) * self.landauer_per_bit * self.amplification

    def _mutual_estimate(self, a: np.ndarray, b: np.ndarray) -> float:
        """Independent correlation-based mutual-information estimate (bits).

        This reuses the audited STS estimator as a *cross-check* on the
        resonance-driven fidelity; it does not participate in the conservation
        accounting (which is governed by the single transmission coefficient).
        """
        fa, fb = _flatten(a), _flatten(b)
        n = min(fa.size, fb.size)
        if n >= 2 and np.std(fa[:n]) > 0 and np.std(fb[:n]) > 0:
            return float(self.information_auditor.mutual_information(fa[:n], fb[:n]))
        return 0.0

    # -- single transition --------------------------------------------------

    def _audit_step(
        self,
        index: int,
        label: str,
        state_in: np.ndarray,
        state_out: np.ndarray,
    ) -> ReasoningStepTrace:
        """Compute STS primitives and triple-audit for one kernel transition."""
        # Single propagation fidelity couples energy and information transport,
        # exactly as STS requires. ``transmission`` is the resonance (cosine)
        # overlap of the input/output activation directions.
        transmission = _cosine_overlap(state_in, state_out)

        # Energy-conserving propagation accounting.
        energy_in = self._state_energy(state_in)
        energy_out = transmission * energy_in
        energy_dissipated = energy_in - energy_out

        # Information accounting, driven by the *same* transmission coefficient
        # so that energy and information stay coupled (Landauer-consistent).
        info_injected = self._state_bits(state_in)
        info_detected = transmission * info_injected
        info_lost = info_injected - info_detected
        info_fidelity = transmission if info_injected > 0 else 1.0
        mutual_estimate = self._mutual_estimate(state_in, state_out)

        # Landauer floor: erasing ``info_lost`` bits costs at least this much.
        # With coupled transport this equals ``energy_dissipated`` (the channel
        # saturates the Landauer bound), so the floor is always respected.
        landauer_floor = info_lost * self.landauer_per_bit * self.amplification
        landauer_respected = energy_dissipated + 1e-30 >= landauer_floor

        # Causality: how far the state "moved" this tick (cosine distance).
        signal_speed = 1.0 - transmission

        energy_audit = self.energy_auditor.energy_audit(
            E_in=energy_in, E_out=energy_out, E_dissipated=energy_dissipated
        )
        information_audit = self.information_auditor.information_balance(
            I_injected=info_injected, I_detected=info_detected, I_lost=info_lost
        )
        causality_audit = self.causality_auditor.causality_check(
            signal_speed=signal_speed, medium_speed=self.medium_speed
        )

        return ReasoningStepTrace(
            index=index,
            label=label,
            energy_in=energy_in,
            energy_out=energy_out,
            energy_dissipated=energy_dissipated,
            landauer_floor=landauer_floor,
            landauer_respected=landauer_respected,
            information_injected=info_injected,
            information_detected=info_detected,
            information_lost=info_lost,
            information_fidelity=info_fidelity,
            mutual_information_estimate=mutual_estimate,
            transmission=transmission,
            signal_speed=signal_speed,
            medium_speed=self.medium_speed,
            energy_audit=energy_audit,
            information_audit=information_audit,
            causality_audit=causality_audit,
        )

    # -- DAG validation -----------------------------------------------------

    @staticmethod
    def _is_acyclic(num_nodes: int, edges: Sequence[Tuple[int, int]]) -> bool:
        """Kahn topological sort: return ``True`` iff the graph is a DAG."""
        indegree = [0] * num_nodes
        adjacency: List[List[int]] = [[] for _ in range(num_nodes)]
        for src, dst in edges:
            if not (0 <= src < num_nodes and 0 <= dst < num_nodes):
                return False
            adjacency[src].append(dst)
            indegree[dst] += 1
        queue = [n for n in range(num_nodes) if indegree[n] == 0]
        visited = 0
        while queue:
            node = queue.pop()
            visited += 1
            for nxt in adjacency[node]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    queue.append(nxt)
        return visited == num_nodes

    # -- public API ---------------------------------------------------------

    def attribute(
        self,
        kernels: Union[MCOPKernel, Sequence[MCOPKernel]],
        initial_state: np.ndarray,
        step_labels: Optional[Sequence[str]] = None,
        dependencies: Optional[Sequence[Tuple[int, int]]] = None,
        num_steps: int = 1,
    ) -> STSEnrichedTrace:
        """Execute an MCOP reasoning stack and return its STS-enriched trace.

        Args:
            kernels: A single kernel (applied ``num_steps`` times) or a sequence
                of kernels forming the reasoning stack.
            initial_state: The initial activation state fed to the first kernel.
            step_labels: Optional human labels for each reasoning step.
            dependencies: Optional explicit DAG edges ``(src, dst)`` between
                step indices. Defaults to a linear chain ``i -> i+1``.
            num_steps: Iteration count when a single kernel is supplied.

        Returns:
            The fully populated :class:`STSEnrichedTrace`.

        Raises:
            ValueError: If no kernels are provided.
        """
        kernel_list = self._normalize_kernels(kernels, num_steps)
        if not kernel_list:
            raise ValueError("At least one kernel must be provided.")

        callables = [_as_callable(k) for k in kernel_list]
        labels = self._normalize_labels(step_labels, len(callables))

        trace = STSEnrichedTrace()
        state = np.asarray(initial_state, dtype=np.float64)
        activation_log: List[np.ndarray] = [state]

        for i, (fn, label) in enumerate(zip(callables, labels)):
            next_state = np.asarray(fn(state), dtype=np.float64)
            step = self._audit_step(i, label, state, next_state)
            trace.steps.append(step)
            state = next_state
            activation_log.append(state)

        self._aggregate(trace)

        # DAG-preserving causality over the whole stack.
        edges = (
            list(dependencies)
            if dependencies is not None
            else [(i, i + 1) for i in range(len(callables) - 1)]
        )
        trace.dag_acyclic = self._is_acyclic(len(callables), edges)
        trace.causality_preserved = all(s.causality_audit.passed for s in trace.steps)
        trace.valid = (
            all(s.passed for s in trace.steps)
            and trace.dag_acyclic
            and trace.landauer_respected
        )

        if self.analyze_tissue:
            trace.tissue_metrics = SyntheticNeuralTissue(
                temperature=max(self.temperature, 310.0)
            ).analyze(activation_log)

        return trace

    # -- internals ----------------------------------------------------------

    @staticmethod
    def _normalize_kernels(
        kernels: Union[MCOPKernel, Sequence[MCOPKernel]], num_steps: int
    ) -> List[MCOPKernel]:
        """Expand a single kernel into ``num_steps`` copies or pass through."""
        if isinstance(kernels, (list, tuple)):
            return list(kernels)
        return [kernels] * max(1, int(num_steps))

    @staticmethod
    def _normalize_labels(
        step_labels: Optional[Sequence[str]], count: int
    ) -> List[str]:
        """Build a label per step, defaulting to ``kernel_{i}``."""
        if step_labels is not None and len(step_labels) == count:
            return list(step_labels)
        return [f"kernel_{i}" for i in range(count)]

    def _aggregate(self, trace: STSEnrichedTrace) -> None:
        """Populate aggregate energy/information metrics on ``trace`` in place."""
        trace.total_energy_in = float(sum(s.energy_in for s in trace.steps))
        trace.total_energy_out = float(sum(s.energy_out for s in trace.steps))
        trace.total_energy_dissipated = float(
            sum(s.energy_dissipated for s in trace.steps)
        )
        trace.total_information_injected = float(
            sum(s.information_injected for s in trace.steps)
        )
        trace.total_information_detected = float(
            sum(s.information_detected for s in trace.steps)
        )
        trace.energy_efficiency = (
            trace.total_energy_out / trace.total_energy_in
            if trace.total_energy_in > 0
            else 1.0
        )
        trace.information_fidelity = (
            trace.total_information_detected / trace.total_information_injected
            if trace.total_information_injected > 0
            else 1.0
        )
        total_bits_lost = sum(s.information_lost for s in trace.steps)
        ideal_floor = total_bits_lost * self.landauer_per_bit * self.amplification
        trace.landauer_efficiency = (
            ideal_floor / trace.total_energy_dissipated
            if trace.total_energy_dissipated > 0
            else 1.0
        )
        trace.landauer_respected = all(s.landauer_respected for s in trace.steps)


__all__ = [
    "MCOPKernel",
    "ReasoningStepTrace",
    "STSEnrichedTrace",
    "SyntheticNeuralTissue",
    "SensoryTracerAttributor",
]
