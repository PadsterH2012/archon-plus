"""
Example Workflow Templates

This module provides example workflow templates demonstrating various
workflow patterns and use cases in the Archon system.
"""

from typing import Dict, Any, List
from .workflow_models import (
    WorkflowTemplate,
    ActionStep,
    ConditionStep,
    WorkflowLinkStep,
    ParallelStep,
    LoopStep,
    WorkflowStatus
)


def create_project_setup_workflow() -> WorkflowTemplate:
    """
    Example workflow for setting up a new project with documentation and tasks.
    
    This workflow demonstrates:
    - Sequential action steps
    - Parameter usage
    - Project and task management integration
    """
    steps = [
        ActionStep(
            name="create_project",
            title="Create New Project",
            description="Create a new project in Archon",
            tool_name="manage_project_archon",
            parameters={
                "action": "create",
                "title": "{{workflow.parameters.project_title}}",
                "description": "{{workflow.parameters.project_description}}",
                "github_repo": "{{workflow.parameters.github_repo}}"
            },
            on_success="create_initial_tasks",
            on_failure="fail"
        ),
        ActionStep(
            name="create_initial_tasks",
            title="Create Initial Tasks",
            description="Create initial project tasks",
            tool_name="manage_task_archon",
            parameters={
                "action": "create",
                "project_id": "{{steps.create_project.output.project.id}}",
                "title": "Project Setup",
                "description": "Initial project setup and configuration",
                "assignee": "{{workflow.parameters.assignee}}"
            },
            on_success="create_documentation",
            on_failure="fail"
        ),
        ActionStep(
            name="create_documentation",
            title="Create Project Documentation",
            description="Create initial project documentation",
            tool_name="manage_document_archon",
            parameters={
                "action": "add",
                "project_id": "{{steps.create_project.output.project.id}}",
                "document_type": "readme",
                "title": "Project README",
                "content": {
                    "title": "{{workflow.parameters.project_title}}",
                    "description": "{{workflow.parameters.project_description}}",
                    "setup_instructions": "Initial setup instructions will be added here."
                }
            },
            on_success="end",
            on_failure="fail"
        )
    ]
    
    return WorkflowTemplate(
        name="project_setup",
        title="Project Setup Workflow",
        description="Complete workflow for setting up a new project with initial tasks and documentation",
        category="project_management",
        tags=["setup", "project", "initialization"],
        parameters={
            "project_title": {
                "type": "string",
                "required": True,
                "description": "Title of the new project"
            },
            "project_description": {
                "type": "string",
                "required": True,
                "description": "Description of the project"
            },
            "github_repo": {
                "type": "string",
                "required": False,
                "description": "GitHub repository URL"
            },
            "assignee": {
                "type": "string",
                "required": False,
                "default": "User",
                "description": "Default assignee for initial tasks"
            }
        },
        outputs={
            "project_id": {
                "type": "string",
                "description": "ID of the created project"
            },
            "initial_task_id": {
                "type": "string", 
                "description": "ID of the initial task"
            }
        },
        steps=steps,
        timeout_minutes=30,
        status=WorkflowStatus.ACTIVE,
        is_public=True
    )


def create_knowledge_ingestion_workflow() -> WorkflowTemplate:
    """
    Example workflow for ingesting knowledge from multiple sources.
    
    This workflow demonstrates:
    - Parallel execution
    - Loop iteration
    - Knowledge base integration
    """
    steps = [
        LoopStep(
            name="process_sources",
            title="Process Knowledge Sources",
            description="Process each knowledge source in the list",
            collection="{{workflow.parameters.knowledge_sources}}",
            item_variable="source",
            steps=[
                ActionStep(
                    name="ingest_source",
                    title="Ingest Knowledge Source",
                    tool_name="perform_rag_query_archon",
                    parameters={
                        "query": "{{source.query}}",
                        "source": "{{source.source_id}}",
                        "match_count": 10
                    }
                )
            ],
            max_iterations=50,
            on_success="generate_summary",
            on_failure="fail"
        ),
        ActionStep(
            name="generate_summary",
            title="Generate Knowledge Summary",
            description="Generate a summary of ingested knowledge",
            tool_name="manage_document_archon",
            parameters={
                "action": "add",
                "project_id": "{{workflow.parameters.project_id}}",
                "document_type": "summary",
                "title": "Knowledge Ingestion Summary",
                "content": {
                    "sources_processed": "{{steps.process_sources.output.processed_count}}",
                    "summary": "Knowledge ingestion completed successfully"
                }
            },
            on_success="end",
            on_failure="fail"
        )
    ]
    
    return WorkflowTemplate(
        name="knowledge_ingestion",
        title="Knowledge Ingestion Workflow",
        description="Workflow for ingesting and processing knowledge from multiple sources",
        category="knowledge_management",
        tags=["knowledge", "ingestion", "rag"],
        parameters={
            "project_id": {
                "type": "string",
                "required": True,
                "description": "Project ID to associate knowledge with"
            },
            "knowledge_sources": {
                "type": "array",
                "required": True,
                "description": "List of knowledge sources to process"
            }
        },
        outputs={
            "summary_document_id": {
                "type": "string",
                "description": "ID of the generated summary document"
            },
            "sources_processed": {
                "type": "integer",
                "description": "Number of sources successfully processed"
            }
        },
        steps=steps,
        timeout_minutes=120,
        status=WorkflowStatus.ACTIVE,
        is_public=True
    )


def create_deployment_workflow() -> WorkflowTemplate:
    """
    Example workflow for application deployment with validation.
    
    This workflow demonstrates:
    - Conditional execution
    - Parallel validation steps
    - Error handling and rollback
    """
    steps = [
        ActionStep(
            name="pre_deployment_check",
            title="Pre-deployment Validation",
            description="Validate system readiness for deployment",
            tool_name="health_check_archon",
            parameters={},
            on_success="check_deployment_type",
            on_failure="fail"
        ),
        ConditionStep(
            name="check_deployment_type",
            title="Check Deployment Type",
            description="Determine deployment strategy based on environment",
            condition="{{workflow.parameters.environment}} == 'production'",
            on_true="production_deployment",
            on_false="development_deployment"
        ),
        ParallelStep(
            name="production_deployment",
            title="Production Deployment",
            description="Execute production deployment with validation",
            steps=[
                ActionStep(
                    name="backup_database",
                    title="Backup Database",
                    tool_name="manage_task_archon",
                    parameters={
                        "action": "create",
                        "project_id": "{{workflow.parameters.project_id}}",
                        "title": "Database Backup",
                        "description": "Create database backup before deployment"
                    }
                ),
                ActionStep(
                    name="validate_configuration",
                    title="Validate Configuration",
                    tool_name="manage_task_archon",
                    parameters={
                        "action": "create",
                        "project_id": "{{workflow.parameters.project_id}}",
                        "title": "Configuration Validation",
                        "description": "Validate deployment configuration"
                    }
                )
            ],
            wait_for_all=True,
            on_success="deploy_application",
            on_failure="rollback_deployment"
        ),
        ActionStep(
            name="development_deployment",
            title="Development Deployment",
            description="Execute development deployment",
            tool_name="manage_task_archon",
            parameters={
                "action": "create",
                "project_id": "{{workflow.parameters.project_id}}",
                "title": "Development Deployment",
                "description": "Deploy to development environment"
            },
            on_success="deploy_application",
            on_failure="fail"
        ),
        ActionStep(
            name="deploy_application",
            title="Deploy Application",
            description="Deploy the application to target environment",
            tool_name="manage_task_archon",
            parameters={
                "action": "create",
                "project_id": "{{workflow.parameters.project_id}}",
                "title": "Application Deployment",
                "description": "Deploy application version {{workflow.parameters.version}} to {{workflow.parameters.environment}}"
            },
            on_success="post_deployment_validation",
            on_failure="rollback_deployment"
        ),
        ActionStep(
            name="post_deployment_validation",
            title="Post-deployment Validation",
            description="Validate deployment success",
            tool_name="health_check_archon",
            parameters={},
            on_success="end",
            on_failure="rollback_deployment"
        ),
        ActionStep(
            name="rollback_deployment",
            title="Rollback Deployment",
            description="Rollback deployment due to failure",
            tool_name="manage_task_archon",
            parameters={
                "action": "create",
                "project_id": "{{workflow.parameters.project_id}}",
                "title": "Deployment Rollback",
                "description": "Rollback failed deployment"
            },
            on_success="fail",
            on_failure="fail"
        )
    ]
    
    return WorkflowTemplate(
        name="application_deployment",
        title="Application Deployment Workflow",
        description="Comprehensive workflow for deploying applications with validation and rollback",
        category="deployment",
        tags=["deployment", "validation", "rollback"],
        parameters={
            "project_id": {
                "type": "string",
                "required": True,
                "description": "Project ID for deployment tracking"
            },
            "environment": {
                "type": "string",
                "required": True,
                "enum": ["development", "staging", "production"],
                "description": "Target deployment environment"
            },
            "version": {
                "type": "string",
                "required": True,
                "description": "Application version to deploy"
            }
        },
        outputs={
            "deployment_status": {
                "type": "string",
                "description": "Final deployment status"
            },
            "deployment_tasks": {
                "type": "array",
                "description": "List of created deployment tasks"
            }
        },
        steps=steps,
        timeout_minutes=60,
        max_retries=2,
        status=WorkflowStatus.ACTIVE,
        is_public=True
    )


def create_sub_workflow_example() -> WorkflowTemplate:
    """
    Example workflow that demonstrates sub-workflow execution.
    
    This workflow demonstrates:
    - Workflow linking
    - Sub-workflow parameter passing
    - Modular workflow design
    """
    steps = [
        ActionStep(
            name="prepare_environment",
            title="Prepare Environment",
            description="Prepare the environment for sub-workflow execution",
            tool_name="manage_project_archon",
            parameters={
                "action": "get",
                "project_id": "{{workflow.parameters.project_id}}"
            },
            on_success="execute_setup_workflow",
            on_failure="fail"
        ),
        WorkflowLinkStep(
            name="execute_setup_workflow",
            title="Execute Project Setup",
            description="Execute the project setup sub-workflow",
            workflow_name="project_setup",
            parameters={
                "project_title": "{{workflow.parameters.sub_project_title}}",
                "project_description": "Sub-project created by workflow orchestration",
                "assignee": "{{workflow.parameters.assignee}}"
            },
            on_success="execute_knowledge_workflow",
            on_failure="fail"
        ),
        WorkflowLinkStep(
            name="execute_knowledge_workflow",
            title="Execute Knowledge Ingestion",
            description="Execute knowledge ingestion for the new project",
            workflow_name="knowledge_ingestion",
            parameters={
                "project_id": "{{steps.execute_setup_workflow.output.project_id}}",
                "knowledge_sources": "{{workflow.parameters.knowledge_sources}}"
            },
            on_success="finalize_orchestration",
            on_failure="fail"
        ),
        ActionStep(
            name="finalize_orchestration",
            title="Finalize Orchestration",
            description="Complete the workflow orchestration",
            tool_name="manage_document_archon",
            parameters={
                "action": "add",
                "project_id": "{{workflow.parameters.project_id}}",
                "document_type": "report",
                "title": "Workflow Orchestration Report",
                "content": {
                    "orchestration_completed": True,
                    "sub_project_id": "{{steps.execute_setup_workflow.output.project_id}}",
                    "knowledge_summary_id": "{{steps.execute_knowledge_workflow.output.summary_document_id}}"
                }
            },
            on_success="end",
            on_failure="fail"
        )
    ]
    
    return WorkflowTemplate(
        name="workflow_orchestration",
        title="Workflow Orchestration Example",
        description="Example of orchestrating multiple sub-workflows",
        category="orchestration",
        tags=["orchestration", "sub-workflows", "automation"],
        parameters={
            "project_id": {
                "type": "string",
                "required": True,
                "description": "Main project ID"
            },
            "sub_project_title": {
                "type": "string",
                "required": True,
                "description": "Title for the sub-project"
            },
            "assignee": {
                "type": "string",
                "required": False,
                "default": "User",
                "description": "Default assignee"
            },
            "knowledge_sources": {
                "type": "array",
                "required": True,
                "description": "Knowledge sources for ingestion"
            }
        },
        outputs={
            "orchestration_report_id": {
                "type": "string",
                "description": "ID of the orchestration report document"
            },
            "sub_project_id": {
                "type": "string",
                "description": "ID of the created sub-project"
            }
        },
        steps=steps,
        timeout_minutes=180,
        status=WorkflowStatus.ACTIVE,
        is_public=True
    )


# Registry of example workflows
EXAMPLE_WORKFLOWS: Dict[str, WorkflowTemplate] = {
    "project_setup": create_project_setup_workflow(),
    "knowledge_ingestion": create_knowledge_ingestion_workflow(),
    "application_deployment": create_deployment_workflow(),
    "workflow_orchestration": create_sub_workflow_example()
}


def get_example_workflow(name: str) -> WorkflowTemplate:
    """
    Get an example workflow by name.
    
    Args:
        name: Name of the example workflow
        
    Returns:
        WorkflowTemplate instance
        
    Raises:
        KeyError: If workflow name is not found
    """
    if name not in EXAMPLE_WORKFLOWS:
        available = ", ".join(EXAMPLE_WORKFLOWS.keys())
        raise KeyError(f"Unknown example workflow '{name}'. Available: {available}")
    
    return EXAMPLE_WORKFLOWS[name]


def list_example_workflows() -> List[str]:
    """
    List all available example workflow names.
    
    Returns:
        List of workflow names
    """
    return list(EXAMPLE_WORKFLOWS.keys())
