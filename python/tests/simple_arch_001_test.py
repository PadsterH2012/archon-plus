#!/usr/bin/env python3
"""
Simple ARCH-001 Test Runner (No Dependencies)

A simple test runner for ARCH-001 that doesn't require pytest or other dependencies.
Uses only standard library modules to test the Issues Kanban functionality.
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from tests.monitor_arch_001 import ARCH001Monitor


class SimpleTestRunner:
    """Simple test runner for ARCH-001"""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
    
    def assert_true(self, condition, message="Assertion failed"):
        """Simple assertion helper"""
        self.tests_run += 1
        if condition:
            self.tests_passed += 1
            print(f"✅ PASS: {message}")
            self.results.append({"test": message, "status": "PASS"})
        else:
            self.tests_failed += 1
            print(f"❌ FAIL: {message}")
            self.results.append({"test": message, "status": "FAIL"})
    
    def assert_false(self, condition, message="Assertion failed"):
        """Simple negative assertion helper"""
        self.assert_true(not condition, message)
    
    def assert_equals(self, actual, expected, message="Values not equal"):
        """Simple equality assertion"""
        self.assert_true(actual == expected, f"{message}: expected {expected}, got {actual}")
    
    def assert_not_equals(self, actual, expected, message="Values should not be equal"):
        """Simple inequality assertion"""
        self.assert_true(actual != expected, f"{message}: both values are {actual}")
    
    def assert_contains(self, text, substring, message="Substring not found"):
        """Simple substring assertion"""
        self.assert_true(substring in text, f"{message}: '{substring}' not in '{text}'")
    
    def test_monitor_creation(self):
        """Test that ARCH001Monitor can be created"""
        print("\n🧪 Testing ARCH001Monitor creation...")
        
        try:
            monitor = ARCH001Monitor()
            self.assert_true(monitor is not None, "Monitor should be created")
            self.assert_true(hasattr(monitor, 'check_arch_001_status'), "Monitor should have check_arch_001_status method")
            self.assert_contains(monitor.mcp_endpoint, "/api/mcp/tools/call", "Monitor should have correct endpoint")
        except Exception as e:
            self.assert_true(False, f"Monitor creation failed: {e}")
    
    def test_arch_001_status_check(self):
        """Test ARCH-001 status checking"""
        print("\n🧪 Testing ARCH-001 status check...")
        
        try:
            monitor = ARCH001Monitor("http://10.202.70.20:9181")
            status = monitor.check_arch_001_status()
            
            # Basic structure tests
            self.assert_true(isinstance(status, dict), "Status should be a dictionary")
            self.assert_true("timestamp" in status, "Status should have timestamp")
            self.assert_true("status" in status, "Status should have status field")
            self.assert_true("resolved" in status, "Status should have resolved field")
            self.assert_true("details" in status, "Status should have details field")
            
            # Status should not be unknown (indicates connection worked)
            self.assert_not_equals(status["status"], "unknown", "Status should not be unknown")
            
            # Print current status for debugging
            print(f"📊 Current ARCH-001 Status: {status['status']}")
            print(f"🎯 Resolved: {status['resolved']}")
            
            # Check for specific ARCH-001 error indicators
            if status["status"] == "endpoint_missing":
                print("❌ ARCH-001 Issue: MCP endpoint returns 404")
            elif status["status"] == "parameter_validation_error":
                print("❌ ARCH-001 Issue: Parameter validation failing")
            elif status["status"] == "import_error":
                print("❌ ARCH-001 Issue: Python module import error")
            elif status["status"] == "undefined_variable_error":
                print("❌ ARCH-001 Issue: mcp_server variable not defined")
            elif status["resolved"]:
                print("✅ ARCH-001 RESOLVED!")
            else:
                print(f"🔍 ARCH-001 Status: {status['status']}")
                
        except Exception as e:
            self.assert_true(False, f"Status check failed: {e}")
    
    def test_endpoint_connectivity(self):
        """Test basic endpoint connectivity"""
        print("\n🧪 Testing endpoint connectivity...")
        
        endpoints_to_test = [
            "http://10.202.70.20:9181/api/mcp/tools/call",
            "http://localhost:8181/api/mcp/tools/call",
            "http://10.202.70.20:8181/api/mcp/tools/call"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                # Simple GET request to see if endpoint exists
                req = urllib.request.Request(endpoint)
                
                try:
                    with urllib.request.urlopen(req, timeout=5.0) as response:
                        # Any response (even error) means endpoint exists
                        print(f"✅ Endpoint reachable: {endpoint} (status: {response.status})")
                        break
                except urllib.error.HTTPError as e:
                    # HTTP errors mean endpoint exists but returned error
                    print(f"🔍 Endpoint exists: {endpoint} (HTTP {e.code})")
                    if e.code != 404:
                        break
                except urllib.error.URLError as e:
                    print(f"❌ Endpoint unreachable: {endpoint} ({e.reason})")
                    
            except Exception as e:
                print(f"❌ Endpoint test failed: {endpoint} ({e})")
    
    def test_mcp_tool_call_format(self):
        """Test MCP tool call format"""
        print("\n🧪 Testing MCP tool call format...")
        
        test_payload = {
            "tool_name": "query_issues_by_project_archon-dev",
            "arguments": {
                "project_name": "Test",
                "limit": 5
            }
        }
        
        try:
            # Test payload serialization
            json_data = json.dumps(test_payload)
            self.assert_true(len(json_data) > 0, "Payload should serialize to JSON")
            
            # Test payload structure
            self.assert_true("tool_name" in test_payload, "Payload should have tool_name")
            self.assert_true("arguments" in test_payload, "Payload should have arguments")
            
            print(f"📦 Test payload: {json_data}")
            
        except Exception as e:
            self.assert_true(False, f"Payload format test failed: {e}")
    
    def run_all_tests(self):
        """Run all ARCH-001 tests"""
        print("🧪 ARCH-001 Simple Test Suite")
        print("=" * 50)
        print(f"⏰ Started: {datetime.now().isoformat()}")
        print()
        
        # Run tests
        self.test_monitor_creation()
        self.test_endpoint_connectivity()
        self.test_mcp_tool_call_format()
        self.test_arch_001_status_check()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"🧪 Tests Run: {self.tests_run}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        
        if self.tests_failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {self.tests_failed} TESTS FAILED")
        
        print(f"\n⏰ Completed: {datetime.now().isoformat()}")
        
        return self.tests_failed == 0


def main():
    """Main function"""
    runner = SimpleTestRunner()
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
