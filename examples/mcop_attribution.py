#!/usr/bin/env python3
"""
STS x MCOP Attribution Example

Demonstrates how to use ``SensoryTracerAttributor`` to trace a perceptual /
activation signal through an MCOP-style reasoning stack and obtain an
energy/information-fidelity account of the whole chain.

This example shows:
1. Defining MCOP kernels as plain callables (np.ndarray -> np.ndarray).
2. Wrapping the reasoning stack with the STS attributor.
3. Reading the enriched trace: per-step audits + end-to-end metrics.
4. Analyzing the activation flow as synthetic neural tissue.
"""

import os
import sys

import numpy as np

# Add project root to path so the example runs from a fresh checkout.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sensory_tracer_science import SensoryTracerAttributor


def make_kernels(hidden: int, seed: int = 0):
    """Build a 3-stage MCOP-style reasoning stack (encoder, stigmergy, etch)."""
    rng = np.random.default_rng(seed)

    # High-fidelity kernels: near-identity mixing keeps the signal coherent.
    weights = [
        np.eye(hidden) + 0.05 * rng.normal(size=(hidden, hidden)) for _ in range(3)
    ]

    def kernel(w):
        return lambda x: np.tanh(w @ np.asarray(x, dtype=float))

    return [kernel(w) for w in weights]


def main() -> None:
    hidden = 64
    rng = np.random.default_rng(42)
    prompt_embedding = rng.normal(size=hidden)

    kernels = make_kernels(hidden)

    attributor = SensoryTracerAttributor(analyze_tissue=True)
    trace = attributor.attribute(
        kernels,
        prompt_embedding,
        step_labels=["encoder", "stigmergy", "etch"],
    )

    print(trace.report())
    print()
    print("Machine-readable summary:")
    for key, value in trace.summary().items():
        print(f"  {key}: {value}")

    print()
    print(f"End-to-end attribution valid: {trace.valid}")


if __name__ == "__main__":
    main()
