#!/usr/bin/env python3
"""
STS Implementation Validation Tool

Comprehensive validation of Sensory Tracer Science implementations
ensuring compliance with all 5 fundamental axioms and biological constraints.
"""

import sys
import os
import argparse
from typing import Dict, List, Tuple, Any

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from sensory_tracer_science.validation.sts_validator import STSValidator, ValidationResult
    from sensory_tracer_science.tracers.biocompatible_neural import (
        BiocompatibleNeuralTracer, BiochemicalTracer, NeuralTracerExperiment
    )
    from sensory_tracer_science.core.sts_constants import STSLimits
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

def validate_biocompatible_tracer() -> Dict[str, Any]:
    """Comprehensive validation of biocompatible neural tracer."""
    print("🧬 Validating Biocompatible Neural Tracer...")
    
    # Create test experiment
    tissue_dims = {'length': 100e-6, 'width': 100e-6, 'height': 50e-6}
    experiment = NeuralTracerExperiment(tissue_dims)
    
    try:
        # Run validation test
        results = experiment.run_neural_tracer_test(simulation_time=30.0, dt=5.0)
        
        validation_summary = {
            'test_status': results['test_status'],
            'biocompatibility_passed': results['biocompatibility_passed'],
            'toxicity_passed': results['toxicity_passed'],
            'neuroinflammation_passed': results['neuroinflammation_passed'],
            'quantum_measurement_passed': results['quantum_measurement_passed'],
            'bbb_permeability_passed': results['bbb_permeability_passed'],
            'max_concentration': results['max_concentration'],
            'max_atp_rate': results['max_atp_rate'],
            'validation_results': results['validation_results']
        }
        
        return validation_summary
        
    except Exception as e:
        return {'error': str(e), 'test_status': 'FAILED'}

def validate_sts_axioms(system_data: Dict[str, float]) -> Dict[str, ValidationResult]:
    """Validate compliance with STS axioms."""
    print("⚡ Validating STS Axiom Compliance...")
    
    validator = STSValidator()
    return validator.full_validation(system_data)

def check_parameter_ranges() -> List[Tuple[str, bool, str]]:
    """Check if all parameters are within expected biological ranges."""
    print("📊 Checking Parameter Ranges...")
    
    from sensory_tracer_science.tracers.biocompatible_neural import BiologicalParameters
    
    params = BiologicalParameters()
    checks = []
    
    # ATP parameters
    checks.append(("ATP concentration", 1e-4 <= params.atp_concentration <= 1e-2, 
                  f"{params.atp_concentration:.2e} mol/L"))
    
    # Toxicity parameters
    checks.append(("LD50 concentration", 1e-6 <= params.ld50_concentration <= 1e-4, 
                  f"{params.ld50_concentration:.2e} mol/L"))
    
    # BBB parameters  
    checks.append(("BBB permeability", 1e-10 <= params.bbb_permeability_coefficient <= 1e-6, 
                  f"{params.bbb_permeability_coefficient:.2e} m/s"))
    
    # Binding parameters
    checks.append(("Binding sites", 1e-6 <= params.binding_site_density <= 1e-2, 
                  f"{params.binding_site_density:.2e} mol/L"))
    
    return checks

def generate_validation_report(biocompat_results: Dict[str, Any], 
                              axiom_results: Dict[str, ValidationResult],
                              parameter_checks: List[Tuple[str, bool, str]]) -> str:
    """Generate comprehensive validation report."""
    
    report = "=" * 80 + "\n"
    report += "STS IMPLEMENTATION VALIDATION REPORT\n"
    report += "=" * 80 + "\n\n"
    
    # Overall status
    overall_status = (biocompat_results.get('test_status') == 'PASSED' and 
                     all(result.passed for result in axiom_results.values()) and
                     all(check[1] for check in parameter_checks))
    
    report += f"OVERALL STATUS: {'✅ PASSED' if overall_status else '❌ FAILED'}\n\n"
    
    # Biocompatible tracer validation
    report += "🧬 BIOCOMPATIBLE TRACER VALIDATION:\n"
    if 'error' in biocompat_results:
        report += f"❌ Error: {biocompat_results['error']}\n"
    else:
        report += f"  Test Status: {'✅' if biocompat_results['test_status'] == 'PASSED' else '❌'} {biocompat_results['test_status']}\n"
        report += f"  Biocompatibility: {'✅' if biocompat_results['biocompatibility_passed'] else '❌'} {'PASSED' if biocompat_results['biocompatibility_passed'] else 'FAILED'}\n"
        report += f"  Toxicity Check: {'✅' if biocompat_results['toxicity_passed'] else '❌'} {'PASSED' if biocompat_results['toxicity_passed'] else 'FAILED'}\n"
        report += f"  Neuroinflammation: {'✅' if biocompat_results['neuroinflammation_passed'] else '❌'} {'PASSED' if biocompat_results['neuroinflammation_passed'] else 'FAILED'}\n"
        report += f"  Quantum Measurement: {'✅' if biocompat_results['quantum_measurement_passed'] else '❌'} {'PASSED' if biocompat_results['quantum_measurement_passed'] else 'FAILED'}\n"
        report += f"  BBB Permeability: {'✅' if biocompat_results['bbb_permeability_passed'] else '❌'} {'PASSED' if biocompat_results['bbb_permeability_passed'] else 'FAILED'}\n"
        report += f"  Max Concentration: {biocompat_results['max_concentration']:.2e} mol/L\n"
        report += f"  Max ATP Rate: {biocompat_results['max_atp_rate']:.2e} mol/L/s\n"
    
    report += "\n"
    
    # STS axiom validation
    report += "⚡ STS AXIOM COMPLIANCE:\n"
    for axiom_name, result in axiom_results.items():
        status = "✅" if result.passed else "❌"
        report += f"  {axiom_name.replace('_', ' ').title()}: {status} {'PASSED' if result.passed else 'FAILED'}\n"
    
    report += "\n"
    
    # Parameter range checks
    report += "📊 PARAMETER RANGE VALIDATION:\n"
    for param_name, is_valid, value in parameter_checks:
        status = "✅" if is_valid else "❌"
        report += f"  {param_name}: {status} {value}\n"
    
    report += "\n" + "=" * 80 + "\n"
    
    if overall_status:
        report += "🎉 VALIDATION SUCCESSFUL!\n"
        report += "✅ All STS axioms satisfied\n"
        report += "✅ Biocompatible tracer experimentally ready\n"
        report += "✅ All parameters within biological ranges\n"
        report += "✅ Framework ready for in vivo validation studies\n"
    else:
        report += "❌ VALIDATION FAILED!\n"
        report += "Some components do not meet STS requirements.\n"
        report += "Review failed checks above and address issues.\n"
    
    report += "=" * 80
    
    return report

def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="STS Implementation Validation Tool")
    parser.add_argument("--output", "-o", help="Output file for validation report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print("🔧 STS Implementation Validation Tool")
    print("=" * 50)
    
    try:
        # Run biocompatible tracer validation
        biocompat_results = validate_biocompatible_tracer()
        
        # Create test system data for axiom validation
        test_system_data = {
            'E_in': 1e-18,      # J
            'E_out': 0.0,       # J
            'E_dissipated': 1e-18,  # J
            'I_injected': 100.0,    # bits
            'I_detected': 95.0,     # bits
            'I_lost': 5.0,          # bits
            'signal_speed': 1e-6,   # m/s
            'medium_speed': 2e8     # m/s
        }
        
        # Run STS axiom validation
        axiom_results = validate_sts_axioms(test_system_data)
        
        # Check parameter ranges
        parameter_checks = check_parameter_ranges()
        
        # Generate report
        report = generate_validation_report(biocompat_results, axiom_results, parameter_checks)
        
        # Output report
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"📄 Report saved to: {args.output}")
        else:
            print(report)
            
        # Exit with appropriate code
        overall_success = (biocompat_results.get('test_status') == 'PASSED' and 
                          all(result.passed for result in axiom_results.values()) and
                          all(check[1] for check in parameter_checks))
        
        sys.exit(0 if overall_success else 1)
        
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()