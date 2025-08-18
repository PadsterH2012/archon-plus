#!/usr/bin/env python3
"""
Complete setup script for the Archon Workflow Orchestration System
"""

import os
import asyncio
import asyncpg
import json
from urllib.parse import urlparse
from datetime import datetime

class WorkflowSystemSetup:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        self.conn = None
        
    async def connect(self):
        """Connect to the Supabase database"""
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables")
        
        # Parse the URL to get database connection details
        parsed = urlparse(self.supabase_url)
        project_ref = parsed.hostname.split('.')[0]
        
        print(f"🔗 Connecting to Supabase project: {project_ref}")
        
        self.conn = await asyncpg.connect(
            host=f"db.{project_ref}.supabase.co",
            port=5432,
            user="postgres",
            password=self.supabase_key,
            database="postgres",
            ssl="require"
        )
        
        print("✅ Connected to database successfully")
        
    async def apply_migration(self):
        """Apply the workflow system migration"""
        print("📄 Reading workflow migration...")
        
        try:
            with open('migration/add_workflow_system.sql', 'r') as f:
                migration_sql = f.read()
        except FileNotFoundError:
            print("❌ Migration file not found: migration/add_workflow_system.sql")
            return False
        
        print("🚀 Applying workflow migration...")
        
        try:
            await self.conn.execute(migration_sql)
            print("✅ Migration applied successfully!")
            return True
        except Exception as e:
            print(f"❌ Error applying migration: {e}")
            return False
    
    async def verify_tables(self):
        """Verify that all workflow tables were created"""
        print("🔍 Verifying workflow tables...")
        
        expected_tables = [
            'archon_workflow_templates',
            'archon_workflow_executions', 
            'archon_step_executions',
            'archon_workflow_versions'
        ]
        
        tables = await self.conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%workflow%'
            ORDER BY table_name;
        """)
        
        found_tables = [table['table_name'] for table in tables]
        
        print(f"📊 Found {len(found_tables)} workflow tables:")
        for table in found_tables:
            status = "✅" if table in expected_tables else "⚠️"
            print(f"  {status} {table}")
        
        missing_tables = set(expected_tables) - set(found_tables)
        if missing_tables:
            print(f"❌ Missing tables: {', '.join(missing_tables)}")
            return False
        
        print("✅ All required tables created successfully!")
        return True
    
    async def seed_example_workflows(self):
        """Create example workflows for testing"""
        print("🌱 Seeding example workflows...")
        
        # Example 1: Simple MCP Tool Workflow
        simple_workflow = {
            "name": "health_check_workflow",
            "title": "System Health Check",
            "description": "Performs a comprehensive system health check using MCP tools",
            "category": "monitoring",
            "tags": ["health", "monitoring", "mcp"],
            "parameters": {},
            "outputs": {
                "health_status": {"type": "object", "description": "System health status"},
                "session_info": {"type": "object", "description": "Current session information"}
            },
            "steps": [
                {
                    "name": "health_check",
                    "title": "Check System Health",
                    "type": "action",
                    "tool_name": "health_check_archon",
                    "parameters": {},
                    "description": "Perform system health check"
                },
                {
                    "name": "session_info",
                    "title": "Get Session Info",
                    "type": "action", 
                    "tool_name": "session_info_archon",
                    "parameters": {},
                    "description": "Retrieve current session information"
                }
            ],
            "timeout_minutes": 10,
            "max_retries": 2,
            "created_by": "system",
            "is_public": True
        }
        
        # Example 2: Complex Workflow with Conditions
        complex_workflow = {
            "name": "project_analysis_workflow",
            "title": "Project Analysis and Documentation",
            "description": "Analyzes a project and creates documentation based on findings",
            "category": "analysis",
            "tags": ["analysis", "documentation", "project"],
            "parameters": {
                "project_id": {"type": "string", "required": True, "description": "Project ID to analyze"}
            },
            "outputs": {
                "analysis_result": {"type": "object", "description": "Project analysis results"},
                "documentation": {"type": "object", "description": "Generated documentation"}
            },
            "steps": [
                {
                    "name": "get_project",
                    "title": "Get Project Details",
                    "type": "action",
                    "tool_name": "manage_project_archon",
                    "parameters": {
                        "action": "get",
                        "project_id": "{{project_id}}"
                    },
                    "description": "Retrieve project information"
                },
                {
                    "name": "check_features",
                    "title": "Check Project Features",
                    "type": "action",
                    "tool_name": "get_project_features_archon", 
                    "parameters": {
                        "project_id": "{{project_id}}"
                    },
                    "description": "Get project features list"
                },
                {
                    "name": "has_features_check",
                    "title": "Has Features?",
                    "type": "condition",
                    "condition": "len(features) > 0",
                    "description": "Check if project has features"
                },
                {
                    "name": "create_documentation",
                    "title": "Create Documentation",
                    "type": "action",
                    "tool_name": "manage_document_archon",
                    "parameters": {
                        "action": "add",
                        "project_id": "{{project_id}}",
                        "document_type": "analysis",
                        "title": "Project Analysis Report"
                    },
                    "description": "Create analysis documentation"
                }
            ],
            "timeout_minutes": 30,
            "max_retries": 3,
            "created_by": "system",
            "is_public": True
        }
        
        workflows = [simple_workflow, complex_workflow]
        
        for workflow in workflows:
            try:
                await self.conn.execute("""
                    INSERT INTO archon_workflow_templates 
                    (name, title, description, category, tags, parameters, outputs, steps, 
                     timeout_minutes, max_retries, created_by, is_public)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """, 
                    workflow["name"],
                    workflow["title"], 
                    workflow["description"],
                    workflow["category"],
                    json.dumps(workflow["tags"]),
                    json.dumps(workflow["parameters"]),
                    json.dumps(workflow["outputs"]),
                    json.dumps(workflow["steps"]),
                    workflow["timeout_minutes"],
                    workflow["max_retries"],
                    workflow["created_by"],
                    workflow["is_public"]
                )
                print(f"  ✅ Created workflow: {workflow['title']}")
            except Exception as e:
                print(f"  ❌ Failed to create workflow {workflow['title']}: {e}")
        
        print("✅ Example workflows seeded successfully!")
    
    async def test_system(self):
        """Test the workflow system"""
        print("🧪 Testing workflow system...")
        
        # Test 1: Count workflows
        count = await self.conn.fetchval("SELECT COUNT(*) FROM archon_workflow_templates")
        print(f"  📊 Total workflows: {count}")
        
        # Test 2: List workflows
        workflows = await self.conn.fetch("""
            SELECT name, title, status, created_at 
            FROM archon_workflow_templates 
            ORDER BY created_at DESC
        """)
        
        print(f"  📋 Available workflows:")
        for workflow in workflows:
            print(f"    • {workflow['title']} ({workflow['name']}) - {workflow['status']}")
        
        # Test 3: Check enums
        enums = await self.conn.fetch("""
            SELECT typname FROM pg_type 
            WHERE typname LIKE '%workflow%' 
            ORDER BY typname
        """)
        
        print(f"  🏷️  Workflow enums created:")
        for enum in enums:
            print(f"    • {enum['typname']}")
        
        print("✅ System tests completed successfully!")
    
    async def close(self):
        """Close database connection"""
        if self.conn:
            await self.conn.close()
            print("🔌 Database connection closed")

async def main():
    """Main setup function"""
    print("🚀 Starting Archon Workflow System Setup")
    print("=" * 50)
    
    setup = WorkflowSystemSetup()
    
    try:
        # Step 1: Connect to database
        await setup.connect()
        
        # Step 2: Apply migration
        if not await setup.apply_migration():
            print("❌ Migration failed. Exiting.")
            return False
        
        # Step 3: Verify tables
        if not await setup.verify_tables():
            print("❌ Table verification failed. Exiting.")
            return False
        
        # Step 4: Seed example workflows
        await setup.seed_example_workflows()
        
        # Step 5: Test system
        await setup.test_system()
        
        print("=" * 50)
        print("🎉 Workflow system setup completed successfully!")
        print("")
        print("Next steps:")
        print("1. Update your .env file with the new Supabase credentials")
        print("2. Restart the Docker containers: docker compose restart")
        print("3. Access the workflow UI at: http://localhost:3000/workflows")
        print("4. Test the API endpoints at: http://localhost:8000/api/workflows")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False
    finally:
        await setup.close()

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
