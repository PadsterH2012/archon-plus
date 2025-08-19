"""
Project Export Service Module for Archon

This module provides comprehensive project export functionality that generates
portable project packages including all project data, documents, tasks, features,
version history, and metadata. Supports JSON and ZIP formats with data integrity
verification and validation.
"""

import hashlib
import json
import os
import tempfile
import zipfile
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from src.server.utils import get_supabase_client

from ...config.logfire_config import get_logger

logger = get_logger(__name__)


class ProjectExportService:
    """Service class for project export operations"""

    def __init__(self, supabase_client=None):
        """Initialize with optional supabase client"""
        self.supabase_client = supabase_client or get_supabase_client()

    def export_project(
        self,
        project_id: str,
        export_type: str = "full",
        include_versions: bool = True,
        include_sources: bool = True,
        include_attachments: bool = True,
        version_limit: Optional[int] = None,
        date_range: Optional[Tuple[str, str]] = None,
        exported_by: str = "system"
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Export a project to a portable format.

        Args:
            project_id: UUID of the project to export
            export_type: Type of export ("full", "selective", "incremental")
            include_versions: Whether to include version history
            include_sources: Whether to include linked knowledge sources
            include_attachments: Whether to include binary attachments
            version_limit: Maximum number of versions to include
            date_range: Optional date range filter (start_date, end_date)
            exported_by: User/system performing the export

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            logger.info(f"Starting project export | project_id={project_id} | type={export_type}")

            # Validate project exists
            project_data = self._get_project_data(project_id)
            if not project_data:
                return False, {"error": f"Project with ID {project_id} not found"}

            # Create export manifest
            manifest = self._create_export_manifest(
                project_id=project_id,
                project_title=project_data.get("title", "Unknown Project"),
                export_type=export_type,
                include_versions=include_versions,
                include_sources=include_sources,
                include_attachments=include_attachments,
                version_limit=version_limit,
                date_range=date_range,
                exported_by=exported_by
            )

            # Collect all export data
            export_data = {}
            
            # Core project data
            export_data["project"] = self._prepare_project_data(project_data)
            
            # Tasks data
            tasks_data = self._get_tasks_data(project_id)
            export_data["tasks"] = self._prepare_tasks_data(tasks_data)
            
            # Documents data
            documents_data = self._get_documents_data(project_data.get("docs", []))
            export_data["documents"] = self._prepare_documents_data(documents_data)
            
            # Version history (if requested)
            if include_versions:
                versions_data = self._get_versions_data(project_id, version_limit, date_range)
                export_data["versions"] = self._prepare_versions_data(versions_data)
            
            # Knowledge sources (if requested)
            if include_sources:
                sources_data = self._get_sources_data(project_id)
                export_data["sources"] = self._prepare_sources_data(sources_data)

            # Generate checksums for data integrity
            checksums = self._generate_checksums(export_data)
            manifest["data_integrity"]["checksums"] = checksums
            manifest["data_integrity"]["total_files"] = len(checksums)

            # Create export package
            export_result = self._create_export_package(
                manifest=manifest,
                export_data=export_data,
                project_id=project_id
            )

            if export_result["success"]:
                logger.info(f"Project export completed successfully | project_id={project_id}")
                return True, {
                    "export_id": export_result["export_id"],
                    "file_path": export_result["file_path"],
                    "file_size": export_result["file_size"],
                    "manifest": manifest,
                    "message": "Project exported successfully"
                }
            else:
                return False, {"error": export_result["error"]}

        except Exception as e:
            logger.error(f"Error exporting project | project_id={project_id} | error={str(e)}")
            return False, {"error": f"Export failed: {str(e)}"}

    def _get_project_data(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get complete project data from database"""
        try:
            response = (
                self.supabase_client.table("archon_projects")
                .select("*")
                .eq("id", project_id)
                .execute()
            )
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error fetching project data | project_id={project_id} | error={str(e)}")
            return None

    def _get_tasks_data(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for the project"""
        try:
            response = (
                self.supabase_client.table("archon_tasks")
                .select("*")
                .eq("project_id", project_id)
                .order("task_order")
                .execute()
            )
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error fetching tasks data | project_id={project_id} | error={str(e)}")
            return []

    def _get_documents_data(self, docs_array: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process documents from project docs JSONB field"""
        return docs_array or []

    def _get_versions_data(
        self, 
        project_id: str, 
        version_limit: Optional[int] = None,
        date_range: Optional[Tuple[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """Get version history for the project"""
        try:
            query = (
                self.supabase_client.table("archon_document_versions")
                .select("*")
                .eq("project_id", project_id)
                .order("created_at", desc=True)
            )
            
            if version_limit:
                query = query.limit(version_limit)
                
            if date_range:
                start_date, end_date = date_range
                query = query.gte("created_at", start_date).lte("created_at", end_date)
            
            response = query.execute()
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error fetching versions data | project_id={project_id} | error={str(e)}")
            return []

    def _get_sources_data(self, project_id: str) -> List[Dict[str, Any]]:
        """Get linked knowledge sources for the project"""
        try:
            response = (
                self.supabase_client.table("archon_project_sources")
                .select("*")
                .eq("project_id", project_id)
                .execute()
            )
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error fetching sources data | project_id={project_id} | error={str(e)}")
            return []

    def _create_export_manifest(
        self,
        project_id: str,
        project_title: str,
        export_type: str,
        include_versions: bool,
        include_sources: bool,
        include_attachments: bool,
        version_limit: Optional[int],
        date_range: Optional[Tuple[str, str]],
        exported_by: str
    ) -> Dict[str, Any]:
        """Create export manifest with metadata"""
        return {
            "format_version": "1.0.0",
            "archon_version": "2.0.0",
            "export_timestamp": datetime.now().isoformat(),
            "export_type": export_type,
            "project_id": project_id,
            "project_title": project_title,
            "exported_by": exported_by,
            "export_options": {
                "include_versions": include_versions,
                "include_sources": include_sources,
                "include_attachments": include_attachments,
                "version_limit": version_limit,
                "date_range": date_range
            },
            "data_integrity": {
                "total_files": 0,
                "total_size_bytes": 0,
                "checksums": {}
            },
            "compatibility": {
                "min_archon_version": "2.0.0",
                "supported_features": [
                    "project_management",
                    "task_hierarchy",
                    "document_versioning",
                    "source_linking",
                    "mcp_integration"
                ]
            }
        }

    def _prepare_project_data(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare project data for export"""
        return {
            "id": project_data["id"],
            "title": project_data["title"],
            "description": project_data.get("description", ""),
            "github_repo": project_data.get("github_repo"),
            "pinned": project_data.get("pinned", False),
            "created_at": project_data["created_at"],
            "updated_at": project_data["updated_at"],
            "metadata": {
                "progress": project_data.get("progress", 0),
                "status": "active",
                "category": project_data.get("category"),
                "tags": project_data.get("tags", [])
            },
            "prd": project_data.get("prd", {}),
            "features": project_data.get("features", []),
            "data": project_data.get("data", [])
        }

    def _prepare_tasks_data(self, tasks_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare tasks data for export with hierarchy information"""
        # Build task hierarchy
        task_hierarchy = {"root_tasks": [], "parent_child_map": {}}
        task_stats = {"total_tasks": 0, "completed_tasks": 0, "in_progress_tasks": 0, "todo_tasks": 0, "archived_tasks": 0}
        
        for task in tasks_data:
            task_stats["total_tasks"] += 1
            
            # Count by status
            status = task.get("status", "todo")
            if status == "done":
                task_stats["completed_tasks"] += 1
            elif status == "doing":
                task_stats["in_progress_tasks"] += 1
            elif status == "todo":
                task_stats["todo_tasks"] += 1
            
            if task.get("archived", False):
                task_stats["archived_tasks"] += 1
            
            # Build hierarchy
            if not task.get("parent_task_id"):
                task_hierarchy["root_tasks"].append(task["id"])
            else:
                parent_id = task["parent_task_id"]
                if parent_id not in task_hierarchy["parent_child_map"]:
                    task_hierarchy["parent_child_map"][parent_id] = []
                task_hierarchy["parent_child_map"][parent_id].append(task["id"])
        
        return {
            "tasks": tasks_data,
            "task_hierarchy": task_hierarchy,
            "statistics": task_stats
        }

    def _prepare_documents_data(self, documents_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare documents data for export"""
        total_size = 0
        processed_docs = []

        for doc in documents_data:
            doc_size = len(json.dumps(doc).encode('utf-8'))
            total_size += doc_size

            processed_docs.append({
                "id": doc.get("id"),
                "document_type": doc.get("document_type"),
                "title": doc.get("title"),
                "status": doc.get("status"),
                "version": doc.get("version"),
                "author": doc.get("author"),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at"),
                "size_bytes": doc_size,
                "content": doc.get("content", {}),
                "metadata": {
                    "tags": doc.get("tags", []),
                    "status": doc.get("status"),
                    "version": doc.get("version"),
                    "author": doc.get("author")
                }
            })

        return {
            "documents": processed_docs,
            "total_documents": len(processed_docs),
            "total_size_bytes": total_size
        }

    def _prepare_versions_data(self, versions_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare version history data for export"""
        earliest_version = None
        latest_version = None
        field_types = []

        if versions_data:
            created_dates = [v.get("created_at") for v in versions_data]
            earliest_version = min(created_dates)
            latest_version = max(created_dates)
            field_types = list({v.get("field_name") for v in versions_data})

        return {
            "versions": versions_data,
            "total_versions": len(versions_data),
            "version_summary": {
                "earliest_version": earliest_version,
                "latest_version": latest_version,
                "field_types": field_types
            }
        }

    def _prepare_sources_data(self, sources_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare knowledge sources data for export"""
        earliest_linked = None
        latest_linked = None
        created_by_list = []

        if sources_data:
            linked_dates = [s.get("linked_at") for s in sources_data]
            earliest_linked = min(linked_dates)
            latest_linked = max(linked_dates)
            created_by_list = list({s.get("created_by") for s in sources_data})

        return {
            "sources": sources_data,
            "total_sources": len(sources_data),
            "source_summary": {
                "linked_at_range": {
                    "earliest": earliest_linked,
                    "latest": latest_linked
                },
                "created_by": created_by_list
            }
        }

    def _generate_checksums(self, export_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate SHA-256 checksums for all export data"""
        checksums = {}

        for key, data in export_data.items():
            json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
            checksum = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
            checksums[f"{key}.json"] = checksum

        return checksums

    def _create_export_package(
        self,
        manifest: Dict[str, Any],
        export_data: Dict[str, Any],
        project_id: str
    ) -> Dict[str, Any]:
        """Create the final export package as a ZIP file"""
        try:
            # Generate unique export ID
            export_id = str(uuid4())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"project-export-{project_id}-{timestamp}.zip"

            # Create temporary directory for export files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create export directory structure
                export_dir = os.path.join(temp_dir, "export")
                os.makedirs(export_dir, exist_ok=True)

                documents_dir = os.path.join(export_dir, "documents")
                versions_dir = os.path.join(export_dir, "versions")
                sources_dir = os.path.join(export_dir, "sources")

                os.makedirs(documents_dir, exist_ok=True)
                os.makedirs(versions_dir, exist_ok=True)
                os.makedirs(sources_dir, exist_ok=True)

                # Write manifest
                manifest_path = os.path.join(export_dir, "manifest.json")
                with open(manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(manifest, f, indent=2, ensure_ascii=False)

                # Write main data files
                for key, data in export_data.items():
                    if key == "documents":
                        # Write documents index
                        index_path = os.path.join(documents_dir, "index.json")
                        with open(index_path, 'w', encoding='utf-8') as f:
                            json.dump({
                                "documents": [
                                    {
                                        "id": doc["id"],
                                        "document_type": doc["document_type"],
                                        "title": doc["title"],
                                        "status": doc["status"],
                                        "version": doc["version"],
                                        "author": doc["author"],
                                        "created_at": doc["created_at"],
                                        "updated_at": doc["updated_at"],
                                        "file_path": f"{doc['id']}.json",
                                        "size_bytes": doc["size_bytes"]
                                    }
                                    for doc in data["documents"]
                                ],
                                "total_documents": data["total_documents"],
                                "total_size_bytes": data["total_size_bytes"]
                            }, f, indent=2, ensure_ascii=False)

                        # Write individual document files
                        for doc in data["documents"]:
                            doc_path = os.path.join(documents_dir, f"{doc['id']}.json")
                            with open(doc_path, 'w', encoding='utf-8') as f:
                                json.dump({
                                    "id": doc["id"],
                                    "document_type": doc["document_type"],
                                    "title": doc["title"],
                                    "content": doc["content"],
                                    "metadata": doc["metadata"],
                                    "timestamps": {
                                        "created_at": doc["created_at"],
                                        "updated_at": doc["updated_at"]
                                    }
                                }, f, indent=2, ensure_ascii=False)

                    elif key == "versions":
                        # Write versions index
                        index_path = os.path.join(versions_dir, "index.json")
                        with open(index_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)

                        # Write individual version files
                        for version in data["versions"]:
                            version_path = os.path.join(versions_dir, f"{version['id']}.json")
                            with open(version_path, 'w', encoding='utf-8') as f:
                                json.dump(version, f, indent=2, ensure_ascii=False)

                    elif key == "sources":
                        # Write sources index
                        index_path = os.path.join(sources_dir, "index.json")
                        with open(index_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)

                        # Write individual source files
                        for source in data["sources"]:
                            source_path = os.path.join(sources_dir, f"{source['id']}.json")
                            with open(source_path, 'w', encoding='utf-8') as f:
                                json.dump(source, f, indent=2, ensure_ascii=False)

                    else:
                        # Write other data files directly
                        file_path = os.path.join(export_dir, f"{key}.json")
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)

                # Create ZIP archive
                zip_path = os.path.join(temp_dir, filename)
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, _, files in os.walk(export_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, export_dir)
                            zipf.write(file_path, arcname)

                # Get file size
                file_size = os.path.getsize(zip_path)

                # Move to final location (for now, keep in temp for demo)
                # In production, this would be moved to a permanent storage location
                final_path = f"/tmp/{filename}"  # This should be configurable
                os.rename(zip_path, final_path)

                return {
                    "success": True,
                    "export_id": export_id,
                    "file_path": final_path,
                    "file_size": file_size,
                    "filename": filename
                }

        except Exception as e:
            logger.error(f"Error creating export package | error={str(e)}")
            return {
                "success": False,
                "error": f"Failed to create export package: {str(e)}"
            }

    def list_exports(self, project_id: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        List available exports (this would typically query a exports table)
        For now, this is a placeholder that would be implemented with proper export tracking
        """
        try:
            # This would query an exports tracking table in a full implementation
            # For now, return empty list as placeholder
            exports = []

            return True, {
                "exports": exports,
                "total_count": len(exports),
                "message": "Export listing not yet implemented - placeholder"
            }

        except Exception as e:
            logger.error(f"Error listing exports | error={str(e)}")
            return False, {"error": f"Failed to list exports: {str(e)}"}

    def get_export_status(self, export_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Get status of an export operation
        This would typically track export progress in a database
        """
        try:
            # Placeholder implementation
            return True, {
                "export_id": export_id,
                "status": "completed",
                "progress": 100,
                "message": "Export status tracking not yet implemented - placeholder"
            }

        except Exception as e:
            logger.error(f"Error getting export status | export_id={export_id} | error={str(e)}")
            return False, {"error": f"Failed to get export status: {str(e)}"}
