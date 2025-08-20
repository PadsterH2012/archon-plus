"""
Context Compilation Service

Manages hierarchical context aggregation from component hierarchy with multi-level caching
and performance optimization. Provides dynamic context compilation for agent instructions.
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID

try:
    from supabase import Client
except ImportError:
    # For testing environments where supabase might not be available
    Client = None

from ..config.logfire_config import get_logger
from ..services.client_manager import get_supabase_client
from ..services.threading_service import get_threading_service
from ..services.component_service import get_component_service
from ..services.template_service import get_template_service
from ..services.search.rag_service import RAGService

logger = get_logger(__name__)


class ContextCompilationError(Exception):
    """Base exception for context compilation errors"""


class ContextNotFoundError(ContextCompilationError):
    """Raised when context cannot be found"""


class ContextCompilationService:
    """
    High-performance context compilation service with multi-level caching.
    
    Features:
    - Hierarchical context aggregation (component → project)
    - Multi-level caching strategy with different TTLs
    - Dynamic context compilation for agent instructions
    - Integration with existing RAG capabilities
    - Performance optimization (<100ms compilation)
    - Context conflict resolution with proper precedence
    """

    def __init__(self, supabase_client: Optional[Client] = None):
        """
        Initialize ContextCompilationService with optional Supabase client.
        
        Args:
            supabase_client: Optional Supabase client instance
        """
        self.supabase = supabase_client or get_supabase_client()
        self.threading_service = get_threading_service()
        self.component_service = get_component_service()
        self.template_service = get_template_service()
        self.rag_service = RAGService(supabase_client)

        # Multi-level caching strategy with different TTLs
        # L1: In-memory compiled context cache (1 hour)
        self._compiled_context_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
        self._compiled_cache_ttl = 3600  # 1 hour

        # L2: Component dependency context cache (30 minutes)
        self._dependency_context_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
        self._dependency_cache_ttl = 1800  # 30 minutes

        # L3: Context compilation cache (15 minutes)
        self._context_compilation_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
        self._compilation_cache_ttl = 900  # 15 minutes

        # L4: Database query cache (5 minutes)
        self._db_query_cache: Dict[str, Tuple[Any, float]] = {}
        self._db_cache_ttl = 300  # 5 minutes

        # Performance metrics
        self._cache_hits = {"L1": 0, "L2": 0, "L3": 0, "L4": 0}
        self._cache_misses = {"L1": 0, "L2": 0, "L3": 0, "L4": 0}

        logger.info("ContextCompilationService initialized with multi-level caching")

    async def compile_component_context(self, component_id: UUID) -> Dict[str, Any]:
        """
        Compile complete context for a component with hierarchical aggregation.
        
        Args:
            component_id: Component UUID
            
        Returns:
            Compiled context dictionary
        """
        start_time = time.time()
        cache_key = f"component_context:{component_id}"

        # L1 Cache: Check compiled context cache
        if cached_context := self._get_cached_context(cache_key, "L1"):
            self._cache_hits["L1"] += 1
            duration = time.time() - start_time
            logger.debug(
                "Component context retrieved from L1 cache",
                component_id=str(component_id),
                duration_ms=round(duration * 1000, 2)
            )
            return cached_context

        self._cache_misses["L1"] += 1

        try:
            # Get component details
            component_response = await self.component_service.get_component(component_id)
            if not component_response.success:
                raise ContextNotFoundError(f"Component {component_id} not found")

            component = component_response.component

            # Aggregate context from hierarchy (parallel processing for performance)
            context_tasks = [
                self._get_component_context(component_id),
                self._get_dependency_context(component_id),
                self._get_template_context(component_id),
                self._get_project_context(component.project_id),
                self._get_rag_context(component_id)
            ]

            # Execute context gathering in parallel
            contexts = await self.threading_service.batch_process(
                items=context_tasks,
                process_func=lambda task: task,
                mode="IO_BOUND"
            )

            component_context, dependency_context, template_context, project_context, rag_context = contexts

            # Merge contexts with proper precedence (component > template > dependency > project > rag)
            compiled_context = self._merge_contexts([
                rag_context,
                project_context,
                dependency_context,
                template_context,
                component_context
            ])

            # Add metadata
            compiled_context["_metadata"] = {
                "component_id": str(component_id),
                "project_id": str(component.project_id),
                "compiled_at": datetime.utcnow().isoformat(),
                "compilation_time_ms": round((time.time() - start_time) * 1000, 2),
                "cache_level": "compiled"
            }

            # Cache the compiled context (L1)
            self._cache_context(cache_key, compiled_context, "L1")

            duration = time.time() - start_time
            logger.info(
                "Component context compiled successfully",
                component_id=str(component_id),
                duration_ms=round(duration * 1000, 2),
                context_keys=list(compiled_context.keys())
            )

            return compiled_context

        except Exception as e:
            logger.error("Error compiling component context for %s: %s", component_id, e)
            raise ContextCompilationError(f"Failed to compile context for component {component_id}: {str(e)}")

    async def compile_project_context(self, project_id: UUID) -> Dict[str, Any]:
        """
        Compile aggregated context for an entire project.
        
        Args:
            project_id: Project UUID
            
        Returns:
            Compiled project context dictionary
        """
        start_time = time.time()
        cache_key = f"project_context:{project_id}"

        # L1 Cache: Check compiled context cache
        if cached_context := self._get_cached_context(cache_key, "L1"):
            self._cache_hits["L1"] += 1
            return cached_context

        self._cache_misses["L1"] += 1

        try:
            # Get all components for the project
            components = await self.component_service.get_components_by_project(project_id)

            # Get project-level context
            project_context = await self._get_project_context(project_id)

            # Aggregate context from all components
            component_contexts = []
            for component in components:
                try:
                    comp_context = await self.compile_component_context(component.id)
                    component_contexts.append(comp_context)
                except Exception as e:
                    logger.warning("Failed to compile context for component %s: %s", component.id, e)

            # Merge all contexts
            all_contexts = [project_context] + component_contexts
            compiled_context = self._merge_contexts(all_contexts)

            # Add project metadata
            compiled_context["_metadata"] = {
                "project_id": str(project_id),
                "component_count": len(components),
                "compiled_at": datetime.utcnow().isoformat(),
                "compilation_time_ms": round((time.time() - start_time) * 1000, 2),
                "cache_level": "project_compiled"
            }

            # Cache the compiled context (L1)
            self._cache_context(cache_key, compiled_context, "L1")

            duration = time.time() - start_time
            logger.info(
                "Project context compiled successfully",
                project_id=str(project_id),
                component_count=len(components),
                duration_ms=round(duration * 1000, 2)
            )

            return compiled_context

        except Exception as e:
            logger.error("Error compiling project context for %s: %s", project_id, e)
            raise ContextCompilationError(f"Failed to compile context for project {project_id}: {str(e)}")

    async def get_agent_context(self, component_id: UUID, agent_type: str = "general") -> Dict[str, Any]:
        """
        Get optimized context for agent instructions.
        
        Args:
            component_id: Component UUID
            agent_type: Type of agent (general, coder, reviewer, etc.)
            
        Returns:
            Agent-optimized context dictionary
        """
        start_time = time.time()

        try:
            # Get compiled component context
            base_context = await self.compile_component_context(component_id)

            # Optimize context for agent type
            agent_context = self._optimize_context_for_agent(base_context, agent_type)

            # Add agent-specific metadata
            agent_context["_agent_metadata"] = {
                "agent_type": agent_type,
                "optimized_at": datetime.utcnow().isoformat(),
                "optimization_time_ms": round((time.time() - start_time) * 1000, 2)
            }

            duration = time.time() - start_time
            logger.info(
                "Agent context prepared",
                component_id=str(component_id),
                agent_type=agent_type,
                duration_ms=round(duration * 1000, 2)
            )

            return agent_context

        except Exception as e:
            logger.error("Error preparing agent context: %s", e)
            raise ContextCompilationError(f"Failed to prepare agent context: {str(e)}")

    def get_cache_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics."""
        total_hits = sum(self._cache_hits.values())
        total_requests = total_hits + sum(self._cache_misses.values())
        hit_ratio = (total_hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "cache_hit_ratio": round(hit_ratio, 2),
            "total_requests": total_requests,
            "cache_hits": self._cache_hits.copy(),
            "cache_misses": self._cache_misses.copy(),
            "cache_sizes": {
                "L1_compiled": len(self._compiled_context_cache),
                "L2_dependency": len(self._dependency_context_cache),
                "L3_compilation": len(self._context_compilation_cache),
                "L4_db_query": len(self._db_query_cache)
            }
        }

    # Private helper methods for context aggregation

    async def _get_component_context(self, component_id: UUID) -> Dict[str, Any]:
        """Get context data from component itself."""
        cache_key = f"component_data:{component_id}"

        # L4 Cache: Database query cache
        if cached_data := self._get_cached_context(cache_key, "L4"):
            self._cache_hits["L4"] += 1
            return cached_data

        self._cache_misses["L4"] += 1

        try:
            component_response = await self.component_service.get_component(component_id)
            if not component_response.success:
                return {}

            component = component_response.component
            context = {
                "component": {
                    "id": str(component.id),
                    "name": component.name,
                    "description": component.description,
                    "type": component.component_type.value,
                    "status": component.status.value,
                    "context_data": component.context_data,
                    "completion_gates": component.completion_gates,
                    "order_index": component.order_index
                }
            }

            # Cache the result (L4)
            self._cache_context(cache_key, context, "L4")
            return context

        except Exception as e:
            logger.error("Error getting component context for %s: %s", component_id, e)
            return {}

    async def _get_dependency_context(self, component_id: UUID) -> Dict[str, Any]:
        """Get context from component dependencies."""
        cache_key = f"dependency_context:{component_id}"

        # L2 Cache: Dependency context cache
        if cached_context := self._get_cached_context(cache_key, "L2"):
            self._cache_hits["L2"] += 1
            return cached_context

        self._cache_misses["L2"] += 1

        try:
            dependencies = await self.component_service.get_component_dependencies(component_id)

            dependency_contexts = []
            for dep in dependencies:
                dep_context = await self._get_component_context(dep.id)
                if dep_context:
                    dependency_contexts.append(dep_context)

            context = {
                "dependencies": {
                    "count": len(dependencies),
                    "components": dependency_contexts,
                    "dependency_chain": [str(dep.id) for dep in dependencies]
                }
            }

            # Cache the result (L2)
            self._cache_context(cache_key, context, "L2")
            return context

        except Exception as e:
            logger.error("Error getting dependency context for %s: %s", component_id, e)
            return {}

    async def _get_template_context(self, component_id: UUID) -> Dict[str, Any]:
        """Get context from applied templates."""
        cache_key = f"template_context:{component_id}"

        # L3 Cache: Context compilation cache
        if cached_context := self._get_cached_context(cache_key, "L3"):
            self._cache_hits["L3"] += 1
            return cached_context

        self._cache_misses["L3"] += 1

        try:
            # Get component to find associated template
            component_response = await self.component_service.get_component(component_id)
            if not component_response.success:
                return {}

            component = component_response.component

            # For now, we'll look for project-level templates
            # In the future, this could be extended to component-specific templates
            project_context = await self._get_project_context(component.project_id)

            context = {
                "template": {
                    "applied": False,
                    "source": "project_level",
                    "context_data": project_context.get("template", {})
                }
            }

            # Cache the result (L3)
            self._cache_context(cache_key, context, "L3")
            return context

        except Exception as e:
            logger.error("Error getting template context for %s: %s", component_id, e)
            return {}

    async def _get_project_context(self, project_id: UUID) -> Dict[str, Any]:
        """Get context from project level."""
        cache_key = f"project_data:{project_id}"

        # L4 Cache: Database query cache
        if cached_data := self._get_cached_context(cache_key, "L4"):
            self._cache_hits["L4"] += 1
            return cached_data

        self._cache_misses["L4"] += 1

        try:
            # Get project data from database
            result = await self.threading_service.run_io_bound(
                lambda: self.supabase.table("archon_projects")
                .select("*")
                .eq("id", str(project_id))
                .execute()
            )

            if not result.data:
                return {}

            project_data = result.data[0]
            context = {
                "project": {
                    "id": str(project_id),
                    "title": project_data.get("title", ""),
                    "description": project_data.get("description", ""),
                    "prd": project_data.get("prd", {}),
                    "github_repo": project_data.get("github_repo", ""),
                    "created_at": project_data.get("created_at", ""),
                    "updated_at": project_data.get("updated_at", "")
                }
            }

            # Cache the result (L4)
            self._cache_context(cache_key, context, "L4")
            return context

        except Exception as e:
            logger.error("Error getting project context for %s: %s", project_id, e)
            return {}

    async def _get_rag_context(self, component_id: UUID) -> Dict[str, Any]:
        """Get relevant context from RAG system."""
        try:
            # Get component details for RAG query
            component_response = await self.component_service.get_component(component_id)
            if not component_response.success:
                return {}

            component = component_response.component

            # Create search query from component information
            query = f"{component.name} {component.description} {component.component_type.value}"

            # Perform RAG search for relevant context
            success, rag_result = await self.rag_service.perform_rag_query(
                query=query,
                match_count=3  # Limit to top 3 results for performance
            )

            if success and rag_result.get("results"):
                context = {
                    "rag": {
                        "relevant_documents": rag_result["results"],
                        "query_used": query,
                        "result_count": len(rag_result["results"])
                    }
                }
            else:
                context = {
                    "rag": {"relevant_documents": [], "query_used": query, "result_count": 0}
                }

            return context

        except Exception as e:
            logger.error("Error getting RAG context for %s: %s", component_id, e)
            return {"rag": {"relevant_documents": [], "error": str(e)}}

    def _merge_contexts(self, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple context dictionaries with proper precedence.
        Later contexts in the list override earlier ones.
        """
        merged = {}

        for context in contexts:
            if not context:
                continue

            for key, value in context.items():
                if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                    # Recursively merge dictionaries
                    merged[key] = self._merge_dict_recursive(merged[key], value)
                else:
                    # Override with new value
                    merged[key] = value

        return merged

    def _merge_dict_recursive(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recursively merge two dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dict_recursive(result[key], value)
            else:
                result[key] = value

        return result

    def _optimize_context_for_agent(
        self, context: Dict[str, Any], agent_type: str
    ) -> Dict[str, Any]:
        """Optimize context for specific agent types."""
        optimized = context.copy()

        if agent_type == "coder":
            # Focus on technical context for coding agents
            optimized["_agent_focus"] = {
                "technical_requirements": True,
                "code_examples": True,
                "dependencies": True,
                "completion_gates": True
            }
        elif agent_type == "reviewer":
            # Focus on quality and validation context
            optimized["_agent_focus"] = {
                "completion_gates": True,
                "quality_criteria": True,
                "dependencies": True,
                "testing_requirements": True
            }
        else:
            # General agent gets full context
            optimized["_agent_focus"] = {"full_context": True}

        return optimized

    # Caching helper methods

    def _get_cached_context(self, cache_key: str, cache_level: str) -> Optional[Dict[str, Any]]:
        """Get context from appropriate cache level."""
        cache_map = {
            "L1": (self._compiled_context_cache, self._compiled_cache_ttl),
            "L2": (self._dependency_context_cache, self._dependency_cache_ttl),
            "L3": (self._context_compilation_cache, self._compilation_cache_ttl),
            "L4": (self._db_query_cache, self._db_cache_ttl)
        }

        if cache_level not in cache_map:
            return None

        cache, ttl = cache_map[cache_level]

        if cache_key in cache:
            context, timestamp = cache[cache_key]
            if time.time() - timestamp < ttl:
                return context
            # Remove expired entry
            del cache[cache_key]

        return None

    def _cache_context(self, cache_key: str, context: Dict[str, Any], cache_level: str):
        """Cache context at appropriate level."""
        cache_map = {
            "L1": self._compiled_context_cache,
            "L2": self._dependency_context_cache,
            "L3": self._context_compilation_cache,
            "L4": self._db_query_cache
        }

        if cache_level in cache_map:
            cache_map[cache_level][cache_key] = (context, time.time())

    def _invalidate_cache(self, cache_key: str, cache_level: Optional[str] = None):
        """Invalidate cache entries."""
        if cache_level:
            cache_map = {
                "L1": self._compiled_context_cache,
                "L2": self._dependency_context_cache,
                "L3": self._context_compilation_cache,
                "L4": self._db_query_cache
            }
            if cache_level in cache_map and cache_key in cache_map[cache_level]:
                del cache_map[cache_level][cache_key]
        else:
            # Invalidate from all cache levels
            for cache in [
                self._compiled_context_cache,
                self._dependency_context_cache,
                self._context_compilation_cache,
                self._db_query_cache
            ]:
                if cache_key in cache:
                    del cache[cache_key]

    def _cleanup_expired_cache(self):
        """Clean up expired cache entries across all levels."""
        current_time = time.time()

        # Clean L1 cache
        expired_l1 = [
            key for key, (_, timestamp) in self._compiled_context_cache.items()
            if current_time - timestamp >= self._compiled_cache_ttl
        ]
        for key in expired_l1:
            del self._compiled_context_cache[key]

        # Clean L2 cache
        expired_l2 = [
            key for key, (_, timestamp) in self._dependency_context_cache.items()
            if current_time - timestamp >= self._dependency_cache_ttl
        ]
        for key in expired_l2:
            del self._dependency_context_cache[key]

        # Clean L3 cache
        expired_l3 = [
            key for key, (_, timestamp) in self._context_compilation_cache.items()
            if current_time - timestamp >= self._compilation_cache_ttl
        ]
        for key in expired_l3:
            del self._context_compilation_cache[key]

        # Clean L4 cache
        expired_l4 = [
            key for key, (_, timestamp) in self._db_query_cache.items()
            if current_time - timestamp >= self._db_cache_ttl
        ]
        for key in expired_l4:
            del self._db_query_cache[key]

        if expired_l1 or expired_l2 or expired_l3 or expired_l4:
            logger.debug(
                "Cache cleanup completed",
                expired_l1=len(expired_l1),
                expired_l2=len(expired_l2),
                expired_l3=len(expired_l3),
                expired_l4=len(expired_l4)
            )


# Global service instance
_context_compilation_service: Optional[ContextCompilationService] = None


def get_context_compilation_service() -> ContextCompilationService:
    """Get the global context compilation service instance."""
    global _context_compilation_service
    if _context_compilation_service is None:
        _context_compilation_service = ContextCompilationService()
    return _context_compilation_service
