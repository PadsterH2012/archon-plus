#!/usr/bin/env python3
"""
Add Git Commit/Push Workflow to Database

This script adds the git commit/push workflow to the Archon workflow system.
It uses the workflow API to create the workflow template.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from python.src.server.models.mcp_workflow_examples import create_git_commit_push_workflow
from python.src.server.services.workflow.workflow_repository import WorkflowRepository
from python.src.server.utils import get_supabase_client


async def add_git_workflow():
    """Add the git commit/push workflow to the database."""
    try:
        print("🚀 Adding Git Commit/Push Workflow to Archon...")
        
        # Get the workflow template
        workflow_template = create_git_commit_push_workflow()
        print(f"📋 Created workflow template: {workflow_template.title}")
        
        # Convert to dict format for repository
        workflow_data = {
            "name": workflow_template.name,
            "title": workflow_template.title,
            "description": workflow_template.description,
            "category": workflow_template.category,
            "tags": workflow_template.tags,
            "parameters": workflow_template.parameters,
            "outputs": workflow_template.outputs,
            "steps": [step.dict() for step in workflow_template.steps],
            "timeout_minutes": workflow_template.timeout_minutes,
            "max_retries": workflow_template.max_retries,
            "created_by": workflow_template.created_by,
            "is_public": workflow_template.is_public,
            "status": workflow_template.status.value
        }
        
        # Initialize repository
        supabase_client = get_supabase_client()
        repository = WorkflowRepository(supabase_client)
        
        # Check if workflow already exists
        print("🔍 Checking if workflow already exists...")
        existing_workflows = repository.supabase_client.table("archon_workflow_templates").select("name").eq("name", workflow_template.name).execute()
        
        if existing_workflows.data:
            print(f"⚠️  Workflow '{workflow_template.name}' already exists. Skipping creation.")
            return True
        
        # Create the workflow
        print("💾 Creating workflow in database...")
        success, result = await repository.create_workflow_template(workflow_data)
        
        if success:
            workflow_id = result["workflow"]["id"]
            print(f"✅ Successfully created workflow!")
            print(f"   ID: {workflow_id}")
            print(f"   Name: {workflow_template.name}")
            print(f"   Title: {workflow_template.title}")
            print(f"   Category: {workflow_template.category}")
            print(f"   Steps: {len(workflow_template.steps)}")
            
            # Print workflow details
            print("\n📝 Workflow Details:")
            print(f"   Description: {workflow_template.description}")
            print(f"   Tags: {', '.join(workflow_template.tags)}")
            print(f"   Timeout: {workflow_template.timeout_minutes} minutes")
            print(f"   Max Retries: {workflow_template.max_retries}")
            print(f"   Public: {workflow_template.is_public}")
            
            print("\n🔧 Input Parameters:")
            for param_name, param_def in workflow_template.parameters.items():
                required = param_def.get("required", False)
                param_type = param_def.get("type", "unknown")
                description = param_def.get("description", "No description")
                default = param_def.get("default", "None")
                print(f"   • {param_name} ({param_type}){' [REQUIRED]' if required else ''}")
                print(f"     {description}")
                if not required and default != "None":
                    print(f"     Default: {default}")
            
            print("\n⚙️  Workflow Steps:")
            for i, step in enumerate(workflow_template.steps, 1):
                step_type = step.type.value if hasattr(step.type, 'value') else step.type
                print(f"   {i}. {step.title} ({step_type})")
                print(f"      {step.description}")
                if hasattr(step, 'tool_name') and step.tool_name:
                    print(f"      Tool: {step.tool_name}")
            
            print("\n🎉 Git Commit/Push workflow is now available!")
            print("\n📖 Usage Instructions:")
            print("1. Go to the Archon UI at http://localhost:3000/workflows")
            print("2. Find 'Git Commit and Push' workflow")
            print("3. Click 'Execute' and provide parameters:")
            print("   • commit_message: Your commit message (required)")
            print("   • repository_path: Path to git repo (optional, defaults to '.')")
            print("   • branch: Branch to push to (optional, defaults to 'main')")
            print("   • add_all: Stage all changes (optional, defaults to true)")
            print("\n🔄 You can also clone/edit this workflow to customize it!")
            
            return True
        else:
            print(f"❌ Failed to create workflow: {result}")
            return False
            
    except Exception as e:
        print(f"💥 Error adding git workflow: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main entry point."""
    print("=" * 60)
    print("🔧 Archon Git Workflow Setup")
    print("=" * 60)
    
    # Check environment
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_KEY"):
        print("❌ Missing required environment variables:")
        print("   SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        print("   Please check your .env file")
        return False
    
    success = await add_git_workflow()
    
    print("=" * 60)
    if success:
        print("🎉 Git workflow setup completed successfully!")
        print("\n🚀 Next Steps:")
        print("1. Restart Docker containers if needed: docker compose restart")
        print("2. Access Archon UI: http://localhost:3000/workflows")
        print("3. Test the git workflow with your repository")
        print("\n💡 Note: The workflow uses 'execute_shell_command' tool")
        print("   Make sure the MCP server includes the shell module!")
    else:
        print("❌ Git workflow setup failed!")
        print("   Check the error messages above for details")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
