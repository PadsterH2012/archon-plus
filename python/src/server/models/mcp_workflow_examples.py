"""
MCP Tool Integration Workflow Examples

This module provides example workflows that demonstrate comprehensive
integration with Archon MCP tools, showcasing real-world use cases
for workflow automation with MCP tool execution.
"""

from typing import Dict, List
from .workflow_models import (
    WorkflowTemplate,
    ActionStep,
    ConditionStep,
    ParallelStep,
    LoopStep,
    WorkflowLinkStep,
    WorkflowStepType,
    WorkflowStatus
)


def create_project_research_workflow() -> WorkflowTemplate:
    """
    Workflow for comprehensive project research using MCP tools.
    
    This workflow demonstrates:
    - RAG queries for knowledge discovery
    - Code example searches
    - Project and task management integration
    - Document creation and version control
    """
    return WorkflowTemplate(
        name="project_research_workflow",
        title="Project Research and Documentation Workflow",
        description="Comprehensive research workflow using Archon MCP tools for project analysis and documentation",
        category="research",
        tags=["research", "mcp", "documentation", "rag"],
        parameters={
            "research_topic": {
                "type": "string",
                "required": True,
                "description": "Main topic to research"
            },
            "project_id": {
                "type": "string",
                "required": True,
                "description": "Project ID to associate research with"
            },
            "depth_level": {
                "type": "string",
                "required": False,
                "default": "comprehensive",
                "description": "Research depth: basic, comprehensive, or deep"
            }
        },
        outputs={
            "research_document_id": {
                "type": "string",
                "description": "ID of the created research document"
            },
            "task_count": {
                "type": "integer",
                "description": "Number of research tasks created"
            },
            "knowledge_sources": {
                "type": "array",
                "description": "List of knowledge sources found"
            }
        },
        steps=[
            ActionStep(
                name="get_available_sources",
                title="Get Available Knowledge Sources",
                type=WorkflowStepType.ACTION,
                tool_name="get_available_sources_archon",
                parameters={},
                description="Retrieve list of available knowledge sources for research"
            ),
            ActionStep(
                name="perform_initial_search",
                title="Perform Initial RAG Search",
                type=WorkflowStepType.ACTION,
                tool_name="perform_rag_query_archon",
                parameters={
                    "query": "{{workflow.parameters.research_topic}} overview architecture patterns",
                    "match_count": 10
                },
                description="Perform initial broad search for the research topic"
            ),
            ActionStep(
                name="search_code_examples",
                title="Search for Code Examples",
                type=WorkflowStepType.ACTION,
                tool_name="search_code_examples_archon",
                parameters={
                    "query": "{{workflow.parameters.research_topic}} implementation examples",
                    "match_count": 8
                },
                description="Find relevant code examples for the research topic"
            ),
            ConditionStep(
                name="check_depth_level",
                title="Check Research Depth Level",
                type=WorkflowStepType.CONDITION,
                condition="{{workflow.parameters.depth_level}} == 'deep'",
                on_success="deep_research",
                on_failure="create_research_tasks",
                description="Determine if deep research is needed"
            ),
            ParallelStep(
                name="deep_research",
                title="Deep Research Phase",
                type=WorkflowStepType.PARALLEL,
                wait_for_all=True,
                steps=[
                    ActionStep(
                        name="search_security_patterns",
                        title="Search Security Patterns",
                        type=WorkflowStepType.ACTION,
                        tool_name="perform_rag_query_archon",
                        parameters={
                            "query": "{{workflow.parameters.research_topic}} security best practices vulnerabilities",
                            "match_count": 5
                        }
                    ),
                    ActionStep(
                        name="search_performance_patterns",
                        title="Search Performance Patterns",
                        type=WorkflowStepType.ACTION,
                        tool_name="perform_rag_query_archon",
                        parameters={
                            "query": "{{workflow.parameters.research_topic}} performance optimization scalability",
                            "match_count": 5
                        }
                    ),
                    ActionStep(
                        name="search_testing_patterns",
                        title="Search Testing Patterns",
                        type=WorkflowStepType.ACTION,
                        tool_name="search_code_examples_archon",
                        parameters={
                            "query": "{{workflow.parameters.research_topic}} testing unit integration",
                            "match_count": 5
                        }
                    )
                ],
                description="Perform deep research in parallel across multiple domains"
            ),
            ActionStep(
                name="create_research_tasks",
                title="Create Research Tasks",
                type=WorkflowStepType.ACTION,
                tool_name="manage_task_archon",
                parameters={
                    "action": "create",
                    "project_id": "{{workflow.parameters.project_id}}",
                    "title": "Research Analysis - {{workflow.parameters.research_topic}}",
                    "description": "Analyze research findings and create implementation plan based on discovered patterns and examples",
                    "assignee": "AI IDE Agent",
                    "feature": "research",
                    "task_order": 10
                },
                description="Create a task to analyze research findings"
            ),
            ActionStep(
                name="create_research_document",
                title="Create Research Documentation",
                type=WorkflowStepType.ACTION,
                tool_name="manage_document_archon",
                parameters={
                    "action": "add",
                    "project_id": "{{workflow.parameters.project_id}}",
                    "document_type": "research",
                    "title": "Research Report: {{workflow.parameters.research_topic}}",
                    "content": {
                        "topic": "{{workflow.parameters.research_topic}}",
                        "depth_level": "{{workflow.parameters.depth_level}}",
                        "initial_search": "{{steps.perform_initial_search.result}}",
                        "code_examples": "{{steps.search_code_examples.result}}",
                        "deep_research": "{{steps.deep_research.result}}",
                        "available_sources": "{{steps.get_available_sources.result}}",
                        "generated_at": "{{workflow.execution.started_at}}"
                    },
                    "metadata": {
                        "tags": ["research", "{{workflow.parameters.research_topic}}"],
                        "status": "draft",
                        "author": "workflow_automation"
                    }
                },
                description="Create comprehensive research document with all findings"
            ),
            ActionStep(
                name="create_document_version",
                title="Create Document Version",
                type=WorkflowStepType.ACTION,
                tool_name="manage_versions_archon",
                parameters={
                    "action": "create",
                    "project_id": "{{workflow.parameters.project_id}}",
                    "field_name": "docs",
                    "content": "{{steps.create_research_document.result}}",
                    "change_summary": "Initial research report for {{workflow.parameters.research_topic}}",
                    "created_by": "workflow_automation"
                },
                description="Create version snapshot of research document"
            )
        ],
        timeout_minutes=60,
        max_retries=2,
        status=WorkflowStatus.ACTIVE,
        is_public=True
    )


def create_task_automation_workflow() -> WorkflowTemplate:
    """
    Workflow for automated task management and project coordination.
    
    This workflow demonstrates:
    - Task lifecycle management
    - Project feature integration
    - Conditional task creation
    - Progress tracking
    """
    return WorkflowTemplate(
        name="task_automation_workflow",
        title="Automated Task Management Workflow",
        description="Automate task creation, assignment, and tracking using Archon MCP tools",
        category="project_management",
        tags=["tasks", "automation", "project", "mcp"],
        parameters={
            "project_id": {
                "type": "string",
                "required": True,
                "description": "Project ID for task management"
            },
            "feature_name": {
                "type": "string",
                "required": True,
                "description": "Feature name for task grouping"
            },
            "task_templates": {
                "type": "array",
                "required": True,
                "description": "List of task templates to create"
            },
            "assignee": {
                "type": "string",
                "required": False,
                "default": "AI IDE Agent",
                "description": "Default assignee for created tasks"
            }
        },
        outputs={
            "created_tasks": {
                "type": "array",
                "description": "List of created task IDs"
            },
            "project_features": {
                "type": "array",
                "description": "Updated project features"
            }
        },
        steps=[
            ActionStep(
                name="get_project_features",
                title="Get Current Project Features",
                type=WorkflowStepType.ACTION,
                tool_name="get_project_features_archon",
                parameters={
                    "project_id": "{{workflow.parameters.project_id}}"
                },
                description="Retrieve current project features"
            ),
            ActionStep(
                name="list_existing_tasks",
                title="List Existing Tasks",
                type=WorkflowStepType.ACTION,
                tool_name="manage_task_archon",
                parameters={
                    "action": "list",
                    "project_id": "{{workflow.parameters.project_id}}",
                    "filter_by": "project",
                    "filter_value": "{{workflow.parameters.project_id}}",
                    "include_closed": False
                },
                description="Get list of existing tasks to avoid duplicates"
            ),
            LoopStep(
                name="create_tasks_loop",
                title="Create Tasks from Templates",
                type=WorkflowStepType.LOOP,
                collection="{{workflow.parameters.task_templates}}",
                item_variable="task_template",
                max_iterations=20,
                steps=[
                    ConditionStep(
                        name="check_task_exists",
                        title="Check if Task Already Exists",
                        type=WorkflowStepType.CONDITION,
                        condition="{{task_template.title}} not in {{steps.list_existing_tasks.result.parsed_result.tasks}}",
                        on_success="create_task",
                        on_failure="skip_task",
                        description="Check if task with same title already exists"
                    ),
                    ActionStep(
                        name="create_task",
                        title="Create New Task",
                        type=WorkflowStepType.ACTION,
                        tool_name="manage_task_archon",
                        parameters={
                            "action": "create",
                            "project_id": "{{workflow.parameters.project_id}}",
                            "title": "{{task_template.title}}",
                            "description": "{{task_template.description}}",
                            "assignee": "{{workflow.parameters.assignee}}",
                            "feature": "{{workflow.parameters.feature_name}}",
                            "task_order": "{{task_template.priority}}"
                        },
                        description="Create new task from template"
                    ),
                    ActionStep(
                        name="skip_task",
                        title="Skip Existing Task",
                        type=WorkflowStepType.ACTION,
                        tool_name="session_info_archon",
                        parameters={},
                        description="Log that task was skipped (using session_info as a no-op)"
                    )
                ],
                description="Iterate through task templates and create tasks"
            ),
            ActionStep(
                name="update_project_status",
                title="Update Project Status",
                type=WorkflowStepType.ACTION,
                tool_name="manage_task_archon",
                parameters={
                    "action": "create",
                    "project_id": "{{workflow.parameters.project_id}}",
                    "title": "Task Automation Completed",
                    "description": "Automated task creation workflow completed for feature: {{workflow.parameters.feature_name}}. Created {{steps.create_tasks_loop.iterations}} tasks.",
                    "assignee": "User",
                    "feature": "automation",
                    "task_order": 1
                },
                description="Create summary task for workflow completion"
            )
        ],
        timeout_minutes=30,
        max_retries=1,
        status=WorkflowStatus.ACTIVE,
        is_public=True
    )


def create_health_monitoring_workflow() -> WorkflowTemplate:
    """
    Workflow for system health monitoring and reporting.
    
    This workflow demonstrates:
    - System health checks
    - Session monitoring
    - Automated reporting
    - Error detection and alerting
    """
    return WorkflowTemplate(
        name="health_monitoring_workflow",
        title="System Health Monitoring Workflow",
        description="Monitor system health and generate reports using Archon MCP tools",
        category="monitoring",
        tags=["health", "monitoring", "system", "mcp"],
        parameters={
            "project_id": {
                "type": "string",
                "required": True,
                "description": "Project ID for health monitoring reports"
            },
            "check_interval": {
                "type": "integer",
                "required": False,
                "default": 5,
                "description": "Number of health checks to perform"
            }
        },
        outputs={
            "health_status": {
                "type": "object",
                "description": "Overall system health status"
            },
            "session_info": {
                "type": "object",
                "description": "Current session information"
            },
            "report_document_id": {
                "type": "string",
                "description": "ID of the generated health report"
            }
        },
        steps=[
            LoopStep(
                name="health_check_loop",
                title="Perform Health Checks",
                type=WorkflowStepType.LOOP,
                collection="[1, 2, 3, 4, 5]",  # Simple array for iteration count
                item_variable="check_number",
                max_iterations="{{workflow.parameters.check_interval}}",
                steps=[
                    ActionStep(
                        name="perform_health_check",
                        title="Perform System Health Check",
                        type=WorkflowStepType.ACTION,
                        tool_name="health_check_archon",
                        parameters={},
                        description="Check system health status"
                    ),
                    ActionStep(
                        name="get_session_info",
                        title="Get Session Information",
                        type=WorkflowStepType.ACTION,
                        tool_name="session_info_archon",
                        parameters={},
                        description="Retrieve current session information"
                    )
                ],
                description="Perform multiple health checks for reliability"
            ),
            ConditionStep(
                name="check_health_status",
                title="Evaluate Health Status",
                type=WorkflowStepType.CONDITION,
                condition="{{steps.health_check_loop.results}} contains 'healthy'",
                on_success="create_success_report",
                on_failure="create_alert_task",
                description="Evaluate overall health based on check results"
            ),
            ActionStep(
                name="create_success_report",
                title="Create Health Success Report",
                type=WorkflowStepType.ACTION,
                tool_name="manage_document_archon",
                parameters={
                    "action": "add",
                    "project_id": "{{workflow.parameters.project_id}}",
                    "document_type": "health_report",
                    "title": "System Health Report - {{workflow.execution.started_at}}",
                    "content": {
                        "status": "healthy",
                        "checks_performed": "{{workflow.parameters.check_interval}}",
                        "health_results": "{{steps.health_check_loop.results}}",
                        "session_info": "{{steps.health_check_loop.results}}",
                        "timestamp": "{{workflow.execution.started_at}}"
                    }
                },
                description="Create health report document for successful checks"
            ),
            ActionStep(
                name="create_alert_task",
                title="Create Health Alert Task",
                type=WorkflowStepType.ACTION,
                tool_name="manage_task_archon",
                parameters={
                    "action": "create",
                    "project_id": "{{workflow.parameters.project_id}}",
                    "title": "URGENT: System Health Alert",
                    "description": "System health checks failed. Immediate attention required. Check results: {{steps.health_check_loop.results}}",
                    "assignee": "User",
                    "feature": "monitoring",
                    "task_order": 100
                },
                description="Create urgent task for health check failures"
            )
        ],
        timeout_minutes=15,
        max_retries=1,
        status=WorkflowStatus.ACTIVE,
        is_public=True
    )


# Registry of MCP integration example workflows
MCP_EXAMPLE_WORKFLOWS = {
    "project_research_workflow": create_project_research_workflow(),
    "task_automation_workflow": create_task_automation_workflow(),
    "health_monitoring_workflow": create_health_monitoring_workflow()
}


def get_mcp_example_workflow(name: str) -> WorkflowTemplate:
    """Get a specific MCP example workflow by name"""
    if name not in MCP_EXAMPLE_WORKFLOWS:
        raise KeyError(f"MCP example workflow '{name}' not found")
    return MCP_EXAMPLE_WORKFLOWS[name]


def list_mcp_example_workflows() -> List[str]:
    """List all available MCP example workflow names"""
    return list(MCP_EXAMPLE_WORKFLOWS.keys())


def get_all_mcp_example_workflows() -> Dict[str, WorkflowTemplate]:
    """Get all MCP example workflows"""
    return MCP_EXAMPLE_WORKFLOWS.copy()
