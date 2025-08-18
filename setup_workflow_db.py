#!/usr/bin/env python3
"""
Setup the workflow database in the new Supabase instance
"""

import os
import asyncio
import asyncpg
import json
from datetime import datetime

async def setup_database():
    """Apply migration and setup the workflow database"""
    
    # Supabase connection details
    supabase_url = "https://aaoewgjxxeiyfpnlkkao.supabase.co"
    service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFhb2V3Z2p4eGVpeWZwbmxra2FvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTUxOTA4NywiZXhwIjoyMDcxMDk1MDg3fQ.VjTlpr6V6eT7tpMxadGc90-yoZtL3LOK-MBpiqKyEwI"
    
    print("🚀 Setting up Archon Workflow Database")
    print("=" * 50)
    
    try:
        # Connect to Supabase database
        print("🔗 Connecting to Supabase database...")
        conn = await asyncpg.connect(
            host="db.aaoewgjxxeiyfpnlkkao.supabase.co",
            port=5432,
            user="postgres",
            password=service_key,
            database="postgres",
            ssl="require"
        )
        print("✅ Connected successfully!")
        
        # Read and apply migration
        print("📄 Reading workflow migration...")
        with open('migration/add_workflow_system.sql', 'r') as f:
            migration_sql = f.read()
        
        print("🚀 Applying workflow migration...")
        await conn.execute(migration_sql)
        print("✅ Migration applied successfully!")
        
        # Verify tables were created
        print("🔍 Verifying workflow tables...")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%workflow%'
            ORDER BY table_name;
        """)
        
        print(f"📊 Created {len(tables)} workflow tables:")
        for table in tables:
            print(f"  ✓ {table['table_name']}")
        
        # Create example workflows
        print("🌱 Creating example workflows...")
        
        # Example 1: Simple Health Check
        await conn.execute("""
            INSERT INTO archon_workflow_templates 
            (name, title, description, category, tags, parameters, outputs, steps, 
             timeout_minutes, max_retries, created_by, is_public)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        """, 
            "health_check_workflow",
            "System Health Check",
            "Performs a comprehensive system health check using MCP tools",
            "monitoring",
            json.dumps(["health", "monitoring", "mcp"]),
            json.dumps({}),
            json.dumps({
                "health_status": {"type": "object", "description": "System health status"},
                "session_info": {"type": "object", "description": "Current session information"}
            }),
            json.dumps([
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
            ]),
            10, 2, "system", True
        )
        print("  ✓ Created: System Health Check")
        
        # Example 2: Project Analysis
        await conn.execute("""
            INSERT INTO archon_workflow_templates 
            (name, title, description, category, tags, parameters, outputs, steps, 
             timeout_minutes, max_retries, created_by, is_public)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        """, 
            "project_analysis_workflow",
            "Project Analysis and Documentation",
            "Analyzes a project and creates documentation based on findings",
            "analysis",
            json.dumps(["analysis", "documentation", "project"]),
            json.dumps({
                "project_id": {"type": "string", "required": True, "description": "Project ID to analyze"}
            }),
            json.dumps({
                "analysis_result": {"type": "object", "description": "Project analysis results"},
                "documentation": {"type": "object", "description": "Generated documentation"}
            }),
            json.dumps([
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
            ]),
            30, 3, "system", True
        )
        print("  ✓ Created: Project Analysis and Documentation")
        
        # Test the system
        print("🧪 Testing workflow system...")
        
        # Count workflows
        count = await conn.fetchval("SELECT COUNT(*) FROM archon_workflow_templates")
        print(f"  📊 Total workflows: {count}")
        
        # List workflows
        workflows = await conn.fetch("""
            SELECT name, title, status, created_at 
            FROM archon_workflow_templates 
            ORDER BY created_at DESC
        """)
        
        print(f"  📋 Available workflows:")
        for workflow in workflows:
            print(f"    • {workflow['title']} ({workflow['name']}) - {workflow['status']}")
        
        await conn.close()
        
        print("=" * 50)
        print("🎉 Workflow database setup completed successfully!")
        print("")
        print("✅ SETUP COMPLETE - Next Steps:")
        print("1. Restart Docker containers: docker compose restart")
        print("2. Access workflow UI: http://localhost:3000")
        print("3. Test API endpoints: http://localhost:8000/api/workflows")
        print("4. View API docs: http://localhost:8000/docs")
        print("")
        print("🔗 Supabase Dashboard: https://aaoewgjxxeiyfpnlkkao.supabase.co")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(setup_database())
    exit(0 if success else 1)
