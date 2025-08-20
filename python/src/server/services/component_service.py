"""
Component Service

Manages component CRUD operations, dependency validation, and caching.
Provides high-performance component management with circular dependency detection.
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID, uuid4

try:
    from supabase import Client
except ImportError:
    # For testing environments where supabase might not be available
    Client = None

from ..config.logfire_config import get_logger
from ..models.component_models import (
    Component,
    ComponentStatus,
    CreateComponentRequest,
    UpdateComponentRequest,
    ComponentResponse,
)
from ..services.client_manager import get_supabase_client
from ..services.threading_service import get_threading_service

logger = get_logger(__name__)


class ComponentServiceError(Exception):
    """Base exception for component service errors"""


class CircularDependencyError(ComponentServiceError):
    """Raised when a circular dependency is detected"""


class ComponentNotFoundError(ComponentServiceError):
    """Raised when a component is not found"""


class DependencyValidationError(ComponentServiceError):
    """Raised when dependency validation fails"""


class ComponentService:
    """
    High-performance component management service with dependency validation and caching.
    
    Features:
    - Async CRUD operations for components
    - Circular dependency detection with caching
    - Completion gate validation
    - Performance optimization for <100ms operations
    - Comprehensive error handling and logging
    """

    def __init__(self, supabase_client: Optional[Client] = None):
        """
        Initialize ComponentService with optional Supabase client.
        
        Args:
            supabase_client: Optional Supabase client instance
        """
        self.supabase = supabase_client or get_supabase_client()
        self.threading_service = get_threading_service()

        # Dependency graph cache with 30-minute TTL
        self._dependency_cache: Dict[str, Tuple[Dict[UUID, Set[UUID]], float]] = {}
        self._cache_ttl = 1800  # 30 minutes in seconds

        # Component cache for frequently accessed components
        self._component_cache: Dict[UUID, Tuple[Component, float]] = {}
        self._component_cache_ttl = 300  # 5 minutes for component cache

        logger.info("ComponentService initialized with caching enabled")

    async def create_component(self, request: CreateComponentRequest) -> ComponentResponse:
        """
        Create a new component with dependency validation.
        
        Args:
            request: Component creation request
            
        Returns:
            ComponentResponse with created component or error
        """
        start_time = time.time()

        try:
            # Validate dependencies exist and are in the same project
            if request.dependencies:
                await self._validate_dependencies_exist(request.project_id, request.dependencies)

            # Check for circular dependencies
            if request.dependencies:
                would_create_cycle = await self._would_create_circular_dependency(
                    request.project_id, None, request.dependencies
                )
                if would_create_cycle:
                    raise CircularDependencyError(
                        f"Component '{request.name}' would create a circular dependency"
                    )

            # Create component data
            component_data = {
                "project_id": str(request.project_id),
                "name": request.name,
                "description": request.description,
                "component_type": request.component_type.value,
                "status": ComponentStatus.NOT_STARTED.value,
                "context_data": request.context_data,
                "completion_gates": request.completion_gates,
                "order_index": request.order_index,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Insert component
            result = await self._execute_db_operation(
                lambda: self.supabase.table("archon_components").insert(component_data).execute()
            )

            if not result.data:
                raise ComponentServiceError("Failed to create component")

            component = Component(**result.data[0])

            # Create dependencies if specified
            if request.dependencies:
                await self._create_component_dependencies(component.id, request.dependencies)

            # Invalidate caches
            self._invalidate_dependency_cache(request.project_id)

            duration = time.time() - start_time
            logger.info(
                "Component created successfully",
                component_id=str(component.id),
                project_id=str(request.project_id),
                duration_ms=round(duration * 1000, 2)
            )
            
            return ComponentResponse(
                success=True,
                component=component,
                message=f"Component '{component.name}' created successfully"
            )
            
        except (CircularDependencyError, DependencyValidationError) as e:
            logger.warning("Component creation validation failed: %s", e)
            return ComponentResponse(
                success=False,
                message="Component creation failed",
                error=str(e)
            )
        except Exception as e:
            logger.error("Unexpected error creating component: %s", e)
            return ComponentResponse(
                success=False,
                message="Component creation failed",
                error=f"Unexpected error: {str(e)}"
            )

    async def get_component(self, component_id: UUID) -> ComponentResponse:
        """
        Get a component by ID with caching.
        
        Args:
            component_id: Component UUID
            
        Returns:
            ComponentResponse with component or error
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cached_component = self._get_cached_component(component_id)
            if cached_component:
                duration = time.time() - start_time
                logger.debug(
                    "Component retrieved from cache",
                    component_id=str(component_id),
                    duration_ms=round(duration * 1000, 2)
                )
                return ComponentResponse(
                    success=True,
                    component=cached_component,
                    message="Component retrieved successfully"
                )
            
            # Fetch from database
            result = await self._execute_db_operation(
                lambda: self.supabase.table("archon_components")
                .select("*")
                .eq("id", str(component_id))
                .execute()
            )
            
            if not result.data:
                raise ComponentNotFoundError(f"Component {component_id} not found")
            
            component = Component(**result.data[0])
            
            # Cache the component
            self._cache_component(component)
            
            duration = time.time() - start_time
            logger.info(
                f"Component retrieved successfully",
                component_id=str(component_id),
                duration_ms=round(duration * 1000, 2)
            )
            
            return ComponentResponse(
                success=True,
                component=component,
                message="Component retrieved successfully"
            )
            
        except ComponentNotFoundError as e:
            logger.warning(f"Component not found: {e}")
            return ComponentResponse(
                success=False,
                message="Component not found",
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error retrieving component: {e}")
            return ComponentResponse(
                success=False,
                message="Component retrieval failed",
                error=f"Unexpected error: {str(e)}"
            )

    async def get_components_by_project(self, project_id: UUID) -> List[Component]:
        """
        Get all components for a project.
        
        Args:
            project_id: Project UUID
            
        Returns:
            List of components
        """
        start_time = time.time()
        
        try:
            result = await self._execute_db_operation(
                lambda: self.supabase.table("archon_components")
                .select("*")
                .eq("project_id", str(project_id))
                .order("order_index")
                .execute()
            )
            
            components = [Component(**row) for row in result.data]
            
            # Cache components
            for component in components:
                self._cache_component(component)
            
            duration = time.time() - start_time
            logger.info(
                f"Retrieved {len(components)} components for project",
                project_id=str(project_id),
                duration_ms=round(duration * 1000, 2)
            )
            
            return components
            
        except Exception as e:
            logger.error(f"Error retrieving components for project {project_id}: {e}")
            return []

    async def update_component(self, component_id: UUID, request: UpdateComponentRequest) -> ComponentResponse:
        """
        Update a component with dependency validation.

        Args:
            component_id: Component UUID
            request: Component update request

        Returns:
            ComponentResponse with updated component or error
        """
        start_time = time.time()

        try:
            # Get existing component
            existing_response = await self.get_component(component_id)
            if not existing_response.success:
                return existing_response

            existing_component = existing_response.component

            # Validate dependencies if being updated
            if request.dependencies is not None:
                await self._validate_dependencies_exist(existing_component.project_id, request.dependencies)

                # Check for circular dependencies
                would_create_cycle = await self._would_create_circular_dependency(
                    existing_component.project_id, component_id, request.dependencies
                )
                if would_create_cycle:
                    raise CircularDependencyError(
                        f"Component '{existing_component.name}' update would create a circular dependency"
                    )

            # Build update data
            update_data = {"updated_at": datetime.utcnow().isoformat()}

            if request.name is not None:
                update_data["name"] = request.name
            if request.description is not None:
                update_data["description"] = request.description
            if request.component_type is not None:
                update_data["component_type"] = request.component_type.value
            if request.status is not None:
                update_data["status"] = request.status.value
            if request.context_data is not None:
                update_data["context_data"] = request.context_data
            if request.completion_gates is not None:
                update_data["completion_gates"] = request.completion_gates
            if request.order_index is not None:
                update_data["order_index"] = request.order_index

            # Update component
            result = await self._execute_db_operation(
                lambda: self.supabase.table("archon_components")
                .update(update_data)
                .eq("id", str(component_id))
                .execute()
            )

            if not result.data:
                raise ComponentServiceError("Failed to update component")

            updated_component = Component(**result.data[0])

            # Update dependencies if specified
            if request.dependencies is not None:
                await self._update_component_dependencies(component_id, request.dependencies)

            # Invalidate caches
            self._invalidate_component_cache(component_id)
            self._invalidate_dependency_cache(existing_component.project_id)

            duration = time.time() - start_time
            logger.info(
                f"Component updated successfully",
                component_id=str(component_id),
                duration_ms=round(duration * 1000, 2)
            )

            return ComponentResponse(
                success=True,
                component=updated_component,
                message=f"Component '{updated_component.name}' updated successfully"
            )

        except (CircularDependencyError, DependencyValidationError) as e:
            logger.warning(f"Component update validation failed: {e}")
            return ComponentResponse(
                success=False,
                message="Component update failed",
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error updating component: {e}")
            return ComponentResponse(
                success=False,
                message="Component update failed",
                error=f"Unexpected error: {str(e)}"
            )

    async def delete_component(self, component_id: UUID) -> ComponentResponse:
        """
        Delete a component and its dependencies.

        Args:
            component_id: Component UUID

        Returns:
            ComponentResponse with success status
        """
        start_time = time.time()

        try:
            # Get existing component for project_id
            existing_response = await self.get_component(component_id)
            if not existing_response.success:
                return existing_response

            existing_component = existing_response.component

            # Check if other components depend on this one
            dependents = await self._get_component_dependents(component_id)
            if dependents:
                dependent_names = [dep.name for dep in dependents]
                raise DependencyValidationError(
                    f"Cannot delete component '{existing_component.name}' - it is required by: {', '.join(dependent_names)}"
                )

            # Delete component dependencies first
            await self._execute_db_operation(
                lambda: self.supabase.table("archon_component_dependencies")
                .delete()
                .eq("component_id", str(component_id))
                .execute()
            )

            # Delete the component
            await self._execute_db_operation(
                lambda: self.supabase.table("archon_components")
                .delete()
                .eq("id", str(component_id))
                .execute()
            )

            # Invalidate caches
            self._invalidate_component_cache(component_id)
            self._invalidate_dependency_cache(existing_component.project_id)

            duration = time.time() - start_time
            logger.info(
                f"Component deleted successfully",
                component_id=str(component_id),
                duration_ms=round(duration * 1000, 2)
            )

            return ComponentResponse(
                success=True,
                message=f"Component '{existing_component.name}' deleted successfully"
            )

        except DependencyValidationError as e:
            logger.warning(f"Component deletion validation failed: {e}")
            return ComponentResponse(
                success=False,
                message="Component deletion failed",
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error deleting component: {e}")
            return ComponentResponse(
                success=False,
                message="Component deletion failed",
                error=f"Unexpected error: {str(e)}"
            )

    async def get_component_dependencies(self, component_id: UUID) -> List[Component]:
        """
        Get all components that this component depends on.

        Args:
            component_id: Component UUID

        Returns:
            List of dependency components
        """
        try:
            result = await self._execute_db_operation(
                lambda: self.supabase.table("archon_component_dependencies")
                .select("depends_on_component_id")
                .eq("component_id", str(component_id))
                .execute()
            )

            if not result.data:
                return []

            dependency_ids = [UUID(row["depends_on_component_id"]) for row in result.data]
            dependencies = []

            for dep_id in dependency_ids:
                dep_response = await self.get_component(dep_id)
                if dep_response.success:
                    dependencies.append(dep_response.component)

            return dependencies

        except Exception as e:
            logger.error(f"Error retrieving component dependencies: {e}")
            return []

    async def validate_completion_gates(self, component_id: UUID) -> Dict[str, bool]:
        """
        Validate completion gates for a component.

        Args:
            component_id: Component UUID

        Returns:
            Dictionary mapping gate names to validation status
        """
        try:
            component_response = await self.get_component(component_id)
            if not component_response.success:
                return {}

            component = component_response.component
            gate_results = {}

            for gate in component.completion_gates:
                # Basic gate validation - can be extended with specific gate logic
                if gate == "dependencies_completed":
                    gate_results[gate] = await self._validate_dependencies_completed(component_id)
                elif gate == "tests_passing":
                    gate_results[gate] = await self._validate_tests_passing(component_id)
                elif gate == "code_review_approved":
                    gate_results[gate] = await self._validate_code_review_approved(component_id)
                else:
                    # Custom gate validation can be added here
                    gate_results[gate] = False

            return gate_results

        except Exception as e:
            logger.error(f"Error validating completion gates: {e}")
            return {}

    async def get_dependency_graph(self, project_id: UUID) -> Dict[UUID, Set[UUID]]:
        """
        Get the complete dependency graph for a project with caching.

        Args:
            project_id: Project UUID

        Returns:
            Dictionary mapping component IDs to their dependency sets
        """
        cache_key = str(project_id)

        # Check cache first
        if cache_key in self._dependency_cache:
            graph, timestamp = self._dependency_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                logger.debug(f"Dependency graph retrieved from cache for project {project_id}")
                return graph

        try:
            # Fetch all components and dependencies for the project
            components_result = await self._execute_db_operation(
                lambda: self.supabase.table("archon_components")
                .select("id")
                .eq("project_id", str(project_id))
                .execute()
            )

            dependencies_result = await self._execute_db_operation(
                lambda: self.supabase.table("archon_component_dependencies")
                .select("component_id, depends_on_component_id")
                .execute()
            )

            # Build dependency graph
            graph = {}
            component_ids = {UUID(row["id"]) for row in components_result.data}

            # Initialize all components with empty dependency sets
            for comp_id in component_ids:
                graph[comp_id] = set()

            # Add dependencies
            for dep_row in dependencies_result.data:
                comp_id = UUID(dep_row["component_id"])
                dep_id = UUID(dep_row["depends_on_component_id"])

                # Only include dependencies within this project
                if comp_id in component_ids and dep_id in component_ids:
                    graph[comp_id].add(dep_id)

            # Cache the graph
            self._dependency_cache[cache_key] = (graph, time.time())

            logger.info(f"Dependency graph built for project {project_id} with {len(graph)} components")
            return graph

        except Exception as e:
            logger.error(f"Error building dependency graph: {e}")
            return {}

    # Private helper methods

    async def _execute_db_operation(self, operation):
        """Execute database operation with threading service for performance."""
        return await self.threading_service.run_io_bound(operation)

    async def _validate_dependencies_exist(self, project_id: UUID, dependency_ids: List[UUID]):
        """Validate that all dependency components exist in the same project."""
        if not dependency_ids:
            return

        result = await self._execute_db_operation(
            lambda: self.supabase.table("archon_components")
            .select("id")
            .eq("project_id", str(project_id))
            .in_("id", [str(dep_id) for dep_id in dependency_ids])
            .execute()
        )

        found_ids = {UUID(row["id"]) for row in result.data}
        missing_ids = set(dependency_ids) - found_ids

        if missing_ids:
            raise DependencyValidationError(
                f"Dependencies not found in project: {[str(id) for id in missing_ids]}"
            )

    async def _would_create_circular_dependency(
        self, project_id: UUID, component_id: Optional[UUID], new_dependencies: List[UUID]
    ) -> bool:
        """Check if adding dependencies would create a circular dependency."""
        if not new_dependencies:
            return False

        # Get current dependency graph
        graph = await self.get_dependency_graph(project_id)

        # If this is a new component, add it to the graph
        if component_id is None:
            component_id = uuid4()  # Temporary ID for validation
            graph[component_id] = set()

        # Add new dependencies to the graph
        graph[component_id] = set(new_dependencies)

        # Check for cycles using DFS
        return self._has_circular_dependency(graph, component_id)

    def _has_circular_dependency(self, graph: Dict[UUID, Set[UUID]], start_component: UUID) -> bool:
        """Check for circular dependencies using depth-first search."""
        visited = set()
        rec_stack = set()

        def dfs(node: UUID) -> bool:
            if node in rec_stack:
                return True  # Cycle detected
            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)

            # Visit all dependencies
            for dependency in graph.get(node, set()):
                if dfs(dependency):
                    return True

            rec_stack.remove(node)
            return False

        return dfs(start_component)

    async def _create_component_dependencies(self, component_id: UUID, dependency_ids: List[UUID]):
        """Create component dependency records."""
        if not dependency_ids:
            return

        dependency_data = [
            {
                "component_id": str(component_id),
                "depends_on_component_id": str(dep_id),
                "dependency_type": "hard",
                "created_at": datetime.utcnow().isoformat(),
            }
            for dep_id in dependency_ids
        ]

        await self._execute_db_operation(
            lambda: self.supabase.table("archon_component_dependencies")
            .insert(dependency_data)
            .execute()
        )

    async def _update_component_dependencies(self, component_id: UUID, dependency_ids: List[UUID]):
        """Update component dependencies by replacing existing ones."""
        # Delete existing dependencies
        await self._execute_db_operation(
            lambda: self.supabase.table("archon_component_dependencies")
            .delete()
            .eq("component_id", str(component_id))
            .execute()
        )

        # Create new dependencies
        await self._create_component_dependencies(component_id, dependency_ids)

    async def _get_component_dependents(self, component_id: UUID) -> List[Component]:
        """Get components that depend on this component."""
        result = await self._execute_db_operation(
            lambda: self.supabase.table("archon_component_dependencies")
            .select("component_id")
            .eq("depends_on_component_id", str(component_id))
            .execute()
        )

        if not result.data:
            return []

        dependent_ids = [UUID(row["component_id"]) for row in result.data]
        dependents = []

        for dep_id in dependent_ids:
            dep_response = await self.get_component(dep_id)
            if dep_response.success:
                dependents.append(dep_response.component)

        return dependents

    async def _validate_dependencies_completed(self, component_id: UUID) -> bool:
        """Validate that all dependencies are completed."""
        dependencies = await self.get_component_dependencies(component_id)
        return all(dep.status == ComponentStatus.COMPLETED for dep in dependencies)

    async def _validate_tests_passing(self, component_id: UUID) -> bool:
        """Validate that tests are passing for the component."""
        # Placeholder for test validation logic
        # This would integrate with your testing framework
        return True

    async def _validate_code_review_approved(self, component_id: UUID) -> bool:
        """Validate that code review is approved for the component."""
        # Placeholder for code review validation logic
        # This would integrate with your code review system
        return True

    # Caching methods

    def _get_cached_component(self, component_id: UUID) -> Optional[Component]:
        """Get component from cache if available and not expired."""
        if component_id in self._component_cache:
            component, timestamp = self._component_cache[component_id]
            if time.time() - timestamp < self._component_cache_ttl:
                return component
            # Remove expired entry
            del self._component_cache[component_id]
        return None

    def _cache_component(self, component: Component):
        """Cache a component with timestamp."""
        if component.id:
            self._component_cache[component.id] = (component, time.time())

    def _invalidate_component_cache(self, component_id: UUID):
        """Invalidate cached component."""
        if component_id in self._component_cache:
            del self._component_cache[component_id]

    def _invalidate_dependency_cache(self, project_id: UUID):
        """Invalidate dependency graph cache for a project."""
        cache_key = str(project_id)
        if cache_key in self._dependency_cache:
            del self._dependency_cache[cache_key]

    def _cleanup_expired_cache(self):
        """Clean up expired cache entries."""
        current_time = time.time()

        # Clean component cache
        expired_components = [
            comp_id for comp_id, (_, timestamp) in self._component_cache.items()
            if current_time - timestamp >= self._component_cache_ttl
        ]
        for comp_id in expired_components:
            del self._component_cache[comp_id]

        # Clean dependency cache
        expired_dependencies = [
            project_id for project_id, (_, timestamp) in self._dependency_cache.items()
            if current_time - timestamp >= self._cache_ttl
        ]
        for project_id in expired_dependencies:
            del self._dependency_cache[project_id]


# Global service instance
_component_service: Optional[ComponentService] = None


def get_component_service() -> ComponentService:
    """Get the global component service instance."""
    global _component_service
    if _component_service is None:
        _component_service = ComponentService()
    return _component_service
