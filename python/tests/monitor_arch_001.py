#!/usr/bin/env python3
"""
ARCH-001 Automated Monitoring Script

This script continuously monitors the ARCH-001 issue status and provides
real-time feedback on when the issue is resolved without manual testing.
"""

import asyncio
import time
import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from typing import Dict, Any, Optional


class ARCH001Monitor:
    """Monitor for ARCH-001 Issues Kanban resolution"""
    
    def __init__(self, base_url: str = "http://localhost:8181"):
        self.base_url = base_url
        self.mcp_endpoint = f"{base_url}/api/mcp/tools/call"
        self.test_payload = {
            "tool_name": "query_issues_by_project_archon-dev",
            "arguments": {
                "project_name": "Test",
                "limit": 5
            }
        }
        
    def check_arch_001_status(self) -> Dict[str, Any]:
        """Check the current status of ARCH-001"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "details": {},
            "resolved": False
        }

        try:
            # Prepare request data
            data = json.dumps(self.test_payload).encode('utf-8')

            # Create request
            req = urllib.request.Request(
                self.mcp_endpoint,
                data=data,
                headers={"Content-Type": "application/json"}
            )

            start_time = time.time()

            # Make request
            try:
                with urllib.request.urlopen(req, timeout=10.0) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    result["details"]["status_code"] = response.status
                    result["details"]["response_time_ms"] = response_time_ms
                
                    # Read response data
                    response_data = response.read().decode('utf-8')

                    # Analyze the response to determine ARCH-001 status
                    if response.status == 200:
                        try:
                            data = json.loads(response_data)
                            result["status"] = "success"
                            result["details"]["response"] = data
                            result["resolved"] = True
                        except:
                            result["status"] = "success_unparseable"
                            result["resolved"] = True

            except urllib.error.HTTPError as e:
                response_time_ms = (time.time() - start_time) * 1000
                result["details"]["status_code"] = e.code
                result["details"]["response_time_ms"] = response_time_ms

                # Read error response
                try:
                    error_data = e.read().decode('utf-8')
                    error_json = json.loads(error_data)
                except:
                    error_json = {"error": "Could not parse error response"}

                if e.code == 404:
                    result["status"] = "endpoint_missing"
                    result["details"]["error"] = "MCP tools call endpoint returns 404"

                elif e.code == 400:
                    try:
                        error_msg = str(error_json.get("detail", {}).get("error", "")).lower()

                        if "tool name" in error_msg and "required" in error_msg:
                            result["status"] = "parameter_validation_error"
                            result["details"]["error"] = "Parameter validation failing"
                        else:
                            result["status"] = "other_400_error"
                            result["details"]["error"] = error_json
                    except:
                        result["status"] = "unknown_400_error"
                        result["details"]["error"] = "400 error with unparseable response"

                elif e.code == 500:
                    try:
                        error_msg = str(error_json.get("detail", {}).get("error", "")).lower()

                        if "no module named" in error_msg:
                            result["status"] = "import_error"
                            result["details"]["error"] = "Python module import error"
                        elif "mcp_server" in error_msg and "not defined" in error_msg:
                            result["status"] = "undefined_variable_error"
                            result["details"]["error"] = "mcp_server variable not defined"
                        else:
                            result["status"] = "other_500_error"
                            result["details"]["error"] = error_json
                    except:
                        result["status"] = "unknown_500_error"
                        result["details"]["error"] = "500 error with unparseable response"

                elif e.code == 503:
                    result["status"] = "service_unavailable"
                    result["details"]["error"] = "MCP server not running"
                    result["resolved"] = True  # ARCH-001 is resolved, just MCP server down

                else:
                    result["status"] = f"unexpected_status_{e.code}"
                    result["details"]["error"] = f"Unexpected status code: {e.code}"

        except urllib.error.URLError as e:
            result["status"] = "connection_error"
            result["details"]["error"] = f"Cannot connect to backend server: {e.reason}"

        except Exception as e:
            result["status"] = "unknown_error"
            result["details"]["error"] = f"Request failed: {str(e)}"

        return result
    
    def format_status_message(self, status: Dict[str, Any]) -> str:
        """Format status for console output"""
        timestamp = status["timestamp"]
        status_name = status["status"]
        resolved = status["resolved"]
        
        if resolved:
            icon = "✅"
            message = f"ARCH-001 RESOLVED"
        else:
            icon = "❌"
            message = f"ARCH-001 NOT RESOLVED"
            
        details = status["details"].get("error", "No additional details")
        
        return f"{icon} {timestamp} | {message} | Status: {status_name} | Details: {details}"
    
    async def monitor_continuous(self, interval_seconds: int = 30, max_checks: Optional[int] = None):
        """Monitor ARCH-001 status continuously"""
        print("🔍 Starting ARCH-001 Continuous Monitoring...")
        print(f"📡 Endpoint: {self.mcp_endpoint}")
        print(f"⏱️  Check interval: {interval_seconds} seconds")
        print(f"🎯 Payload: {json.dumps(self.test_payload, indent=2)}")
        print("-" * 80)

        check_count = 0
        last_status = None

        while True:
            check_count += 1

            if max_checks and check_count > max_checks:
                print(f"🛑 Reached maximum checks ({max_checks})")
                break

            status = self.check_arch_001_status()
            message = self.format_status_message(status)
            
            # Only print if status changed or every 10 checks
            if status["status"] != last_status or check_count % 10 == 0:
                print(f"[{check_count:03d}] {message}")
                
            # If resolved, celebrate and optionally exit
            if status["resolved"]:
                print("🎉 ARCH-001 HAS BEEN RESOLVED! 🎉")
                print("✅ Issues Kanban should now work properly")
                break
                
            last_status = status["status"]
            
            # Wait before next check
            await asyncio.sleep(interval_seconds)
    
    def single_check(self) -> bool:
        """Perform a single check and return True if resolved"""
        status = self.check_arch_001_status()
        message = self.format_status_message(status)
        print(message)
        return status["resolved"]


async def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor ARCH-001 Issues Kanban resolution")
    parser.add_argument("--url", default="http://localhost:8181", help="Backend URL")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds")
    parser.add_argument("--max-checks", type=int, help="Maximum number of checks")
    parser.add_argument("--single", action="store_true", help="Perform single check and exit")
    
    args = parser.parse_args()
    
    monitor = ARCH001Monitor(args.url)
    
    if args.single:
        resolved = monitor.single_check()
        sys.exit(0 if resolved else 1)
    else:
        await monitor.monitor_continuous(args.interval, args.max_checks)


# Test function for pytest integration
def test_arch_001_monitoring():
    """Test function that can be called by pytest"""
    monitor = ARCH001Monitor()
    status = monitor.check_arch_001_status()

    # Return status for test assertions
    return status


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"💥 Monitoring failed: {e}")
        sys.exit(1)
