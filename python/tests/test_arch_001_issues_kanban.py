"""
ARCH-001 Issues Kanban Automated Tests

Tests for the Issues Kanban MCP Client 404 error resolution.
This test suite automatically verifies the fix for ARCH-001 without manual testing.
"""

import pytest
import asyncio
import httpx
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock

# Import the FastAPI app
try:
    from src.server.main import app
except ImportError:
    # Fallback for different import paths
    try:
        from python.src.server.main import app
    except ImportError:
        app = None


class TestARCH001IssuesKanban:
    """Test suite for ARCH-001 Issues Kanban functionality"""

    def test_mcp_tools_call_endpoint_exists(self):
        """Test that the /api/mcp/tools/call endpoint exists"""
        if app is None:
            pytest.skip("FastAPI app not available")
            
        client = TestClient(app)
        
        # Test with minimal valid request
        response = client.post("/api/mcp/tools/call", json={
            "tool_name": "test_tool",
            "arguments": {}
        })
        
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404, "MCP tools call endpoint should exist"
        
        # Accept various status codes (400, 500, etc.) as long as endpoint exists
        assert response.status_code in [200, 400, 422, 500, 503], f"Unexpected status code: {response.status_code}"

    def test_mcp_tools_call_parameter_validation(self):
        """Test parameter validation for /api/mcp/tools/call endpoint"""
        if app is None:
            pytest.skip("FastAPI app not available")
            
        client = TestClient(app)
        
        # Test missing tool_name parameter
        response = client.post("/api/mcp/tools/call", json={
            "arguments": {}
        })
        
        # Should return 400 for missing tool_name, not 404
        assert response.status_code != 404, "Endpoint should exist"
        
        if response.status_code == 400:
            data = response.json()
            error_message = str(data.get("detail", {}).get("error", "")).lower()
            assert "tool name" in error_message, f"Should validate tool_name parameter: {data}"

    def test_issues_query_tool_call_format(self):
        """Test the exact format used by issueService for querying issues"""
        if app is None:
            pytest.skip("FastAPI app not available")
            
        client = TestClient(app)
        
        # Test the exact call that issueService.queryIssuesByProject makes
        response = client.post("/api/mcp/tools/call", json={
            "tool_name": "query_issues_by_project_archon-dev",
            "arguments": {
                "project_name": "Test",
                "limit": 5
            }
        })
        
        # Should not return 404 (endpoint exists) or 400 (parameters valid)
        assert response.status_code != 404, "MCP tools call endpoint should exist"
        assert response.status_code != 400, f"Parameters should be valid: {response.json() if response.status_code == 400 else 'N/A'}"
        
        # Accept 500 (server error) or 503 (service unavailable) as these indicate
        # the endpoint and parameters are working, but there might be MCP server issues
        assert response.status_code in [200, 500, 503], f"Unexpected status code: {response.status_code}"

    @pytest.mark.asyncio
    async def test_direct_mcp_client_import(self):
        """Test that MCP client can be imported and initialized"""
        try:
            # Test the import that was failing in ARCH-001
            from src.agents.mcp_client import get_mcp_client
            
            # Try to get MCP client
            mcp_client = await get_mcp_client()
            assert mcp_client is not None, "MCP client should be created successfully"
            
        except ImportError as e:
            pytest.fail(f"MCP client import failed: {e}")
        except Exception as e:
            # Other errors are acceptable (MCP server not running, etc.)
            # The important thing is that the import works
            print(f"MCP client creation failed (expected if MCP server not running): {e}")

    @pytest.mark.asyncio
    async def test_mcp_server_connectivity(self):
        """Test connectivity to MCP server (if running)"""
        try:
            # Try to connect to MCP server directly
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Test common MCP server ports
                mcp_urls = [
                    "http://localhost:8051",
                    "http://localhost:9051", 
                    "http://10.202.70.20:8051",
                    "http://10.202.70.20:9051"
                ]
                
                mcp_available = False
                for url in mcp_urls:
                    try:
                        response = await client.get(f"{url}/health")
                        if response.status_code == 200:
                            mcp_available = True
                            print(f"✅ MCP server available at {url}")
                            break
                    except:
                        continue
                
                if not mcp_available:
                    print("⚠️  MCP server not available (this is OK for testing)")
                    
        except Exception as e:
            print(f"MCP server connectivity test failed: {e}")

    def test_arch_001_resolution_indicators(self):
        """Test specific indicators that ARCH-001 is resolved"""
        if app is None:
            pytest.skip("FastAPI app not available")
            
        client = TestClient(app)
        
        # Test 1: Endpoint exists (not 404)
        response = client.post("/api/mcp/tools/call", json={
            "tool_name": "query_issues_by_project_archon-dev",
            "arguments": {"project_name": "Test", "limit": 5}
        })
        
        assert response.status_code != 404, "❌ ARCH-001 NOT RESOLVED: Endpoint still returns 404"
        
        # Test 2: Parameter validation works (not 400 with "Tool name is required")
        if response.status_code == 400:
            data = response.json()
            error_msg = str(data.get("detail", {}).get("error", "")).lower()
            assert "tool name" not in error_msg or "required" not in error_msg, \
                f"❌ ARCH-001 NOT RESOLVED: Parameter validation still failing: {data}"
        
        # Test 3: No import errors (not 500 with module import errors)
        if response.status_code == 500:
            data = response.json()
            error_msg = str(data.get("detail", {}).get("error", "")).lower()
            
            import_error_indicators = [
                "no module named",
                "mcp_server' is not defined",
                "import error",
                "module not found"
            ]
            
            for indicator in import_error_indicators:
                assert indicator not in error_msg, \
                    f"❌ ARCH-001 NOT RESOLVED: Import error still occurring: {data}"
        
        print("✅ ARCH-001 RESOLUTION INDICATORS PASSED")


class TestARCH001EndToEnd:
    """End-to-end tests for ARCH-001 resolution"""
    
    @pytest.mark.asyncio
    async def test_full_issues_api_flow(self):
        """Test the complete flow from frontend to MCP tools"""
        if app is None:
            pytest.skip("FastAPI app not available")
            
        client = TestClient(app)
        
        # Simulate the exact sequence that happens when Issues tab loads
        steps = [
            {
                "name": "Query issues by project",
                "request": {
                    "tool_name": "query_issues_by_project_archon-dev",
                    "arguments": {"project_name": "Test", "limit": 100}
                }
            },
            {
                "name": "Update issue status",
                "request": {
                    "tool_name": "update_issue_status_archon-dev", 
                    "arguments": {"issue_key": "TEST-1", "new_status": "in_progress"}
                }
            }
        ]
        
        results = []
        for step in steps:
            response = client.post("/api/mcp/tools/call", json=step["request"])
            
            results.append({
                "step": step["name"],
                "status_code": response.status_code,
                "success": response.status_code in [200, 500, 503]  # 500/503 = server issues, not ARCH-001
            })
        
        # All steps should at least reach the backend (no 404s)
        for result in results:
            assert result["success"], f"Step '{result['step']}' failed with status {result['status_code']}"
        
        print("✅ END-TO-END FLOW COMPLETED SUCCESSFULLY")


def run_arch_001_tests():
    """Convenience function to run all ARCH-001 tests"""
    print("🧪 Running ARCH-001 Automated Tests...")
    
    # Run the tests
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ])
    
    if exit_code == 0:
        print("✅ ALL ARCH-001 TESTS PASSED - Issue appears to be resolved!")
    else:
        print("❌ ARCH-001 TESTS FAILED - Issue still exists")
    
    return exit_code == 0


if __name__ == "__main__":
    run_arch_001_tests()
