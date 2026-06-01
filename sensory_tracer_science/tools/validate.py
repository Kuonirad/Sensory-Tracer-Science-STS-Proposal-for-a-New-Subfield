#!/usr/bin/env python3
"""
Sensory Tracer Science (STS) - Validation Tool

Command-line interface for running comprehensive STS validation tests.
"""

import argparse
import sys
import traceback
from typing import Any, Dict

# Import STS framework components
from ..core.sts_constants import (
    validate_augmented_physics,
    validate_physical_consistency,
)
from ..core.sts_equations import validate_equations
from ..tracers.biocompatible_neural import run_biocompatible_tracer_tests
from ..tracers.fiber_optic_brillouin import run_comprehensive_brillouin_tests
from ..tracers.quantum_enhanced import run_quantum_tracer_tests
from ..validation.sts_validator import run_validation_tests


def run_core_validation() -> Dict[str, Any]:
    """Run core STS framework validation."""
    print("🔬 Running Core STS Framework Validation...")

    results = {}

    # Validate physical constants
    print("  • Validating physical constants...")
    try:
        constants_result = validate_physical_consistency()
        results["constants"] = constants_result
        status = (
            "✅ PASSED"
            if constants_result["validation_status"] == "PASSED"
            else "❌ FAILED"
        )
        print(f"    {status}: Physical constants validation")
    except Exception as e:
        results["constants"] = {"validation_status": "FAILED", "error": str(e)}
        print(f"    ❌ FAILED: Physical constants validation - {e}")

    # Validate equations
    print("  • Validating governing equations...")
    try:
        equations_result = validate_equations()
        results["equations"] = equations_result
        status = (
            "✅ PASSED"
            if equations_result["validation_status"] == "PASSED"
            else "❌ FAILED"
        )
        print(f"    {status}: Governing equations validation")
    except Exception as e:
        results["equations"] = {"validation_status": "FAILED", "error": str(e)}
        print(f"    ❌ FAILED: Governing equations validation - {e}")

    # Validate augmented physics
    print("  • Validating augmented physics...")
    try:
        augmented_result = validate_augmented_physics()
        results["augmented"] = augmented_result
        status = (
            "✅ PASSED"
            if augmented_result["augmented_validation_status"] == "PASSED"
            else "❌ FAILED"
        )
        print(f"    {status}: Augmented physics validation")
    except Exception as e:
        results["augmented"] = {
            "augmented_validation_status": "FAILED",
            "error": str(e),
        }
        print(f"    ❌ FAILED: Augmented physics validation - {e}")

    # Run validation tests
    print("  • Running validation framework tests...")
    try:
        validator_result = run_validation_tests()
        results["validator"] = validator_result
        status = (
            "✅ PASSED"
            if validator_result["overall_validator_status"] == "PASSED"
            else "❌ FAILED"
        )
        print(f"    {status}: Validation framework tests")
    except Exception as e:
        results["validator"] = {"overall_validator_status": "FAILED", "error": str(e)}
        print(f"    ❌ FAILED: Validation framework tests - {e}")

    return results


def run_tracer_validation() -> Dict[str, Any]:
    """Run tracer implementation validation."""
    print("\n🧬 Running Tracer Implementation Validation...")

    results = {}

    # Biocompatible neural tracer
    print("  • Testing biocompatible neural tracer...")
    try:
        bio_result = run_biocompatible_tracer_tests()
        results["biocompatible"] = bio_result
        overall_status = bio_result["overall_summary"]["overall_status"]
        status = "✅ PASSED" if overall_status == "PASSED" else "❌ FAILED"
        print(
            f"    {status}: Biocompatible neural tracer ({bio_result['overall_summary']['pass_rate']*100:.0f}% pass rate)"
        )
    except Exception as e:
        results["biocompatible"] = {
            "overall_summary": {"overall_status": "FAILED"},
            "error": str(e),
        }
        print(f"    ❌ FAILED: Biocompatible neural tracer - {e}")

    # Quantum enhanced tracer
    print("  • Testing quantum enhanced tracer...")
    try:
        quantum_result = run_quantum_tracer_tests()
        results["quantum"] = quantum_result
        overall_status = quantum_result["overall_summary"]["overall_status"]
        status = "✅ PASSED" if overall_status == "PASSED" else "❌ FAILED"
        print(
            f"    {status}: Quantum enhanced tracer ({quantum_result['overall_summary']['pass_rate']*100:.0f}% pass rate)"
        )
    except Exception as e:
        results["quantum"] = {
            "overall_summary": {"overall_status": "FAILED"},
            "error": str(e),
        }
        print(f"    ❌ FAILED: Quantum enhanced tracer - {e}")

    # Fiber optic Brillouin tracer
    print("  • Testing fiber optic Brillouin tracer...")
    try:
        brillouin_result = run_comprehensive_brillouin_tests()
        results["brillouin"] = brillouin_result
        overall_status = brillouin_result["overall_summary"]["overall_status"]
        status = "✅ PASSED" if overall_status == "PASSED" else "❌ FAILED"
        print(
            f"    {status}: Fiber optic Brillouin tracer ({brillouin_result['overall_summary']['pass_rate']*100:.0f}% pass rate)"
        )
    except Exception as e:
        results["brillouin"] = {
            "overall_summary": {"overall_status": "FAILED"},
            "error": str(e),
        }
        print(f"    ❌ FAILED: Fiber optic Brillouin tracer - {e}")

    return results


def generate_validation_report(
    core_results: Dict[str, Any], tracer_results: Dict[str, Any]
) -> str:
    """Generate comprehensive validation report."""

    report = "=" * 80 + "\n"
    report += "SENSORY TRACER SCIENCE (STS) - COMPREHENSIVE VALIDATION REPORT\n"
    report += "=" * 80 + "\n\n"

    # Core framework status
    report += "CORE FRAMEWORK STATUS:\n"
    core_passed = 0
    core_total = 0

    for component, result in core_results.items():
        if isinstance(result, dict):
            status_key = next((k for k in result.keys() if "status" in k.lower()), None)
            if status_key:
                status = result[status_key]
                passed = status == "PASSED"
                core_passed += int(passed)
                core_total += 1
                icon = "✅" if passed else "❌"
                report += f"  {icon} {component.title()}: {status}\n"

    core_pass_rate = (core_passed / core_total * 100) if core_total > 0 else 0
    report += f"\nCore Framework Pass Rate: {core_passed}/{core_total} ({core_pass_rate:.0f}%)\n\n"

    # Tracer implementations status
    report += "TRACER IMPLEMENTATIONS STATUS:\n"
    tracer_passed = 0
    tracer_total = 0

    for tracer_name, result in tracer_results.items():
        if isinstance(result, dict) and "overall_summary" in result:
            summary = result["overall_summary"]
            status = summary["overall_status"]
            passed = status == "PASSED"
            tracer_passed += int(passed)
            tracer_total += 1
            icon = "✅" if passed else "❌"
            pass_rate = summary.get("pass_rate", 0) * 100
            report += f"  {icon} {tracer_name.title()}: {status} ({pass_rate:.0f}% pass rate)\n"

    tracer_pass_rate = (tracer_passed / tracer_total * 100) if tracer_total > 0 else 0
    report += f"\nTracer Implementations Pass Rate: {tracer_passed}/{tracer_total} ({tracer_pass_rate:.0f}%)\n\n"

    # Overall assessment
    overall_passed = core_passed + tracer_passed
    overall_total = core_total + tracer_total
    overall_pass_rate = (
        (overall_passed / overall_total * 100) if overall_total > 0 else 0
    )

    report += "OVERALL ASSESSMENT:\n"
    report += f"Total Tests Passed: {overall_passed}/{overall_total} ({overall_pass_rate:.0f}%)\n"

    if overall_pass_rate >= 100:
        report += (
            "🎉 STATUS: ALL SYSTEMS OPERATIONAL - FRAMEWORK READY FOR DEPLOYMENT\n"
        )
    elif overall_pass_rate >= 90:
        report += "⚠️  STATUS: MOSTLY OPERATIONAL - MINOR ISSUES NEED ATTENTION\n"
    elif overall_pass_rate >= 70:
        report += (
            "🔧 STATUS: PARTIALLY OPERATIONAL - SIGNIFICANT ISSUES REQUIRE FIXES\n"
        )
    else:
        report += "❌ STATUS: CRITICAL ISSUES - FRAMEWORK NOT READY FOR USE\n"

    report += "\n" + "=" * 80

    return report


def main() -> int:
    """Main entry point for STS validation tool."""
    parser = argparse.ArgumentParser(
        description="Sensory Tracer Science (STS) Validation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--core-only",
        action="store_true",
        help="Run only core framework validation (skip tracer tests)",
    )

    parser.add_argument(
        "--tracers-only",
        action="store_true",
        help="Run only tracer implementation tests (skip core validation)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument("--output", "-o", help="Output report to file")

    args = parser.parse_args()

    print("🧪 STS Validation Tool Starting...")
    print("=" * 60)

    core_results = {}
    tracer_results = {}

    try:
        # Run core validation unless tracers-only
        if not args.tracers_only:
            core_results = run_core_validation()

        # Run tracer validation unless core-only
        if not args.core_only:
            tracer_results = run_tracer_validation()

        # Generate report
        print("\n📊 Generating Validation Report...")
        report = generate_validation_report(core_results, tracer_results)

        # Output report
        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
            print(f"📄 Report saved to: {args.output}")
        else:
            print("\n" + report)

        # Determine exit code
        all_passed = True

        for result in core_results.values():
            if isinstance(result, dict):
                status_key = next(
                    (k for k in result.keys() if "status" in k.lower()), None
                )
                if status_key and result[status_key] != "PASSED":
                    all_passed = False
                    break

        for result in tracer_results.values():
            if isinstance(result, dict) and "overall_summary" in result:
                if result["overall_summary"]["overall_status"] != "PASSED":
                    all_passed = False
                    break

        return 0 if all_passed else 1

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        if args.verbose:
            traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
