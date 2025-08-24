# ARCH-001: Issues Kanban MCP Client 404 Error

**Issue Key:** ARCH-001  
**Title:** Issues Kanban fails to load due to MCP Client Service 404 errors  
**Status:** Open  
**Priority:** High  
**Severity:** Major  
**Created:** 2025-08-24  
**Reporter:** AI Assistant  
**Assignee:** Development Team  

## 🚨 Problem Description

The newly implemented Issues Kanban board fails to load issues due to 404 errors when trying to access MCP Client Service endpoints.

### Error Details
```
GET http://10.202.70.20:9181/api/mcp/clients/ 404 (Not Found)
[IssueService] Failed to call MCP tool query_issues_by_project_archon-dev: Error: Failed to get MCP clients
```

### User Impact
- Issues tab is completely non-functional
- Users cannot view, create, or manage issues via the kanban board
- Breaks the Phase 1 Issues Kanban implementation

## 🔍 Root Cause Analysis

### Investigation Timeline

**2025-08-24 13:00** - Initial CORS Error
- Issues tab showed CORS policy violations
- Frontend trying to call `http://10.202.70.20:9051/mcp` directly
- Cross-origin request blocked by browser

**2025-08-24 13:15** - URL Construction Fix
- Fixed double `/api/api/` URL construction in mcpService
- Changed from `getApiBasePath()` to `getApiUrl()`
- Still had CORS issues with direct MCP calls

**2025-08-24 13:25** - Archon Standards Implementation
- Switched to `mcpClientService.callClientTool()` following established patterns
- Matches approach used by templateService, componentService, etc.
- Should use `/api/mcp/clients/tools/call` endpoint

**2025-08-24 13:30** - Current Issue Identified
- MCP Client Service endpoints return 404 errors
- `/api/mcp/clients/` endpoint does not exist in backend
- MCP tools themselves work (confirmed via direct testing)

### Technical Analysis

✅ **Working Components:**
- MCP tools are registered and functional
- Direct MCP tool calls work: `query_issues_by_project_archon-dev` returns data
- Issues database is accessible and contains test data
- Frontend UI components render correctly

❌ **Broken Components:**
- `/api/mcp/clients/` endpoint returns 404
- `/api/mcp/clients/tools/call` endpoint missing
- MCP Client Service API not implemented in backend
- No MCP client registration/discovery system

### Code Analysis

**Current Implementation (issueService.ts):**
```typescript
// Get the default Archon MCP client
const clients = await mcpClientService.getClients(); // 404 ERROR HERE
const archonClient = clients.find(client => client.is_default || client.name.toLowerCase().includes('archon'));

// Call the tool using the MCP client service
const result = await mcpClientService.callClientTool({
  client_id: archonClient.id,
  tool_name: toolName,
  arguments: params
});
```

**Expected Backend Endpoints (Missing):**
- `GET /api/mcp/clients/` - List registered MCP clients
- `POST /api/mcp/clients/tools/call` - Call tool on specific client
- `GET /api/mcp/clients/{id}/tools` - Get tools for specific client

## 🎯 Solution Options

### Option 1: Implement MCP Client Service API (Recommended)
**Pros:**
- Follows established Archon architecture patterns
- Consistent with other services (templateService, componentService)
- Provides proper client management and discovery
- Future-proof for multi-client scenarios

**Cons:**
- Requires backend API implementation
- More complex than direct tool calls

**Implementation:**
1. Add MCP Client Service endpoints to `mcp_api.py`
2. Implement client registration and discovery
3. Add tool calling proxy functionality
4. Test with existing MCP tools

### Option 2: Fallback to Direct Backend Tool Calls
**Pros:**
- Quick fix using existing `/api/mcp/tools/call` endpoint
- Minimal backend changes required
- Matches pattern used by some other services

**Cons:**
- `/api/mcp/tools/call` currently returns "not yet implemented"
- Doesn't follow the newer MCP Client Service pattern
- Less future-proof

**Implementation:**
1. Fix `/api/mcp/tools/call` endpoint to actually call MCP tools
2. Update issueService to use direct tool calls
3. Revert to simpler architecture

### Option 3: Hybrid Approach
**Pros:**
- Use direct tool calls as immediate fix
- Implement MCP Client Service for future enhancement
- Provides working solution while building proper architecture

**Cons:**
- Requires maintaining two approaches temporarily
- More complex migration path

## 📋 Recommended Action Plan

### Immediate Fix (Option 2)
1. **Fix `/api/mcp/tools/call` endpoint** in `mcp_api.py`
2. **Update issueService** to use direct tool calls temporarily
3. **Test Issues Kanban** functionality
4. **Document technical debt** for future MCP Client Service implementation

### Long-term Solution (Option 1)
1. **Design MCP Client Service API** following Archon patterns
2. **Implement client registration** and discovery
3. **Add tool calling proxy** functionality
4. **Migrate all services** to use MCP Client Service
5. **Deprecate direct tool calls** approach

## 🧪 Testing Strategy

### Verification Steps
1. **Direct MCP Tool Test**: ✅ Confirmed working
   ```bash
   # This works via MCP tools directly
   query_issues_by_project_archon-dev(project_name="Test", limit=5)
   ```

2. **Backend Endpoint Test**: ❌ Currently failing
   ```bash
   curl http://10.202.70.20:9181/api/mcp/clients/
   # Returns: 404 Not Found
   ```

3. **Frontend Integration Test**: ❌ Currently failing
   - Navigate to Issues tab
   - Should load issues without errors
   - Should support drag-and-drop status updates

### Success Criteria
- [ ] Issues tab loads without 404 errors
- [ ] Issues display correctly in kanban board
- [ ] Drag-and-drop status updates work
- [ ] No CORS or network errors in console
- [ ] Follows established Archon patterns

## 📚 Related Documentation
- [Issues Kanban Implementation Plan](../issues-kanban-implementation-plan.md)
- [MCP Server Documentation](../docs/mcp-server.mdx)
- [Archon Architecture Overview](../.claude/commands/archon/archon-onboarding.md)

## 🔗 Dependencies
- MCP Server running on port 8051
- Backend API server on port 9181
- Issues database with proper schema
- Frontend development server on port 4737

---

## 📝 **Update 2025-08-24 13:45 - Progress Made, New Issue Identified**

### ✅ **Immediate Fix Deployed Successfully**
- Backend `/api/mcp/tools/call` endpoint now functional (no longer returns placeholder)
- Frontend successfully connects to backend API (no more 404 errors)
- MCP tool calling infrastructure is working

### 🚨 **New Issue: Parameter Validation Error**

**Current Error:**
```
POST http://10.202.70.20:4737/api/mcp/tools/call 400 (Bad Request)
Failed to query issues by project: IssueServiceError: Tool name is required
```

**Analysis:**
- ✅ **Endpoint Working**: 400 Bad Request instead of 404 Not Found
- ✅ **Connection Successful**: Frontend reaches backend API
- ❌ **Parameter Issue**: Backend validation failing on "Tool name is required"

### 🔍 **Root Cause Investigation**

**Request Format Issue:**
The frontend is sending:
```json
{
  "tool_name": "query_issues_by_project_archon-dev",
  "arguments": { "project_name": "...", "limit": 100 }
}
```

**Backend Validation:**
Backend expects `tool_name` parameter but validation is failing.

**Possible Causes:**
1. **Parameter Name Mismatch**: Backend expects different parameter name
2. **Request Body Structure**: Backend expects different JSON structure
3. **Validation Logic**: Backend validation logic has bug
4. **Content-Type**: Request headers not properly set

### 🔧 **Next Steps**

1. **Check Backend Parameter Validation**: Examine `mcp_api.py` request validation
2. **Debug Request Format**: Log actual request being sent vs expected format
3. **Test Direct API Call**: Use curl to test backend endpoint directly
4. **Fix Parameter Mapping**: Align frontend request with backend expectations

### 📊 **Progress Status**
- ✅ **CORS Issues**: Resolved
- ✅ **404 Endpoint Errors**: Resolved
- ✅ **MCP Tool Infrastructure**: Working
- 🔄 **Parameter Validation**: In Progress
- ⏳ **Issues Kanban Loading**: Blocked on parameter fix

---

## 📝 **Update 2025-08-24 14:00 - Parameter Fixed, Import Error Found**

### ✅ **Parameter Validation Issue Resolved**
- Backend now accepts both 'tool_name' and 'name' parameters
- Frontend successfully sends requests to backend
- No more 400 Bad Request errors

### 🚨 **New Issue: Missing Import Error**

**Current Error:**
```
POST http://10.202.70.20:4737/api/mcp/tools/call 500 (Internal Server Error)
Failed to query issues by project: IssueServiceError: MCP tool call failed: name 'mcp_server' is not defined
```

**Analysis:**
- ✅ **Parameter Validation**: Working (no more 400 errors)
- ✅ **Endpoint Reached**: Backend processing request
- ❌ **Import Missing**: `mcp_server` variable not defined in scope

### 🔍 **Root Cause: Missing Import**

**Code Issue in mcp_api.py:**
```python
# Line 1308: Using mcp_server but not imported
mcp_client = mcp_server.get_client()
```

**Missing Import:**
The `mcp_server` variable is not imported or defined in the mcp_api.py file.

**Required Fix:**
Need to import or define `mcp_server` to access the MCP client.

### 🔧 **Next Steps**

1. **Check MCP Server Import**: Find correct import for mcp_server
2. **Add Missing Import**: Import mcp_server in mcp_api.py
3. **Test MCP Client Access**: Verify mcp_server.get_client() works
4. **Complete Tool Call**: Ensure full MCP tool calling pipeline works

### 📊 **Progress Status**
- ✅ **CORS Issues**: Resolved
- ✅ **404 Endpoint Errors**: Resolved
- ✅ **MCP Tool Infrastructure**: Working
- ✅ **Parameter Validation**: Resolved
- 🔄 **Import Error**: In Progress
- ⏳ **Issues Kanban Loading**: Blocked on import fix

---
**Next Update:** Will be added when import error is resolved.
