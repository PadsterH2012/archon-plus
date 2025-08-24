#!/usr/bin/env python3
"""
ARCH-001 Test Runner

Comprehensive test runner for ARCH-001 Issues Kanban resolution.
Runs all automated tests and provides clear feedback on issue status.
"""

import asyncio
import subprocess
import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.monitor_arch_001 import ARCH001Monitor


class ARCH001TestRunner:
    """Comprehensive test runner for ARCH-001"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "unknown",
            "arch_001_resolved": False
        }
    
    def run_command(self, command: List[str], cwd: Path = None) -> Dict[str, Any]:
        """Run a command and return results"""
        if cwd is None:
            cwd = self.project_root
            
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(command)
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out",
                "command": " ".join(command)
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "command": " ".join(command)
            }
    
    def test_python_backend(self) -> Dict[str, Any]:
        """Run Python backend tests"""
        print("🐍 Running Python backend tests...")
        
        # Test if pytest is available
        pytest_check = self.run_command(["python", "-m", "pytest", "--version"])
        if not pytest_check["success"]:
            return {
                "success": False,
                "error": "pytest not available",
                "details": pytest_check
            }
        
        # Run ARCH-001 specific tests
        test_file = self.project_root / "tests" / "test_arch_001_issues_kanban.py"
        if not test_file.exists():
            return {
                "success": False,
                "error": "ARCH-001 test file not found",
                "details": {"expected_path": str(test_file)}
            }
        
        result = self.run_command([
            "python", "-m", "pytest", 
            str(test_file),
            "-v",
            "--tb=short"
        ])
        
        return {
            "success": result["success"],
            "details": result,
            "test_file": str(test_file)
        }
    
    def test_frontend(self) -> Dict[str, Any]:
        """Run frontend tests"""
        print("⚛️  Running frontend tests...")
        
        frontend_dir = self.project_root.parent / "archon-ui-main"
        if not frontend_dir.exists():
            return {
                "success": False,
                "error": "Frontend directory not found",
                "details": {"expected_path": str(frontend_dir)}
            }
        
        # Check if npm is available
        npm_check = self.run_command(["npm", "--version"], cwd=frontend_dir)
        if not npm_check["success"]:
            return {
                "success": False,
                "error": "npm not available",
                "details": npm_check
            }
        
        # Run ARCH-001 frontend tests
        test_file = frontend_dir / "test" / "arch-001-issues-kanban.test.tsx"
        if not test_file.exists():
            return {
                "success": False,
                "error": "ARCH-001 frontend test file not found",
                "details": {"expected_path": str(test_file)}
            }
        
        result = self.run_command([
            "npm", "test", "--", 
            "--run",
            "arch-001-issues-kanban.test.tsx"
        ], cwd=frontend_dir)
        
        return {
            "success": result["success"],
            "details": result,
            "test_file": str(test_file)
        }
    
    async def test_live_monitoring(self) -> Dict[str, Any]:
        """Test live monitoring of ARCH-001 status"""
        print("📡 Running live monitoring test...")
        
        try:
            monitor = ARCH001Monitor()
            status = await monitor.check_arch_001_status()
            
            return {
                "success": True,
                "status": status,
                "resolved": status["resolved"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "resolved": False
            }
    
    def test_file_structure(self) -> Dict[str, Any]:
        """Test that all required files exist"""
        print("📁 Checking file structure...")
        
        required_files = [
            self.project_root / "tests" / "test_arch_001_issues_kanban.py",
            self.project_root / "tests" / "monitor_arch_001.py",
            self.project_root / "tests" / "run_arch_001_tests.py",
            self.project_root.parent / "archon-ui-main" / "test" / "arch-001-issues-kanban.test.tsx"
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in required_files:
            if file_path.exists():
                existing_files.append(str(file_path))
            else:
                missing_files.append(str(file_path))
        
        return {
            "success": len(missing_files) == 0,
            "existing_files": existing_files,
            "missing_files": missing_files,
            "total_files": len(required_files)
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all ARCH-001 tests"""
        print("🧪 ARCH-001 Comprehensive Test Suite")
        print("=" * 50)
        
        # Test 1: File structure
        self.results["tests"]["file_structure"] = self.test_file_structure()
        
        # Test 2: Live monitoring (most important)
        self.results["tests"]["live_monitoring"] = await self.test_live_monitoring()
        
        # Test 3: Python backend tests
        self.results["tests"]["python_backend"] = self.test_python_backend()
        
        # Test 4: Frontend tests
        self.results["tests"]["frontend"] = self.test_frontend()
        
        # Determine overall status
        live_status = self.results["tests"]["live_monitoring"]
        if live_status["success"] and live_status.get("resolved", False):
            self.results["overall_status"] = "resolved"
            self.results["arch_001_resolved"] = True
        elif live_status["success"]:
            self.results["overall_status"] = "not_resolved"
            self.results["arch_001_resolved"] = False
        else:
            self.results["overall_status"] = "monitoring_failed"
            self.results["arch_001_resolved"] = False
        
        return self.results
    
    def print_results(self):
        """Print formatted test results"""
        print("\n" + "=" * 50)
        print("🧪 ARCH-001 TEST RESULTS")
        print("=" * 50)
        
        for test_name, result in self.results["tests"].items():
            status_icon = "✅" if result["success"] else "❌"
            print(f"{status_icon} {test_name.replace('_', ' ').title()}: {'PASS' if result['success'] else 'FAIL'}")
            
            if not result["success"] and "error" in result:
                print(f"   Error: {result['error']}")
        
        print("\n" + "-" * 50)
        
        if self.results["arch_001_resolved"]:
            print("🎉 ARCH-001 IS RESOLVED! 🎉")
            print("✅ Issues Kanban should work properly")
        else:
            print("❌ ARCH-001 IS NOT YET RESOLVED")
            print("🔧 Continue debugging based on test results")
        
        print(f"\n📊 Overall Status: {self.results['overall_status']}")
        print(f"⏰ Test Run: {self.results['timestamp']}")


async def main():
    """Main function"""
    runner = ARCH001TestRunner()
    
    try:
        await runner.run_all_tests()
        runner.print_results()
        
        # Exit with appropriate code
        sys.exit(0 if runner.results["arch_001_resolved"] else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Test runner failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
