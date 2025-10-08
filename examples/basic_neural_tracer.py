#!/usr/bin/env python3
"""
Basic Neural Tracer Example

A simple example demonstrating how to use the biocompatible neural tracer
with the STS framework for neural activity monitoring.

This example shows:
1. Setting up a biocompatible neural tracer
2. Running a basic simulation
3. Analyzing results for experimental readiness
4. Understanding biological constraints and safety limits
"""

import sys
import os
import numpy as np

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sensory_tracer_science.tracers.biocompatible_neural import (
    BiocompatibleNeuralTracer, BiochemicalTracer, BiologicalParameters,
    NeuralTracerExperiment
)

def demonstrate_basic_usage():
    """Demonstrate basic biocompatible neural tracer usage."""
    
    print("🧬 Basic Biocompatible Neural Tracer Example")
    print("=" * 60)
    
    # Step 1: Define tissue geometry (brain slice for experiment)
    print("\n📏 Step 1: Defining Tissue Geometry")
    tissue_dimensions = {
        'length': 500e-6,   # 500 μm (typical brain slice thickness)
        'width': 500e-6,    # 500 μm
        'height': 200e-6    # 200 μm
    }
    
    print(f"   Tissue volume: {tissue_dimensions['length']*1e6:.0f} × {tissue_dimensions['width']*1e6:.0f} × {tissue_dimensions['height']*1e6:.0f} μm³")
    
    # Step 2: Create the neural tracer experiment
    print("\n🔬 Step 2: Creating Neural Tracer Experiment")
    experiment = NeuralTracerExperiment(tissue_dimensions)
    
    print(f"   Tracer molecule: {experiment.tracer.name}")
    print(f"   Molecular weight: {experiment.tracer.molecular_weight} g/mol")
    print(f"   Diffusion coefficient: {experiment.tracer.diffusion_coefficient:.2e} m²/s")
    
    # Step 3: Show biological parameters
    print("\n🧬 Step 3: Biological Parameters Overview")
    params = experiment.neural_tracer.params
    
    print("   Energy Parameters:")
    print(f"     ATP per uptake: {params.atp_per_uptake} molecules")
    print(f"     ATP per binding: {params.atp_per_binding} molecules")
    print(f"     ATP per clearance: {params.atp_per_clearance} molecules")
    
    print("   Safety Parameters:")
    print(f"     LD50 concentration: {params.ld50_concentration:.2e} mol/L")
    print(f"     NOAEL concentration: {params.noael_concentration:.2e} mol/L")
    print(f"     Max safe concentration: {experiment.neural_tracer.max_concentration:.2e} mol/L")
    
    print("   Transport Parameters:")
    print(f"     BBB permeability: {params.bbb_permeability_coefficient:.2e} m/s")
    print(f"     Binding site density: {params.binding_site_density:.2e} mol/L")
    
    # Step 4: Run simulation
    print("\n⚡ Step 4: Running Simulation (120 seconds, 5s timesteps)")
    
    try:
        results = experiment.run_neural_tracer_test(
            simulation_time=120.0,  # 2 minutes
            dt=5.0                  # 5 second timesteps
        )
        
        # Step 5: Analyze results
        print("\n📊 Step 5: Results Analysis")
        
        print("   Simulation Status:")
        print(f"     Overall Status: {'✅ PASSED' if results['test_status'] == 'PASSED' else '❌ FAILED'}")
        print(f"     Status Message: {results['status_message']}")
        
        print("   Concentration Analysis:")
        print(f"     Maximum concentration: {results['max_concentration']:.2e} mol/L")
        print(f"     Concentration limit: {experiment.neural_tracer.max_concentration:.2e} mol/L")
        concentration_safety = (results['max_concentration'] / experiment.neural_tracer.max_concentration) * 100
        print(f"     Safety margin: {100 - concentration_safety:.1f}% below limit")
        
        print("   Energy Analysis:")
        print(f"     Maximum ATP rate: {results['max_atp_rate']:.2e} mol/L/s")
        print(f"     ATP limit: {abs(experiment.neural_tracer.max_atp_depletion):.2e} mol/L/s")
        atp_usage = (results['max_atp_rate'] / abs(experiment.neural_tracer.max_atp_depletion)) * 100
        print(f"     ATP usage: {atp_usage:.4f}% of available budget")
        
        print("   Biological Validation:")
        print(f"     Biocompatibility: {'✅ PASSED' if results['biocompatibility_passed'] else '❌ FAILED'}")
        print(f"     Toxicity check: {'✅ PASSED' if results['toxicity_passed'] else '❌ FAILED'}")
        print(f"     Neuroinflammation: {'✅ PASSED' if results['neuroinflammation_passed'] else '❌ FAILED'}")
        print(f"     BBB permeability: {'✅ PASSED' if results['bbb_permeability_passed'] else '❌ FAILED'}")
        print(f"     Quantum measurement: {'✅ PASSED' if results['quantum_measurement_passed'] else '❌ FAILED'}")
        
        print("   Information Extraction:")
        info = results['information_metrics']
        print(f"     Spatial resolution: {info['spatial_resolution']:.2e} m")
        print(f"     Information entropy: {info['information_entropy']:.2f} bits")
        print(f"     Total information: {info['total_information_bits']:.1f} bits")
        print(f"     Signal-to-noise ratio: {info['signal_to_noise_ratio']:.2f}")
        
        # Step 6: Show advanced biological metrics
        print("\n🧬 Step 6: Advanced Biological Analysis")
        
        if 'toxicity_history' in results:
            # Analyze toxicity over time
            toxicity_data = results['toxicity_history']
            if toxicity_data:
                max_cytotoxicity = np.max([np.max(tox['cytotoxicity_fraction']) for tox in toxicity_data])
                max_inflammation = np.max([np.max(tox['inflammatory_response']) for tox in toxicity_data])
                
                print(f"     Maximum cytotoxicity: {max_cytotoxicity:.1%}")
                print(f"     Maximum inflammation: {max_inflammation:.2e} 1/s")
                print(f"     Cytotoxicity safety: {'✅ Safe' if max_cytotoxicity < 0.1 else '⚠️ Elevated' if max_cytotoxicity < 0.5 else '❌ Dangerous'}")
        
        if 'bbb_permeability' in results:
            print(f"     BBB permeability: {results['bbb_permeability']:.2e} m/s")
            delivery_efficiency = results['bbb_permeability'] / params.bbb_permeability_coefficient
            print(f"     Delivery efficiency: {delivery_efficiency:.1f}x baseline")
        
        if 'quantum_noise_history' in results:
            avg_quantum_noise = np.mean(results['quantum_noise_history'])
            print(f"     Average quantum noise: {avg_quantum_noise:.1%}")
            print(f"     Measurement fidelity: {(1-avg_quantum_noise)*100:.1f}%")
        
        # Step 7: Experimental readiness assessment
        print("\n🎯 Step 7: Experimental Readiness Assessment")
        
        if results['test_status'] == 'PASSED':
            print("   ✅ EXPERIMENTALLY READY!")
            print("   The biocompatible neural tracer meets all STS requirements:")
            print("     • All 5 STS axioms satisfied")
            print("     • Complete biological realism implemented")
            print("     • Safety limits respected")
            print("     • Energy constraints satisfied")
            print("     • Information preservation validated")
            print("   ")
            print("   🧬 Ready for in vivo validation studies!")
            print("   Next steps:")
            print("     1. Prepare experimental protocols")
            print("     2. Obtain regulatory approvals")  
            print("     3. Conduct pilot in vivo studies")
            print("     4. Validate computational predictions")
        else:
            print("   ⚠️ REQUIRES OPTIMIZATION")
            print("   Some validation checks failed. Review:")
            if not results['biocompatibility_passed']:
                print("     • Biocompatibility constraints")
            if not results['toxicity_passed']:
                print("     • Toxicity limits")
            print("   Optimize parameters before experimental use.")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Simulation failed: {e}")
        return None

def demonstrate_parameter_effects():
    """Demonstrate how different parameters affect tracer performance."""
    
    print("\n" + "=" * 60)
    print("🔧 Parameter Effects Demonstration")
    print("=" * 60)
    
    # Create base experiment
    tissue_dims = {'length': 200e-6, 'width': 200e-6, 'height': 100e-6}
    
    # Test different molecular weights
    molecular_weights = [500, 1000, 2000]  # g/mol
    
    print("\n📊 Effect of Molecular Weight on Performance:")
    print("   MW (g/mol)  | Diffusion (m²/s) | Stokes Radius (m) | Performance")
    print("   " + "-" * 65)
    
    for mw in molecular_weights:
        tracer = BiochemicalTracer("Test Tracer", mw)
        experiment = NeuralTracerExperiment(tissue_dims)
        experiment.tracer = tracer
        experiment.neural_tracer = BiocompatibleNeuralTracer(tracer, tissue_dims)
        
        # Quick test
        try:
            results = experiment.run_neural_tracer_test(simulation_time=60.0, dt=10.0)
            performance = "✅ PASSED" if results['test_status'] == 'PASSED' else "❌ FAILED"
            
            print(f"   {mw:8.0f}    | {tracer.diffusion_coefficient:.2e}    | {tracer.stokes_radius:.2e}     | {performance}")
        except Exception as e:
            print(f"   {mw:8.0f}    | {tracer.diffusion_coefficient:.2e}    | {tracer.stokes_radius:.2e}     | ❌ ERROR")
    
    print("\n💡 Key Insights:")
    print("   • Smaller molecules diffuse faster but may have lower binding")
    print("   • Larger molecules may have better fluorescence but slower transport")
    print("   • Optimal size balances diffusion, binding, and detection")

def main():
    """Main demonstration function."""
    
    # Run basic demonstration
    results = demonstrate_basic_usage()
    
    if results:
        # Show parameter effects
        demonstrate_parameter_effects()
        
        print("\n" + "=" * 60)
        print("🎉 Basic Neural Tracer Example Complete!")
        print("=" * 60)
        print("\n📚 Next Steps:")
        print("   • Explore advanced examples in this directory")
        print("   • Try parameter sensitivity analysis")
        print("   • Design your own experimental protocols")
        print("   • Validate with experimental data")
        print("\n🔬 Happy experimenting with STS!")
    
    return results is not None

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)