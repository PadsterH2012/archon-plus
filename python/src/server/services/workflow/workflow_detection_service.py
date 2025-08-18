"""
Workflow Detection Service

Provides intelligent workflow suggestion and detection capabilities for task management.
Integrates with the existing workflow system to suggest relevant workflows based on task descriptions.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logfire

from ..embeddings.embedding_service import create_embedding
from .workflow_repository import WorkflowRepository
from .mcp_tool_integration import get_mcp_workflow_integration
from ...models.workflow_models import WorkflowTemplate
from ...models.mcp_workflow_examples import get_all_mcp_example_workflows, list_mcp_example_workflows


class WorkflowDetectionService:
    """
    Service for detecting and suggesting workflows based on task descriptions.
    
    Features:
    - Keyword-based workflow matching
    - Semantic similarity using embeddings
    - MCP tool integration suggestions
    - Workflow parameter extraction from task context
    - Task-to-workflow binding recommendations
    """
    
    def __init__(self, supabase_client):
        self.supabase_client = supabase_client
        self.workflow_repository = WorkflowRepository(supabase_client)
        self.mcp_integration = get_mcp_workflow_integration()
        
        # Common workflow patterns and keywords
        self.workflow_patterns = {
            "project_setup": {
                "keywords": ["setup", "initialize", "create project", "scaffold", "bootstrap", "new project"],
                "description": "Project initialization and setup workflows",
                "category": "project_management"
            },
            "documentation": {
                "keywords": ["document", "docs", "readme", "guide", "manual", "specification"],
                "description": "Documentation creation and management workflows",
                "category": "documentation"
            },
            "testing": {
                "keywords": ["test", "testing", "unit test", "integration test", "qa", "quality"],
                "description": "Testing and quality assurance workflows",
                "category": "testing"
            },
            "deployment": {
                "keywords": ["deploy", "deployment", "release", "publish", "production"],
                "description": "Deployment and release workflows",
                "category": "deployment"
            },
            "research": {
                "keywords": ["research", "investigate", "analyze", "study", "explore"],
                "description": "Research and investigation workflows",
                "category": "research"
            },
            "code_review": {
                "keywords": ["review", "code review", "pr", "pull request", "merge"],
                "description": "Code review and collaboration workflows",
                "category": "collaboration"
            },
            "monitoring": {
                "keywords": ["monitor", "health check", "status", "metrics", "analytics"],
                "description": "Monitoring and health check workflows",
                "category": "monitoring"
            },
            "data_processing": {
                "keywords": ["process", "transform", "migrate", "import", "export"],
                "description": "Data processing and transformation workflows",
                "category": "data"
            }
        }
    
    async def detect_workflows_for_task(
        self,
        task_title: str,
        task_description: str,
        project_id: Optional[str] = None,
        max_suggestions: int = 5
    ) -> Dict[str, Any]:
        """
        Detect and suggest workflows for a given task.
        
        Args:
            task_title: Title of the task
            task_description: Description of the task
            project_id: Optional project ID for context
            max_suggestions: Maximum number of workflow suggestions
            
        Returns:
            Dictionary containing workflow suggestions and metadata
        """
        try:
            logfire.info(f"Detecting workflows for task | title={task_title} | project_id={project_id}")
            
            # Combine title and description for analysis
            full_text = f"{task_title} {task_description}".strip()
            
            # Get workflow suggestions using multiple methods
            keyword_suggestions = await self._get_keyword_based_suggestions(full_text)
            mcp_suggestions = await self._get_mcp_workflow_suggestions(full_text)
            existing_suggestions = await self._get_existing_workflow_suggestions(full_text, project_id)
            
            # Combine and rank suggestions
            all_suggestions = []
            all_suggestions.extend(keyword_suggestions)
            all_suggestions.extend(mcp_suggestions)
            all_suggestions.extend(existing_suggestions)
            
            # Remove duplicates and rank by score
            unique_suggestions = self._deduplicate_and_rank_suggestions(all_suggestions)
            
            # Limit to max suggestions
            top_suggestions = unique_suggestions[:max_suggestions]
            
            # Extract potential workflow parameters
            extracted_parameters = self._extract_workflow_parameters(full_text)
            
            # Generate workflow binding recommendations
            binding_recommendations = self._generate_binding_recommendations(
                task_title, task_description, top_suggestions
            )
            
            result = {
                "task_title": task_title,
                "task_description": task_description,
                "workflow_suggestions": top_suggestions,
                "extracted_parameters": extracted_parameters,
                "binding_recommendations": binding_recommendations,
                "detection_metadata": {
                    "total_suggestions_found": len(all_suggestions),
                    "keyword_matches": len(keyword_suggestions),
                    "mcp_matches": len(mcp_suggestions),
                    "existing_workflow_matches": len(existing_suggestions),
                    "detected_at": datetime.now().isoformat()
                }
            }
            
            logfire.info(f"Workflow detection completed | suggestions={len(top_suggestions)}")
            return result
            
        except Exception as e:
            logfire.error(f"Error detecting workflows for task | error={str(e)}")
            return {
                "task_title": task_title,
                "task_description": task_description,
                "workflow_suggestions": [],
                "extracted_parameters": {},
                "binding_recommendations": [],
                "error": str(e)
            }

    async def _get_keyword_based_suggestions(self, text: str) -> List[Dict[str, Any]]:
        """Get workflow suggestions based on keyword matching."""
        suggestions = []
        text_lower = text.lower()

        for pattern_name, pattern_info in self.workflow_patterns.items():
            score = 0
            matched_keywords = []

            # Check for keyword matches
            for keyword in pattern_info["keywords"]:
                if keyword.lower() in text_lower:
                    score += 1
                    matched_keywords.append(keyword)

            if score > 0:
                suggestions.append({
                    "type": "keyword_pattern",
                    "pattern_name": pattern_name,
                    "title": pattern_info["description"],
                    "category": pattern_info["category"],
                    "score": score,
                    "confidence": min(score / len(pattern_info["keywords"]), 1.0),
                    "matched_keywords": matched_keywords,
                    "suggestion_reason": f"Matched {score} keywords: {', '.join(matched_keywords)}"
                })

        return suggestions

    async def _get_mcp_workflow_suggestions(self, text: str) -> List[Dict[str, Any]]:
        """Get MCP workflow suggestions based on text analysis."""
        suggestions = []

        try:
            # Get all MCP example workflows
            mcp_workflows = get_all_mcp_example_workflows()

            for workflow_name, workflow in mcp_workflows.items():
                score = self._calculate_text_similarity(text, workflow.description)

                # Also check title and tags
                title_score = self._calculate_text_similarity(text, workflow.title)
                tag_score = 0
                if workflow.tags:
                    tag_text = " ".join(workflow.tags)
                    tag_score = self._calculate_text_similarity(text, tag_text)

                # Combined score
                total_score = score + (title_score * 0.5) + (tag_score * 0.3)

                if total_score > 0.1:  # Minimum threshold
                    suggestions.append({
                        "type": "mcp_workflow",
                        "workflow_name": workflow_name,
                        "title": workflow.title,
                        "description": workflow.description,
                        "category": workflow.category,
                        "tags": workflow.tags,
                        "score": total_score,
                        "confidence": min(total_score, 1.0),
                        "suggestion_reason": f"MCP workflow with {total_score:.2f} similarity",
                        "workflow_data": workflow.dict()
                    })

        except Exception as e:
            logfire.warning(f"Error getting MCP workflow suggestions | error={str(e)}")

        return suggestions

    async def _get_existing_workflow_suggestions(
        self,
        text: str,
        project_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get suggestions from existing workflows in the system."""
        suggestions = []

        try:
            # Get existing workflows
            success, result = await self.workflow_repository.list_workflow_templates(
                limit=50,  # Reasonable limit for analysis
                offset=0
            )

            if success and result.get("workflows"):
                for workflow in result["workflows"]:
                    # Calculate similarity with workflow title and description
                    title_score = self._calculate_text_similarity(text, workflow.get("title", ""))
                    desc_score = self._calculate_text_similarity(
                        text, workflow.get("description", "")
                    )

                    # Boost score if same project
                    same_project = project_id and workflow.get("project_id") == project_id
                    project_boost = 0.2 if same_project else 0

                    total_score = max(title_score, desc_score) + project_boost

                    if total_score > 0.15:  # Minimum threshold
                        suggestions.append({
                            "type": "existing_workflow",
                            "workflow_id": workflow.get("id"),
                            "workflow_name": workflow.get("name"),
                            "title": workflow.get("title"),
                            "description": workflow.get("description"),
                            "category": workflow.get("category"),
                            "tags": workflow.get("tags", []),
                            "score": total_score,
                            "confidence": min(total_score, 1.0),
                            "suggestion_reason": f"Existing workflow with {total_score:.2f} similarity",
                            "is_same_project": same_project
                        })

        except Exception as e:
            logfire.warning(f"Error getting existing workflow suggestions | error={str(e)}")

        return suggestions

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity based on common words."""
        if not text1 or not text2:
            return 0.0

        # Convert to lowercase and split into words
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))

        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        words1 = words1 - stop_words
        words2 = words2 - stop_words

        if not words1 or not words2:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    def _deduplicate_and_rank_suggestions(
        self, suggestions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicates and rank suggestions by score."""
        # Group by workflow name/pattern to remove duplicates
        unique_suggestions = {}

        for suggestion in suggestions:
            # Create a unique key based on type and name
            if suggestion["type"] == "keyword_pattern":
                key = f"pattern_{suggestion['pattern_name']}"
            elif suggestion["type"] == "mcp_workflow":
                key = f"mcp_{suggestion['workflow_name']}"
            elif suggestion["type"] == "existing_workflow":
                key = f"existing_{suggestion['workflow_id']}"
            else:
                key = f"unknown_{suggestion.get('title', 'unnamed')}"

            # Keep the suggestion with the highest score
            current_score = unique_suggestions.get(key, {}).get("score", 0)
            if key not in unique_suggestions or suggestion["score"] > current_score:
                unique_suggestions[key] = suggestion

        # Sort by score (descending) and confidence
        ranked_suggestions = sorted(
            unique_suggestions.values(),
            key=lambda x: (x["score"], x["confidence"]),
            reverse=True
        )

        return ranked_suggestions

    def _extract_workflow_parameters(self, text: str) -> Dict[str, Any]:
        """Extract potential workflow parameters from task text."""
        parameters = {}

        # Extract URLs
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        if urls:
            parameters["urls"] = urls

        # Extract file paths
        file_pattern = r'[./][\w/.-]+\.\w+'
        files = re.findall(file_pattern, text)
        if files:
            parameters["files"] = files

        # Extract quoted strings (potential names, titles)
        quoted_pattern = r'"([^"]+)"'
        quoted_strings = re.findall(quoted_pattern, text)
        if quoted_strings:
            parameters["quoted_strings"] = quoted_strings

        # Extract technology/framework mentions
        tech_keywords = [
            'react', 'vue', 'angular', 'python', 'javascript', 'typescript', 'node',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'postgres', 'mysql',
            'redis', 'mongodb', 'fastapi', 'express', 'django', 'flask'
        ]

        mentioned_tech = []
        text_lower = text.lower()
        for tech in tech_keywords:
            if tech in text_lower:
                mentioned_tech.append(tech)

        if mentioned_tech:
            parameters["technologies"] = mentioned_tech

        return parameters

    def _generate_binding_recommendations(
        self,
        task_title: str,
        task_description: str,
        workflow_suggestions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations for binding tasks to workflows."""
        recommendations = []

        for suggestion in workflow_suggestions[:3]:  # Top 3 suggestions
            recommendation = {
                "workflow_suggestion": suggestion,
                "binding_type": "automatic",
                "confidence": suggestion["confidence"],
                "recommended_action": "suggest_to_user",
                "binding_context": {
                    "task_title": task_title,
                    "task_description": task_description,
                    "match_reason": suggestion["suggestion_reason"]
                }
            }

            # Determine binding type based on confidence
            if suggestion["confidence"] > 0.8:
                recommendation["binding_type"] = "auto_execute"
                recommendation["recommended_action"] = "auto_bind_and_execute"
            elif suggestion["confidence"] > 0.6:
                recommendation["binding_type"] = "suggest_with_preview"
                recommendation["recommended_action"] = "show_preview_and_suggest"
            else:
                recommendation["binding_type"] = "manual_review"
                recommendation["recommended_action"] = "suggest_for_manual_review"

            # Add specific recommendations based on workflow type
            if suggestion["type"] == "mcp_workflow":
                recommendation["execution_notes"] = [
                    "This is an MCP-integrated workflow",
                    "Parameters will be auto-extracted from task context",
                    "Execution can be triggered automatically"
                ]
            elif suggestion["type"] == "existing_workflow":
                recommendation["execution_notes"] = [
                    "This workflow already exists in your project",
                    "Consider reusing or adapting this workflow",
                    "Check if parameters need customization"
                ]
            else:
                recommendation["execution_notes"] = [
                    "This is a pattern-based suggestion",
                    "May require manual workflow creation",
                    "Use as a template for new workflow"
                ]

            recommendations.append(recommendation)

        return recommendations


# Global service instance
WORKFLOW_DETECTION_SERVICE = None


def get_workflow_detection_service(supabase_client=None):
    """Get the global workflow detection service instance."""
    global WORKFLOW_DETECTION_SERVICE

    if WORKFLOW_DETECTION_SERVICE is None:
        if supabase_client is None:
            # Import here to avoid circular imports
            try:
                from ...database.supabase_client import get_supabase_client
                supabase_client = get_supabase_client()
            except ImportError:
                # Fallback for testing or different import paths
                from ...database import get_supabase_client
                supabase_client = get_supabase_client()
        WORKFLOW_DETECTION_SERVICE = WorkflowDetectionService(supabase_client)

    return WORKFLOW_DETECTION_SERVICE
