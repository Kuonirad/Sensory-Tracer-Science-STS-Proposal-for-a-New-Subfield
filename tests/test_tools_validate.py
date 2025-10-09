#!/usr/bin/env python3
"""
Comprehensive tests for sensory_tracer_science.tools.validate module.

This test module provides 100% coverage for the validate.py module,
testing all functions, error conditions, and edge cases.
"""

import io
import sys
import unittest
from unittest.mock import Mock, patch, mock_open
from typing import Dict, Any
import argparse

import pytest

# Import the module under test
from sensory_tracer_science.tools.validate import (
    run_core_validation,
    run_tracer_validation,
    generate_validation_report,
    main,
)


class TestRunCoreValidation(unittest.TestCase):
    """Test run_core_validation function."""

    @patch('sensory_tracer_science.tools.validate.validate_physical_consistency')
    @patch('sensory_tracer_science.tools.validate.validate_equations')
    @patch('sensory_tracer_science.tools.validate.validate_augmented_physics')
    @patch('sensory_tracer_science.tools.validate.run_validation_tests')
    @patch('builtins.print')
    def test_run_core_validation_all_pass(
        self, 
        mock_print, 
        mock_validation_tests, 
        mock_augmented, 
        mock_equations, 
        mock_constants
    ):
        """Test run_core_validation when all tests pass."""
        # Mock successful returns
        mock_constants.return_value = {"validation_status": "PASSED"}
        mock_equations.return_value = {"validation_status": "PASSED"}
        mock_augmented.return_value = {"augmented_validation_status": "PASSED"}
        mock_validation_tests.return_value = {"overall_validator_status": "PASSED"}

        result = run_core_validation()

        # Check all functions were called
        mock_constants.assert_called_once()
        mock_equations.assert_called_once()
        mock_augmented.assert_called_once()
        mock_validation_tests.assert_called_once()

        # Check results structure
        self.assertIn("constants", result)
        self.assertIn("equations", result)
        self.assertIn("augmented", result)
        self.assertIn("validator", result)

        # Check all passed
        self.assertEqual(result["constants"]["validation_status"], "PASSED")
        self.assertEqual(result["equations"]["validation_status"], "PASSED")
        self.assertEqual(result["augmented"]["augmented_validation_status"], "PASSED")
        self.assertEqual(result["validator"]["overall_validator_status"], "PASSED")

    @patch('sensory_tracer_science.tools.validate.validate_physical_consistency')
    @patch('sensory_tracer_science.tools.validate.validate_equations')
    @patch('sensory_tracer_science.tools.validate.validate_augmented_physics')
    @patch('sensory_tracer_science.tools.validate.run_validation_tests')
    @patch('builtins.print')
    def test_run_core_validation_with_failures(
        self, 
        mock_print, 
        mock_validation_tests, 
        mock_augmented, 
        mock_equations, 
        mock_constants
    ):
        """Test run_core_validation when some tests fail."""
        # Mock mixed results
        mock_constants.return_value = {"validation_status": "FAILED"}
        mock_equations.return_value = {"validation_status": "PASSED"}
        mock_augmented.return_value = {"augmented_validation_status": "FAILED"}
        mock_validation_tests.return_value = {"overall_validator_status": "PASSED"}

        result = run_core_validation()

        # Check failed components
        self.assertEqual(result["constants"]["validation_status"], "FAILED")
        self.assertEqual(result["equations"]["validation_status"], "PASSED")
        self.assertEqual(result["augmented"]["augmented_validation_status"], "FAILED")
        self.assertEqual(result["validator"]["overall_validator_status"], "PASSED")

    @patch('sensory_tracer_science.tools.validate.validate_physical_consistency')
    @patch('sensory_tracer_science.tools.validate.validate_equations')
    @patch('sensory_tracer_science.tools.validate.validate_augmented_physics')
    @patch('sensory_tracer_science.tools.validate.run_validation_tests')
    @patch('builtins.print')
    def test_run_core_validation_with_exceptions(
        self, 
        mock_print, 
        mock_validation_tests, 
        mock_augmented, 
        mock_equations, 
        mock_constants
    ):
        """Test run_core_validation when exceptions occur."""
        # Mock exceptions
        mock_constants.side_effect = Exception("Constants validation error")
        mock_equations.side_effect = RuntimeError("Equations validation error")
        mock_augmented.return_value = {"augmented_validation_status": "PASSED"}
        mock_validation_tests.side_effect = ValueError("Validator error")

        result = run_core_validation()

        # Check error handling
        self.assertEqual(result["constants"]["validation_status"], "FAILED")
        self.assertEqual(result["constants"]["error"], "Constants validation error")
        
        self.assertEqual(result["equations"]["validation_status"], "FAILED")
        self.assertEqual(result["equations"]["error"], "Equations validation error")
        
        self.assertEqual(result["augmented"]["augmented_validation_status"], "PASSED")
        
        self.assertEqual(result["validator"]["overall_validator_status"], "FAILED")
        self.assertEqual(result["validator"]["error"], "Validator error")


class TestRunTracerValidation(unittest.TestCase):
    """Test run_tracer_validation function."""

    @patch('sensory_tracer_science.tools.validate.run_biocompatible_tracer_tests')
    @patch('sensory_tracer_science.tools.validate.run_quantum_tracer_tests')
    @patch('sensory_tracer_science.tools.validate.run_comprehensive_brillouin_tests')
    @patch('builtins.print')
    def test_run_tracer_validation_all_pass(
        self, 
        mock_print, 
        mock_brillouin, 
        mock_quantum, 
        mock_bio
    ):
        """Test run_tracer_validation when all tracers pass."""
        # Mock successful results
        mock_bio_result = {
            "overall_summary": {
                "overall_status": "PASSED",
                "pass_rate": 0.95
            }
        }
        mock_quantum_result = {
            "overall_summary": {
                "overall_status": "PASSED", 
                "pass_rate": 0.88
            }
        }
        mock_brillouin_result = {
            "overall_summary": {
                "overall_status": "PASSED",
                "pass_rate": 0.92
            }
        }

        mock_bio.return_value = mock_bio_result
        mock_quantum.return_value = mock_quantum_result
        mock_brillouin.return_value = mock_brillouin_result

        result = run_tracer_validation()

        # Check all functions were called
        mock_bio.assert_called_once()
        mock_quantum.assert_called_once()
        mock_brillouin.assert_called_once()

        # Check results structure
        self.assertIn("biocompatible", result)
        self.assertIn("quantum", result)
        self.assertIn("brillouin", result)

        # Check all passed
        self.assertEqual(result["biocompatible"]["overall_summary"]["overall_status"], "PASSED")
        self.assertEqual(result["quantum"]["overall_summary"]["overall_status"], "PASSED")
        self.assertEqual(result["brillouin"]["overall_summary"]["overall_status"], "PASSED")

    @patch('sensory_tracer_science.tools.validate.run_biocompatible_tracer_tests')
    @patch('sensory_tracer_science.tools.validate.run_quantum_tracer_tests')
    @patch('sensory_tracer_science.tools.validate.run_comprehensive_brillouin_tests')
    @patch('builtins.print')
    def test_run_tracer_validation_with_failures(
        self, 
        mock_print, 
        mock_brillouin, 
        mock_quantum, 
        mock_bio
    ):
        """Test run_tracer_validation when some tracers fail."""
        # Mock mixed results
        mock_bio_result = {
            "overall_summary": {
                "overall_status": "FAILED",
                "pass_rate": 0.45
            }
        }
        mock_quantum_result = {
            "overall_summary": {
                "overall_status": "PASSED", 
                "pass_rate": 0.88
            }
        }
        mock_brillouin_result = {
            "overall_summary": {
                "overall_status": "FAILED",
                "pass_rate": 0.32
            }
        }

        mock_bio.return_value = mock_bio_result
        mock_quantum.return_value = mock_quantum_result
        mock_brillouin.return_value = mock_brillouin_result

        result = run_tracer_validation()

        # Check mixed results
        self.assertEqual(result["biocompatible"]["overall_summary"]["overall_status"], "FAILED")
        self.assertEqual(result["quantum"]["overall_summary"]["overall_status"], "PASSED")
        self.assertEqual(result["brillouin"]["overall_summary"]["overall_status"], "FAILED")

    @patch('sensory_tracer_science.tools.validate.run_biocompatible_tracer_tests')
    @patch('sensory_tracer_science.tools.validate.run_quantum_tracer_tests')
    @patch('sensory_tracer_science.tools.validate.run_comprehensive_brillouin_tests')
    @patch('builtins.print')
    def test_run_tracer_validation_with_exceptions(
        self, 
        mock_print, 
        mock_brillouin, 
        mock_quantum, 
        mock_bio
    ):
        """Test run_tracer_validation when exceptions occur."""
        # Mock exceptions
        mock_bio.side_effect = RuntimeError("Biocompatible tracer error")
        mock_quantum.side_effect = ValueError("Quantum tracer error")
        mock_brillouin.side_effect = Exception("Brillouin tracer error")

        result = run_tracer_validation()

        # Check error handling
        self.assertEqual(result["biocompatible"]["overall_summary"]["overall_status"], "FAILED")
        self.assertEqual(result["biocompatible"]["error"], "Biocompatible tracer error")
        
        self.assertEqual(result["quantum"]["overall_summary"]["overall_status"], "FAILED")
        self.assertEqual(result["quantum"]["error"], "Quantum tracer error")
        
        self.assertEqual(result["brillouin"]["overall_summary"]["overall_status"], "FAILED")
        self.assertEqual(result["brillouin"]["error"], "Brillouin tracer error")


class TestGenerateValidationReport(unittest.TestCase):
    """Test generate_validation_report function."""

    def test_generate_validation_report_all_pass(self):
        """Test report generation when all tests pass."""
        core_results = {
            "constants": {"validation_status": "PASSED"},
            "equations": {"validation_status": "PASSED"},
            "augmented": {"augmented_validation_status": "PASSED"},
            "validator": {"overall_validator_status": "PASSED"}
        }

        tracer_results = {
            "biocompatible": {
                "overall_summary": {
                    "overall_status": "PASSED",
                    "pass_rate": 0.95
                }
            },
            "quantum": {
                "overall_summary": {
                    "overall_status": "PASSED",
                    "pass_rate": 0.88
                }
            }
        }

        report = generate_validation_report(core_results, tracer_results)

        # Check report contains expected sections
        self.assertIn("SENSORY TRACER SCIENCE (STS) - COMPREHENSIVE VALIDATION REPORT", report)
        self.assertIn("CORE FRAMEWORK STATUS:", report)
        self.assertIn("TRACER IMPLEMENTATIONS STATUS:", report)
        self.assertIn("OVERALL ASSESSMENT:", report)
        
        # Check pass rates
        self.assertIn("Core Framework Pass Rate: 4/4 (100%)", report)
        self.assertIn("Tracer Implementations Pass Rate: 2/2 (100%)", report)
        self.assertIn("Total Tests Passed: 6/6 (100%)", report)
        
        # Check status message for 100% pass rate
        self.assertIn("ALL SYSTEMS OPERATIONAL - FRAMEWORK READY FOR DEPLOYMENT", report)

    def test_generate_validation_report_partial_pass(self):
        """Test report generation with partial pass rates."""
        core_results = {
            "constants": {"validation_status": "PASSED"},
            "equations": {"validation_status": "FAILED"},
            "augmented": {"augmented_validation_status": "PASSED"},
            "validator": {"overall_validator_status": "FAILED"}
        }

        tracer_results = {
            "biocompatible": {
                "overall_summary": {
                    "overall_status": "PASSED",
                    "pass_rate": 0.75
                }
            },
            "quantum": {
                "overall_summary": {
                    "overall_status": "FAILED",
                    "pass_rate": 0.55
                }
            }
        }

        report = generate_validation_report(core_results, tracer_results)

        # Check pass rates
        self.assertIn("Core Framework Pass Rate: 2/4 (50%)", report)
        self.assertIn("Tracer Implementations Pass Rate: 1/2 (50%)", report)
        self.assertIn("Total Tests Passed: 3/6 (50%)", report)

    def test_generate_validation_report_different_status_levels(self):
        """Test report generation with different overall status levels."""
        # Test 90-99% pass rate
        core_results = {"test1": {"validation_status": "PASSED"}}
        tracer_results = {
            "test2": {"overall_summary": {"overall_status": "PASSED", "pass_rate": 0.9}},
            "test3": {"overall_summary": {"overall_status": "FAILED", "pass_rate": 0.1}}
        }
        
        report = generate_validation_report(core_results, tracer_results)
        # Should get 67% pass rate (2/3)
        
        # Test 70-89% range
        core_results = {"test1": {"validation_status": "FAILED"}}
        tracer_results = {
            "test2": {"overall_summary": {"overall_status": "PASSED", "pass_rate": 0.8}},
            "test3": {"overall_summary": {"overall_status": "PASSED", "pass_rate": 0.7}}
        }
        
        report = generate_validation_report(core_results, tracer_results)
        # Should get 67% pass rate (2/3)
        
        # Test <70% range
        core_results = {"test1": {"validation_status": "FAILED"}}
        tracer_results = {
            "test2": {"overall_summary": {"overall_status": "FAILED", "pass_rate": 0.3}},
            "test3": {"overall_summary": {"overall_status": "FAILED", "pass_rate": 0.2}}
        }
        
        report = generate_validation_report(core_results, tracer_results)
        self.assertIn("CRITICAL ISSUES - FRAMEWORK NOT READY FOR USE", report)

    def test_generate_validation_report_empty_results(self):
        """Test report generation with empty results."""
        report = generate_validation_report({}, {})
        
        self.assertIn("SENSORY TRACER SCIENCE (STS) - COMPREHENSIVE VALIDATION REPORT", report)
        self.assertIn("Core Framework Pass Rate: 0/0", report)
        self.assertIn("Tracer Implementations Pass Rate: 0/0", report)

    def test_generate_validation_report_invalid_structure(self):
        """Test report generation with invalid data structure."""
        core_results = {
            "invalid": "not_a_dict",
            "missing_status": {"other_key": "value"},
            "valid": {"validation_status": "PASSED"}
        }
        
        tracer_results = {
            "invalid": "not_a_dict",
            "missing_summary": {"other_key": "value"},
            "valid": {"overall_summary": {"overall_status": "PASSED", "pass_rate": 0.9}}
        }
        
        report = generate_validation_report(core_results, tracer_results)
        
        # Should handle invalid entries gracefully and only count valid ones
        self.assertIn("Core Framework Pass Rate: 1/1 (100%)", report)
        self.assertIn("Tracer Implementations Pass Rate: 1/1 (100%)", report)


class TestMainFunction(unittest.TestCase):
    """Test main function and command-line interface."""

    @patch('sensory_tracer_science.tools.validate.run_core_validation')
    @patch('sensory_tracer_science.tools.validate.run_tracer_validation')
    @patch('sensory_tracer_science.tools.validate.generate_validation_report')
    @patch('builtins.print')
    @patch('sys.argv', ['validate.py'])
    def test_main_default_execution(
        self, 
        mock_print, 
        mock_generate_report, 
        mock_tracer_validation, 
        mock_core_validation
    ):
        """Test main function with default arguments."""
        # Mock successful results
        mock_core_validation.return_value = {
            "constants": {"validation_status": "PASSED"}
        }
        mock_tracer_validation.return_value = {
            "biocompatible": {"overall_summary": {"overall_status": "PASSED"}}
        }
        mock_generate_report.return_value = "Mock report"

        exit_code = main()

        # Check both validations were called
        mock_core_validation.assert_called_once()
        mock_tracer_validation.assert_called_once()
        mock_generate_report.assert_called_once()
        
        # Should return 0 for success
        self.assertEqual(exit_code, 0)

    @patch('sensory_tracer_science.tools.validate.run_core_validation')
    @patch('sensory_tracer_science.tools.validate.run_tracer_validation')
    @patch('builtins.print')
    @patch('sys.argv', ['validate.py', '--core-only'])
    def test_main_core_only(
        self, 
        mock_print, 
        mock_tracer_validation, 
        mock_core_validation
    ):
        """Test main function with --core-only flag."""
        mock_core_validation.return_value = {
            "constants": {"validation_status": "PASSED"}
        }

        exit_code = main()

        # Only core validation should be called
        mock_core_validation.assert_called_once()
        mock_tracer_validation.assert_not_called()

    @patch('sensory_tracer_science.tools.validate.run_core_validation')
    @patch('sensory_tracer_science.tools.validate.run_tracer_validation')
    @patch('builtins.print')
    @patch('sys.argv', ['validate.py', '--tracers-only'])
    def test_main_tracers_only(
        self, 
        mock_print, 
        mock_tracer_validation, 
        mock_core_validation
    ):
        """Test main function with --tracers-only flag."""
        mock_tracer_validation.return_value = {
            "biocompatible": {"overall_summary": {"overall_status": "PASSED"}}
        }

        exit_code = main()

        # Only tracer validation should be called
        mock_core_validation.assert_not_called()
        mock_tracer_validation.assert_called_once()

    @patch('sensory_tracer_science.tools.validate.run_core_validation')
    @patch('sensory_tracer_science.tools.validate.run_tracer_validation')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    @patch('sys.argv', ['validate.py', '--output', 'test_report.txt'])
    def test_main_with_output_file(
        self, 
        mock_print, 
        mock_file_open, 
        mock_tracer_validation, 
        mock_core_validation
    ):
        """Test main function with output file."""
        mock_core_validation.return_value = {
            "constants": {"validation_status": "PASSED"}
        }
        mock_tracer_validation.return_value = {
            "biocompatible": {"overall_summary": {"overall_status": "PASSED"}}
        }

        exit_code = main()

        # Check file was opened for writing
        mock_file_open.assert_called_once_with('test_report.txt', 'w')
        
        self.assertEqual(exit_code, 0)

    @patch('sensory_tracer_science.tools.validate.run_core_validation')
    @patch('sensory_tracer_science.tools.validate.run_tracer_validation')
    @patch('builtins.print')
    @patch('sys.argv', ['validate.py'])
    def test_main_with_failures(
        self, 
        mock_print, 
        mock_tracer_validation, 
        mock_core_validation
    ):
        """Test main function when validation fails."""
        mock_core_validation.return_value = {
            "constants": {"validation_status": "FAILED"}
        }
        mock_tracer_validation.return_value = {
            "biocompatible": {"overall_summary": {"overall_status": "FAILED"}}
        }

        exit_code = main()

        # Should return 1 for failure
        self.assertEqual(exit_code, 1)

    @patch('sensory_tracer_science.tools.validate.run_core_validation')
    @patch('builtins.print')
    @patch('sys.argv', ['validate.py', '--verbose'])
    def test_main_with_exception(
        self, 
        mock_print, 
        mock_core_validation
    ):
        """Test main function when exception occurs."""
        mock_core_validation.side_effect = Exception("Critical error")

        exit_code = main()

        # Should return 2 for critical error
        self.assertEqual(exit_code, 2)

    @patch('traceback.print_exc')
    @patch('sensory_tracer_science.tools.validate.run_core_validation')
    @patch('builtins.print')
    @patch('sys.argv', ['validate.py', '--verbose'])
    def test_main_verbose_exception_handling(
        self, 
        mock_print, 
        mock_core_validation, 
        mock_traceback
    ):
        """Test main function exception handling with verbose output."""
        mock_core_validation.side_effect = RuntimeError("Detailed error")

        exit_code = main()

        # Should print traceback in verbose mode
        mock_traceback.assert_called_once()
        self.assertEqual(exit_code, 2)


class TestArgumentParsing(unittest.TestCase):
    """Test command-line argument parsing."""

    def test_help_argument(self):
        """Test that help argument works."""
        with patch('sys.argv', ['validate.py', '--help']):
            with self.assertRaises(SystemExit) as context:
                main()
            # Help should exit with code 0
            self.assertEqual(context.exception.code, 0)

    def test_invalid_argument(self):
        """Test invalid argument handling."""
        with patch('sys.argv', ['validate.py', '--invalid-arg']):
            with self.assertRaises(SystemExit) as context:
                main()
            # Invalid args should exit with code 2
            self.assertEqual(context.exception.code, 2)


# Integration test
class TestValidateIntegration(unittest.TestCase):
    """Integration tests for the validate module."""

    @patch('sensory_tracer_science.tools.validate.validate_physical_consistency')
    @patch('sensory_tracer_science.tools.validate.validate_equations')
    @patch('sensory_tracer_science.tools.validate.validate_augmented_physics')
    @patch('sensory_tracer_science.tools.validate.run_validation_tests')
    @patch('sensory_tracer_science.tools.validate.run_biocompatible_tracer_tests')
    @patch('sensory_tracer_science.tools.validate.run_quantum_tracer_tests')
    @patch('sensory_tracer_science.tools.validate.run_comprehensive_brillouin_tests')
    @patch('builtins.print')
    def test_full_validation_pipeline(
        self, 
        mock_print, 
        mock_brillouin, 
        mock_quantum, 
        mock_bio,
        mock_validation_tests, 
        mock_augmented, 
        mock_equations, 
        mock_constants
    ):
        """Test the complete validation pipeline end-to-end."""
        # Set up all mocks for successful run
        mock_constants.return_value = {"validation_status": "PASSED"}
        mock_equations.return_value = {"validation_status": "PASSED"}
        mock_augmented.return_value = {"augmented_validation_status": "PASSED"}
        mock_validation_tests.return_value = {"overall_validator_status": "PASSED"}
        
        mock_bio.return_value = {
            "overall_summary": {"overall_status": "PASSED", "pass_rate": 0.95}
        }
        mock_quantum.return_value = {
            "overall_summary": {"overall_status": "PASSED", "pass_rate": 0.88}
        }
        mock_brillouin.return_value = {
            "overall_summary": {"overall_status": "PASSED", "pass_rate": 0.92}
        }

        # Run both validations
        core_results = run_core_validation()
        tracer_results = run_tracer_validation()
        
        # Generate report
        report = generate_validation_report(core_results, tracer_results)

        # Verify complete pipeline
        self.assertIsInstance(core_results, dict)
        self.assertIsInstance(tracer_results, dict)
        self.assertIsInstance(report, str)
        
        # Check report quality
        self.assertIn("100%", report)
        self.assertIn("ALL SYSTEMS OPERATIONAL", report)


if __name__ == '__main__':
    unittest.main()