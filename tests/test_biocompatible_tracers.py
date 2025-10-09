"""
Comprehensive test suite for biocompatible neural tracer validation.
Tests the complete biocompatible neural tracer framework and safety margins.
"""

import pytest
import numpy as np
import numpy.testing as npt
from sensory_tracer_science.tracers.biocompatible_neural import (
    BiocompatibleNeuralTracer, BiochemicalTracer, BiologicalParameters,
    NeuralTracerExperiment
)
from sensory_tracer_science.core.sts_constants import STSLimits, ImplementationLimits


class TestBiocompatibleTracerValidation:
    """Test biocompatible neural tracer validation framework."""
    
    def test_neural_tracer_construction(self):
        """Test basic neural tracer construction with proper parameters."""
        # Create biochemical tracer
        tracer = BiochemicalTracer(
            name="Test Ca Indicator",
            molecular_weight=800.0,  # g/mol (typical Ca indicator)
            fluorescence_quantum_yield=0.7,
            binding_affinity=1e-6  # mol/L
        )
        
        # Create tissue geometry
        tissue_geometry = {
            'length': 500e-6,   # 500 μm
            'width': 500e-6,    # 500 μm  
            'height': 200e-6    # 200 μm
        }
        
        # Create neural tracer with default parameters
        neural_tracer = BiocompatibleNeuralTracer(
            tracer=tracer,
            tissue_geometry=tissue_geometry
        )
        
        # Verify construction
        assert neural_tracer.tracer.name == "Test Ca Indicator"
        assert neural_tracer.tissue_volume == 500e-6 * 500e-6 * 200e-6
        assert neural_tracer.max_concentration == ImplementationLimits.Biocompatible.MAX_TRACER_CONCENTRATION
    
    def test_biological_parameters_validation(self):
        """Test biological parameters are within physiological ranges."""
        params = BiologicalParameters()
        
        # Test ATP parameters
        assert params.atp_concentration > 0, "ATP concentration must be positive"
        assert 1e-6 <= params.atp_concentration <= 1e-1, "ATP concentration outside physiological range"
        assert params.atp_free_energy > 0, "ATP free energy should be positive (stored as positive value)"
        
        # Test cellular parameters
        assert params.cell_radius > 0, "Cell radius must be positive"
        assert 1e-6 <= params.cell_radius <= 100e-6, "Cell radius outside reasonable range"
        
        # Test diffusion coefficients
        assert params.diffusion_coefficient_tissue > 0, "Tissue diffusion coefficient must be positive"
        assert params.diffusion_coefficient_cytoplasm >= params.diffusion_coefficient_tissue, \
               "Cytoplasm diffusion should be >= tissue diffusion"
        
        # Test toxicity parameters
        assert params.ld50_concentration > params.noael_concentration, \
               "LD50 must be greater than NOAEL"
        assert params.noael_concentration > 0, "NOAEL must be positive"

    def test_biochemical_tracer_properties(self):
        """Test biochemical tracer property calculations."""
        # Test different molecular weights
        molecular_weights = [500, 1000, 2000]  # g/mol
        
        for mw in molecular_weights:
            tracer = BiochemicalTracer(
                name=f"Test MW {mw}",
                molecular_weight=mw,
                fluorescence_quantum_yield=0.7
            )
            
            # Verify stokes radius scales with molecular weight
            assert tracer.stokes_radius > 0, "Stokes radius must be positive"
            assert 1e-10 <= tracer.stokes_radius <= 1e-7, "Stokes radius outside reasonable range"
            
            # Verify diffusion coefficient is inversely related to radius
            assert tracer.diffusion_coefficient > 0, "Diffusion coefficient must be positive"
            assert 1e-13 <= tracer.diffusion_coefficient <= 1e-9, "Diffusion coefficient outside reasonable range"
            
            # Larger molecules should diffuse slower
            if mw > 500:
                smaller_tracer = BiochemicalTracer("Small", 500, 0.7)
                assert tracer.diffusion_coefficient < smaller_tracer.diffusion_coefficient, \
                       "Larger molecules should diffuse slower"
    
    def test_neural_tracer_experiment(self):
        """Test neural tracer experiment framework."""
        tissue_geometry = {
            'length': 200e-6,   # 200 μm
            'width': 200e-6,    # 200 μm
            'height': 100e-6    # 100 μm
        }
        
        # Create experiment
        experiment = NeuralTracerExperiment(tissue_geometry)
        
        # Verify experiment setup
        assert experiment.tracer is not None, "Experiment should have a tracer"
        assert experiment.neural_tracer is not None, "Experiment should have a neural tracer"
        assert experiment.dimensions == tissue_geometry
        
        # Verify tracer properties  
        assert experiment.tracer.name == "Calcium Green-1"  # Default tracer
        assert experiment.tracer.molecular_weight == 1000.0  # Expected MW
        
    def test_toxicity_calculation(self):
        """Test toxicity response calculations."""
        tracer = BiochemicalTracer("Test Tracer", 800.0)
        tissue_geometry = {'length': 100e-6, 'width': 100e-6, 'height': 100e-6}
        neural_tracer = BiocompatibleNeuralTracer(tracer, tissue_geometry)
        
        # Test concentration field
        concentration_field = np.array([[[1e-7, 5e-7], [1e-6, 2e-6]]])  # mol/L
        
        toxicity_metrics = neural_tracer.calculate_toxicity_response(concentration_field)
        
        # Verify toxicity metrics structure
        assert 'cytotoxicity_fraction' in toxicity_metrics
        assert 'inflammatory_response' in toxicity_metrics
        assert 'apoptosis_rate' in toxicity_metrics
        
        # Verify toxicity values are reasonable
        assert np.all(toxicity_metrics['cytotoxicity_fraction'] >= 0)
        assert np.all(toxicity_metrics['cytotoxicity_fraction'] <= 1)
        assert np.all(toxicity_metrics['inflammatory_response'] >= 0)
        
    def test_bbb_permeability_calculation(self):
        """Test blood-brain barrier permeability calculation."""
        tracer = BiochemicalTracer("Test Tracer", 800.0)
        tissue_geometry = {'length': 100e-6, 'width': 100e-6, 'height': 100e-6}
        neural_tracer = BiocompatibleNeuralTracer(tracer, tissue_geometry)
        
        # Test with tracer properties
        tracer_props = {'concentration': np.array([1e-6])}  # 1 μM
        
        bbb_permeability = neural_tracer.calculate_bbb_permeability(tracer_props)
        
        # Verify permeability is reasonable
        assert bbb_permeability > 0, "BBB permeability must be positive"
        assert 1e-12 <= bbb_permeability <= 1e-4, "BBB permeability outside reasonable range"
        
    def test_quantum_measurement_noise(self):
        """Test quantum measurement noise calculation."""
        tracer = BiochemicalTracer("Test Tracer", 800.0)
        tissue_geometry = {'length': 100e-6, 'width': 100e-6, 'height': 100e-6}
        neural_tracer = BiocompatibleNeuralTracer(tracer, tissue_geometry)
        
        voxel_volume = 1e-18  # m³ (1 μm³)
        dt = 1e-3  # 1 ms
        
        quantum_noise = neural_tracer.calculate_quantum_measurement_noise(voxel_volume, dt)
        
        # Verify quantum noise is reasonable
        assert quantum_noise >= 0, "Quantum noise must be non-negative"
        assert quantum_noise <= 1, "Quantum noise should not exceed 100%"
        
        # Smaller volumes should have higher relative noise
        smaller_volume = voxel_volume / 10
        smaller_noise = neural_tracer.calculate_quantum_measurement_noise(smaller_volume, dt)
        assert smaller_noise >= quantum_noise, "Smaller volumes should have higher relative noise"


class TestNeuralTracerExperiment:
    """Test neural tracer experiment functionality."""
    
    def test_experiment_construction(self):
        """Test experiment construction with default parameters.""" 
        tissue_dims = {'length': 500e-6, 'width': 500e-6, 'height': 200e-6}
        experiment = NeuralTracerExperiment(tissue_dims)
        
        # Verify components exist
        assert hasattr(experiment, 'tracer')
        assert hasattr(experiment, 'neural_tracer') 
        assert hasattr(experiment, 'dimensions')
        
        # Verify dimensions
        assert experiment.dimensions == tissue_dims
        
    def test_basic_experiment_functionality(self):
        """Test basic experiment functionality without complex report generation."""
        tissue_dims = {'length': 100e-6, 'width': 100e-6, 'height': 100e-6}
        experiment = NeuralTracerExperiment(tissue_dims)
        
        # Verify experiment has required methods
        assert hasattr(experiment, 'run_neural_tracer_test')
        assert hasattr(experiment, 'generate_biocompatibility_report')
        assert hasattr(experiment, 'create_test_scenario')
        
        # Verify tracer and neural tracer exist and are properly configured
        assert experiment.tracer.molecular_weight > 0
        assert experiment.neural_tracer.max_concentration > 0
        assert experiment.neural_tracer.params.atp_concentration > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])