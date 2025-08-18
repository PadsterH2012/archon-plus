"""
Settings API endpoints for Archon

Handles:
- OpenAI API key management
- Other credentials and configuration
- Settings storage and retrieval
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Import logging
from ..config.logfire_config import logfire
from ..services.credential_service import credential_service
from ..services.embeddings import get_embedding_provider_health
from ..utils import get_supabase_client

router = APIRouter(prefix="/api", tags=["settings"])


class CredentialRequest(BaseModel):
    key: str
    value: str
    is_encrypted: bool = False
    category: str | None = None
    description: str | None = None


class CredentialUpdateRequest(BaseModel):
    value: str
    is_encrypted: bool | None = None
    category: str | None = None
    description: str | None = None


class CredentialResponse(BaseModel):
    success: bool
    message: str


# Credential Management Endpoints
@router.get("/credentials")
async def list_credentials(category: str | None = None):
    """List all credentials and their categories."""
    try:
        logfire.info(f"Listing credentials | category={category}")
        credentials = await credential_service.list_all_credentials()

        if category:
            # Filter by category
            credentials = [cred for cred in credentials if cred.category == category]

        result_count = len(credentials)
        logfire.info(
            f"Credentials listed successfully | count={result_count} | category={category}"
        )

        return [
            {
                "key": cred.key,
                "value": cred.value,
                "encrypted_value": cred.encrypted_value,
                "is_encrypted": cred.is_encrypted,
                "category": cred.category,
                "description": cred.description,
            }
            for cred in credentials
        ]
    except Exception as e:
        logfire.error(f"Error listing credentials | category={category} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/credentials/categories/{category}")
async def get_credentials_by_category(category: str):
    """Get all credentials for a specific category."""
    try:
        logfire.info(f"Getting credentials by category | category={category}")
        credentials = await credential_service.get_credentials_by_category(category)

        logfire.info(
            f"Credentials retrieved by category | category={category} | count={len(credentials)}"
        )

        return {"credentials": credentials}
    except Exception as e:
        logfire.error(
            f"Error getting credentials by category | category={category} | error={str(e)}"
        )
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("/credentials")
async def create_credential(request: CredentialRequest):
    """Create or update a credential."""
    try:
        logfire.info(
            f"Creating/updating credential | key={request.key} | is_encrypted={request.is_encrypted} | category={request.category}"
        )

        success = await credential_service.set_credential(
            key=request.key,
            value=request.value,
            is_encrypted=request.is_encrypted,
            category=request.category,
            description=request.description,
        )

        if success:
            logfire.info(
                f"Credential saved successfully | key={request.key} | is_encrypted={request.is_encrypted}"
            )

            return {
                "success": True,
                "message": f"Credential {request.key} {'encrypted and ' if request.is_encrypted else ''}saved successfully",
            }
        else:
            logfire.error(f"Failed to save credential | key={request.key}")
            raise HTTPException(status_code=500, detail={"error": "Failed to save credential"})

    except Exception as e:
        logfire.error(f"Error creating credential | key={request.key} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


# Define optional settings with their default values
# These are user preferences that should return defaults instead of 404
# This prevents console errors in the frontend when settings haven't been explicitly set
# The frontend can check the 'is_default' flag to know if it's a default or user-set value
OPTIONAL_SETTINGS_WITH_DEFAULTS = {
    "DISCONNECT_SCREEN_ENABLED": "true",  # Show disconnect screen when server is unavailable
    "PROJECTS_ENABLED": "false",  # Enable project management features
    "LOGFIRE_ENABLED": "false",  # Enable Pydantic Logfire integration
}


@router.get("/credentials/{key}")
async def get_credential(key: str, decrypt: bool = True):
    """Get a specific credential by key."""
    try:
        logfire.info(f"Getting credential | key={key} | decrypt={decrypt}")
        value = await credential_service.get_credential(key, decrypt=decrypt)

        if value is None:
            # Check if this is an optional setting with a default value
            if key in OPTIONAL_SETTINGS_WITH_DEFAULTS:
                logfire.info(f"Returning default value for optional setting | key={key}")
                return {
                    "key": key,
                    "value": OPTIONAL_SETTINGS_WITH_DEFAULTS[key],
                    "is_default": True,
                    "category": "features",
                    "description": f"Default value for {key}",
                }

            logfire.warning(f"Credential not found | key={key}")
            raise HTTPException(status_code=404, detail={"error": f"Credential {key} not found"})

        logfire.info(f"Credential retrieved successfully | key={key}")

        # For encrypted credentials, return metadata instead of the actual value for security
        if isinstance(value, dict) and value.get("is_encrypted") and not decrypt:
            return {
                "key": key,
                "is_encrypted": True,
                "category": value.get("category"),
                "description": value.get("description"),
                "has_value": bool(value.get("encrypted_value")),
            }

        return {"key": key, "value": value, "is_encrypted": False}

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error getting credential | key={key} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.put("/credentials/{key}")
async def update_credential(key: str, request: dict[str, Any]):
    """Update an existing credential."""
    try:
        logfire.info(f"Updating credential | key={key}")

        # Handle both CredentialUpdateRequest and full Credential object formats
        if isinstance(request, dict):
            # If the request contains a 'value' field directly, use it
            value = request.get("value", "")
            is_encrypted = request.get("is_encrypted")
            category = request.get("category")
            description = request.get("description")
        else:
            value = request.value
            is_encrypted = request.is_encrypted
            category = request.category
            description = request.description

        # Get existing credential to preserve metadata if not provided
        existing_creds = await credential_service.list_all_credentials()
        existing = next((c for c in existing_creds if c.key == key), None)

        if existing is None:
            # If credential doesn't exist, create it
            is_encrypted = is_encrypted if is_encrypted is not None else False
            logfire.info(f"Creating new credential via PUT | key={key}")
        else:
            # Preserve existing values if not provided
            if is_encrypted is None:
                is_encrypted = existing.is_encrypted
            if category is None:
                category = existing.category
            if description is None:
                description = existing.description
            logfire.info(f"Updating existing credential | key={key} | category={category}")

        success = await credential_service.set_credential(
            key=key,
            value=value,
            is_encrypted=is_encrypted,
            category=category,
            description=description,
        )

        if success:
            logfire.info(
                f"Credential updated successfully | key={key} | is_encrypted={is_encrypted}"
            )

            return {"success": True, "message": f"Credential {key} updated successfully"}
        else:
            logfire.error(f"Failed to update credential | key={key}")
            raise HTTPException(status_code=500, detail={"error": "Failed to update credential"})

    except Exception as e:
        logfire.error(f"Error updating credential | key={key} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.delete("/credentials/{key}")
async def delete_credential(key: str):
    """Delete a credential."""
    try:
        logfire.info(f"Deleting credential | key={key}")
        success = await credential_service.delete_credential(key)

        if success:
            logfire.info(f"Credential deleted successfully | key={key}")

            return {"success": True, "message": f"Credential {key} deleted successfully"}
        else:
            logfire.error(f"Failed to delete credential | key={key}")
            raise HTTPException(status_code=500, detail={"error": "Failed to delete credential"})

    except Exception as e:
        logfire.error(f"Error deleting credential | key={key} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("/credentials/initialize")
async def initialize_credentials_endpoint():
    """Reload credentials from database."""
    try:
        logfire.info("Reloading credentials from database")
        await credential_service.initialize_credentials()

        logfire.info("Credentials reloaded successfully")

        return {"success": True, "message": "Credentials reloaded from database"}
    except Exception as e:
        logfire.error(f"Error reloading credentials | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/database/metrics")
async def database_metrics():
    """Get database metrics and statistics."""
    try:
        logfire.info("Getting database metrics")
        supabase_client = get_supabase_client()

        # Get various table counts
        tables_info = {}

        # Get projects count
        projects_response = (
            supabase_client.table("archon_projects").select("id", count="exact").execute()
        )
        tables_info["projects"] = (
            projects_response.count if projects_response.count is not None else 0
        )

        # Get tasks count
        tasks_response = supabase_client.table("archon_tasks").select("id", count="exact").execute()
        tables_info["tasks"] = tasks_response.count if tasks_response.count is not None else 0

        # Get crawled pages count
        pages_response = (
            supabase_client.table("archon_crawled_pages").select("id", count="exact").execute()
        )
        tables_info["crawled_pages"] = (
            pages_response.count if pages_response.count is not None else 0
        )

        # Get settings count
        settings_response = (
            supabase_client.table("archon_settings").select("id", count="exact").execute()
        )
        tables_info["settings"] = (
            settings_response.count if settings_response.count is not None else 0
        )

        total_records = sum(tables_info.values())
        logfire.info(
            f"Database metrics retrieved | total_records={total_records} | tables={tables_info}"
        )

        return {
            "status": "healthy",
            "database": "supabase",
            "tables": tables_info,
            "total_records": total_records,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logfire.error(f"Error getting database metrics | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/settings/health")
async def settings_health():
    """Health check for settings API."""
    logfire.info("Settings health check requested")
    result = {"status": "healthy", "service": "settings"}

    return result


@router.get("/provider-health")
async def get_provider_health():
    """
    Get health status of all embedding providers.

    Returns provider health information including failure counts,
    last failure times, and whether providers are currently healthy.
    """
    try:
        logfire.info("Getting provider health status")
        health_status = await get_embedding_provider_health()

        # Add summary statistics
        total_providers = len(health_status)
        healthy_providers = sum(1 for status in health_status.values() if status["is_healthy"])
        unhealthy_providers = total_providers - healthy_providers

        overall_health = "healthy" if unhealthy_providers == 0 else "degraded" if healthy_providers > 0 else "critical"

        logfire.info(
            f"Provider health retrieved | total={total_providers} | healthy={healthy_providers} | unhealthy={unhealthy_providers} | overall={overall_health}"
        )

        return {
            "providers": health_status,
            "summary": {
                "total_providers": total_providers,
                "healthy_providers": healthy_providers,
                "unhealthy_providers": unhealthy_providers,
                "overall_health": overall_health
            }
        }
    except Exception as e:
        logfire.error(f"Error getting provider health | error={str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get provider health: {str(e)}")


@router.post("/provider-health/reset")
async def reset_provider_health():
    """
    Reset health status for all providers.

    This clears failure counts and marks all providers as healthy.
    Useful for testing or after resolving provider issues.
    """
    try:
        logfire.info("Resetting provider health status")
        from ..services.embeddings.embedding_fallback_service import embedding_fallback_service

        # Reset all provider health
        provider_count = len(embedding_fallback_service.provider_health)
        embedding_fallback_service.provider_health.clear()

        logfire.info(f"Provider health reset successfully | providers_reset={provider_count}")

        return {"success": True, "message": f"Provider health status reset for {provider_count} providers"}
    except Exception as e:
        logfire.error(f"Error resetting provider health | error={str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reset provider health: {str(e)}")


@router.post("/test-chat-provider")
async def test_chat_provider(request: dict[str, Any]):
    """
    Test a chat provider connection and validate it's working.

    Args:
        request: Dict containing provider, api_key, base_url, model

    Returns:
        Dict with success status and details
    """
    try:
        provider = request.get("provider")
        api_key = request.get("api_key")
        base_url = request.get("base_url")
        model = request.get("model", "gpt-4o-mini")

        if not provider:
            raise HTTPException(status_code=400, detail="Provider is required")

        logfire.info(f"Testing chat provider | provider={provider} | model={model}")

        # Import here to avoid circular imports
        from ..services.llm_provider_service import get_llm_client

        # Test the provider with a simple chat completion
        async with get_llm_client(provider=provider) as client:
            # Override client configuration if custom values provided
            if api_key:
                client.api_key = api_key
            if base_url:
                client.base_url = base_url

            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hello, this is a connection test. Please respond with 'OK'."}],
                max_tokens=10,
                temperature=0
            )

            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                logfire.info(f"Chat provider test successful | provider={provider} | response_length={len(content) if content else 0}")

                return {
                    "success": True,
                    "provider": provider,
                    "model": model,
                    "message": "Provider connection successful",
                    "test_response": content[:50] + "..." if content and len(content) > 50 else content
                }
            else:
                raise Exception("No response received from provider")

    except Exception as e:
        error_msg = str(e)
        logfire.error(f"Chat provider test failed | provider={provider} | error={error_msg}")

        return {
            "success": False,
            "provider": provider,
            "error": error_msg,
            "message": f"Provider connection failed: {error_msg}"
        }


@router.post("/test-embedding-provider")
async def test_embedding_provider(request: dict[str, Any]):
    """
    Test an embedding provider connection and validate it's working.

    Args:
        request: Dict containing provider, api_key, base_url, model

    Returns:
        Dict with success status and details
    """
    try:
        provider = request.get("provider")
        api_key = request.get("api_key")
        base_url = request.get("base_url")
        model = request.get("model", "text-embedding-3-small")

        if not provider:
            raise HTTPException(status_code=400, detail="Provider is required")

        logfire.info(f"Testing embedding provider | provider={provider} | model={model}")

        # Import here to avoid circular imports
        from ..services.llm_provider_service import get_llm_client

        # Test the provider with a simple embedding
        async with get_llm_client(provider=provider, use_embedding_provider=True) as client:
            # Override client configuration if custom values provided
            if api_key:
                client.api_key = api_key
            if base_url:
                client.base_url = base_url

            response = await client.embeddings.create(
                model=model,
                input=["This is a test embedding to validate the provider connection."]
            )

            if response.data and len(response.data) > 0 and response.data[0].embedding:
                embedding_length = len(response.data[0].embedding)
                logfire.info(f"Embedding provider test successful | provider={provider} | embedding_length={embedding_length}")

                return {
                    "success": True,
                    "provider": provider,
                    "model": model,
                    "message": "Provider connection successful",
                    "embedding_dimensions": embedding_length
                }
            else:
                raise Exception("No embedding received from provider")

    except Exception as e:
        error_msg = str(e)
        logfire.error(f"Embedding provider test failed | provider={provider} | error={error_msg}")

        return {
            "success": False,
            "provider": provider,
            "error": error_msg,
            "message": f"Provider connection failed: {error_msg}"
        }
