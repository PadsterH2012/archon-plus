"""
Template Service

Manages template inheritance resolution, conflict detection, and application logic.
Provides high-performance template management with caching and inheritance chain resolution.
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any
from uuid import UUID

try:
    from supabase import Client
except ImportError:
    # For testing environments where supabase might not be available
    Client = None

from ..config.logfire_config import get_logger
from ..models.template_models import (
    TemplateDefinition,
    TemplateApplication,
    TemplateType,
    TemplateStatus,
    CreateTemplateDefinitionRequest,
    UpdateTemplateDefinitionRequest,
    ApplyTemplateRequest,
    TemplateDefinitionResponse,
    TemplateApplicationResponse,
    validate_template_inheritance_chain,
    resolve_template_inheritance,
)
from ..services.client_manager import get_supabase_client
from ..services.threading_service import get_threading_service

logger = get_logger(__name__)


class TemplateServiceError(Exception):
    """Base exception for template service errors"""


class CircularInheritanceError(TemplateServiceError):
    """Raised when a circular inheritance is detected"""


class TemplateNotFoundError(TemplateServiceError):
    """Raised when a template is not found"""


class InheritanceValidationError(TemplateServiceError):
    """Raised when inheritance validation fails"""


class TemplateApplicationError(TemplateServiceError):
    """Raised when template application fails"""


class TemplateService:
    """
    High-performance template management service with inheritance resolution and caching.
    
    Features:
    - Template inheritance chain resolution (3 levels)
    - Conflict detection and resolution logic
    - Template application to components
    - Performance optimization (<50ms resolution)
    - Template customization tracking
    - Comprehensive caching (1 hour TTL)
    """

    def __init__(self, supabase_client: Optional[Client] = None):
        """
        Initialize TemplateService with optional Supabase client.
        
        Args:
            supabase_client: Optional Supabase client instance
        """
        self.supabase = supabase_client or get_supabase_client()
        self.threading_service = get_threading_service()

        # Template resolution cache with 1-hour TTL
        self._resolution_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
        self._cache_ttl = 3600  # 1 hour in seconds

        # Template cache for frequently accessed templates
        self._template_cache: Dict[UUID, Tuple[TemplateDefinition, float]] = {}
        self._template_cache_ttl = 1800  # 30 minutes for template cache

        # Inheritance chain cache
        self._inheritance_cache: Dict[UUID, Tuple[List[TemplateDefinition], float]] = {}
        self._inheritance_cache_ttl = 3600  # 1 hour for inheritance chains

        logger.info("TemplateService initialized with caching enabled")

    async def create_template(self, request: CreateTemplateDefinitionRequest) -> TemplateDefinitionResponse:
        """
        Create a new template with inheritance validation.
        
        Args:
            request: Template creation request
            
        Returns:
            TemplateDefinitionResponse with created template or error
        """
        start_time = time.time()

        try:
            # Validate parent template exists if specified
            if request.parent_template_id:
                parent_response = await self.get_template(request.parent_template_id)
                if not parent_response.success:
                    raise InheritanceValidationError(f"Parent template {request.parent_template_id} not found")

                # Check for circular inheritance
                would_create_cycle = await self._would_create_circular_inheritance(
                    None, request.parent_template_id
                )
                if would_create_cycle:
                    raise CircularInheritanceError(
                        f"Template '{request.name}' would create circular inheritance"
                    )

            # Create template data
            template_data = {
                "name": request.name,
                "title": request.title,
                "description": request.description,
                "template_type": request.template_type.value,
                "parent_template_id": str(request.parent_template_id) if request.parent_template_id else None,
                "workflow_assignments": request.workflow_assignments,
                "component_templates": request.component_templates,
                "inheritance_rules": request.inheritance_rules,
                "is_public": request.is_public,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Insert template
            result = await self._execute_db_operation(
                lambda: self.supabase.table("archon_template_definitions").insert(template_data).execute()
            )

            if not result.data:
                raise TemplateServiceError("Failed to create template")

            template = TemplateDefinition(**result.data[0])

            # Invalidate caches
            self._invalidate_all_caches()

            duration = time.time() - start_time
            logger.info(
                "Template created successfully",
                template_id=str(template.id),
                template_name=template.name,
                duration_ms=round(duration * 1000, 2)
            )

            return TemplateDefinitionResponse(
                success=True,
                template=template,
                message=f"Template '{template.name}' created successfully"
            )

        except (CircularInheritanceError, InheritanceValidationError) as e:
            logger.warning("Template creation validation failed: %s", e)
            return TemplateDefinitionResponse(
                success=False,
                message="Template creation failed",
                error=str(e)
            )
        except Exception as e:
            logger.error("Unexpected error creating template: %s", e)
            return TemplateDefinitionResponse(
                success=False,
                message="Template creation failed",
                error=f"Unexpected error: {str(e)}"
            )

    async def get_template(self, template_id: UUID) -> TemplateDefinitionResponse:
        """
        Get a template by ID with caching.
        
        Args:
            template_id: Template UUID
            
        Returns:
            TemplateDefinitionResponse with template or error
        """
        start_time = time.time()

        try:
            # Check cache first
            cached_template = self._get_cached_template(template_id)
            if cached_template:
                duration = time.time() - start_time
                logger.debug(
                    "Template retrieved from cache",
                    template_id=str(template_id),
                    duration_ms=round(duration * 1000, 2)
                )
                return TemplateDefinitionResponse(
                    success=True,
                    template=cached_template,
                    message="Template retrieved successfully"
                )

            # Fetch from database
            result = await self._execute_db_operation(
                lambda: self.supabase.table("archon_template_definitions")
                .select("*")
                .eq("id", str(template_id))
                .execute()
            )

            if not result.data:
                raise TemplateNotFoundError(f"Template {template_id} not found")

            template = TemplateDefinition(**result.data[0])

            # Cache the template
            self._cache_template(template)

            duration = time.time() - start_time
            logger.info(
                "Template retrieved successfully",
                template_id=str(template_id),
                duration_ms=round(duration * 1000, 2)
            )

            return TemplateDefinitionResponse(
                success=True,
                template=template,
                message="Template retrieved successfully"
            )

        except TemplateNotFoundError as e:
            logger.warning("Template not found: %s", e)
            return TemplateDefinitionResponse(
                success=False,
                message="Template not found",
                error=str(e)
            )
        except Exception as e:
            logger.error("Unexpected error retrieving template: %s", e)
            return TemplateDefinitionResponse(
                success=False,
                message="Template retrieval failed",
                error=f"Unexpected error: {str(e)}"
            )

    async def get_templates_by_type(self, template_type: TemplateType) -> List[TemplateDefinition]:
        """
        Get all templates of a specific type.
        
        Args:
            template_type: Type of templates to retrieve
            
        Returns:
            List of templates
        """
        start_time = time.time()

        try:
            result = await self._execute_db_operation(
                lambda: self.supabase.table("archon_template_definitions")
                .select("*")
                .eq("template_type", template_type.value)
                .eq("is_active", True)
                .order("name")
                .execute()
            )

            templates = [TemplateDefinition(**row) for row in result.data]

            # Cache templates
            for template in templates:
                self._cache_template(template)

            duration = time.time() - start_time
            logger.info(
                "Retrieved templates by type",
                template_type=template_type.value,
                count=len(templates),
                duration_ms=round(duration * 1000, 2)
            )

            return templates

        except Exception as e:
            logger.error("Error retrieving templates by type %s: %s", template_type.value, e)
            return []

    async def update_template(self, template_id: UUID, request: UpdateTemplateDefinitionRequest) -> TemplateDefinitionResponse:
        """
        Update a template with inheritance validation.

        Args:
            template_id: Template UUID
            request: Template update request

        Returns:
            TemplateDefinitionResponse with updated template or error
        """
        start_time = time.time()

        try:
            # Get existing template
            existing_response = await self.get_template(template_id)
            if not existing_response.success:
                return existing_response

            existing_template = existing_response.template

            # Validate parent template if being updated
            if request.parent_template_id is not None:
                if request.parent_template_id:
                    parent_response = await self.get_template(request.parent_template_id)
                    if not parent_response.success:
                        raise InheritanceValidationError(f"Parent template {request.parent_template_id} not found")

                    # Check for circular inheritance
                    would_create_cycle = await self._would_create_circular_inheritance(
                        template_id, request.parent_template_id
                    )
                    if would_create_cycle:
                        raise CircularInheritanceError(
                            f"Template '{existing_template.name}' update would create circular inheritance"
                        )

            # Build update data
            update_data = {"updated_at": datetime.utcnow().isoformat()}

            if request.name is not None:
                update_data["name"] = request.name
            if request.title is not None:
                update_data["title"] = request.title
            if request.description is not None:
                update_data["description"] = request.description
            if request.template_type is not None:
                update_data["template_type"] = request.template_type.value
            if request.parent_template_id is not None:
                update_data["parent_template_id"] = str(request.parent_template_id) if request.parent_template_id else None
            if request.workflow_assignments is not None:
                update_data["workflow_assignments"] = request.workflow_assignments
            if request.component_templates is not None:
                update_data["component_templates"] = request.component_templates
            if request.inheritance_rules is not None:
                update_data["inheritance_rules"] = request.inheritance_rules
            if request.is_public is not None:
                update_data["is_public"] = request.is_public

            # Update template
            result = await self._execute_db_operation(
                lambda: self.supabase.table("archon_template_definitions")
                .update(update_data)
                .eq("id", str(template_id))
                .execute()
            )

            if not result.data:
                raise TemplateServiceError("Failed to update template")

            updated_template = TemplateDefinition(**result.data[0])

            # Invalidate caches
            self._invalidate_template_cache(template_id)
            self._invalidate_inheritance_cache(template_id)
            self._invalidate_resolution_cache(template_id)

            duration = time.time() - start_time
            logger.info(
                "Template updated successfully",
                template_id=str(template_id),
                duration_ms=round(duration * 1000, 2)
            )

            return TemplateDefinitionResponse(
                success=True,
                template=updated_template,
                message=f"Template '{updated_template.name}' updated successfully"
            )

        except (CircularInheritanceError, InheritanceValidationError) as e:
            logger.warning("Template update validation failed: %s", e)
            return TemplateDefinitionResponse(
                success=False,
                message="Template update failed",
                error=str(e)
            )
        except Exception as e:
            logger.error("Unexpected error updating template: %s", e)
            return TemplateDefinitionResponse(
                success=False,
                message="Template update failed",
                error=f"Unexpected error: {str(e)}"
            )

    async def delete_template(self, template_id: UUID) -> TemplateDefinitionResponse:
        """
        Delete a template and check for dependent templates.

        Args:
            template_id: Template UUID

        Returns:
            TemplateDefinitionResponse with success status
        """
        start_time = time.time()

        try:
            # Get existing template
            existing_response = await self.get_template(template_id)
            if not existing_response.success:
                return existing_response

            existing_template = existing_response.template

            # Check if other templates depend on this one
            dependents = await self._get_template_dependents(template_id)
            if dependents:
                dependent_names = [dep.name for dep in dependents]
                raise InheritanceValidationError(
                    f"Cannot delete template '{existing_template.name}' - it is inherited by: {', '.join(dependent_names)}"
                )

            # Delete the template
            await self._execute_db_operation(
                lambda: self.supabase.table("archon_template_definitions")
                .delete()
                .eq("id", str(template_id))
                .execute()
            )

            # Invalidate caches
            self._invalidate_template_cache(template_id)
            self._invalidate_inheritance_cache(template_id)
            self._invalidate_resolution_cache(template_id)

            duration = time.time() - start_time
            logger.info(
                "Template deleted successfully",
                template_id=str(template_id),
                duration_ms=round(duration * 1000, 2)
            )

            return TemplateDefinitionResponse(
                success=True,
                message=f"Template '{existing_template.name}' deleted successfully"
            )

        except InheritanceValidationError as e:
            logger.warning("Template deletion validation failed: %s", e)
            return TemplateDefinitionResponse(
                success=False,
                message="Template deletion failed",
                error=str(e)
            )
        except Exception as e:
            logger.error("Unexpected error deleting template: %s", e)
            return TemplateDefinitionResponse(
                success=False,
                message="Template deletion failed",
                error=f"Unexpected error: {str(e)}"
            )

    async def _get_template_dependents(self, template_id: UUID) -> List[TemplateDefinition]:
        """Get templates that inherit from this template."""
        try:
            result = await self._execute_db_operation(
                lambda: self.supabase.table("archon_template_definitions")
                .select("*")
                .eq("parent_template_id", str(template_id))
                .execute()
            )

            return [TemplateDefinition(**row) for row in result.data]

        except Exception as e:
            logger.error("Error retrieving template dependents: %s", e)
            return []

    async def resolve_template_inheritance(self, template_id: UUID) -> Dict[str, Any]:
        """
        Resolve template inheritance chain with caching.

        Args:
            template_id: Template UUID to resolve

        Returns:
            Resolved template configuration
        """
        start_time = time.time()
        cache_key = str(template_id)

        # Check cache first
        if cache_key in self._resolution_cache:
            resolved_config, timestamp = self._resolution_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                logger.debug("Template resolution retrieved from cache for template %s", template_id)
                return resolved_config

        try:
            # Get inheritance chain
            inheritance_chain = await self._get_inheritance_chain(template_id)
            if not inheritance_chain:
                return {}

            # Build template map for resolution
            template_map = {tmpl.id: tmpl for tmpl in inheritance_chain if tmpl.id}

            # Resolve using utility function
            root_template = inheritance_chain[0]
            resolved_config = resolve_template_inheritance(root_template, template_map)

            # Cache the resolved configuration
            self._resolution_cache[cache_key] = (resolved_config, time.time())

            duration = time.time() - start_time
            logger.info(
                "Template inheritance resolved",
                template_id=str(template_id),
                chain_length=len(inheritance_chain),
                duration_ms=round(duration * 1000, 2)
            )

            return resolved_config

        except Exception as e:
            logger.error("Error resolving template inheritance for %s: %s", template_id, e)
            return {}

    async def apply_template_to_component(self, request: ApplyTemplateRequest) -> TemplateApplicationResponse:
        """
        Apply a template to a component with customizations.

        Args:
            request: Template application request

        Returns:
            TemplateApplicationResponse with application result
        """
        start_time = time.time()

        try:
            # Validate template exists
            template_response = await self.get_template(request.template_id)
            if not template_response.success:
                raise TemplateApplicationError(f"Template {request.template_id} not found")

            # Resolve template inheritance
            resolved_config = await self.resolve_template_inheritance(request.template_id)

            # Apply customizations
            final_config = self._apply_customizations(resolved_config, request.customizations)

            # Create application record
            application_data = {
                "project_id": str(request.project_id),
                "template_id": str(request.template_id),
                "applied_by": request.applied_by,
                "customizations": request.customizations,
                "applied_at": datetime.utcnow().isoformat(),
            }

            result = await self._execute_db_operation(
                lambda: self.supabase.table("archon_template_applications").insert(application_data).execute()
            )

            if not result.data:
                raise TemplateApplicationError("Failed to record template application")

            application = TemplateApplication(**result.data[0])

            duration = time.time() - start_time
            logger.info(
                "Template applied successfully",
                template_id=str(request.template_id),
                project_id=str(request.project_id),
                duration_ms=round(duration * 1000, 2)
            )

            return TemplateApplicationResponse(
                success=True,
                application=application,
                message="Template applied successfully"
            )

        except TemplateApplicationError as e:
            logger.warning("Template application failed: %s", e)
            return TemplateApplicationResponse(
                success=False,
                message="Template application failed",
                error=str(e)
            )
        except Exception as e:
            logger.error("Unexpected error applying template: %s", e)
            return TemplateApplicationResponse(
                success=False,
                message="Template application failed",
                error=f"Unexpected error: {str(e)}"
            )

    async def get_template_conflicts(self, template_id: UUID) -> Dict[str, List[str]]:
        """
        Detect conflicts in template inheritance chain.

        Args:
            template_id: Template UUID to check

        Returns:
            Dictionary of conflict types and descriptions
        """
        try:
            inheritance_chain = await self._get_inheritance_chain(template_id)
            conflicts = {
                "workflow_conflicts": [],
                "component_conflicts": [],
                "rule_conflicts": []
            }

            # Check for workflow assignment conflicts
            workflow_assignments = {}
            for template in inheritance_chain:
                for workflow_key, workflow_config in template.workflow_assignments.items():
                    if workflow_key in workflow_assignments:
                        conflicts["workflow_conflicts"].append(
                            f"Workflow '{workflow_key}' defined in multiple templates"
                        )
                    workflow_assignments[workflow_key] = workflow_config

            # Check for component template conflicts
            component_templates = {}
            for template in inheritance_chain:
                for comp_type, comp_config in template.component_templates.items():
                    if comp_type in component_templates:
                        conflicts["component_conflicts"].append(
                            f"Component template '{comp_type}' defined in multiple templates"
                        )
                    component_templates[comp_type] = comp_config

            return conflicts

        except Exception as e:
            logger.error("Error detecting template conflicts: %s", e)
            return {"error": [str(e)]}

    # Private helper methods

    async def _execute_db_operation(self, operation):
        """Execute database operation with threading service for performance."""
        return await self.threading_service.run_io_bound(operation)

    async def _get_inheritance_chain(self, template_id: UUID) -> List[TemplateDefinition]:
        """Get the complete inheritance chain for a template with caching."""
        # Check cache first
        if template_id in self._inheritance_cache:
            chain, timestamp = self._inheritance_cache[template_id]
            if time.time() - timestamp < self._inheritance_cache_ttl:
                return chain

        try:
            chain = []
            current_id = template_id
            visited = set()

            while current_id and current_id not in visited:
                visited.add(current_id)

                template_response = await self.get_template(current_id)
                if not template_response.success:
                    break

                template = template_response.template
                chain.append(template)

                current_id = template.parent_template_id

            # Cache the inheritance chain
            self._inheritance_cache[template_id] = (chain, time.time())

            return chain

        except Exception as e:
            logger.error("Error building inheritance chain for template %s: %s", template_id, e)
            return []

    async def _would_create_circular_inheritance(
        self, template_id: Optional[UUID], parent_template_id: UUID
    ) -> bool:
        """Check if adding parent would create circular inheritance."""
        if not parent_template_id:
            return False

        # Get parent's inheritance chain
        parent_chain = await self._get_inheritance_chain(parent_template_id)
        parent_ids = {tmpl.id for tmpl in parent_chain if tmpl.id}

        # Check if template_id is already in parent's chain
        return template_id in parent_ids if template_id else False

    def _apply_customizations(self, base_config: Dict[str, Any], customizations: Dict[str, Any]) -> Dict[str, Any]:
        """Apply customizations to base template configuration."""
        final_config = base_config.copy()

        # Apply workflow assignment customizations
        if "workflow_assignments" in customizations:
            final_config.setdefault("workflow_assignments", {})
            final_config["workflow_assignments"].update(customizations["workflow_assignments"])

        # Apply component template customizations
        if "component_templates" in customizations:
            final_config.setdefault("component_templates", {})
            for comp_type, comp_config in customizations["component_templates"].items():
                if comp_type not in final_config["component_templates"]:
                    final_config["component_templates"][comp_type] = {}
                final_config["component_templates"][comp_type].update(comp_config)

        # Apply inheritance rule customizations
        if "inheritance_rules" in customizations:
            final_config.setdefault("inheritance_rules", {})
            final_config["inheritance_rules"].update(customizations["inheritance_rules"])

        return final_config

    # Caching methods

    def _get_cached_template(self, template_id: UUID) -> Optional[TemplateDefinition]:
        """Get template from cache if available and not expired."""
        if template_id in self._template_cache:
            template, timestamp = self._template_cache[template_id]
            if time.time() - timestamp < self._template_cache_ttl:
                return template
            # Remove expired entry
            del self._template_cache[template_id]
        return None

    def _cache_template(self, template: TemplateDefinition):
        """Cache a template with timestamp."""
        if template.id:
            self._template_cache[template.id] = (template, time.time())

    def _invalidate_template_cache(self, template_id: UUID):
        """Invalidate cached template."""
        if template_id in self._template_cache:
            del self._template_cache[template_id]

    def _invalidate_inheritance_cache(self, template_id: UUID):
        """Invalidate inheritance chain cache for a template."""
        if template_id in self._inheritance_cache:
            del self._inheritance_cache[template_id]

    def _invalidate_resolution_cache(self, template_id: UUID):
        """Invalidate resolution cache for a template."""
        cache_key = str(template_id)
        if cache_key in self._resolution_cache:
            del self._resolution_cache[cache_key]

    def _invalidate_all_caches(self):
        """Invalidate all caches (used when templates are modified)."""
        self._template_cache.clear()
        self._inheritance_cache.clear()
        self._resolution_cache.clear()

    def _cleanup_expired_cache(self):
        """Clean up expired cache entries."""
        current_time = time.time()

        # Clean template cache
        expired_templates = [
            tmpl_id for tmpl_id, (_, timestamp) in self._template_cache.items()
            if current_time - timestamp >= self._template_cache_ttl
        ]
        for tmpl_id in expired_templates:
            del self._template_cache[tmpl_id]

        # Clean inheritance cache
        expired_inheritance = [
            tmpl_id for tmpl_id, (_, timestamp) in self._inheritance_cache.items()
            if current_time - timestamp >= self._inheritance_cache_ttl
        ]
        for tmpl_id in expired_inheritance:
            del self._inheritance_cache[tmpl_id]

        # Clean resolution cache
        expired_resolution = [
            cache_key for cache_key, (_, timestamp) in self._resolution_cache.items()
            if current_time - timestamp >= self._cache_ttl
        ]
        for cache_key in expired_resolution:
            del self._resolution_cache[cache_key]


# Global service instance
_template_service: Optional[TemplateService] = None


def get_template_service() -> TemplateService:
    """Get the global template service instance."""
    global _template_service
    if _template_service is None:
        _template_service = TemplateService()
    return _template_service
