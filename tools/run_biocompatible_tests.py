#!/usr/bin/env python3
"""
Biocompatible Tracer Testing Suite

Comprehensive testing suite for biocompatible neural tracers
with detailed analysis and reporting capabilities.
"""

import sys
import os
import argparse
import json
import time
from typing import Dict, List, Any

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from sensory_tracer_science.tracers.biocompatible_neural import (
        BiocompatibleNeuralTracer, BiochemicalTracer, BiologicalParameters,
        NeuralTracerExperiment, run_biocompatible_tracer_tests
    )
    import numpy as np
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

def run_quick_validation() -> Dict[str, Any]:
    """Run quick validation test (30 seconds)."""
    print("⚡ Running Quick Validation Test (30s)...")
    
    tissue_dims = {'length': 50e-6, 'width': 50e-6, 'height': 25e-6}
    experiment = NeuralTracerExperiment(tissue_dims)
    
    start_time = time.time()
    results = experiment.run_neural_tracer_test(simulation_time=30.0, dt=5.0)
    end_time = time.time()
    
    results['execution_time'] = end_time - start_time
    results['test_type'] = 'quick_validation'
    
    return results

def run_standard_tests() -> Dict[str, Any]:
    """Run standard biocompatible tracer tests."""
    print("🧬 Running Standard Biocompatible Tracer Tests...")
    
    start_time = time.time()
    results = run_biocompatible_tracer_tests()
    end_time = time.time()
    
    # Add execution time to overall summary
    results['overall_summary']['execution_time'] = end_time - start_time
    
    return results

def run_stress_test() -> Dict[str, Any]:
    """Run stress test with challenging parameters."""
    print("💪 Running Stress Test with Challenging Parameters...")
    
    # Large tissue volume with long simulation
    large_tissue = {
        'length': 2e-3,   # 2 mm
        'width': 2e-3,    # 2 mm  
        'height': 1e-3    # 1 mm
    }
    
    experiment = NeuralTracerExperiment(large_tissue)
    
    start_time = time.time()
    results = experiment.run_neural_tracer_test(simulation_time=600.0, dt=10.0)  # 10 minutes
    end_time = time.time()
    
    results['execution_time'] = end_time - start_time
    results['test_type'] = 'stress_test'
    
    return results

def run_parameter_sensitivity_analysis() -> Dict[str, Any]:
    """Run parameter sensitivity analysis."""
    print("📊 Running Parameter Sensitivity Analysis...")
    
    base_params = BiologicalParameters()
    tissue_dims = {'length': 100e-6, 'width': 100e-6, 'height': 50e-6}
    
    # Parameters to vary
    sensitivity_tests = {
        'atp_per_uptake': [0.5, 1.0, 2.0],
        'ld50_concentration': [5e-6, 10e-6, 20e-6],
        'bbb_permeability_coefficient': [5e-9, 1e-8, 2e-8],
        'binding_site_density': [5e-4, 1e-3, 2e-3]
    }
    
    sensitivity_results = {}
    
    for param_name, values in sensitivity_tests.items():
        print(f"  Testing {param_name}...")
        param_results = {}
        
        for value in values:
            # Create modified parameters
            params = BiologicalParameters()
            setattr(params, param_name, value)
            
            # Run test with modified parameters
            tracer = BiochemicalTracer("Test Tracer", 1000.0)
            neural_tracer = BiocompatibleNeuralTracer(tracer, tissue_dims, params)
            experiment = NeuralTracerExperiment(tissue_dims)
            experiment.neural_tracer = neural_tracer
            
            try:
                results = experiment.run_neural_tracer_test(simulation_time=60.0, dt=5.0)
                param_results[str(value)] = {
                    'test_status': results['test_status'],
                    'max_concentration': results['max_concentration'],
                    'max_atp_rate': results['max_atp_rate'],
                    'biocompatibility_passed': results['biocompatibility_passed']
                }
            except Exception as e:
                param_results[str(value)] = {'error': str(e)}
        
        sensitivity_results[param_name] = param_results
    
    return {'sensitivity_analysis': sensitivity_results}

def run_different_tracers_comparison() -> Dict[str, Any]:
    """Compare different tracer molecules."""
    print("🔬 Running Different Tracer Molecules Comparison...")
    
    tissue_dims = {'length': 100e-6, 'width': 100e-6, 'height': 50e-6}
    
    # Different tracer configurations
    tracers_config = {
        'calcium_green_1': {'name': 'Calcium Green-1', 'mw': 1000.0, 'qy': 0.8, 'ka': 1e-6},
        'fluo_4': {'name': 'Fluo-4', 'mw': 750.0, 'qy': 0.9, 'ka': 3e-7},
        'oregon_green': {'name': 'Oregon Green BAPTA', 'mw': 1200.0, 'qy': 0.7, 'ka': 2e-6},
        'small_molecule': {'name': 'Small Test Tracer', 'mw': 300.0, 'qy': 0.6, 'ka': 1e-5}
    }
    
    comparison_results = {}
    
    for tracer_id, config in tracers_config.items():
        print(f"  Testing {config['name']}...")
        
        # Create tracer
        tracer = BiochemicalTracer(
            name=config['name'],
            molecular_weight=config['mw'],
            fluorescence_quantum_yield=config['qy'],
            binding_affinity=config['ka']
        )
        
        # Create experiment
        experiment = NeuralTracerExperiment(tissue_dims)
        experiment.tracer = tracer
        experiment.neural_tracer = BiocompatibleNeuralTracer(tracer, tissue_dims)
        
        try:
            results = experiment.run_neural_tracer_test(simulation_time=120.0, dt=5.0)
            comparison_results[tracer_id] = {
                'tracer_properties': {
                    'name': config['name'],
                    'molecular_weight': config['mw'],
                    'diffusion_coefficient': tracer.diffusion_coefficient,
                    'stokes_radius': tracer.stokes_radius
                },
                'test_status': results['test_status'],
                'max_concentration': results['max_concentration'],
                'max_atp_rate': results['max_atp_rate'],
                'biocompatibility_passed': results['biocompatibility_passed'],
                'information_bits': results['information_metrics']['total_information_bits']
            }
        except Exception as e:
            comparison_results[tracer_id] = {'error': str(e)}
    
    return {'tracer_comparison': comparison_results}

def generate_comprehensive_report(all_results: Dict[str, Any]) -> str:
    """Generate comprehensive testing report."""
    
    report = "=" * 80 + "\n"
    report += "BIOCOMPATIBLE TRACER COMPREHENSIVE TEST REPORT\n"
    report += "=" * 80 + "\n\n"
    
    report += f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Quick validation results
    if 'quick_validation' in all_results:
        qv = all_results['quick_validation']
        report += "⚡ QUICK VALIDATION TEST:\n"
        report += f"  Status: {'✅' if qv['test_status'] == 'PASSED' else '❌'} {qv['test_status']}\n"
        report += f"  Execution Time: {qv.get('execution_time', 0):.1f} seconds\n"
        report += f"  Biocompatibility: {'PASSED' if qv.get('biocompatibility_passed', False) else 'FAILED'}\n\n"
    
    # Standard test results
    if 'standard_tests' in all_results:
        st = all_results['standard_tests']
        if 'overall_summary' in st:
            summary = st['overall_summary']
            report += "🧬 STANDARD TESTS SUMMARY:\n"
            report += f"  Passed Tests: {summary['passed_tests']}/{summary['total_tests']}\n"
            report += f"  Pass Rate: {summary['pass_rate']*100:.1f}%\n"
            report += f"  Overall Status: {'✅' if summary['overall_status'] == 'PASSED' else '❌'} {summary['overall_status']}\n"
            report += f"  Execution Time: {summary.get('execution_time', 0):.1f} seconds\n\n"
    
    # Stress test results
    if 'stress_test' in all_results:
        stress = all_results['stress_test']
        report += "💪 STRESS TEST:\n"
        report += f"  Status: {'✅' if stress['test_status'] == 'PASSED' else '❌'} {stress['test_status']}\n"
        report += f"  Execution Time: {stress.get('execution_time', 0):.1f} seconds\n"
        report += f"  Max Concentration: {stress.get('max_concentration', 0):.2e} mol/L\n"
        report += f"  Biocompatibility: {'PASSED' if stress.get('biocompatibility_passed', False) else 'FAILED'}\n\n"
    
    # Parameter sensitivity analysis
    if 'sensitivity_analysis' in all_results:
        sens = all_results['sensitivity_analysis']['sensitivity_analysis']
        report += "📊 PARAMETER SENSITIVITY ANALYSIS:\n"
        for param_name, param_results in sens.items():
            report += f"  {param_name}:\n"
            for value, result in param_results.items():
                if 'error' in result:
                    report += f"    {value}: ❌ ERROR - {result['error']}\n"
                else:
                    status = "✅" if result['test_status'] == 'PASSED' else "❌"
                    report += f"    {value}: {status} {result['test_status']}\n"
        report += "\n"
    
    # Tracer comparison
    if 'tracer_comparison' in all_results:
        comp = all_results['tracer_comparison']['tracer_comparison']
        report += "🔬 TRACER MOLECULES COMPARISON:\n"
        for tracer_id, result in comp.items():
            if 'error' in result:
                report += f"  {tracer_id}: ❌ ERROR - {result['error']}\n"
            else:
                props = result['tracer_properties']
                status = "✅" if result['test_status'] == 'PASSED' else "❌"
                report += f"  {props['name']}: {status}\n"
                report += f"    Molecular Weight: {props['molecular_weight']:.0f} g/mol\n"
                report += f"    Diffusion Coeff: {props['diffusion_coefficient']:.2e} m²/s\n"
                report += f"    Information Bits: {result.get('information_bits', 0):.1f}\n"
        report += "\n"
    
    # Overall assessment
    report += "=" * 80 + "\n"
    
    # Count successful tests
    successful_tests = 0
    total_tests = 0
    
    if 'quick_validation' in all_results:
        total_tests += 1
        if all_results['quick_validation']['test_status'] == 'PASSED':
            successful_tests += 1
    
    if 'standard_tests' in all_results and 'overall_summary' in all_results['standard_tests']:
        summary = all_results['standard_tests']['overall_summary']
        total_tests += summary['total_tests']
        successful_tests += summary['passed_tests']
    
    if 'stress_test' in all_results:
        total_tests += 1
        if all_results['stress_test']['test_status'] == 'PASSED':
            successful_tests += 1
    
    overall_success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    if overall_success_rate >= 90:
        report += "🎉 COMPREHENSIVE TESTING: EXCELLENT RESULTS!\n"
        report += f"✅ Success Rate: {overall_success_rate:.1f}% ({successful_tests}/{total_tests})\n"
        report += "✅ Biocompatible tracer is experimentally ready\n"
        report += "✅ Framework shows robust performance\n"
        report += "🧬 READY FOR IN VIVO VALIDATION STUDIES!\n"
    elif overall_success_rate >= 70:
        report += "⚠️  COMPREHENSIVE TESTING: GOOD RESULTS WITH AREAS FOR IMPROVEMENT\n"
        report += f"Success Rate: {overall_success_rate:.1f}% ({successful_tests}/{total_tests})\n"
        report += "Some tests failed - review individual results for optimization\n"
    else:
        report += "❌ COMPREHENSIVE TESTING: SIGNIFICANT ISSUES DETECTED\n"
        report += f"Success Rate: {overall_success_rate:.1f}% ({successful_tests}/{total_tests})\n"
        report += "Multiple test failures - requires debugging and optimization\n"
    
    report += "=" * 80
    
    return report

def main():
    """Main testing function."""
    parser = argparse.ArgumentParser(description="Biocompatible Tracer Testing Suite")
    parser.add_argument("--test-type", choices=['quick', 'standard', 'stress', 'sensitivity', 'comparison', 'all'],
                       default='all', help="Type of test to run")
    parser.add_argument("--output", "-o", help="Output file for test results (JSON)")
    parser.add_argument("--report", "-r", help="Output file for test report (text)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print("🧪 Biocompatible Tracer Testing Suite")
    print("=" * 50)
    
    all_results = {}
    
    try:
        if args.test_type in ['quick', 'all']:
            all_results['quick_validation'] = run_quick_validation()
        
        if args.test_type in ['standard', 'all']:
            all_results['standard_tests'] = run_standard_tests()
        
        if args.test_type in ['stress', 'all']:
            all_results['stress_test'] = run_stress_test()
        
        if args.test_type in ['sensitivity', 'all']:
            all_results.update(run_parameter_sensitivity_analysis())
        
        if args.test_type in ['comparison', 'all']:
            all_results.update(run_different_tracers_comparison())
        
        # Generate report
        report = generate_comprehensive_report(all_results)
        
        # Save results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(all_results, f, indent=2, default=str)
            print(f"📄 Results saved to: {args.output}")
        
        if args.report:
            with open(args.report, 'w') as f:
                f.write(report)
            print(f"📊 Report saved to: {args.report}")
        
        if not args.output and not args.report:
            print(report)
        
    except Exception as e:
        print(f"❌ Testing failed with error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()