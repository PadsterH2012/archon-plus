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
**Next Update:** Will be added when investigation continues or solution is implemented.
