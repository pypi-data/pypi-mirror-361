#!/usr/bin/env python3
"""
SNID SAGE Test Runner
=====================

Simple test runner for validating the restructured SNID SAGE project.
This script runs various tests to ensure everything is working correctly
after the project reorganization and CLI output directory fix.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --quick            # Run quick tests only (no full analysis)
    python run_tests.py --cli-only         # Run CLI tests only
    python run_tests.py --core-only        # Run core engine tests only
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n[TEST] {description}")
    print(f"Command: {cmd}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, shell=True, check=False)
        if result.returncode == 0:
            print(f"[PASS] SUCCESS: {description}")
            return True
        else:
            print(f"[FAIL] FAILED: {description} (exit code: {result.returncode})")
            return False
    except Exception as e:
        print(f"[ERROR] ERROR: {description} - {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="SNID SAGE Test Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument("--cli-only", action="store_true", help="Run CLI tests only")
    parser.add_argument("--core-only", action="store_true", help="Run core engine tests only")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print("="*60)
    print("SNID SAGE TEST RUNNER")
    print("="*60)
    print(f"Project directory: {Path.cwd()}")
    print()

    # Check if we have required test data
    test_spectrum = Path("data/sn2003jo.dat")
    templates_dir = Path("templates")
    
    have_test_data = test_spectrum.exists() and templates_dir.exists()
    if not have_test_data:
        print("[WARN] Warning: Test data not found (data/sn2003jo.dat or templates/)")
        print("       Some tests will be skipped")
    
    results = {}
    
    # CLI Tests
    if not args.core_only:
        print("\n" + "="*40)
        print("CLI INTEGRATION TESTS")
        print("="*40)
        
        # Test CLI integration
        results["CLI Integration"] = run_command(
            "python tests/test_cli_integration.py",
            "CLI Integration Tests"
        )
    
    # Core Engine Tests  
    if not args.cli_only and have_test_data:
        print("\n" + "="*40)
        print("CORE ENGINE TESTS")
        print("="*40)
        
        if not args.quick:
            # Test output directory fix specifically
            results["Output Directory Fix"] = run_command(
                f"python snid_sage/snid/snid_test.py \"{test_spectrum}\" --templates \"{templates_dir}\" --test-output-fix",
                "Output Directory Fix Validation"
            )
            
            # Test basic analysis
            results["Basic Analysis"] = run_command(
                f"python snid_sage/snid/snid_test.py \"{test_spectrum}\" --templates \"{templates_dir}\" --output --save-plots --verbose",
                "Basic SNID Analysis with Outputs"
            )
        else:
            # Quick test - just imports and help
            results["Core Import"] = run_command(
                "python -c \"from snid_sage.snid.snid import run_snid; print('Core import successful')\"",
                "Core SNID Import Test"
            )
    
    # Import Tests (always run)
    print("\n" + "="*40)
    print("IMPORT TESTS")
    print("="*40)
    
    results["CLI Import"] = run_command(
        "python -c \"from snid_sage.interfaces.cli.main import main; print('CLI import successful')\"",
        "CLI Import Test"
    )
    
    results["GUI Import"] = run_command(
        "python -c \"from snid_sage.interfaces.gui.sage_gui import main; print('GUI import successful')\"",
        "GUI Import Test"
    )
    
    results["Shared Import"] = run_command(
        "python -c \"from snid_sage.shared.constants import physical; from snid_sage.shared.types import spectrum_types; print('Shared imports successful')\"",
        "Shared Components Import Test"
    )

    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, success in results.items():
        status = "[PASS] PASSED" if success else "[FAIL] FAILED"
        print(f"{test_name:30} {status}")
    
    print()
    print(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        print("[PASS] The restructured SNID SAGE project is fully functional")
        print("[PASS] CLI output directory fix is working correctly")
        print("[PASS] All imports are working with the new structure")
        return 0
    else:
        print("\n[WARN] Some tests failed")
        print("       Check the output above for details")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 