#!/usr/bin/env python3
"""
Comprehensive Test Runner for Export/Import System

This script runs the complete export/import testing suite including:
- Unit tests
- Integration tests
- Performance tests
- Data integrity validation
- End-to-end scenarios
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional


class ExportImportTestRunner:
    """Test runner for export/import system"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent
        
        # Test categories and their paths
        self.test_categories = {
            "unit": [
                "test_export_service.py",
                "test_import_service.py", 
                "test_export_import_api.py",
                "test_backup_system.py",
                "test_mcp_export_import_tools.py"
            ],
            "integration": [
                "integration/test_export_import_integration.py"
            ],
            "performance": [
                "performance/test_export_import_performance.py"
            ],
            "validation": [
                "validation/test_data_integrity.py"
            ],
            "scenarios": [
                "scenarios/test_export_import_scenarios.py"
            ]
        }
    
    def run_tests(
        self, 
        categories: Optional[List[str]] = None,
        pattern: Optional[str] = None,
        markers: Optional[List[str]] = None,
        coverage: bool = False,
        parallel: bool = False,
        stop_on_first_failure: bool = False
    ) -> bool:
        """
        Run export/import tests with specified options
        
        Args:
            categories: Test categories to run (unit, integration, performance, etc.)
            pattern: Test name pattern to match
            markers: Pytest markers to filter tests
            coverage: Generate coverage report
            parallel: Run tests in parallel
            stop_on_first_failure: Stop on first test failure
            
        Returns:
            True if all tests passed, False otherwise
        """
        print("🚀 Starting Export/Import Test Suite")
        print("=" * 60)
        
        # Determine which tests to run
        test_files = self._get_test_files(categories, pattern)
        
        if not test_files:
            print("❌ No test files found matching criteria")
            return False
        
        print(f"📋 Running {len(test_files)} test files:")
        for test_file in test_files:
            print(f"  • {test_file}")
        print()
        
        # Build pytest command
        cmd = self._build_pytest_command(
            test_files, markers, coverage, parallel, stop_on_first_failure
        )
        
        # Run tests
        start_time = time.time()
        success = self._execute_tests(cmd)
        end_time = time.time()
        
        # Print summary
        self._print_summary(success, end_time - start_time, test_files)
        
        return success
    
    def run_quick_tests(self) -> bool:
        """Run a quick subset of tests for development"""
        print("⚡ Running Quick Export/Import Tests")
        print("=" * 50)
        
        quick_tests = [
            "test_export_service.py::TestProjectExportService::test_export_project_success",
            "test_import_service.py::TestProjectImportService::test_import_project_success",
            "test_export_import_api.py::TestExportImportAPI::test_export_project_endpoint"
        ]
        
        cmd = ["python", "-m", "pytest", "-v"] + quick_tests
        return self._execute_tests(cmd)
    
    def run_smoke_tests(self) -> bool:
        """Run smoke tests to verify basic functionality"""
        print("💨 Running Export/Import Smoke Tests")
        print("=" * 50)
        
        cmd = [
            "python", "-m", "pytest", "-v",
            "-m", "not slow",  # Exclude slow tests
            "--tb=short",
            "test_export_service.py",
            "test_import_service.py"
        ]
        
        return self._execute_tests(cmd)
    
    def run_performance_benchmarks(self) -> bool:
        """Run performance benchmarks"""
        print("📊 Running Export/Import Performance Benchmarks")
        print("=" * 60)
        
        cmd = [
            "python", "-m", "pytest", "-v",
            "-m", "performance",
            "--tb=short",
            "--benchmark-only",
            "performance/"
        ]
        
        return self._execute_tests(cmd)
    
    def validate_test_environment(self) -> bool:
        """Validate that the test environment is properly set up"""
        print("🔍 Validating Test Environment")
        print("=" * 40)
        
        checks = [
            ("Python version", self._check_python_version),
            ("Required packages", self._check_required_packages),
            ("Test files exist", self._check_test_files_exist),
            ("Environment variables", self._check_environment_variables)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                result = check_func()
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"  {check_name}: {status}")
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"  {check_name}: ❌ ERROR - {e}")
                all_passed = False
        
        print()
        return all_passed
    
    def _get_test_files(self, categories: Optional[List[str]], pattern: Optional[str]) -> List[str]:
        """Get list of test files to run"""
        if categories is None:
            categories = ["unit", "integration"]  # Default categories
        
        test_files = []
        for category in categories:
            if category in self.test_categories:
                test_files.extend(self.test_categories[category])
            else:
                print(f"⚠️  Unknown test category: {category}")
        
        # Filter by pattern if provided
        if pattern:
            test_files = [f for f in test_files if pattern in f]
        
        # Verify files exist
        existing_files = []
        for test_file in test_files:
            full_path = self.test_dir / test_file
            if full_path.exists():
                existing_files.append(test_file)
            else:
                print(f"⚠️  Test file not found: {test_file}")
        
        return existing_files
    
    def _build_pytest_command(
        self,
        test_files: List[str],
        markers: Optional[List[str]],
        coverage: bool,
        parallel: bool,
        stop_on_first_failure: bool
    ) -> List[str]:
        """Build pytest command with options"""
        cmd = ["python", "-m", "pytest"]
        
        # Add verbosity
        if self.verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        # Add markers
        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])
        
        # Add coverage
        if coverage:
            cmd.extend([
                "--cov=src.server.services.projects",
                "--cov=src.server.services.backup",
                "--cov=src.mcp.modules",
                "--cov-report=html",
                "--cov-report=term-missing"
            ])
        
        # Add parallel execution
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Stop on first failure
        if stop_on_first_failure:
            cmd.append("-x")
        
        # Add test files
        cmd.extend(test_files)
        
        return cmd
    
    def _execute_tests(self, cmd: List[str]) -> bool:
        """Execute pytest command"""
        if self.verbose:
            print(f"🔧 Running command: {' '.join(cmd)}")
            print()
        
        try:
            # Change to test directory
            original_cwd = os.getcwd()
            os.chdir(self.test_dir)
            
            # Run tests
            result = subprocess.run(cmd, capture_output=False)
            
            # Restore directory
            os.chdir(original_cwd)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
    
    def _print_summary(self, success: bool, duration: float, test_files: List[str]):
        """Print test execution summary"""
        print("\n" + "=" * 60)
        print("📊 TEST EXECUTION SUMMARY")
        print("=" * 60)
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"Status: {status}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Test files: {len(test_files)}")
        
        if success:
            print("\n🎉 All export/import tests passed successfully!")
        else:
            print("\n💥 Some tests failed. Check output above for details.")
        
        print("=" * 60)
    
    def _check_python_version(self) -> bool:
        """Check Python version"""
        return sys.version_info >= (3, 8)
    
    def _check_required_packages(self) -> bool:
        """Check if required packages are installed"""
        required_packages = ["pytest", "fastapi", "supabase"]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                return False
        
        return True
    
    def _check_test_files_exist(self) -> bool:
        """Check if test files exist"""
        all_test_files = []
        for files in self.test_categories.values():
            all_test_files.extend(files)
        
        for test_file in all_test_files:
            if not (self.test_dir / test_file).exists():
                return False
        
        return True
    
    def _check_environment_variables(self) -> bool:
        """Check required environment variables"""
        required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY"]
        
        for var in required_vars:
            if not os.getenv(var):
                return False
        
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run export/import system tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_export_import_tests.py                    # Run default tests
  python run_export_import_tests.py --quick            # Run quick tests
  python run_export_import_tests.py --smoke            # Run smoke tests
  python run_export_import_tests.py --performance      # Run performance tests
  python run_export_import_tests.py --all              # Run all tests
  python run_export_import_tests.py --categories unit integration
  python run_export_import_tests.py --pattern export
  python run_export_import_tests.py --coverage --parallel
        """
    )
    
    parser.add_argument("--quick", action="store_true", help="Run quick tests")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--validate", action="store_true", help="Validate test environment")
    
    parser.add_argument("--categories", nargs="+", 
                       choices=["unit", "integration", "performance", "validation", "scenarios"],
                       help="Test categories to run")
    parser.add_argument("--pattern", help="Test name pattern to match")
    parser.add_argument("--markers", nargs="+", help="Pytest markers to filter tests")
    
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--stop-on-failure", action="store_true", help="Stop on first failure")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = ExportImportTestRunner(verbose=args.verbose)
    
    # Validate environment if requested
    if args.validate:
        success = runner.validate_test_environment()
        sys.exit(0 if success else 1)
    
    # Run specific test types
    if args.quick:
        success = runner.run_quick_tests()
    elif args.smoke:
        success = runner.run_smoke_tests()
    elif args.performance:
        success = runner.run_performance_benchmarks()
    elif args.all:
        success = runner.run_tests(
            categories=["unit", "integration", "performance", "validation", "scenarios"],
            coverage=args.coverage,
            parallel=args.parallel,
            stop_on_first_failure=args.stop_on_failure
        )
    else:
        # Run with specified options
        success = runner.run_tests(
            categories=args.categories,
            pattern=args.pattern,
            markers=args.markers,
            coverage=args.coverage,
            parallel=args.parallel,
            stop_on_first_failure=args.stop_on_failure
        )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
