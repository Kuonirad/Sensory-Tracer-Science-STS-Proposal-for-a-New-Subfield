"""
Tests for the STS <-> MCOP bridging adapter (``sts_mcop_adapter``).

These tests verify that the :class:`SensoryTracerAttributor` respects the three
STS conservation primitives (energy, information, causality) when wrapping an
MCOP-style reasoning stack, and that the bio-tracer generalization (synthetic
neural tissue) runs over LLM-like activation flows.
"""

import numpy as np
import pytest

from sensory_tracer_science.core.sts_constants import (
    STSLimits,
    ValidationTolerances,
)
from sensory_tracer_science.sts_mcop_adapter import (
    ReasoningStepTrace,
    SensoryTracerAttributor,
    STSEnrichedTrace,
    SyntheticNeuralTissue,
)


def _identity(x):
    """A loss-free kernel: output direction equals input direction."""
    return np.asarray(x, dtype=np.float64).copy()


def _lossy(x):
    """A lossy kernel that mixes the signal with an orthogonal component."""
    x = np.asarray(x, dtype=np.float64)
    rolled = np.roll(x, 1)
    return 0.4 * x + 0.6 * rolled


class _KernelObject:
    """Duck-typed MCOP kernel exposing ``execute`` instead of ``__call__``."""

    def __init__(self, gain=1.0):
        self.gain = gain

    def execute(self, x):
        return self.gain * np.asarray(x, dtype=np.float64)


@pytest.fixture
def state():
    rng = np.random.default_rng(1234)
    return rng.normal(size=48)


def test_identity_kernel_is_fully_valid(state):
    """A loss-free reasoning stack must pass all audits with unit fidelity."""
    attr = SensoryTracerAttributor()
    trace = attr.attribute([_identity, _identity, _identity], state)

    assert isinstance(trace, STSEnrichedTrace)
    assert trace.valid is True
    assert trace.dag_acyclic is True
    assert trace.causality_preserved is True
    assert trace.landauer_respected is True
    assert trace.information_fidelity == pytest.approx(1.0, abs=1e-9)
    assert trace.energy_efficiency == pytest.approx(1.0, abs=1e-9)


def test_energy_is_conserved_each_step(state):
    """E_in == E_out + E_dissipated within the STS energy-audit tolerance."""
    attr = SensoryTracerAttributor()
    trace = attr.attribute([_lossy, _lossy], state)

    for step in trace.steps:
        residual = abs(step.energy_in - (step.energy_out + step.energy_dissipated))
        max_allowed = ValidationTolerances.ENERGY_AUDIT_TOLERANCE * step.energy_in
        assert residual <= max_allowed + 1e-30
        assert step.energy_audit.passed


def test_information_balance_each_step(state):
    """I_injected == I_detected + I_lost and the info audit passes."""
    attr = SensoryTracerAttributor()
    trace = attr.attribute([_lossy, _lossy, _lossy], state)

    for step in trace.steps:
        assert step.information_injected == pytest.approx(
            step.information_detected + step.information_lost, rel=1e-9, abs=1e-12
        )
        assert step.information_audit.passed
        assert 0.0 <= step.information_fidelity <= 1.0


def test_causality_never_exceeds_medium_speed(state):
    """Signal speed must never exceed the configured medium speed."""
    attr = SensoryTracerAttributor(medium_speed=1.0)
    trace = attr.attribute([_lossy, _identity], state)

    for step in trace.steps:
        assert step.signal_speed <= step.medium_speed + 1e-12
        assert step.causality_audit.passed


def test_lossy_kernel_reduces_fidelity_but_conserves(state):
    """A lossy kernel lowers fidelity yet still satisfies conservation audits."""
    attr = SensoryTracerAttributor()
    lossy_trace = attr.attribute([_lossy], state)
    identity_trace = attr.attribute([_identity], state)

    assert lossy_trace.information_fidelity < identity_trace.information_fidelity
    # Conservation audits still pass (they verify balance, not quality).
    assert all(s.energy_audit.passed for s in lossy_trace.steps)
    assert all(s.information_audit.passed for s in lossy_trace.steps)


def test_landauer_floor_respected(state):
    """Dissipation must not fall below the Landauer cost of erased bits."""
    attr = SensoryTracerAttributor()
    trace = attr.attribute([_lossy, _lossy], state)

    landauer_per_bit = STSLimits.landauer_limit(attr.temperature)
    assert landauer_per_bit > 0
    for step in trace.steps:
        assert step.energy_dissipated + 1e-30 >= step.landauer_floor
        assert step.landauer_respected


def test_duck_typed_kernel_object(state):
    """Kernels exposing ``execute`` (no ``__call__``) are supported."""
    attr = SensoryTracerAttributor()
    trace = attr.attribute(_KernelObject(gain=1.0), state, num_steps=2)

    assert len(trace.steps) == 2
    assert trace.valid is True


def test_single_kernel_iterated(state):
    """A single kernel can be iterated ``num_steps`` times."""
    attr = SensoryTracerAttributor()
    trace = attr.attribute(_identity, state, num_steps=5)
    assert len(trace.steps) == 5
    assert all(isinstance(s, ReasoningStepTrace) for s in trace.steps)


def test_cyclic_dependencies_flagged_invalid(state):
    """A cyclic dependency graph must be detected and invalidate the trace."""
    attr = SensoryTracerAttributor()
    # Edges form a cycle 0 -> 1 -> 0 over two steps.
    trace = attr.attribute([_identity, _identity], state, dependencies=[(0, 1), (1, 0)])
    assert trace.dag_acyclic is False
    assert trace.valid is False


def test_custom_step_labels(state):
    """Provided labels (e.g. the MCOP triad) are attached to steps."""
    attr = SensoryTracerAttributor()
    labels = ["encoder", "stigmergy", "etch"]
    trace = attr.attribute([_identity, _identity, _identity], state, step_labels=labels)
    assert [s.label for s in trace.steps] == labels


def test_summary_and_report(state):
    """``summary`` exposes expected keys and ``report`` returns a string."""
    attr = SensoryTracerAttributor()
    trace = attr.attribute([_identity, _lossy], state)
    summary = trace.summary()
    for key in (
        "num_steps",
        "valid",
        "energy_efficiency",
        "information_fidelity",
        "landauer_efficiency",
    ):
        assert key in summary
    assert summary["num_steps"] == 2
    assert "ATTRIBUTION REPORT" in trace.report()


def test_determinism(state):
    """Identical inputs must produce identical attribution metrics."""
    attr = SensoryTracerAttributor()
    a = attr.attribute([_lossy, _identity], state).summary()
    b = attr.attribute([_lossy, _identity], state).summary()
    assert a == b


def test_synthetic_neural_tissue_analysis(state):
    """The bio-tracer generalization runs over an activation stack."""
    rng = np.random.default_rng(7)
    activations = [rng.normal(size=32) for _ in range(4)]
    metrics = SyntheticNeuralTissue().analyze(activations)
    for key in (
        "information_entropy",
        "mutual_information",
        "total_information_bits",
        "signal_to_noise_ratio",
    ):
        assert key in metrics
        assert np.isfinite(metrics[key])
    assert metrics["information_entropy"] >= 0.0


def test_attribute_with_tissue_metrics(state):
    """When enabled, tissue metrics are attached to the trace."""
    attr = SensoryTracerAttributor(analyze_tissue=True)
    trace = attr.attribute([_identity, _lossy], state)
    assert trace.tissue_metrics is not None
    assert "information_entropy" in trace.tissue_metrics


def test_empty_kernel_list_raises(state):
    """An empty reasoning stack is an error."""
    attr = SensoryTracerAttributor()
    with pytest.raises(ValueError):
        attr.attribute([], state)
