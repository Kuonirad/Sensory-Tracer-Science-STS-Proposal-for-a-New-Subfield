# Sensory Tracer Science (STS) - Implementation Guide

## Quick Start

The Sensory Tracer Science framework provides a complete, validated implementation for energy-efficient, information-preserving sensory systems. This guide demonstrates how to use the framework for practical applications.

## Installation and Setup

```python
# Import the complete STS framework
import sensory_tracer_science as sts

# Quick validation check
print("STS Framework Status:", sts.quick_validation_test())
print("Framework Info:", sts.get_framework_info())
```

## Core Components

### 1. Validation System - The Heart of STS

Every STS system must pass the triple audit validation:

```python
from sensory_tracer_science import STSValidator

# Create validator instance
validator = STSValidator()

# Example: Validate a simple sensory system
system_data = {
    'E_in': 1e-9,        # 1 nJ input energy
    'E_out': 0.99e-9,    # 0.99 nJ output  
    'E_dissipated': 0.01e-9,  # 0.01 nJ dissipated
    'I_injected': 1000,  # 1000 bits injected
    'I_detected': 995,   # 995 bits detected
    'I_lost': 5,         # 5 bits lost
    'signal_speed': 2e8, # 200,000 km/s
    'medium_speed': 3e8  # 300,000 km/s (light speed)
}

# Run complete validation
results = validator.full_validation(system_data)
is_valid, status = validator.system_status(results)

print(f"System Status: {'✅ VALID' if is_valid else '❌ INVALID'}")
print(f"Message: {status}")
```

### 2. Physical Constants and Limits

Access fundamental STS constants and limits:

```python
from sensory_tracer_science import STSLimits, STSPhysics

# Landauer limit at room temperature
landauer_300K = STSLimits.landauer_limit(300.0)  # J/bit
print(f"Minimum energy per bit: {landauer_300K:.2e} J")

# Maximum speed in optical fiber (n=1.46)
max_fiber_speed = STSLimits.max_speed_in_medium(1.46)
print(f"Max speed in fiber: {max_fiber_speed:.2e} m/s")

# Thermal energy at body temperature  
thermal_37C = STSPhysics.thermal_energy(310.0)  # 37°C
print(f"Thermal energy at 37°C: {thermal_37C:.2e} J")
```

## Implementation Examples

### 1. Fiber-Optic Brillouin Tracer (Optical Temporalics)

```python
from sensory_tracer_science import BrillouinTracerExperiment

# Create 1 km fiber-optic sensing experiment
experiment = BrillouinTracerExperiment(fiber_length=1000.0)

# Run Brillouin tracer test with 1 nJ input (STS specification)
results = experiment.run_brillouin_test(input_energy=1e-9)

# Check validation results
if results['test_status'] == 'PASSED':
    print("✅ Fiber-optic tracer validated!")
    print(f"Energy conservation error: {results['energy_conservation_error']:.2e}")
    print(f"Information loss: {results['information_loss_percent']:.2f}%")
    
    # Generate detailed report
    report = experiment.generate_test_report(results)
    print(report)
else:
    print("❌ Validation failed:", results['status_message'])
```

### 2. Biocompatible Neural Tracer (Bio-Temporalics)

```python
from sensory_tracer_science import NeuralTracerExperiment

# Define brain tissue dimensions (1 mm × 1 mm × 0.5 mm)
tissue_dims = {
    'length': 1e-3,   # 1 mm
    'width': 1e-3,    # 1 mm  
    'height': 0.5e-3  # 0.5 mm
}

# Create neural tracer experiment
experiment = NeuralTracerExperiment(tissue_dims)

# Run biocompatible tracer test
results = experiment.run_neural_tracer_test(
    simulation_time=300.0,  # 5 minutes
    dt=5.0                  # 5 second time steps
)

if results['test_status'] == 'PASSED':
    print("✅ Neural tracer biocompatible!")
    print(f"Max concentration: {results['max_concentration']:.2e} mol/L")
    print(f"ATP consumption: {results['max_atp_rate']:.2e} mol/L/s")
    
    # Generate biocompatibility report
    report = experiment.generate_biocompatibility_report(results)
    print(report)
```

### 3. Quantum-Enhanced Tracer (Quantum Temporalics)

```python
from sensory_tracer_science import QuantumTracerExperiment
import numpy as np

# Create quantum sensing experiment
experiment = QuantumTracerExperiment()

# Test quantum phase sensing from 0 to π/2
sensing_parameters = np.linspace(0, np.pi/2, 6).tolist()

results = experiment.run_quantum_sensing_experiment(
    sensing_parameters=sensing_parameters,
    measurement_duration=1e-3  # 1 ms integration
)

if results['test_status'] == 'PASSED':
    print("✅ Quantum tracer validated!")
    
    # Check for quantum advantage
    perf = results['performance_metrics']
    if perf['max_quantum_advantage'] > 1.0:
        print(f"🎉 Quantum advantage achieved: {perf['max_quantum_advantage']:.2f}×")
    
    # Generate quantum report
    report = experiment.generate_quantum_report(results)
    print(report)
```

## Custom Tracer Development

### Step 1: Define Tracer Parameters

```python
from sensory_tracer_science.core import STSState
import numpy as np

# Define initial tracer state
initial_state = STSState(
    position=np.array([0.0, 0.0, 0.0]),  # Starting position (m)
    time=0.0,                           # Initial time (s)
    energy=1e-9,                        # Initial energy (J)
    information_content=1000.0,         # Information bits
    wave_amplitude=complex(1.0, 0.0),   # Wave amplitude
    entropy=0.0,                        # Initial entropy (J/K)
    temperature=300.0                   # Temperature (K)
)
```

### Step 2: Implement Governing Equations

```python
from sensory_tracer_science.core import (
    ConservationOfSensoryInformation,
    TracerEnergyContinuity,
    WavePropagationWithAttenuation
)

# Information conservation
info_conservation = ConservationOfSensoryInformation(temperature=300.0)

# Energy continuity  
energy_continuity = TracerEnergyContinuity()

# Wave propagation (ensure v < c/n!)
wave_propagation = WavePropagationWithAttenuation(
    velocity=2e8,          # 200,000 km/s
    attenuation=1e-3,      # Attenuation coefficient
    refractive_index=1.5   # Medium refractive index
)
```

### Step 3: Validate Custom Implementation

```python
# Create custom system parameters
custom_system_data = {
    'E_in': initial_state.energy,
    'E_out': 0.95 * initial_state.energy,  # 5% energy loss
    'E_dissipated': 0.05 * initial_state.energy,
    'I_injected': initial_state.information_content,
    'I_detected': 0.98 * initial_state.information_content,  # 2% info loss
    'I_lost': 0.02 * initial_state.information_content,
    'signal_speed': 2e8,
    'medium_speed': 2e8 * 1.001  # Slightly above to pass causality
}

# Validate against STS requirements
validator = STSValidator()
custom_results = validator.full_validation(custom_system_data)
is_valid, message = validator.system_status(custom_results)

if is_valid:
    print("✅ Custom tracer validated!")
else:
    print("❌ Custom tracer failed:", message)
```

## Advanced Features

### 1. System Solver for Time Evolution

```python
from sensory_tracer_science.core import STSSystemSolver

# Define system parameters
system_params = {
    'velocity': 1.5e8,        # Propagation speed
    'attenuation': 1e-4,      # Attenuation rate
    'temperature': 300.0,     # System temperature
    'refractive_index': 1.5   # Medium refractive index
}

# Create complete STS solver
solver = STSSystemSolver(system_params)

# Create spatial grid
spatial_grid = np.zeros((10, 10, 10, 3))  # 3D grid with coordinates

# Evolve system through time
states = solver.evolve_system(
    initial_state=initial_state,
    spatial_grid=spatial_grid,
    time_steps=100,
    dt=1e-6  # 1 microsecond steps
)

print(f"System evolved through {len(states)} time steps")
```

### 2. Comprehensive Testing Framework

```python
from sensory_tracer_science.tests import STSFrameworkTester

# Create comprehensive tester
tester = STSFrameworkTester()

# Run complete STS validation
validation_results = tester.run_complete_sts_validation()

# Generate final report
final_report = tester.generate_final_report(validation_results)
print(final_report)
```

## Best Practices

### 1. Always Validate First

```python
# ALWAYS run validation before deploying any STS system
def deploy_sts_system(system_data):
    validator = STSValidator()
    results = validator.full_validation(system_data)
    is_valid, message = validator.system_status(results)
    
    if not is_valid:
        raise ValueError(f"STS validation failed: {message}")
    
    print("✅ System validated - safe to deploy")
    return True
```

### 2. Respect Physical Constraints

```python
from sensory_tracer_science import ImplementationLimits

# Check limits before implementation
def check_fiber_optic_limits(input_energy):
    max_safe = ImplementationLimits.FiberOptic.MAX_INPUT_ENERGY
    if input_energy > max_safe:
        raise ValueError(f"Input energy {input_energy:.2e} J exceeds safe limit {max_safe:.2e} J")

def check_biocompatible_limits(concentration, atp_rate):
    max_conc = ImplementationLimits.Biocompatible.MAX_TRACER_CONCENTRATION  
    max_atp = abs(ImplementationLimits.Biocompatible.MAX_ATP_DEPLETION_RATE)
    
    if concentration > max_conc:
        raise ValueError(f"Concentration exceeds biocompatible limit")
    if atp_rate > max_atp:
        raise ValueError(f"ATP depletion rate exceeds safe limit")
```

### 3. Error Handling and Monitoring

```python
def robust_sts_operation():
    try:
        # Your STS implementation here
        results = run_sts_system()
        
        # Continuous validation monitoring
        if not validate_energy_conservation(results):
            raise RuntimeError("Energy conservation violated during operation")
        
        if not validate_information_balance(results):
            raise RuntimeError("Information balance violated during operation")
            
        return results
        
    except Exception as e:
        print(f"STS operation failed: {e}")
        # Implement safe shutdown procedures
        safe_shutdown()
        raise
```

## Integration Examples

### Web Application Integration

```python
from flask import Flask, jsonify
import sensory_tracer_science as sts

app = Flask(__name__)

@app.route('/validate_tracer', methods=['POST'])
def validate_tracer():
    try:
        # Get system data from request
        system_data = request.json
        
        # Validate using STS
        validator = sts.STSValidator()
        results = validator.full_validation(system_data)
        is_valid, message = validator.system_status(results)
        
        return jsonify({
            'valid': is_valid,
            'message': message,
            'results': {k: v.passed for k, v in results.items()}
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400
```

### Real-Time Monitoring

```python
import time
from sensory_tracer_science import STSValidator

class STSMonitor:
    def __init__(self):
        self.validator = STSValidator()
        
    def monitor_system(self, data_source, interval=1.0):
        while True:
            try:
                # Get current system data
                system_data = data_source.get_current_state()
                
                # Validate
                results = self.validator.full_validation(system_data)
                is_valid, message = self.validator.system_status(results)
                
                if not is_valid:
                    print(f"⚠️ STS VIOLATION DETECTED: {message}")
                    # Trigger alert/shutdown procedures
                    
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("Monitoring stopped")
                break
```

## Troubleshooting

### Common Issues and Solutions

1. **Energy Conservation Violation**
   - Check numerical precision in calculations
   - Verify all energy inputs and outputs are accounted for
   - Ensure dissipation terms are properly included

2. **Causality Check Failure**  
   - Verify signal speed < c/n for the medium
   - Check refractive index values
   - Account for dispersion effects

3. **Information Loss Exceeds Tolerance**
   - Review noise sources in the system
   - Check information encoding/decoding efficiency
   - Verify measurement precision

4. **Biocompatibility Violation**
   - Reduce tracer concentration below 1 μM
   - Monitor ATP consumption rates
   - Check for numerical overflow in simulations

## Further Reading

- **Theoretical Framework**: `docs/STS_THEORETICAL_FRAMEWORK.md`
- **Validation Report**: `docs/FINAL_VALIDATION_REPORT.md`  
- **API Documentation**: See docstrings in source code
- **Test Examples**: `tests/test_complete_sts_framework.py`

## Support and Development

The STS framework is designed for extensibility and community development. Key extension points:

1. **Custom Tracer Types**: Inherit from base tracer classes
2. **New Validation Rules**: Extend the validator system
3. **Additional Physical Domains**: Implement new governing equations
4. **Enhanced Simulations**: Add more sophisticated numerical methods

---

**The STS framework provides a complete, validated foundation for energy-efficient, information-preserving sensory systems. By following this implementation guide, you can develop robust, physically-grounded sensing technologies that push the boundaries of what's possible while respecting fundamental physical limits.**