Sensory Tracer Science (STS)
=============================

A rigorous physics-based framework for sensory tracer analysis with complete biological realism.

.. toctree::
   :maxdepth: 2
   :caption: Documentation:
   
   api/index

Introduction
------------

The Sensory Tracer Science (STS) framework provides a comprehensive approach to understanding 
and designing biocompatible neural tracers based on fundamental physical principles.

**Core Principles:**

1. **Information Conservation**: Total information is conserved throughout measurement processes
2. **Quantum Measurement Limits**: Respects Heisenberg uncertainty principle constraints  
3. **Thermodynamic Limits**: Complies with Landauer's principle (minimum energy per bit)
4. **Biological Compatibility**: Maintains cellular viability and metabolic constraints
5. **Causal Structure**: Preserves spacetime causal relationships

Key Features
============

* **CODATA 2022 Compliance**: Exact fundamental physical constants
* **Landauer Principle**: Thermodynamic information processing limits
* **ATP Energetics**: Complete cellular energy budget analysis
* **Biocompatible Design**: Safe tracer concentration and flux limits
* **Augmented Validation**: 6-check validation framework for safety
* **Scientific Computing**: Professional-grade numerical precision

Mathematical Framework
======================

The STS framework is built on rigorous mathematical foundations:

**Energy Conservation**:

.. math::

   E_{total} = E_{optical} + E_{metabolic} + E_{dissipated}

**Information Limits**:

.. math::

   E_{min} = N_{bits} \cdot k_B T \ln(2)

where :math:`E_{min}` is the Landauer limit for :math:`N_{bits}` of information processing.

**ATP Energy Budget**:

.. math::

   E_{ATP} = n_{ATP} \cdot |\Delta G_{hydrolysis}| \cdot \eta

where :math:`\eta` is the ATP-to-work efficiency.

Installation
============

Install the STS package using pip:

.. code-block:: bash

   pip install sensory-tracer-science

For development installation:

.. code-block:: bash

   git clone https://github.com/Kuonirad/Sensory-Tracer-Science-STS-Proposal-for-a-New-Subfield
   cd Sensory-Tracer-Science-STS-Proposal-for-a-New-Subfield
   pip install -e .

Quick Start
===========

Basic usage example:

.. code-block:: python

   from sensory_tracer_science.core.sts_constants import *
   from sensory_tracer_science.tracers.biocompatible_neural import *
   
   # Create a biocompatible tracer
   tracer = BiochemicalTracer(
       name="Calcium indicator",
       molecular_weight=500.0,  # Da
       fluorescence_quantum_yield=0.8,
       binding_affinity=1e-6  # M
   )
   
   # Define tissue geometry
   geometry = {
       'length': 1e-3,    # 1 mm
       'width': 1e-3,     # 1 mm  
       'height': 100e-6,  # 100 μm
   }
   
   # Initialize tracer system
   system = BiocompatibleNeuralTracer(tracer, geometry)
   
   # Validate biocompatibility
   results = system.validate_biocompatibility()

**Validation Results:**

The framework performs comprehensive validation including:

- Energy conservation checks
- ATP compliance verification  
- Toxicity assessment
- Thermodynamic feasibility

Bibliography
============

.. bibliography::
   :style: alpha
   :all:

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`  
* :ref:`search`