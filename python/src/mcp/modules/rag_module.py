"""
RAG Module for Archon MCP Server (HTTP-based version)

This module provides tools for:
- RAG query and search
- Source management
- Code example extraction and search

This version uses HTTP calls to the server service instead of importing
service modules directly, enabling true microservices architecture.
"""

import json
import logging
import os
from urllib.parse import urljoin

import httpx

from mcp.server.fastmcp import Context, FastMCP

# Import service discovery for HTTP communication
from src.server.config.service_discovery import get_api_url

logger = logging.getLogger(__name__)


def get_setting(key: str, default: str = "false") -> str:
    """Get a setting from environment variable."""
    return os.getenv(key, default)


def get_bool_setting(key: str, default: bool = False) -> bool:
    """Get a boolean setting from environment variable."""
    value = get_setting(key, "false" if not default else "true")
    return value.lower() in ("true", "1", "yes", "on")


def register_rag_tools(mcp: FastMCP):
    """Register all RAG tools with the MCP server."""

    @mcp.tool()
    async def get_available_sources(ctx: Context) -> str:
        """
        Get list of available sources in the knowledge base.

        This tool uses HTTP call to the API service.

        Returns:
            JSON string with list of sources
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(urljoin(api_url, "/api/rag/sources"))

                if response.status_code == 200:
                    result = response.json()
                    sources = result.get("sources", [])

                    return json.dumps(
                        {"success": True, "sources": sources, "count": len(sources)}, indent=2
                    )
                else:
                    error_detail = response.text
                    return json.dumps(
                        {"success": False, "error": f"HTTP {response.status_code}: {error_detail}"},
                        indent=2,
                    )

        except Exception as e:
            logger.error(f"Error getting sources: {e}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)

    @mcp.tool()
    async def perform_rag_query(
        ctx: Context, query: str, source: str = None, match_count: int = 5
    ) -> str:
        """
        Perform a RAG (Retrieval Augmented Generation) query on stored content.

        This tool searches the vector database for content relevant to the query and returns
        the matching documents. Optionally filter by source domain.
        Get the source by using the get_available_sources tool before calling this search!

        Args:
            query: The search query
            source: Optional source domain to filter results (e.g., 'example.com')
            match_count: Maximum number of results to return (default: 5)

        Returns:
            JSON string with search results
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                request_data = {"query": query, "match_count": match_count}
                if source:
                    request_data["source"] = source

                response = await client.post(urljoin(api_url, "/api/rag/query"), json=request_data)

                if response.status_code == 200:
                    result = response.json()
                    return json.dumps(
                        {
                            "success": True,
                            "results": result.get("results", []),
                            "reranked": result.get("reranked", False),
                            "error": None,
                        },
                        indent=2,
                    )
                else:
                    error_detail = response.text
                    return json.dumps(
                        {
                            "success": False,
                            "results": [],
                            "error": f"HTTP {response.status_code}: {error_detail}",
                        },
                        indent=2,
                    )

        except Exception as e:
            logger.error(f"Error performing RAG query: {e}")
            return json.dumps({"success": False, "results": [], "error": str(e)}, indent=2)

    @mcp.tool()
    async def search_code_examples(
        ctx: Context, query: str, source_id: str = None, match_count: int = 5
    ) -> str:
        """
        Search for code examples relevant to the query.

        This tool searches the vector database for code examples relevant to the query and returns
        the matching examples with their summaries. Optionally filter by source_id.
        Get the source_id by using the get_available_sources tool before calling this search!

        Use the get_available_sources tool first to see what sources are available for filtering.

        Args:
            query: The search query
            source_id: Optional source ID to filter results (e.g., 'example.com')
            match_count: Maximum number of results to return (default: 5)

        Returns:
            JSON string with search results
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                request_data = {"query": query, "match_count": match_count}
                if source_id:
                    request_data["source"] = source_id

                # Call the dedicated code examples endpoint
                response = await client.post(
                    urljoin(api_url, "/api/rag/code-examples"), json=request_data
                )

                if response.status_code == 200:
                    result = response.json()
                    return json.dumps(
                        {
                            "success": True,
                            "results": result.get("results", []),
                            "reranked": result.get("reranked", False),
                            "error": None,
                        },
                        indent=2,
                    )
                else:
                    error_detail = response.text
                    return json.dumps(
                        {
                            "success": False,
                            "results": [],
                            "error": f"HTTP {response.status_code}: {error_detail}",
                        },
                        indent=2,
                    )

        except Exception as e:
            logger.error(f"Error searching code examples: {e}")
            return json.dumps({"success": False, "results": [], "error": str(e)}, indent=2)

    # Log successful registration

    @mcp.tool()
    async def upload_document(
        ctx: Context,
        file_path: str,
        knowledge_type: str = "technical",
        tags: str | list[str] | None = None,
    ) -> str:
        """
        Upload a document (Markdown, Text, PDF, DOCX) to Archon knowledge base via HTTP API.

        Args:
            file_path: Absolute or relative path to the file on disk
            knowledge_type: Optional categorization (e.g., "technical", "business")
            tags: Optional tags as JSON string (e.g., '["kb","doc"]') or list of strings

        Returns:
            JSON string with upload result and progressId if started successfully
        """
        import os
        import json as _json
        import mimetypes
        from urllib.parse import urljoin as _urljoin

        try:
            # Resolve and validate file
            abs_path = os.path.abspath(file_path)
            if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
                return _json.dumps({
                    "success": False,
                    "error": f"File not found or not a file: {file_path}"
                }, indent=2)

            filename = os.path.basename(abs_path)
            guessed, _ = mimetypes.guess_type(filename)
            # Better defaults for common docs
            if not guessed:
                ext = os.path.splitext(filename)[1].lower()
                if ext == ".md":
                    guessed = "text/markdown"
                elif ext == ".txt":
                    guessed = "text/plain"
                elif ext == ".pdf":
                    guessed = "application/pdf"
                elif ext == ".docx":
                    guessed = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                else:
                    guessed = "application/octet-stream"

            with open(abs_path, "rb") as f:
                file_bytes = f.read()

            api_url = get_api_url()
            timeout = httpx.Timeout(60.0, connect=10.0)

            # Prepare multipart form
            data_fields = {}
            if knowledge_type:
                data_fields["knowledge_type"] = knowledge_type

            # Normalize tags
            if tags is not None:
                try:
                    if isinstance(tags, list):
                        data_fields["tags"] = _json.dumps(tags)
                    elif isinstance(tags, str):
                        # Accept either a JSON string or a comma-separated list
                        t = tags.strip()
                        if t.startswith("["):
                            # Validate JSON array
                            _ = _json.loads(t)
                            data_fields["tags"] = t
                        else:
                            # convert "a,b,c" to ["a","b","c"]
                            arr = [s.strip() for s in t.split(",") if s.strip()]
                            data_fields["tags"] = _json.dumps(arr)
                    else:
                        data_fields["tags"] = _json.dumps([])
                except Exception as e:
                    return _json.dumps({
                        "success": False,
                        "error": f"Invalid tags format: {e}"
                    }, indent=2)

            files = {"file": (filename, file_bytes, guessed)}

            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(_urljoin(api_url, "/api/documents/upload"), data=data_fields, files=files)
                if resp.status_code == 200:
                    return _json.dumps(resp.json(), indent=2)
                else:
                    # Try to parse JSON error, fallback to text
                    try:
                        err = resp.json()
                    except Exception:
                        err = {"error": resp.text}
                    return _json.dumps({
                        "success": False,
                        "status": resp.status_code,
                        **err
                    }, indent=2)

        except Exception as e:
            logger.error(f"Error uploading document via MCP: {e}")
            return _json.dumps({"success": False, "error": str(e)}, indent=2)

    logger.info("✓ RAG tools registered (HTTP-based version)")
