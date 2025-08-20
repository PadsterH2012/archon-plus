"""
Template Injection Service

Core service for template expansion and management in the Archon Template Injection System.
Provides high-performance template expansion with caching and comprehensive error handling.
"""

import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID

try:
    from supabase import Client
except ImportError:
    # For testing environments where supabase might not be available
    Client = None

from ..config.logfire_config import get_logger
from ..models.template_injection_models import (
    TemplateComponent,
    TemplateDefinition,
    TemplateAssignment,
    TemplateExpansionResult,
    TemplateComponentType,
    TemplateInjectionLevel,
    HierarchyType,
    CreateTemplateDefinitionRequest,
    TemplateDefinitionResponse,
    TemplateExpansionRequest,
    TemplateExpansionResponse,
    validate_template_hierarchy_assignment
)
from ..services.client_manager import get_supabase_client
from ..services.threading_service import get_threading_service

logger = get_logger(__name__)


class TemplateInjectionServiceError(Exception):
    """Base exception for template injection service errors"""


class TemplateNotFoundError(TemplateInjectionServiceError):
    """Raised when a template is not found"""


class ComponentNotFoundError(TemplateInjectionServiceError):
    """Raised when a template component is not found"""


class TemplateExpansionError(TemplateInjectionServiceError):
    """Raised when template expansion fails"""


class TemplateValidationError(TemplateInjectionServiceError):
    """Raised when template validation fails"""


class TemplateInjectionService:
    """
    Core service for template injection system.
    
    Provides template expansion, component management, and caching
    with comprehensive error handling and performance monitoring.
    """

    def __init__(self, supabase_client: Optional[Client] = None):
        """
        Initialize TemplateInjectionService with optional Supabase client.
        
        Args:
            supabase_client: Optional Supabase client instance
        """
        self.supabase = supabase_client or get_supabase_client()
        self.threading_service = get_threading_service()

        # Template cache with 30-minute TTL
        self._template_cache: Dict[str, Tuple[TemplateDefinition, float]] = {}
        self._template_cache_ttl = 1800  # 30 minutes in seconds

        # Component cache with 15-minute TTL
        self._component_cache: Dict[str, Tuple[TemplateComponent, float]] = {}
        self._component_cache_ttl = 900  # 15 minutes in seconds

        # Expansion cache with 5-minute TTL for frequently used expansions
        self._expansion_cache: Dict[str, Tuple[str, float]] = {}
        self._expansion_cache_ttl = 300  # 5 minutes in seconds

        logger.info("TemplateInjectionService initialized with caching enabled")

    async def expand_task_description(
        self,
        original_description: str,
        project_id: Optional[UUID] = None,
        template_name: str = "workflow_default",
        context_data: Optional[Dict[str, Any]] = None
    ) -> TemplateExpansionResponse:
        """
        Main template expansion method - expands user task with operational workflow.
        
        Args:
            original_description: Original user task description
            project_id: Optional project UUID for context
            template_name: Template to use (default: workflow_default)
            context_data: Optional context data for expansion
            
        Returns:
            TemplateExpansionResponse with expanded instructions or error
        """
        start_time = time.time()
        
        try:
            # Create cache key for this expansion
            cache_key = f"{template_name}:{hash(original_description)}:{project_id}"
            
            # Check expansion cache first
            cached_expansion = self._get_cached_expansion(cache_key)
            if cached_expansion:
                duration = time.time() - start_time
                logger.debug(
                    "Template expansion retrieved from cache",
                    template_name=template_name,
                    duration_ms=round(duration * 1000, 2)
                )
                return TemplateExpansionResponse(
                    success=True,
                    result=TemplateExpansionResult(
                        original_task=original_description,
                        expanded_instructions=cached_expansion,
                        template_name=template_name,
                        expansion_time_ms=int(round(duration * 1000))
                    ),
                    message="Template expansion completed successfully (cached)"
                )

            # Get template
            template_response = await self.get_template(template_name)
            if not template_response.success or not template_response.template:
                raise TemplateNotFoundError(f"Template '{template_name}' not found")

            template = template_response.template
            
            # Extract template content from template_data
            template_content = template.template_data.get("template_content", "")
            if not template_content:
                raise TemplateExpansionError(f"Template '{template_name}' has no content")

            # Expand placeholders in template content
            expanded_content = await self.expand_placeholders(
                template_content, 
                context_data or {}
            )

            # Insert user task at the specified position
            user_task_position = template.template_data.get("user_task_position", 6)
            final_instructions = self._insert_user_task(
                expanded_content, 
                original_description, 
                user_task_position
            )

            # Cache the expansion
            self._cache_expansion(cache_key, final_instructions)

            duration = time.time() - start_time
            logger.info(
                "Template expansion completed successfully",
                template_name=template_name,
                original_length=len(original_description),
                expanded_length=len(final_instructions),
                duration_ms=round(duration * 1000, 2)
            )

            return TemplateExpansionResponse(
                success=True,
                result=TemplateExpansionResult(
                    original_task=original_description,
                    expanded_instructions=final_instructions,
                    template_name=template_name,
                    expansion_time_ms=int(round(duration * 1000)),
                    template_metadata={
                        "template_id": str(template.id) if template.id else None,
                        "user_task_position": user_task_position,
                        "estimated_duration": template.template_data.get("estimated_duration", 30),
                        "required_tools": template.template_data.get("required_tools", [])
                    }
                ),
                message="Template expansion completed successfully"
            )

        except (TemplateNotFoundError, ComponentNotFoundError, TemplateExpansionError) as e:
            logger.warning("Template expansion failed: %s", e)
            return TemplateExpansionResponse(
                success=False,
                message="Template expansion failed",
                error=str(e)
            )
        except Exception as e:
            logger.error("Unexpected error during template expansion: %s", e)
            return TemplateExpansionResponse(
                success=False,
                message="Template expansion failed",
                error=f"Unexpected error: {str(e)}"
            )

    async def get_template(self, template_name: str) -> TemplateDefinitionResponse:
        """
        Get template by name with caching.
        
        Args:
            template_name: Name of the template to retrieve
            
        Returns:
            TemplateDefinitionResponse with template or error
        """
        start_time = time.time()

        try:
            # Check cache first
            cached_template = self._get_cached_template(template_name)
            if cached_template:
                duration = time.time() - start_time
                logger.debug(
                    "Template retrieved from cache",
                    template_name=template_name,
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
                .eq("name", template_name)
                .eq("is_active", True)
                .execute()
            )

            if not result.data:
                raise TemplateNotFoundError(f"Template '{template_name}' not found")

            template = TemplateDefinition(**result.data[0])

            # Cache the template
            self._cache_template(template_name, template)

            duration = time.time() - start_time
            logger.info(
                "Template retrieved successfully",
                template_name=template_name,
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

    async def expand_placeholders(
        self,
        template_content: str,
        context_data: Dict[str, Any]
    ) -> str:
        """
        Expand {{group::name}} placeholders with component instruction text.

        Args:
            template_content: Template content with placeholders
            context_data: Context data for expansion

        Returns:
            Expanded template content with components replaced
        """
        start_time = time.time()

        try:
            # Find all placeholders in the template
            placeholders = re.findall(r'\{\{([^}]+)\}\}', template_content)
            expanded_content = template_content

            for placeholder in placeholders:
                # Skip USER_TASK placeholder - handled separately
                if placeholder == "USER_TASK":
                    continue

                # Get component for this placeholder
                component = await self.get_component(placeholder)
                if component:
                    # Replace placeholder with component instruction text
                    expanded_content = expanded_content.replace(
                        f"{{{{{placeholder}}}}}",
                        component.instruction_text
                    )
                else:
                    logger.warning(f"Component not found for placeholder: {placeholder}")
                    # Leave placeholder as-is if component not found

            duration = time.time() - start_time
            logger.debug(
                "Placeholders expanded successfully",
                placeholder_count=len(placeholders),
                duration_ms=round(duration * 1000, 2)
            )

            return expanded_content

        except Exception as e:
            logger.error("Error expanding placeholders: %s", e)
            raise TemplateExpansionError(f"Failed to expand placeholders: {str(e)}")

    async def get_component(self, component_name: str) -> Optional[TemplateComponent]:
        """
        Get template component by name with caching.

        Args:
            component_name: Name of the component (e.g., "group::understand_homelab_env")

        Returns:
            TemplateComponent if found, None otherwise
        """
        start_time = time.time()

        try:
            # Check cache first
            cached_component = self._get_cached_component(component_name)
            if cached_component:
                duration = time.time() - start_time
                logger.debug(
                    "Component retrieved from cache",
                    component_name=component_name,
                    duration_ms=round(duration * 1000, 2)
                )
                return cached_component

            # Fetch from database
            result = await self._execute_db_operation(
                lambda: self.supabase.table("archon_template_components")
                .select("*")
                .eq("name", component_name)
                .eq("is_active", True)
                .execute()
            )

            if not result.data:
                logger.warning(f"Component '{component_name}' not found")
                return None

            component = TemplateComponent(**result.data[0])

            # Cache the component
            self._cache_component(component_name, component)

            duration = time.time() - start_time
            logger.debug(
                "Component retrieved successfully",
                component_name=component_name,
                duration_ms=round(duration * 1000, 2)
            )

            return component

        except Exception as e:
            logger.error("Error retrieving component: %s", e)
            return None

    def _insert_user_task(
        self,
        template_content: str,
        user_task: str,
        position: int
    ) -> str:
        """
        Insert user task at the specified position in template content.

        Args:
            template_content: Template content with {{USER_TASK}} placeholder
            user_task: Original user task description
            position: Position where user task should appear

        Returns:
            Final instructions with user task inserted
        """
        try:
            # Replace {{USER_TASK}} placeholder with actual user task
            final_instructions = template_content.replace("{{USER_TASK}}", user_task)

            logger.debug(
                "User task inserted successfully",
                user_task_length=len(user_task),
                position=position
            )

            return final_instructions

        except Exception as e:
            logger.error("Error inserting user task: %s", e)
            raise TemplateExpansionError(f"Failed to insert user task: {str(e)}")

    async def validate_template(self, template: TemplateDefinition) -> bool:
        """
        Validate template content and component references.

        Args:
            template: Template to validate

        Returns:
            True if template is valid, False otherwise
        """
        try:
            template_content = template.template_data.get("template_content", "")

            # Check if template contains USER_TASK placeholder
            if "{{USER_TASK}}" not in template_content:
                logger.error("Template missing {{USER_TASK}} placeholder")
                return False

            # Find all component placeholders
            placeholders = re.findall(r'\{\{([^}]+)\}\}', template_content)
            component_placeholders = [p for p in placeholders if p != "USER_TASK"]

            # Validate each component exists
            for placeholder in component_placeholders:
                component = await self.get_component(placeholder)
                if not component:
                    logger.error(f"Template references non-existent component: {placeholder}")
                    return False

            logger.info(
                "Template validation successful",
                template_name=template.name,
                component_count=len(component_placeholders)
            )

            return True

        except Exception as e:
            logger.error("Error validating template: %s", e)
            return False

    # Database operation helper

    async def _execute_db_operation(self, operation):
        """Execute database operation with error handling."""
        try:
            return await self.threading_service.run_io_bound(operation)
        except Exception as e:
            logger.error("Database operation failed: %s", e)
            raise

    # Caching methods

    def _get_cached_template(self, template_name: str) -> Optional[TemplateDefinition]:
        """Get template from cache if available and not expired."""
        if template_name in self._template_cache:
            template, timestamp = self._template_cache[template_name]
            if time.time() - timestamp < self._template_cache_ttl:
                return template
            # Remove expired entry
            del self._template_cache[template_name]
        return None

    def _cache_template(self, template_name: str, template: TemplateDefinition):
        """Cache a template with timestamp."""
        self._template_cache[template_name] = (template, time.time())

    def _get_cached_component(self, component_name: str) -> Optional[TemplateComponent]:
        """Get component from cache if available and not expired."""
        if component_name in self._component_cache:
            component, timestamp = self._component_cache[component_name]
            if time.time() - timestamp < self._component_cache_ttl:
                return component
            # Remove expired entry
            del self._component_cache[component_name]
        return None

    def _cache_component(self, component_name: str, component: TemplateComponent):
        """Cache a component with timestamp."""
        self._component_cache[component_name] = (component, time.time())

    def _get_cached_expansion(self, cache_key: str) -> Optional[str]:
        """Get expansion from cache if available and not expired."""
        if cache_key in self._expansion_cache:
            expansion, timestamp = self._expansion_cache[cache_key]
            if time.time() - timestamp < self._expansion_cache_ttl:
                return expansion
            # Remove expired entry
            del self._expansion_cache[cache_key]
        return None

    def _cache_expansion(self, cache_key: str, expansion: str):
        """Cache an expansion with timestamp."""
        self._expansion_cache[cache_key] = (expansion, time.time())

    def clear_cache(self):
        """Clear all caches."""
        self._template_cache.clear()
        self._component_cache.clear()
        self._expansion_cache.clear()
        logger.info("All caches cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "template_cache_size": len(self._template_cache),
            "component_cache_size": len(self._component_cache),
            "expansion_cache_size": len(self._expansion_cache),
            "template_cache_ttl": self._template_cache_ttl,
            "component_cache_ttl": self._component_cache_ttl,
            "expansion_cache_ttl": self._expansion_cache_ttl
        }


# Singleton instance
_template_injection_service: Optional[TemplateInjectionService] = None


def get_template_injection_service() -> TemplateInjectionService:
    """Get singleton TemplateInjectionService instance."""
    global _template_injection_service
    if _template_injection_service is None:
        _template_injection_service = TemplateInjectionService()
    return _template_injection_service
