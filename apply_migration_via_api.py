#!/usr/bin/env python3
"""
Apply workflow migration via Supabase REST API
"""

import requests
import json

def apply_migration():
    """Apply the workflow migration using Supabase REST API"""
    
    # Supabase configuration
    supabase_url = "https://aaoewgjxxeiyfpnlkkao.supabase.co"
    service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFhb2V3Z2p4eGVpeWZwbmxra2FvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTUxOTA4NywiZXhwIjoyMDcxMDk1MDg3fQ.VjTlpr6V6eT7tpMxadGc90-yoZtL3LOK-MBpiqKyEwI"
    
    print("🚀 Applying Workflow Migration via Supabase API")
    print("=" * 50)
    
    # Headers for API requests
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Read the migration SQL
        print("📄 Reading migration file...")
        with open('migration/add_workflow_system.sql', 'r') as f:
            migration_sql = f.read()
        
        print(f"✅ Migration file loaded ({len(migration_sql)} characters)")
        
        # Apply migration using Supabase SQL API
        print("🚀 Applying migration via Supabase SQL API...")
        
        sql_url = f"{supabase_url}/rest/v1/rpc/exec_sql"
        
        # Note: Supabase doesn't have a direct SQL execution endpoint via REST API
        # We need to apply the migration manually through the Supabase dashboard
        
        print("⚠️  MANUAL MIGRATION REQUIRED")
        print("")
        print("The migration needs to be applied manually through the Supabase dashboard:")
        print("")
        print("1. Go to: https://aaoewgjxxeiyfpnlkkao.supabase.co/project/default/sql/new")
        print("2. Copy the entire contents of 'migration/add_workflow_system.sql'")
        print("3. Paste it into the SQL editor")
        print("4. Click 'Run' to execute the migration")
        print("")
        
        # Show migration preview
        lines = migration_sql.split('\n')[:20]
        print("📋 MIGRATION PREVIEW (first 20 lines):")
        print("-" * 40)
        for i, line in enumerate(lines, 1):
            print(f"{i:2d}: {line}")
        print("... (continue with full file)")
        print("-" * 40)
        print("")
        
        # After manual migration, we can test the API
        print("🧪 Testing Supabase connection...")
        
        # Test basic connection
        test_url = f"{supabase_url}/rest/v1/"
        response = requests.get(test_url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Supabase API connection successful")
        else:
            print(f"❌ Supabase API connection failed: {response.status_code}")
            return False
        
        # Try to check if workflow tables exist (this will fail until migration is applied)
        print("🔍 Checking for workflow tables...")
        
        tables_to_check = [
            "archon_workflow_templates",
            "archon_workflow_executions",
            "archon_workflow_step_executions",
            "archon_workflow_template_versions"
        ]
        
        tables_exist = 0
        for table in tables_to_check:
            try:
                table_url = f"{supabase_url}/rest/v1/{table}?select=id&limit=1"
                response = requests.get(table_url, headers=headers)
                if response.status_code == 200:
                    print(f"  ✅ {table} exists")
                    tables_exist += 1
                else:
                    print(f"  ❌ {table} missing (status: {response.status_code})")
            except Exception as e:
                print(f"  ❌ {table} error: {e}")
        
        if tables_exist == len(tables_to_check):
            print("🎉 All workflow tables exist! Migration was successful.")
            
            # Create example workflows
            print("🌱 Creating example workflows...")
            create_example_workflows(supabase_url, headers)
            
        else:
            print(f"⚠️  Only {tables_exist}/{len(tables_to_check)} tables exist.")
            print("   Please apply the migration manually first.")
        
        print("")
        print("📋 NEXT STEPS:")
        print("1. Apply migration manually in Supabase dashboard")
        print("2. Run this script again to create example workflows")
        print("3. Test the system at: http://localhost:3000")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_example_workflows(supabase_url, headers):
    """Create example workflows via REST API"""
    
    # Example workflow 1: Health Check
    workflow1 = {
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
    
    # Example workflow 2: Project Analysis
    workflow2 = {
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
            }
        ],
        "timeout_minutes": 30,
        "max_retries": 3,
        "created_by": "system",
        "is_public": True
    }
    
    workflows = [workflow1, workflow2]
    
    for workflow in workflows:
        try:
            url = f"{supabase_url}/rest/v1/archon_workflow_templates"
            response = requests.post(url, headers=headers, json=workflow)
            
            if response.status_code in [200, 201]:
                print(f"  ✅ Created workflow: {workflow['title']}")
            else:
                print(f"  ❌ Failed to create workflow {workflow['title']}: {response.status_code}")
                print(f"     Response: {response.text}")
        except Exception as e:
            print(f"  ❌ Error creating workflow {workflow['title']}: {e}")

if __name__ == "__main__":
    success = apply_migration()
    exit(0 if success else 1)
