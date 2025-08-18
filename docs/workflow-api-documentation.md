# Workflow API Documentation

## Overview

The Workflow API provides comprehensive endpoints for managing workflow templates, executing workflows, and monitoring progress. It follows RESTful principles and includes real-time execution tracking.

**Base URL**: `/api/workflows`

## Authentication

All endpoints require proper authentication. Include the appropriate authentication headers with your requests.

## Workflow Template Endpoints

### List Workflows

**GET** `/api/workflows`

List workflow templates with filtering and pagination.

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `per_page` (integer, optional): Items per page (default: 20, max: 100)
- `status` (string, optional): Filter by status (`draft`, `active`, `deprecated`, `archived`)
- `category` (string, optional): Filter by category
- `created_by` (string, optional): Filter by creator
- `is_public` (boolean, optional): Filter by public/private visibility
- `search` (string, optional): Search in name, title, description

**Response:**
```json
{
  "workflows": [
    {
      "id": "uuid",
      "name": "workflow_name",
      "title": "Workflow Title",
      "description": "Workflow description",
      "status": "active",
      "category": "deployment",
      "tags": ["tag1", "tag2"],
      "created_by": "user_id",
      "is_public": true,
      "created_at": "2025-08-18T10:30:00Z",
      "updated_at": "2025-08-18T10:30:00Z"
    }
  ],
  "total_count": 25,
  "page": 1,
  "per_page": 20,
  "has_more": true
}
```

### Create Workflow

**POST** `/api/workflows`

Create a new workflow template.

**Request Body:**
```json
{
  "name": "my_workflow",
  "title": "My Workflow",
  "description": "Description of the workflow",
  "category": "automation",
  "tags": ["automation", "deployment"],
  "parameters": {
    "param1": {
      "type": "string",
      "required": true,
      "description": "Parameter description"
    }
  },
  "outputs": {
    "result": {
      "type": "object",
      "description": "Workflow result"
    }
  },
  "steps": [
    {
      "name": "step1",
      "title": "First Step",
      "type": "action",
      "tool_name": "manage_task_archon",
      "parameters": {
        "action": "create",
        "title": "{{workflow.parameters.param1}}"
      }
    }
  ],
  "timeout_minutes": 60,
  "max_retries": 3,
  "is_public": false
}
```

**Response (201):**
```json
{
  "message": "Workflow created successfully",
  "workflow": {
    "id": "uuid",
    "name": "my_workflow",
    "title": "My Workflow",
    "status": "draft",
    "version": "1.0.0",
    "created_at": "2025-08-18T10:30:00Z"
  }
}
```

### Get Workflow

**GET** `/api/workflows/{workflow_id}`

Get detailed information about a specific workflow template.

**Response:**
```json
{
  "workflow": {
    "id": "uuid",
    "name": "workflow_name",
    "title": "Workflow Title",
    "description": "Detailed description",
    "steps": [...],
    "parameters": {...},
    "outputs": {...},
    "status": "active",
    "created_at": "2025-08-18T10:30:00Z"
  },
  "validation_result": {
    "is_valid": true,
    "errors": [],
    "warnings": [],
    "info": []
  }
}
```

### Update Workflow

**PUT** `/api/workflows/{workflow_id}`

Update an existing workflow template.

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "status": "active",
  "steps": [...]
}
```

**Response:**
```json
{
  "message": "Workflow updated successfully",
  "workflow": {
    "id": "uuid",
    "title": "Updated Title",
    "updated_at": "2025-08-18T10:35:00Z"
  }
}
```

### Delete Workflow

**DELETE** `/api/workflows/{workflow_id}`

Delete a workflow template permanently.

**Response:**
```json
{
  "message": "Workflow deleted successfully"
}
```

## Workflow Execution Endpoints

### Execute Workflow

**POST** `/api/workflows/{workflow_id}/execute`

Start execution of a workflow template.

**Request Body:**
```json
{
  "workflow_template_id": "uuid",
  "triggered_by": "user_id",
  "input_parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "trigger_context": {
    "source": "api",
    "task_id": "optional_task_id"
  }
}
```

**Response (202):**
```json
{
  "message": "Workflow execution started",
  "execution_id": "uuid",
  "status": "pending",
  "workflow_id": "uuid"
}
```

### Get Execution Status

**GET** `/api/workflows/executions/{execution_id}`

Get detailed status and progress of a workflow execution.

**Response:**
```json
{
  "execution": {
    "id": "uuid",
    "workflow_template_id": "uuid",
    "status": "running",
    "progress_percentage": 65.0,
    "current_step_index": 2,
    "total_steps": 4,
    "triggered_by": "user_id",
    "started_at": "2025-08-18T10:30:00Z",
    "input_parameters": {...},
    "output_data": {...},
    "execution_log": [...]
  },
  "step_executions": [
    {
      "id": "uuid",
      "step_index": 0,
      "step_name": "step1",
      "status": "completed",
      "started_at": "2025-08-18T10:30:00Z",
      "completed_at": "2025-08-18T10:31:00Z",
      "output_data": {...}
    }
  ],
  "total_steps": 4
}
```

### List Executions

**GET** `/api/workflows/executions`

List workflow executions with filtering.

**Query Parameters:**
- `workflow_id` (string, optional): Filter by workflow template ID
- `status` (string, optional): Filter by execution status
- `triggered_by` (string, optional): Filter by who triggered the execution
- `page` (integer, optional): Page number
- `per_page` (integer, optional): Items per page

**Response:**
```json
{
  "executions": [
    {
      "id": "uuid",
      "workflow_template_id": "uuid",
      "status": "completed",
      "progress_percentage": 100.0,
      "triggered_by": "user_id",
      "started_at": "2025-08-18T10:30:00Z",
      "completed_at": "2025-08-18T10:35:00Z"
    }
  ],
  "total_count": 15,
  "page": 1,
  "per_page": 20,
  "has_more": false
}
```

### Cancel Execution

**POST** `/api/workflows/executions/{execution_id}/cancel`

Cancel a running workflow execution.

**Response:**
```json
{
  "message": "Execution cancelled successfully",
  "execution_id": "uuid",
  "status": "cancelled"
}
```

## Workflow Validation Endpoints

### Validate Workflow

**POST** `/api/workflows/{workflow_id}/validate`

Perform comprehensive validation of a workflow template.

**Response:**
```json
{
  "is_valid": false,
  "errors": [
    {
      "code": "CIRCULAR_REFERENCE",
      "message": "Circular reference detected: step1 -> step2 -> step1",
      "step_name": "step1",
      "field": "on_success",
      "suggestion": "Remove circular references to prevent infinite loops"
    }
  ],
  "warnings": [
    {
      "code": "UNUSED_PARAMETER",
      "message": "Parameter 'unused_param' is declared but never used",
      "field": "parameters",
      "suggestion": "Remove unused parameters or add them to workflow steps"
    }
  ],
  "info": [
    {
      "code": "PERFORMANCE_INFO",
      "message": "Workflow has moderate complexity score of 25",
      "suggestion": "Consider optimizing for better performance"
    }
  ]
}
```

## Search and Discovery Endpoints

### Search Workflows

**POST** `/api/workflows/search`

Advanced search for workflow templates.

**Request Body:**
```json
{
  "query": "deployment",
  "category": "automation",
  "status": "active",
  "is_public": true
}
```

**Response:**
```json
{
  "workflows": [...],
  "total_count": 8,
  "query": "deployment"
}
```

### Get Categories

**GET** `/api/workflows/categories`

Get all available workflow categories.

**Response:**
```json
{
  "categories": [
    "automation",
    "deployment",
    "testing",
    "monitoring"
  ],
  "total_count": 4
}
```

### Get Examples

**GET** `/api/workflows/examples`

Get available example workflow templates.

**Response:**
```json
{
  "examples": [
    {
      "name": "project_setup",
      "title": "Project Setup Workflow",
      "description": "Complete workflow for setting up a new project",
      "category": "project_management",
      "tags": ["setup", "project"],
      "step_count": 3,
      "complexity": "simple"
    }
  ],
  "total_count": 4
}
```

### Get Specific Example

**GET** `/api/workflows/examples/{example_name}`

Get a specific example workflow template.

**Response:**
```json
{
  "example": {
    "name": "project_setup",
    "title": "Project Setup Workflow",
    "description": "Complete workflow for setting up a new project",
    "steps": [...],
    "parameters": {...}
  },
  "name": "project_setup"
}
```

## Error Responses

All endpoints return consistent error responses:

**400 Bad Request:**
```json
{
  "error": "Validation failed: Workflow name contains invalid characters"
}
```

**404 Not Found:**
```json
{
  "error": "Workflow template with ID uuid not found"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error occurred"
}
```

## Status Codes

- `200 OK`: Successful GET request
- `201 Created`: Successful POST request (creation)
- `202 Accepted`: Successful POST request (async operation)
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Rate Limiting

API endpoints are subject to rate limiting. Check response headers for current limits:
- `X-RateLimit-Limit`: Requests per time window
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets

## WebSocket Support

Real-time execution updates are available via WebSocket connections:

**Connection:** `ws://host/api/workflows/executions/{execution_id}/ws`

**Events:**
- `execution_started`: Execution began
- `step_started`: Step execution started
- `step_completed`: Step execution completed
- `execution_completed`: Execution finished
- `execution_failed`: Execution failed
- `execution_cancelled`: Execution cancelled

## SDK Examples

### Python Example

```python
import requests

# Create workflow
workflow_data = {
    "name": "my_workflow",
    "title": "My Workflow",
    "steps": [...]
}

response = requests.post(
    "http://localhost:8181/api/workflows",
    json=workflow_data,
    headers={"Authorization": "Bearer your_token"}
)

workflow = response.json()["workflow"]

# Execute workflow
execution_data = {
    "workflow_template_id": workflow["id"],
    "triggered_by": "user_id",
    "input_parameters": {"param1": "value1"}
}

response = requests.post(
    f"http://localhost:8181/api/workflows/{workflow['id']}/execute",
    json=execution_data,
    headers={"Authorization": "Bearer your_token"}
)

execution_id = response.json()["execution_id"]

# Monitor execution
response = requests.get(
    f"http://localhost:8181/api/workflows/executions/{execution_id}",
    headers={"Authorization": "Bearer your_token"}
)

execution_status = response.json()["execution"]
print(f"Status: {execution_status['status']}")
print(f"Progress: {execution_status['progress_percentage']}%")
```

### JavaScript Example

```javascript
// Create workflow
const workflowData = {
  name: "my_workflow",
  title: "My Workflow",
  steps: [...]
};

const createResponse = await fetch('/api/workflows', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your_token'
  },
  body: JSON.stringify(workflowData)
});

const workflow = await createResponse.json();

// Execute workflow
const executionData = {
  workflow_template_id: workflow.workflow.id,
  triggered_by: "user_id",
  input_parameters: { param1: "value1" }
};

const executeResponse = await fetch(`/api/workflows/${workflow.workflow.id}/execute`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your_token'
  },
  body: JSON.stringify(executionData)
});

const execution = await executeResponse.json();
console.log(`Execution started: ${execution.execution_id}`);
```
