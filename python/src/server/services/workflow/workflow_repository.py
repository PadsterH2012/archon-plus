"""
Workflow Repository Service

This module provides data access layer for workflow operations including:
- CRUD operations for workflow templates
- Workflow search and filtering
- Version management
- Database transaction handling
- Error handling and logging

Follows Archon service patterns for consistency.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from ...models.workflow_models import (
    WorkflowTemplate,
    WorkflowExecution,
    WorkflowStepExecution,
    WorkflowTemplateVersion,
    WorkflowStatus,
    WorkflowExecutionStatus,
    StepExecutionStatus,
    parse_workflow_step,
    validate_workflow_template_data
)
from ...utils import get_supabase_client

logger = logging.getLogger(__name__)


class WorkflowRepository:
    """Repository for workflow data operations"""

    def __init__(self, supabase_client=None):
        """Initialize with optional supabase client"""
        self.supabase_client = supabase_client or get_supabase_client()

    # =====================================================
    # WORKFLOW TEMPLATE OPERATIONS
    # =====================================================

    async def create_workflow_template(self, template_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a new workflow template.

        Args:
            template_data: Workflow template data

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Validate template data
            template = validate_workflow_template_data(template_data)

            # Prepare data for database
            db_data = {
                "name": template.name,
                "title": template.title,
                "description": template.description,
                "version": template.version,
                "status": template.status.value,
                "category": template.category,
                "tags": template.tags,
                "parameters": template.parameters,
                "outputs": template.outputs,
                "steps": [step.dict() for step in template.steps],
                "timeout_minutes": template.timeout_minutes,
                "max_retries": template.max_retries,
                "retry_delay_seconds": template.retry_delay_seconds,
                "created_by": template.created_by,
                "is_public": template.is_public,
                "allowed_assignees": template.allowed_assignees
            }

            # Insert into database
            response = self.supabase_client.table("archon_workflow_templates").insert(db_data).execute()

            if not response.data:
                logger.error("Supabase returned empty data for workflow template creation")
                return False, {"error": "Failed to create workflow template - database returned no data"}

            template_record = response.data[0]
            template_id = template_record["id"]
            logger.info(f"Workflow template created successfully with ID: {template_id}")

            # Create initial version
            await self._create_template_version(
                template_id=template_id,
                template_data=template_record,
                version_tag=template.version,
                change_summary="Initial template creation",
                change_type="create",
                created_by=template.created_by
            )

            return True, {
                "template": self._format_template_response(template_record)
            }

        except Exception as e:
            logger.error(f"Error creating workflow template: {e}")
            return False, {"error": f"Error creating workflow template: {str(e)}"}

    def list_workflow_templates(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        created_by: Optional[str] = None,
        is_public: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        List workflow templates with filtering.

        Args:
            status: Filter by workflow status
            category: Filter by category
            created_by: Filter by creator
            is_public: Filter by public/private
            search: Search in name, title, description
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Start with base query
            query = self.supabase_client.table("archon_workflow_templates").select("*")

            # Apply filters
            filters_applied = []

            if status:
                query = query.eq("status", status)
                filters_applied.append(f"status={status}")

            if category:
                query = query.eq("category", category)
                filters_applied.append(f"category={category}")

            if created_by:
                query = query.eq("created_by", created_by)
                filters_applied.append(f"created_by={created_by}")

            if is_public is not None:
                query = query.eq("is_public", is_public)
                filters_applied.append(f"is_public={is_public}")

            if search:
                search_pattern = f"%{search}%"
                query = query.or_(
                    f"name.ilike.{search_pattern},title.ilike.{search_pattern},description.ilike.{search_pattern}"
                )
                filters_applied.append(f"search={search}")

            # Apply pagination and ordering
            query = query.order("created_at", desc=True).range(offset, offset + limit - 1)

            logger.info(f"Listing workflow templates with filters: {', '.join(filters_applied) if filters_applied else 'none'}")

            response = query.execute()

            templates = [self._format_template_response(template) for template in response.data]

            return True, {
                "templates": templates,
                "count": len(templates),
                "limit": limit,
                "offset": offset
            }

        except Exception as e:
            logger.error(f"Error listing workflow templates: {e}")
            return False, {"error": f"Error listing workflow templates: {str(e)}"}

    def get_workflow_template(self, template_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Get a specific workflow template by ID.

        Args:
            template_id: Template UUID

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            response = (
                self.supabase_client.table("archon_workflow_templates")
                .select("*")
                .eq("id", template_id)
                .execute()
            )

            if response.data:
                template = response.data[0]
                return True, {"template": self._format_template_response(template)}
            else:
                return False, {"error": f"Workflow template with ID {template_id} not found"}

        except Exception as e:
            logger.error(f"Error getting workflow template: {e}")
            return False, {"error": f"Error getting workflow template: {str(e)}"}

    async def update_workflow_template(
        self,
        template_id: str,
        update_data: Dict[str, Any],
        updated_by: str = "system"
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Update a workflow template.

        Args:
            template_id: Template UUID
            update_data: Fields to update
            updated_by: Who is making the update

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Get current template for versioning
            current_success, current_result = self.get_workflow_template(template_id)
            if not current_success:
                return current_success, current_result

            current_template = current_result["template"]

            # Prepare update data
            db_update = {}

            # Handle step updates with validation
            if "steps" in update_data:
                # Validate steps
                validated_steps = []
                for step_data in update_data["steps"]:
                    if isinstance(step_data, dict):
                        validated_step = parse_workflow_step(step_data)
                        validated_steps.append(validated_step.dict())
                    else:
                        validated_steps.append(step_data)
                db_update["steps"] = validated_steps

            # Copy other allowed fields
            allowed_fields = [
                "title", "description", "category", "tags", "parameters", "outputs",
                "timeout_minutes", "max_retries", "retry_delay_seconds", "status",
                "is_public", "allowed_assignees"
            ]

            for field in allowed_fields:
                if field in update_data:
                    if field == "status" and isinstance(update_data[field], WorkflowStatus):
                        db_update[field] = update_data[field].value
                    else:
                        db_update[field] = update_data[field]

            # Add update timestamp
            db_update["updated_at"] = datetime.now().isoformat()

            # Update in database
            response = (
                self.supabase_client.table("archon_workflow_templates")
                .update(db_update)
                .eq("id", template_id)
                .execute()
            )

            if response.data:
                updated_template = response.data[0]

                # Create version if significant changes
                if self._should_create_version(current_template, updated_template):
                    await self._create_template_version(
                        template_id=template_id,
                        template_data=updated_template,
                        version_tag=updated_template.get("version", "1.0.0"),
                        change_summary="Template updated",
                        change_type="update",
                        created_by=updated_by
                    )

                logger.info(f"Workflow template {template_id} updated successfully")
                return True, {"template": self._format_template_response(updated_template)}
            else:
                return False, {"error": "Failed to update workflow template"}

        except Exception as e:
            logger.error(f"Error updating workflow template: {e}")
            return False, {"error": f"Error updating workflow template: {str(e)}"}

    def delete_workflow_template(self, template_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Delete a workflow template.

        Args:
            template_id: Template UUID

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Check if template exists
            success, result = self.get_workflow_template(template_id)
            if not success:
                return success, result

            # Delete template (cascade will handle versions and executions)
            response = (
                self.supabase_client.table("archon_workflow_templates")
                .delete()
                .eq("id", template_id)
                .execute()
            )

            if response.data:
                logger.info(f"Workflow template {template_id} deleted successfully")
                return True, {"message": "Workflow template deleted successfully"}
            else:
                return False, {"error": "Failed to delete workflow template"}

        except Exception as e:
            logger.error(f"Error deleting workflow template: {e}")
            return False, {"error": f"Error deleting workflow template: {str(e)}"}

    # =====================================================
    # WORKFLOW EXECUTION OPERATIONS
    # =====================================================

    async def create_workflow_execution(self, execution_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a new workflow execution.

        Args:
            execution_data: Execution data

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Prepare data for database
            db_data = {
                "workflow_template_id": execution_data["workflow_template_id"],
                "triggered_by": execution_data["triggered_by"],
                "trigger_context": execution_data.get("trigger_context", {}),
                "input_parameters": execution_data.get("input_parameters", {}),
                "execution_context": execution_data.get("execution_context", {}),
                "status": execution_data.get("status", WorkflowExecutionStatus.PENDING.value),
                "total_steps": execution_data.get("total_steps", 0),
                "execution_log": []
            }

            # Insert into database
            response = self.supabase_client.table("archon_workflow_executions").insert(db_data).execute()

            if not response.data:
                logger.error("Supabase returned empty data for workflow execution creation")
                return False, {"error": "Failed to create workflow execution - database returned no data"}

            execution = response.data[0]
            execution_id = execution["id"]
            logger.info(f"Workflow execution created successfully with ID: {execution_id}")

            return True, {
                "execution": self._format_execution_response(execution)
            }

        except Exception as e:
            logger.error(f"Error creating workflow execution: {e}")
            return False, {"error": f"Error creating workflow execution: {str(e)}"}

    def list_workflow_executions(
        self,
        workflow_template_id: Optional[str] = None,
        status: Optional[str] = None,
        triggered_by: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        List workflow executions with filtering.

        Args:
            workflow_template_id: Filter by template ID
            status: Filter by execution status
            triggered_by: Filter by who triggered the execution
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Start with base query
            query = self.supabase_client.table("archon_workflow_executions").select("*")

            # Apply filters
            filters_applied = []

            if workflow_template_id:
                query = query.eq("workflow_template_id", workflow_template_id)
                filters_applied.append(f"template_id={workflow_template_id}")

            if status:
                query = query.eq("status", status)
                filters_applied.append(f"status={status}")

            if triggered_by:
                query = query.eq("triggered_by", triggered_by)
                filters_applied.append(f"triggered_by={triggered_by}")

            # Apply pagination and ordering
            query = query.order("created_at", desc=True).range(offset, offset + limit - 1)

            filters_str = ', '.join(filters_applied) if filters_applied else 'none'
            logger.info(f"Listing workflow executions with filters: {filters_str}")

            response = query.execute()

            executions = [self._format_execution_response(execution) for execution in response.data]

            return True, {
                "executions": executions,
                "count": len(executions),
                "limit": limit,
                "offset": offset
            }

        except Exception as e:
            logger.error(f"Error listing workflow executions: {e}")
            return False, {"error": f"Error listing workflow executions: {str(e)}"}

    def get_workflow_execution(self, execution_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Get a specific workflow execution by ID.

        Args:
            execution_id: Execution UUID

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            response = (
                self.supabase_client.table("archon_workflow_executions")
                .select("*")
                .eq("id", execution_id)
                .execute()
            )

            if response.data:
                execution = response.data[0]
                return True, {"execution": self._format_execution_response(execution)}
            else:
                return False, {"error": f"Workflow execution with ID {execution_id} not found"}

        except Exception as e:
            logger.error(f"Error getting workflow execution: {e}")
            return False, {"error": f"Error getting workflow execution: {str(e)}"}

    async def update_workflow_execution(
        self,
        execution_id: str,
        update_data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Update a workflow execution.

        Args:
            execution_id: Execution UUID
            update_data: Fields to update

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Prepare update data
            db_update = {}

            # Copy allowed fields
            allowed_fields = [
                "status", "current_step_index", "progress_percentage", "started_at",
                "completed_at", "paused_at", "output_data", "error_message",
                "error_details", "execution_context", "execution_log"
            ]

            for field in allowed_fields:
                if field in update_data:
                    if field == "status" and isinstance(update_data[field], WorkflowExecutionStatus):
                        db_update[field] = update_data[field].value
                    else:
                        db_update[field] = update_data[field]

            # Add update timestamp
            db_update["updated_at"] = datetime.now().isoformat()

            # Update in database
            response = (
                self.supabase_client.table("archon_workflow_executions")
                .update(db_update)
                .eq("id", execution_id)
                .execute()
            )

            if response.data:
                updated_execution = response.data[0]
                logger.info(f"Workflow execution {execution_id} updated successfully")
                return True, {"execution": self._format_execution_response(updated_execution)}
            else:
                return False, {"error": "Failed to update workflow execution"}

        except Exception as e:
            logger.error(f"Error updating workflow execution: {e}")
            return False, {"error": f"Error updating workflow execution: {str(e)}"}

    # =====================================================
    # WORKFLOW STEP EXECUTION OPERATIONS
    # =====================================================

    async def create_step_execution(self, step_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a new step execution.

        Args:
            step_data: Step execution data

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Prepare data for database
            db_data = {
                "workflow_execution_id": step_data["workflow_execution_id"],
                "step_index": step_data["step_index"],
                "step_name": step_data["step_name"],
                "step_type": step_data["step_type"],
                "step_config": step_data.get("step_config", {}),
                "status": step_data.get("status", StepExecutionStatus.PENDING.value),
                "max_attempts": step_data.get("max_attempts", 1),
                "input_data": step_data.get("input_data", {}),
                "tool_name": step_data.get("tool_name"),
                "tool_parameters": step_data.get("tool_parameters", {}),
                "sub_workflow_execution_id": step_data.get("sub_workflow_execution_id")
            }

            # Insert into database
            response = (
                self.supabase_client.table("archon_workflow_step_executions")
                .insert(db_data)
                .execute()
            )

            if not response.data:
                logger.error("Supabase returned empty data for step execution creation")
                error_msg = "Failed to create step execution - database returned no data"
                return False, {"error": error_msg}

            step_execution = response.data[0]
            step_execution_id = step_execution["id"]
            logger.info(f"Step execution created successfully with ID: {step_execution_id}")

            return True, {
                "step_execution": self._format_step_execution_response(step_execution)
            }

        except Exception as e:
            logger.error(f"Error creating step execution: {e}")
            return False, {"error": f"Error creating step execution: {str(e)}"}

    def list_step_executions(
        self,
        workflow_execution_id: str,
        status: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        List step executions for a workflow execution.

        Args:
            workflow_execution_id: Parent execution UUID
            status: Filter by step status

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Start with base query
            query = (
                self.supabase_client.table("archon_workflow_step_executions")
                .select("*")
                .eq("workflow_execution_id", workflow_execution_id)
            )

            # Apply status filter if provided
            if status:
                query = query.eq("status", status)

            # Order by step index
            query = query.order("step_index")

            response = query.execute()

            step_executions = [self._format_step_execution_response(step) for step in response.data]

            return True, {
                "step_executions": step_executions,
                "count": len(step_executions)
            }

        except Exception as e:
            logger.error(f"Error listing step executions: {e}")
            return False, {"error": f"Error listing step executions: {str(e)}"}

    async def update_step_execution(
        self,
        step_execution_id: str,
        update_data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Update a step execution.

        Args:
            step_execution_id: Step execution UUID
            update_data: Fields to update

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Prepare update data
            db_update = {}

            # Copy allowed fields
            allowed_fields = [
                "status", "attempt_number", "started_at", "completed_at", "input_data",
                "output_data", "error_message", "error_details", "tool_result"
            ]

            for field in allowed_fields:
                if field in update_data:
                    if field == "status" and isinstance(update_data[field], StepExecutionStatus):
                        db_update[field] = update_data[field].value
                    else:
                        db_update[field] = update_data[field]

            # Add update timestamp
            db_update["updated_at"] = datetime.now().isoformat()

            # Update in database
            response = (
                self.supabase_client.table("archon_workflow_step_executions")
                .update(db_update)
                .eq("id", step_execution_id)
                .execute()
            )

            if response.data:
                updated_step = response.data[0]
                logger.info(f"Step execution {step_execution_id} updated successfully")
                return True, {"step_execution": self._format_step_execution_response(updated_step)}
            else:
                return False, {"error": "Failed to update step execution"}

        except Exception as e:
            logger.error(f"Error updating step execution: {e}")
            return False, {"error": f"Error updating step execution: {str(e)}"}

    # =====================================================
    # HELPER METHODS
    # =====================================================

    def _format_template_response(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Format template data for API response"""
        return {
            "id": template["id"],
            "name": template["name"],
            "title": template["title"],
            "description": template["description"],
            "version": template["version"],
            "status": template["status"],
            "category": template.get("category"),
            "tags": template.get("tags", []),
            "parameters": template.get("parameters", {}),
            "outputs": template.get("outputs", {}),
            "steps": template.get("steps", []),
            "timeout_minutes": template["timeout_minutes"],
            "max_retries": template["max_retries"],
            "retry_delay_seconds": template.get("retry_delay_seconds", 30),
            "created_by": template["created_by"],
            "is_public": template["is_public"],
            "allowed_assignees": template.get("allowed_assignees", []),
            "created_at": template["created_at"],
            "updated_at": template["updated_at"]
        }

    def _format_execution_response(self, execution: Dict[str, Any]) -> Dict[str, Any]:
        """Format execution data for API response"""
        return {
            "id": execution["id"],
            "workflow_template_id": execution["workflow_template_id"],
            "triggered_by": execution["triggered_by"],
            "trigger_context": execution.get("trigger_context", {}),
            "input_parameters": execution.get("input_parameters", {}),
            "execution_context": execution.get("execution_context", {}),
            "status": execution["status"],
            "current_step_index": execution["current_step_index"],
            "total_steps": execution["total_steps"],
            "progress_percentage": execution["progress_percentage"],
            "started_at": execution.get("started_at"),
            "completed_at": execution.get("completed_at"),
            "paused_at": execution.get("paused_at"),
            "output_data": execution.get("output_data", {}),
            "error_message": execution.get("error_message"),
            "error_details": execution.get("error_details", {}),
            "execution_log": execution.get("execution_log", []),
            "created_at": execution["created_at"],
            "updated_at": execution["updated_at"]
        }

    async def _create_template_version(
        self,
        template_id: str,
        template_data: Dict[str, Any],
        version_tag: str,
        change_summary: str,
        change_type: str = "update",
        created_by: str = "system"
    ) -> bool:
        """Create a version record for a template"""
        try:
            # Get next version number
            version_response = (
                self.supabase_client.table("archon_workflow_template_versions")
                .select("version_number")
                .eq("workflow_template_id", template_id)
                .order("version_number", desc=True)
                .limit(1)
                .execute()
            )

            next_version_number = 1
            if version_response.data:
                next_version_number = version_response.data[0]["version_number"] + 1

            # Create version record
            version_data = {
                "workflow_template_id": template_id,
                "version_number": next_version_number,
                "version_tag": version_tag,
                "template_snapshot": template_data,
                "change_summary": change_summary,
                "change_type": change_type,
                "created_by": created_by
            }

            response = self.supabase_client.table("archon_workflow_template_versions").insert(version_data).execute()

            if response.data:
                logger.info(f"Created version {next_version_number} for template {template_id}")
                return True
            else:
                logger.error(f"Failed to create version for template {template_id}")
                return False

        except Exception as e:
            logger.error(f"Error creating template version: {e}")
            return False

    def _should_create_version(self, old_template: Dict[str, Any], new_template: Dict[str, Any]) -> bool:
        """Determine if changes warrant a new version"""
        # Create version for significant changes
        significant_fields = ["steps", "parameters", "outputs", "status"]

        for field in significant_fields:
            if old_template.get(field) != new_template.get(field):
                return True

        return False

    def _format_step_execution_response(self, step_execution: Dict[str, Any]) -> Dict[str, Any]:
        """Format step execution data for API response"""
        return {
            "id": step_execution["id"],
            "workflow_execution_id": step_execution["workflow_execution_id"],
            "step_index": step_execution["step_index"],
            "step_name": step_execution["step_name"],
            "step_type": step_execution["step_type"],
            "step_config": step_execution.get("step_config", {}),
            "status": step_execution["status"],
            "attempt_number": step_execution["attempt_number"],
            "max_attempts": step_execution["max_attempts"],
            "started_at": step_execution.get("started_at"),
            "completed_at": step_execution.get("completed_at"),
            "input_data": step_execution.get("input_data", {}),
            "output_data": step_execution.get("output_data", {}),
            "error_message": step_execution.get("error_message"),
            "error_details": step_execution.get("error_details", {}),
            "tool_name": step_execution.get("tool_name"),
            "tool_parameters": step_execution.get("tool_parameters", {}),
            "tool_result": step_execution.get("tool_result", {}),
            "sub_workflow_execution_id": step_execution.get("sub_workflow_execution_id"),
            "created_at": step_execution["created_at"],
            "updated_at": step_execution["updated_at"]
        }
