#!/usr/bin/env python3
"""
Sensory Tracer Science (STS) - Test Runner Tool

Command-line interface for running specific STS tests with detailed output.
"""

import sys
import argparse
import time
from typing import Dict, Any, Optional
import traceback

# Import STS framework components
from ..tracers.biocompatible_neural import NeuralTracerExperiment
from ..tracers.quantum_enhanced import QuantumTracerExperiment
from ..tracers.fiber_optic_brillouin import BrillouinTracerExperiment


def run_biocompatible_test(tissue_size: str = "standard", duration: float = 60.0, verbose: bool = False) -> Dict[str, Any]:
    """Run biocompatible neural tracer test."""
    
    # Define tissue geometries
    geometries = {
        'micro': {'length': 100e-6, 'width': 50e-6, 'height': 10e-6},   # Microfluidic
        'standard': {'length': 1e-3, 'width': 1e-3, 'height': 0.5e-3},  # Brain tissue
        'large': {'length': 5e-3, 'width': 5e-3, 'height': 2e-3}        # Larger sample
    }
    
    if tissue_size not in geometries:
        raise ValueError(f"Invalid tissue size. Choose from: {list(geometries.keys())}")
    
    print(f"🧬 Running Biocompatible Neural Tracer Test...")
    print(f"   Tissue Size: {tissue_size}")
    print(f"   Duration: {duration} seconds")
    
    experiment = NeuralTracerExperiment(geometries[tissue_size])
    
    start_time = time.time()
    results = experiment.run_neural_tracer_test(simulation_time=duration, dt=min(duration/10, 10.0))
    execution_time = time.time() - start_time
    
    if verbose:
        report = experiment.generate_biocompatibility_report(results)
        print("\n" + report)
    
    return {
        'test_type': 'biocompatible_neural',
        'parameters': {'tissue_size': tissue_size, 'duration': duration},
        'execution_time': execution_time,
        'results': results
    }


def run_quantum_test(measurement_type: str = "standard", precision: str = "normal", verbose: bool = False) -> Dict[str, Any]:
    """Run quantum enhanced tracer test."""
    
    import numpy as np
    from ..tracers.quantum_enhanced import QuantumSensorParameters
    
    # Define measurement configurations
    if precision == "high":
        params = QuantumSensorParameters()
        params.detector_dark_count_rate = 10.0  # Low noise
        params.interference_visibility = 0.98   # High visibility  
        params.measurement_time = 2e-3          # Longer integration
        sensing_params = [0, np.pi/16, np.pi/8, np.pi/4]  # Fine resolution
    elif precision == "ultra":
        params = QuantumSensorParameters()
        params.detector_dark_count_rate = 1.0   # Ultra-low noise
        params.interference_visibility = 0.995  # Ultra-high visibility
        params.measurement_time = 5e-3          # Very long integration
        sensing_params = [0, np.pi/32, np.pi/16, np.pi/8]  # Ultra-fine resolution
    else:  # normal
        params = QuantumSensorParameters()
        sensing_params = [0, np.pi/8, np.pi/4, np.pi/2]  # Standard resolution
    
    print(f"⚛️  Running Quantum Enhanced Tracer Test...")
    print(f"   Measurement Type: {measurement_type}")
    print(f"   Precision: {precision}")
    
    experiment = QuantumTracerExperiment(params)
    
    start_time = time.time()
    results = experiment.run_quantum_sensing_experiment(
        sensing_parameters=sensing_params,
        measurement_duration=params.measurement_time
    )
    execution_time = time.time() - start_time
    
    if verbose:
        report = experiment.generate_quantum_report(results)
        print("\n" + report)
    
    return {
        'test_type': 'quantum_enhanced',
        'parameters': {'measurement_type': measurement_type, 'precision': precision},
        'execution_time': execution_time,
        'results': results
    }


def run_brillouin_test(fiber_length: float = 1000.0, input_energy: float = 1e-9, verbose: bool = False) -> Dict[str, Any]:
    """Run fiber optic Brillouin tracer test."""
    
    print(f"🌊 Running Fiber Optic Brillouin Tracer Test...")
    print(f"   Fiber Length: {fiber_length} meters")
    print(f"   Input Energy: {input_energy*1e9:.1f} nJ")
    
    experiment = BrillouinTracerExperiment(fiber_length=fiber_length)
    
    start_time = time.time()
    results = experiment.run_brillouin_test(input_energy=input_energy)
    execution_time = time.time() - start_time
    
    if verbose:
        report = experiment.generate_test_report(results)
        print("\n" + report)
    
    return {
        'test_type': 'fiber_optic_brillouin',
        'parameters': {'fiber_length': fiber_length, 'input_energy': input_energy},
        'execution_time': execution_time,
        'results': results
    }


def run_performance_benchmark(test_type: str = "all", iterations: int = 3) -> Dict[str, Any]:
    """Run performance benchmarks."""
    
    print(f"🏃 Running Performance Benchmarks...")
    print(f"   Test Type: {test_type}")
    print(f"   Iterations: {iterations}")
    
    benchmark_results = {}
    
    if test_type in ["all", "biocompatible"]:
        print("\n   • Benchmarking biocompatible tracer...")
        bio_times = []
        for i in range(iterations):
            result = run_biocompatible_test(tissue_size="standard", duration=30.0, verbose=False)
            bio_times.append(result['execution_time'])
            print(f"     Iteration {i+1}: {result['execution_time']:.2f}s")
        
        benchmark_results['biocompatible'] = {
            'mean_time': sum(bio_times) / len(bio_times),
            'min_time': min(bio_times),
            'max_time': max(bio_times),
            'times': bio_times
        }
    
    if test_type in ["all", "quantum"]:
        print("\n   • Benchmarking quantum tracer...")
        quantum_times = []
        for i in range(iterations):
            result = run_quantum_test(precision="normal", verbose=False)
            quantum_times.append(result['execution_time'])
            print(f"     Iteration {i+1}: {result['execution_time']:.2f}s")
        
        benchmark_results['quantum'] = {
            'mean_time': sum(quantum_times) / len(quantum_times),
            'min_time': min(quantum_times),
            'max_time': max(quantum_times),
            'times': quantum_times
        }
    
    if test_type in ["all", "brillouin"]:
        print("\n   • Benchmarking Brillouin tracer...")
        brillouin_times = []
        for i in range(iterations):
            result = run_brillouin_test(fiber_length=1000.0, verbose=False)
            brillouin_times.append(result['execution_time'])
            print(f"     Iteration {i+1}: {result['execution_time']:.2f}s")
        
        benchmark_results['brillouin'] = {
            'mean_time': sum(brillouin_times) / len(brillouin_times),
            'min_time': min(brillouin_times),
            'max_time': max(brillouin_times),
            'times': brillouin_times
        }
    
    return benchmark_results


def main():
    """Main entry point for STS test runner tool."""
    parser = argparse.ArgumentParser(
        description="Sensory Tracer Science (STS) Test Runner Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sts-test --biocompatible --tissue-size standard --duration 60
  sts-test --quantum --precision high  
  sts-test --brillouin --fiber-length 5000 --input-energy 0.5e-9
  sts-test --benchmark --iterations 5
        """
    )
    
    # Test type selection
    test_group = parser.add_mutually_exclusive_group(required=True)
    test_group.add_argument('--biocompatible', action='store_true', help='Run biocompatible neural tracer test')
    test_group.add_argument('--quantum', action='store_true', help='Run quantum enhanced tracer test')
    test_group.add_argument('--brillouin', action='store_true', help='Run fiber optic Brillouin tracer test')
    test_group.add_argument('--benchmark', action='store_true', help='Run performance benchmarks')
    
    # Biocompatible tracer options
    parser.add_argument('--tissue-size', choices=['micro', 'standard', 'large'], default='standard',
                       help='Tissue sample size for biocompatible test')
    parser.add_argument('--duration', type=float, default=60.0,
                       help='Simulation duration in seconds for biocompatible test')
    
    # Quantum tracer options  
    parser.add_argument('--precision', choices=['normal', 'high', 'ultra'], default='normal',
                       help='Measurement precision for quantum test')
    parser.add_argument('--measurement-type', default='standard',
                       help='Type of quantum measurement')
    
    # Brillouin tracer options
    parser.add_argument('--fiber-length', type=float, default=1000.0,
                       help='Fiber length in meters for Brillouin test')
    parser.add_argument('--input-energy', type=float, default=1e-9,
                       help='Input pulse energy in Joules for Brillouin test')
    
    # Benchmark options
    parser.add_argument('--benchmark-type', choices=['all', 'biocompatible', 'quantum', 'brillouin'], 
                       default='all', help='Type of benchmarks to run')
    parser.add_argument('--iterations', type=int, default=3,
                       help='Number of benchmark iterations')
    
    # General options
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--output', '-o', help='Output results to file')
    
    args = parser.parse_args()
    
    print("🧪 STS Test Runner Starting...")
    print("=" * 50)
    
    try:
        result = None
        
        if args.biocompatible:
            result = run_biocompatible_test(
                tissue_size=args.tissue_size,
                duration=args.duration,
                verbose=args.verbose
            )
        
        elif args.quantum:
            result = run_quantum_test(
                measurement_type=args.measurement_type,
                precision=args.precision,
                verbose=args.verbose
            )
        
        elif args.brillouin:
            result = run_brillouin_test(
                fiber_length=args.fiber_length,
                input_energy=args.input_energy,
                verbose=args.verbose
            )
        
        elif args.benchmark:
            result = run_performance_benchmark(
                test_type=args.benchmark_type,
                iterations=args.iterations
            )
        
        # Output results
        if result and args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n📄 Results saved to: {args.output}")
        
        if result:
            if 'results' in result:
                test_results = result['results']
                status = test_results.get('test_status', 'UNKNOWN')
                execution_time = result.get('execution_time', 0)
                
                print(f"\n✨ Test Complete!")
                print(f"   Status: {status}")
                print(f"   Execution Time: {execution_time:.2f} seconds")
                
                return 0 if status == 'PASSED' else 1
            else:
                # Benchmark results
                print(f"\n📊 Benchmark Results:")
                for test_name, bench_data in result.items():
                    print(f"   {test_name.title()}:")
                    print(f"     Mean Time: {bench_data['mean_time']:.2f}s")
                    print(f"     Min Time:  {bench_data['min_time']:.2f}s")
                    print(f"     Max Time:  {bench_data['max_time']:.2f}s")
                
                return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        if args.verbose:
            traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())