#!/usr/bin/env python3
"""
Setup script for the new Supabase workflow instance
"""

import os
import asyncio
import asyncpg
import json
from datetime import datetime

async def setup_workflow_database():
    """Setup the workflow database with the new Supabase instance"""
    
    # Your Supabase project details
    project_url = "https://aaoewgjxxeiyfpnlkkao.supabase.co"
    anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFhb2V3Z2p4eGVpeWZwbmxra2FvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU1MTkwODcsImV4cCI6MjA3MTA5NTA4N30.BHimR8VPpjLySO5M3W5wxsJoffG6DVanG53KSM-06_A"
    
    print("🚀 Setting up Archon Workflow System")
    print("=" * 50)
    print(f"📍 Project URL: {project_url}")
    print(f"🔑 Anon Key: {anon_key[:20]}...")
    print()
    
    print("📋 NEXT STEPS TO COMPLETE SETUP:")
    print()
    print("1. Get your SERVICE ROLE key:")
    print("   • Go to: https://aaoewgjxxeiyfpnlkkao.supabase.co/project/settings/api")
    print("   • Copy the 'service_role' key (NOT the anon key)")
    print("   • It should start with 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'")
    print()
    print("2. Update the environment:")
    print("   • Copy .env.workflow to .env")
    print("   • Replace 'your-service-role-key-here' with your actual service role key")
    print()
    print("3. Apply the database migration:")
    print("   • Go to: https://aaoewgjxxeiyfpnlkkao.supabase.co/project/default/sql/new")
    print("   • Copy and paste the contents of 'migration/add_workflow_system.sql'")
    print("   • Click 'Run' to execute the migration")
    print()
    print("4. Restart the containers:")
    print("   • Run: docker compose restart")
    print()
    print("5. Test the system:")
    print("   • Frontend: http://localhost:3000")
    print("   • API: http://localhost:8000/api/workflows")
    print("   • Docs: http://localhost:8000/docs")
    print()
    
    # Create the updated .env file template
    env_content = f"""# Archon Workflow System Environment Configuration
# Updated with new Supabase project credentials

# =====================================================
# WORKFLOW SUPABASE CONFIGURATION
# =====================================================

# Supabase project URL
SUPABASE_URL={project_url}

# Supabase service role key (REPLACE THIS WITH YOUR ACTUAL SERVICE ROLE KEY)
SUPABASE_SERVICE_KEY=your-service-role-key-here

# Supabase anon key
SUPABASE_ANON_KEY={anon_key}

# =====================================================
# EXISTING ARCHON CONFIGURATION
# =====================================================

# MCP Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8181

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
FRONTEND_PORT=3000

# Development Configuration
NODE_ENV=development
PYTHONPATH=/app/src

# =====================================================
# WORKFLOW SYSTEM SPECIFIC SETTINGS
# =====================================================

# Workflow execution settings
WORKFLOW_MAX_CONCURRENT_EXECUTIONS=10
WORKFLOW_DEFAULT_TIMEOUT_MINUTES=60
WORKFLOW_LOG_RETENTION_DAYS=30

# WebSocket settings for real-time monitoring
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=8182

# Background task settings
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Monitoring and logging
LOG_LEVEL=INFO
ENABLE_WORKFLOW_METRICS=true
ENABLE_REAL_TIME_MONITORING=true
"""
    
    # Write the updated .env file
    with open('.env.new', 'w') as f:
        f.write(env_content)
    
    print("✅ Created '.env.new' file with your Supabase credentials")
    print("   • Review the file and copy it to '.env' after adding your service role key")
    print()
    
    # Show the migration SQL for easy copying
    try:
        with open('migration/add_workflow_system.sql', 'r') as f:
            migration_sql = f.read()
        
        print("📄 MIGRATION SQL READY:")
        print("   • File: migration/add_workflow_system.sql")
        print(f"   • Size: {len(migration_sql)} characters")
        print("   • Copy this entire file content to your Supabase SQL editor")
        print()
        
        # Show first few lines as preview
        lines = migration_sql.split('\n')[:10]
        print("📋 MIGRATION PREVIEW (first 10 lines):")
        for i, line in enumerate(lines, 1):
            print(f"   {i:2d}: {line}")
        print("   ... (continue with full file)")
        print()
        
    except FileNotFoundError:
        print("❌ Migration file not found: migration/add_workflow_system.sql")
        print("   • Make sure you're running this from the project root directory")
    
    print("🎯 QUICK SETUP CHECKLIST:")
    print("   □ Get service role key from Supabase dashboard")
    print("   □ Update .env file with service role key")
    print("   □ Run migration SQL in Supabase SQL editor")
    print("   □ Restart Docker containers")
    print("   □ Test the workflow system")
    print()
    print("🆘 NEED HELP?")
    print("   • Supabase docs: https://supabase.com/docs")
    print("   • Project dashboard: https://aaoewgjxxeiyfpnlkkao.supabase.co")
    print("   • SQL editor: https://aaoewgjxxeiyfpnlkkao.supabase.co/project/default/sql/new")

if __name__ == "__main__":
    asyncio.run(setup_workflow_database())
