#!/usr/bin/env python3
"""
Comprehensive Workflow Test Runner

This script runs all workflow engine tests with proper categorization and reporting.
Provides options for running specific test categories and generating detailed reports.
"""

import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any


class WorkflowTestRunner:
    """Test runner for workflow engine tests."""
    
    def __init__(self):
        self.test_categories = {
            "validation": {
                "description": "Workflow validation logic and error cases",
                "files": [
                    "test_workflow_validation_comprehensive.py",
                    "test_workflow_models.py"
                ],
                "markers": ["validation"]
            },
            "execution": {
                "description": "Workflow execution engine and step processing",
                "files": [
                    "test_workflow_executor.py",
                    "test_workflow_execution_service_comprehensive.py"
                ],
                "markers": ["execution"]
            },
            "error_handling": {
                "description": "Error handling and rollback mechanisms",
                "files": [
                    "test_workflow_error_handling.py"
                ],
                "markers": ["error_handling"]
            },
            "chaining": {
                "description": "Workflow chaining and parameter passing",
                "files": [
                    "test_workflow_chaining_parameters.py"
                ],
                "markers": ["chaining"]
            },
            "performance": {
                "description": "Performance tests for large workflows",
                "files": [
                    "test_workflow_performance.py"
                ],
                "markers": ["performance"]
            },
            "integration": {
                "description": "Integration tests with database and MCP tools",
                "files": [
                    "test_workflow_integration.py",
                    "test_workflow_repository.py",
                    "test_mcp_tool_integration.py"
                ],
                "markers": ["integration"]
            },
            "websocket": {
                "description": "WebSocket real-time monitoring tests",
                "files": [
                    "test_workflow_websocket.py"
                ],
                "markers": ["websocket"]
            }
        }
    
    def run_category_tests(self, category: str, verbose: bool = False) -> Dict[str, Any]:
        """Run tests for a specific category."""
        if category not in self.test_categories:
            raise ValueError(f"Unknown test category: {category}")
        
        category_info = self.test_categories[category]
        print(f"\n🧪 Running {category} tests: {category_info['description']}")
        print("=" * 80)
        
        results = {
            "category": category,
            "description": category_info["description"],
            "files": [],
            "total_passed": 0,
            "total_failed": 0,
            "total_skipped": 0,
            "execution_time": 0,
            "success": True
        }
        
        start_time = time.time()
        
        for test_file in category_info["files"]:
            file_result = self._run_test_file(test_file, category_info["markers"], verbose)
            results["files"].append(file_result)
            results["total_passed"] += file_result["passed"]
            results["total_failed"] += file_result["failed"]
            results["total_skipped"] += file_result["skipped"]
            
            if not file_result["success"]:
                results["success"] = False
        
        results["execution_time"] = time.time() - start_time
        
        # Print category summary
        status = "✅ PASSED" if results["success"] else "❌ FAILED"
        print(f"\n{status} {category} tests:")
        print(f"  📊 {results['total_passed']} passed, {results['total_failed']} failed, {results['total_skipped']} skipped")
        print(f"  ⏱️  Execution time: {results['execution_time']:.2f}s")
        
        return results
    
    def _run_test_file(self, test_file: str, markers: List[str], verbose: bool = False) -> Dict[str, Any]:
        """Run tests in a specific file."""
        print(f"\n📁 Running {test_file}...")
        
        # Build pytest command
        cmd = ["python", "-m", "pytest", f"tests/{test_file}", "-v"]
        
        # Add markers if specified
        if markers:
            marker_expr = " or ".join(markers)
            cmd.extend(["-m", marker_expr])
        
        # Add verbose output if requested
        if verbose:
            cmd.append("-s")
        
        # Add coverage if available
        cmd.extend(["--tb=short"])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            # Parse pytest output
            output_lines = result.stdout.split('\n')
            passed = failed = skipped = 0
            
            for line in output_lines:
                if "passed" in line and "failed" in line:
                    # Parse summary line like "5 passed, 2 failed, 1 skipped"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed" and i > 0:
                            passed = int(parts[i-1])
                        elif part == "failed" and i > 0:
                            failed = int(parts[i-1])
                        elif part == "skipped" and i > 0:
                            skipped = int(parts[i-1])
                elif line.strip().endswith("passed"):
                    # Parse simple "X passed" line
                    parts = line.strip().split()
                    if len(parts) >= 2 and parts[-1] == "passed":
                        passed = int(parts[-2])
            
            success = result.returncode == 0
            
            # Print file result
            status = "✅" if success else "❌"
            print(f"  {status} {passed} passed, {failed} failed, {skipped} skipped")
            
            if not success and verbose:
                print(f"  Error output: {result.stderr}")
            
            return {
                "file": test_file,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "success": success,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except Exception as e:
            print(f"  ❌ Error running {test_file}: {str(e)}")
            return {
                "file": test_file,
                "passed": 0,
                "failed": 1,
                "skipped": 0,
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    def run_all_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run all workflow tests."""
        print("🚀 Running comprehensive workflow engine tests")
        print("=" * 80)
        
        overall_results = {
            "categories": [],
            "total_passed": 0,
            "total_failed": 0,
            "total_skipped": 0,
            "execution_time": 0,
            "success": True
        }
        
        start_time = time.time()
        
        for category in self.test_categories.keys():
            category_result = self.run_category_tests(category, verbose)
            overall_results["categories"].append(category_result)
            overall_results["total_passed"] += category_result["total_passed"]
            overall_results["total_failed"] += category_result["total_failed"]
            overall_results["total_skipped"] += category_result["total_skipped"]
            
            if not category_result["success"]:
                overall_results["success"] = False
        
        overall_results["execution_time"] = time.time() - start_time
        
        # Print overall summary
        print("\n" + "=" * 80)
        status = "✅ ALL TESTS PASSED" if overall_results["success"] else "❌ SOME TESTS FAILED"
        print(f"{status}")
        print(f"📊 Total: {overall_results['total_passed']} passed, {overall_results['total_failed']} failed, {overall_results['total_skipped']} skipped")
        print(f"⏱️  Total execution time: {overall_results['execution_time']:.2f}s")
        
        # Print category breakdown
        print("\n📋 Category Breakdown:")
        for category_result in overall_results["categories"]:
            status = "✅" if category_result["success"] else "❌"
            print(f"  {status} {category_result['category']}: {category_result['total_passed']} passed, {category_result['total_failed']} failed")
        
        return overall_results
    
    def list_categories(self):
        """List all available test categories."""
        print("📋 Available test categories:")
        print("=" * 50)
        
        for category, info in self.test_categories.items():
            print(f"\n🏷️  {category}")
            print(f"   📝 {info['description']}")
            print(f"   📁 Files: {', '.join(info['files'])}")
    
    def check_test_files(self):
        """Check if all test files exist."""
        print("🔍 Checking test file availability...")
        
        missing_files = []
        existing_files = []
        
        for category, info in self.test_categories.items():
            for test_file in info["files"]:
                file_path = Path(__file__).parent / test_file
                if file_path.exists():
                    existing_files.append(test_file)
                    print(f"  ✅ {test_file}")
                else:
                    missing_files.append(test_file)
                    print(f"  ❌ {test_file} (missing)")
        
        print(f"\n📊 Summary: {len(existing_files)} found, {len(missing_files)} missing")
        
        if missing_files:
            print(f"\n⚠️  Missing test files:")
            for file in missing_files:
                print(f"    - {file}")
            return False
        
        return True


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="Run workflow engine tests")
    parser.add_argument(
        "category",
        nargs="?",
        help="Test category to run (or 'all' for all tests)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available test categories"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if all test files exist"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    runner = WorkflowTestRunner()
    
    if args.list:
        runner.list_categories()
        return
    
    if args.check:
        if runner.check_test_files():
            print("\n✅ All test files are available")
            sys.exit(0)
        else:
            print("\n❌ Some test files are missing")
            sys.exit(1)
    
    if not args.category:
        print("Please specify a test category or use --list to see available categories")
        sys.exit(1)
    
    try:
        if args.category == "all":
            results = runner.run_all_tests(args.verbose)
        else:
            results = runner.run_category_tests(args.category, args.verbose)
        
        # Exit with appropriate code
        sys.exit(0 if results["success"] else 1)
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nUse --list to see available categories")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
