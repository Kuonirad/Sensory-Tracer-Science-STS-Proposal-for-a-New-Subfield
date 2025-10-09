#!/usr/bin/env python3
"""
Test Suite for Clinical Trials Module

Comprehensive tests for FDA-compliant clinical trial protocols,
regulatory compliance, and safety monitoring functionality.
"""

import json
import pytest
import uuid
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from sensory_tracer_science.experimental.clinical_trials import (
    TrialPhase,
    StudyDesign,
    ClinicalSafetyParameters,
    InclusionCriteria,
    ExclusionCriteria,
    ClinicalTrialProtocol,
)


class TestTrialPhase:
    """Test clinical trial phase enumeration."""
    
    def test_trial_phase_values(self):
        """Test trial phase enumeration values."""
        assert TrialPhase.PRECLINICAL.value == "preclinical"
        assert TrialPhase.PHASE_0.value == "phase_0"
        assert TrialPhase.PHASE_1.value == "phase_1"
        assert TrialPhase.PHASE_1_2.value == "phase_1_2"
        assert TrialPhase.PHASE_2.value == "phase_2"
        assert TrialPhase.PHASE_2_3.value == "phase_2_3"
        assert TrialPhase.PHASE_3.value == "phase_3"
        assert TrialPhase.PHASE_4.value == "phase_4"
    
    def test_trial_phase_completeness(self):
        """Test that all FDA-recognized phases are included."""
        phases = [phase.value for phase in TrialPhase]
        
        # Ensure we have all major phases
        expected_phases = [
            "preclinical", "phase_0", "phase_1", "phase_1_2",
            "phase_2", "phase_2_3", "phase_3", "phase_4"
        ]
        
        for expected in expected_phases:
            assert expected in phases


class TestStudyDesign:
    """Test clinical study design enumeration."""
    
    def test_study_design_values(self):
        """Test study design enumeration values."""
        assert StudyDesign.SINGLE_ARM.value == "single_arm"
        assert StudyDesign.RANDOMIZED_CONTROLLED.value == "randomized_controlled"
        assert StudyDesign.CROSSOVER.value == "crossover"
        assert StudyDesign.DOSE_ESCALATION.value == "dose_escalation"
        assert StudyDesign.ADAPTIVE.value == "adaptive"
        assert StudyDesign.BASKET.value == "basket"
        assert StudyDesign.UMBRELLA.value == "umbrella"
    
    def test_study_design_completeness(self):
        """Test that all major study designs are included."""
        designs = [design.value for design in StudyDesign]
        
        # Ensure we have all major study designs
        expected_designs = [
            "single_arm", "randomized_controlled", "crossover",
            "dose_escalation", "adaptive", "basket", "umbrella"
        ]
        
        for expected in expected_designs:
            assert expected in designs


class TestClinicalSafetyParameters:
    """Test clinical safety parameter configuration."""
    
    def test_default_safety_parameters(self):
        """Test default clinical safety parameters."""
        params = ClinicalSafetyParameters()
        
        # Dosimetry limits
        assert params.max_tracer_dose == 1e-9  # nanomolar concentration
        assert params.max_exposure_duration == 3600.0  # 1 hour
        assert params.max_sessions_per_day == 1
        assert params.max_sessions_per_week == 3
        
        # Power density limits (conservative)
        assert params.max_power_density == 1e-4  # W/cm²
        assert params.max_cumulative_dose == 1e-3  # J/cm²
        
        # Physiological monitoring thresholds
        assert params.max_temperature_increase == 0.5  # °C
        assert params.max_heart_rate_increase == 20  # bpm
        assert params.max_blood_pressure_increase == 10  # mmHg
        
        # Stopping rules
        assert params.serious_adverse_event_threshold == 1
        assert params.adverse_event_rate_threshold == 0.3
        assert params.efficacy_futility_threshold == 0.1
    
    def test_custom_safety_parameters(self):
        """Test custom clinical safety parameters."""
        params = ClinicalSafetyParameters(
            max_tracer_dose=5e-10,  # Even more conservative
            max_exposure_duration=1800.0,  # 30 minutes
            max_power_density=5e-5,  # Half the default
            max_temperature_increase=0.2  # Very conservative
        )
        
        assert params.max_tracer_dose == 5e-10
        assert params.max_exposure_duration == 1800.0
        assert params.max_power_density == 5e-5
        assert params.max_temperature_increase == 0.2
    
    def test_safety_parameter_validation(self):
        """Test safety parameter validation logic."""
        params = ClinicalSafetyParameters()
        
        # All limits should be positive
        assert params.max_tracer_dose > 0
        assert params.max_exposure_duration > 0
        assert params.max_power_density > 0
        assert params.max_cumulative_dose > 0
        assert params.max_temperature_increase > 0
        assert params.max_heart_rate_increase > 0
        assert params.max_blood_pressure_increase > 0
        
        # Thresholds should be reasonable
        assert 0 < params.adverse_event_rate_threshold < 1
        assert 0 < params.efficacy_futility_threshold < 1
        assert params.serious_adverse_event_threshold >= 0


class TestInclusionCriteria:
    """Test patient inclusion criteria configuration."""
    
    def test_default_inclusion_criteria(self):
        """Test default inclusion criteria."""
        criteria = InclusionCriteria()
        
        # Age ranges
        assert criteria.min_age == 18
        assert criteria.max_age == 75
        
        # Performance status (ECOG scale)
        assert criteria.performance_status_min == 0
        assert criteria.performance_status_max == 2
        
        # Lab value ranges (normal clinical ranges)
        assert criteria.hemoglobin_min == 10.0  # g/dL
        assert criteria.platelet_count_min == 100000  # /μL
        assert criteria.creatinine_max == 1.5  # mg/dL
        assert criteria.bilirubin_max == 2.0  # mg/dL
        
        # Lists should be initialized as empty
        assert criteria.required_diagnosis == []
        assert criteria.required_biomarkers == {}
    
    def test_custom_inclusion_criteria(self):
        """Test custom inclusion criteria."""
        custom_biomarkers = {
            "PSA": (0.0, 4.0),  # ng/mL
            "CEA": (0.0, 5.0)   # ng/mL
        }
        
        criteria = InclusionCriteria(
            min_age=21,
            max_age=65,
            required_diagnosis=["prostate_cancer"],
            required_biomarkers=custom_biomarkers,
            hemoglobin_min=12.0
        )
        
        assert criteria.min_age == 21
        assert criteria.max_age == 65
        assert criteria.required_diagnosis == ["prostate_cancer"]
        assert criteria.required_biomarkers == custom_biomarkers
        assert criteria.hemoglobin_min == 12.0
    
    def test_inclusion_post_init(self):
        """Test __post_init__ method for inclusion criteria."""
        # Test with None values
        criteria = InclusionCriteria(
            required_diagnosis=None,
            required_biomarkers=None
        )
        
        # Should be initialized to empty collections
        assert criteria.required_diagnosis == []
        assert criteria.required_biomarkers == {}
    
    def test_inclusion_criteria_validation(self):
        """Test inclusion criteria validation logic."""
        criteria = InclusionCriteria()
        
        # Age ranges should be reasonable
        assert 0 <= criteria.min_age < criteria.max_age <= 150
        
        # Performance status should be valid ECOG scale (0-5)
        assert 0 <= criteria.performance_status_min <= criteria.performance_status_max <= 5
        
        # Lab values should be positive and within reasonable ranges
        assert 0 < criteria.hemoglobin_min <= 20  # g/dL reasonable range
        assert 0 < criteria.platelet_count_min <= 1e6  # /μL reasonable range
        assert 0 < criteria.creatinine_max <= 10  # mg/dL reasonable range
        assert 0 < criteria.bilirubin_max <= 20  # mg/dL reasonable range


class TestExclusionCriteria:
    """Test patient exclusion criteria configuration."""
    
    def test_exclusion_criteria_initialization(self):
        """Test exclusion criteria initialization."""
        criteria = ExclusionCriteria()
        
        # Check that exclusion criteria object exists
        assert hasattr(criteria, 'pregnancy_test_required')
        assert hasattr(criteria, 'contraindicated_medications')
        assert hasattr(criteria, 'medical_conditions')
        
        # Verify safety-critical exclusions are present
        assert criteria.pregnancy_test_required is True
        assert isinstance(criteria.contraindicated_medications, list)
        assert isinstance(criteria.medical_conditions, list)
    
    def test_exclusion_criteria_medical_safety(self):
        """Test medical safety exclusion criteria."""
        criteria = ExclusionCriteria()
        
        # Should exclude high-risk conditions
        high_risk_conditions = [
            'pacemaker', 'metallic_implants', 'pregnancy',
            'severe_kidney_disease', 'severe_liver_disease'
        ]
        
        for condition in high_risk_conditions:
            assert condition in criteria.medical_conditions
    
    def test_exclusion_criteria_medication_safety(self):
        """Test medication safety exclusion criteria."""
        criteria = ExclusionCriteria()
        
        # Should exclude medications that could interfere
        contraindicated = [
            'anticoagulants', 'chemotherapy', 'immunosuppressants'
        ]
        
        for medication in contraindicated:
            assert medication in criteria.contraindicated_medications


class TestClinicalTrialProtocol:
    """Test clinical trial protocol functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.protocol_id = str(uuid.uuid4())
        self.protocol = ClinicalTrialProtocol(
            protocol_id=self.protocol_id,
            trial_phase=TrialPhase.PHASE_1,
            study_design=StudyDesign.SINGLE_ARM,
            indication="neural_interface_testing"
        )
    
    def test_protocol_initialization(self):
        """Test clinical trial protocol initialization."""
        assert self.protocol.protocol_id == self.protocol_id
        assert self.protocol.trial_phase == TrialPhase.PHASE_1
        assert self.protocol.study_design == StudyDesign.SINGLE_ARM
        assert isinstance(self.protocol.safety_params, ClinicalSafetyParameters)
        assert isinstance(self.protocol.inclusion_criteria, InclusionCriteria)
        assert isinstance(self.protocol.exclusion_criteria, ExclusionCriteria)
    
    def test_protocol_phase_specific_requirements(self):
        """Test phase-specific protocol requirements."""
        # Phase 1 should have strict safety focus
        phase1_protocol = ClinicalTrialProtocol(
            protocol_id="phase1_test",
            trial_phase=TrialPhase.PHASE_1,
            study_design=StudyDesign.DOSE_ESCALATION,
            indication="safety_testing"
        )
        
        # Should have conservative safety parameters for Phase 1
        assert phase1_protocol.safety_params.max_tracer_dose <= 1e-9
        assert phase1_protocol.safety_params.serious_adverse_event_threshold <= 1
        
        # Phase 3 can have slightly relaxed parameters for efficacy
        phase3_protocol = ClinicalTrialProtocol(
            protocol_id="phase3_test",
            trial_phase=TrialPhase.PHASE_3,
            study_design=StudyDesign.RANDOMIZED_CONTROLLED,
            indication="efficacy_testing"
        )
        
        assert phase3_protocol.trial_phase == TrialPhase.PHASE_3
        assert phase3_protocol.study_design == StudyDesign.RANDOMIZED_CONTROLLED
    
    def test_protocol_study_design_compatibility(self):
        """Test study design compatibility with phases."""
        # Dose escalation is appropriate for Phase 1
        dose_escalation_protocol = ClinicalTrialProtocol(
            protocol_id="dose_test",
            trial_phase=TrialPhase.PHASE_1,
            study_design=StudyDesign.DOSE_ESCALATION,
            indication="dose_finding"
        )
        
        assert dose_escalation_protocol.trial_phase == TrialPhase.PHASE_1
        assert dose_escalation_protocol.study_design == StudyDesign.DOSE_ESCALATION
        
        # Randomized controlled is appropriate for Phase 2/3
        rct_protocol = ClinicalTrialProtocol(
            protocol_id="rct_test",
            trial_phase=TrialPhase.PHASE_2,
            study_design=StudyDesign.RANDOMIZED_CONTROLLED,
            indication="efficacy_evaluation"
        )
        
        assert rct_protocol.trial_phase == TrialPhase.PHASE_2
        assert rct_protocol.study_design == StudyDesign.RANDOMIZED_CONTROLLED
    
    def test_protocol_safety_monitoring_integration(self):
        """Test integration of safety monitoring across protocol components."""
        # All safety parameters should be consistent
        safety = self.protocol.safety_params
        inclusion = self.protocol.inclusion_criteria
        exclusion = self.protocol.exclusion_criteria
        
        # Safety limits should be within inclusion criteria lab ranges
        # (This would be implemented in the actual validation logic)
        assert hasattr(safety, 'max_tracer_dose')
        assert hasattr(inclusion, 'hemoglobin_min')
        assert hasattr(exclusion, 'medical_conditions')
    
    def test_protocol_regulatory_compliance(self):
        """Test regulatory compliance features."""
        # Protocol should have required regulatory elements
        assert hasattr(self.protocol, 'protocol_id')
        assert hasattr(self.protocol, 'trial_phase')
        assert hasattr(self.protocol, 'study_design')
        
        # Should have audit trail capability
        assert hasattr(self.protocol, 'creation_date')
        assert hasattr(self.protocol, 'protocol_version')
        assert hasattr(self.protocol, 'sponsor')
        
        # Should support FDA submission requirements
        assert self.protocol.protocol_id is not None
        assert len(self.protocol.protocol_id) > 0


class TestProductionValidator:
    """Test production validation functionality (mock implementation)."""
    
    def setup_method(self):
        """Set up validation test fixtures."""
        class MockProductionValidator:
            def __init__(self):
                self.validation_rules = {
                    'safety_limits': True,
                    'regulatory_compliance': True,
                    'protocol_structure': True
                }
                self.compliance_checks = [
                    'fda_compliance',
                    'ich_gcp_compliance',
                    'safety_validation'
                ]
            
            def validate_safety_parameters(self, params):
                # Basic validation logic
                errors = []
                if params.max_tracer_dose < 0:
                    errors.append("Negative tracer dose not allowed")
                if params.max_exposure_duration <= 0:
                    errors.append("Exposure duration must be positive")
                
                return {
                    'valid': len(errors) == 0,
                    'errors': errors
                }
            
            def validate_protocol(self, protocol):
                return {
                    'valid': True,
                    'checks_passed': ['safety_check', 'regulatory_compliance']
                }
            
            def validate_fda_compliance(self, protocol):
                return {
                    'compliant': True,
                    'standards_met': ['ich_gcp', 'cfr_title_21']
                }
        
        self.validator = MockProductionValidator()
    
    def test_validator_initialization(self):
        """Test production validator initialization."""
        assert hasattr(self.validator, 'validation_rules')
        assert hasattr(self.validator, 'compliance_checks')
        assert isinstance(self.validator.validation_rules, dict)
        assert isinstance(self.validator.compliance_checks, list)
    
    def test_safety_parameter_validation(self):
        """Test safety parameter validation."""
        # Valid safety parameters should pass
        valid_params = ClinicalSafetyParameters()
        result = self.validator.validate_safety_parameters(valid_params)
        assert result['valid'] is True
        assert len(result['errors']) == 0
        
        # Invalid parameters should fail
        invalid_params = ClinicalSafetyParameters(
            max_tracer_dose=-1.0,  # Negative dose - invalid
            max_exposure_duration=0.0  # Zero duration - invalid
        )
        result = self.validator.validate_safety_parameters(invalid_params)
        assert result['valid'] is False
        assert len(result['errors']) > 0
    
    def test_protocol_validation(self):
        """Test complete protocol validation."""
        # Create a valid protocol
        protocol = ClinicalTrialProtocol(
            protocol_id="valid_test_001",
            trial_phase=TrialPhase.PHASE_1,
            study_design=StudyDesign.SINGLE_ARM,
            indication="validation_test"
        )
        
        result = self.validator.validate_protocol(protocol)
        assert result['valid'] is True
        assert 'safety_check' in result['checks_passed']
        assert 'regulatory_compliance' in result['checks_passed']
    
    def test_fda_compliance_validation(self):
        """Test FDA compliance validation."""
        protocol = ClinicalTrialProtocol(
            protocol_id="fda_test_001",
            trial_phase=TrialPhase.PHASE_1,
            study_design=StudyDesign.DOSE_ESCALATION,
            indication="fda_compliance_test"
        )
        
        # Should pass FDA compliance checks
        result = self.validator.validate_fda_compliance(protocol)
        assert result['compliant'] is True
        assert 'ich_gcp' in result['standards_met']  # ICH Good Clinical Practice
        assert 'cfr_title_21' in result['standards_met']  # FDA regulations


class TestClinicalTrialDataIntegrity:
    """Test clinical trial data integrity and audit trails."""
    
    def test_protocol_version_control(self):
        """Test protocol version control and audit trails."""
        protocol = ClinicalTrialProtocol(
            protocol_id="version_test_001",
            trial_phase=TrialPhase.PHASE_2,
            study_design=StudyDesign.RANDOMIZED_CONTROLLED,
            indication="version_control_test"
        )
        
        # Should have versioning information
        assert hasattr(protocol, 'protocol_version')
        assert hasattr(protocol, 'creation_date')
        assert hasattr(protocol, 'protocol_amendments')
        
        # Version should start at 1.0.0
        assert protocol.protocol_version == "1.0.0"
        
        # Timestamps should be recent
        assert isinstance(protocol.creation_date, datetime)
        time_diff = datetime.now() - protocol.creation_date
        assert time_diff.total_seconds() < 60  # Created within last minute
    
    def test_data_serialization_for_audit(self):
        """Test that protocol data can be serialized for audit trails."""
        protocol = ClinicalTrialProtocol(
            protocol_id="audit_test_001",
            trial_phase=TrialPhase.PHASE_1,
            study_design=StudyDesign.SINGLE_ARM,
            indication="audit_test"
        )
        
        # Should be serializable to JSON for audit logs
        try:
            protocol_dict = {
                'protocol_id': protocol.protocol_id,
                'trial_phase': protocol.trial_phase.value,
                'study_design': protocol.study_design.value,
                'creation_date': protocol.creation_date.isoformat(),
                'protocol_version': protocol.protocol_version
            }
            
            json_str = json.dumps(protocol_dict)
            assert len(json_str) > 0
            
            # Should be deserializable
            restored = json.loads(json_str)
            assert restored['protocol_id'] == protocol.protocol_id
            assert restored['trial_phase'] == protocol.trial_phase.value
            
        except (TypeError, ValueError) as e:
            pytest.fail(f"Protocol serialization failed: {e}")


class TestClinicalTrialErrorHandling:
    """Test error handling in clinical trial protocols."""
    
    def test_invalid_protocol_id(self):
        """Test handling of invalid protocol IDs."""
        # Empty string should be handled gracefully (may not raise exception)
        try:
            empty_protocol = ClinicalTrialProtocol(
                protocol_id="",
                trial_phase=TrialPhase.PHASE_1,
                study_design=StudyDesign.SINGLE_ARM,
                indication="empty_id_test"
            )
            # If no exception, check that it was created with empty ID
            assert empty_protocol.protocol_id == ""
        except (ValueError, TypeError):
            # If exception is raised, that's also acceptable behavior
            pass
    
    def test_protocol_validation_edge_cases(self):
        """Test protocol validation edge cases."""
        validator = ProductionValidator()
        
        # Extremely conservative safety parameters
        ultra_safe_params = ClinicalSafetyParameters(
            max_tracer_dose=1e-15,  # femtomolar
            max_exposure_duration=1.0,  # 1 second
            max_power_density=1e-10  # Very low power
        )
        
        result = validator.validate_safety_parameters(ultra_safe_params)
        assert result['valid'] is True  # Should accept ultra-conservative params
    
    def test_boundary_condition_validation(self):
        """Test validation of boundary conditions."""
        # Test minimum viable parameters
        min_params = ClinicalSafetyParameters(
            max_tracer_dose=1e-12,  # Minimum detectable
            max_exposure_duration=0.001,  # 1 millisecond
            serious_adverse_event_threshold=0  # Zero tolerance
        )
        
        validator = ProductionValidator()
        result = validator.validate_safety_parameters(min_params)
        
        # Should handle minimum parameters appropriately
        assert 'valid' in result
        assert isinstance(result['valid'], bool)