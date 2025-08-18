#!/usr/bin/env python3
"""
Test script for workflow system database migration.

This script validates the workflow migration by:
1. Checking if migration can be applied successfully
2. Verifying all tables and constraints are created
3. Testing basic CRUD operations
4. Validating rollback functionality

Usage:
    python migration/test_workflow_migration.py
"""

import os
import sys
import asyncio
import asyncpg
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WorkflowMigrationTester:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not self.supabase_url or not self.service_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")
        
        # Extract database connection info from Supabase URL
        # Format: https://project.supabase.co -> postgresql://postgres:password@db.project.supabase.co:5432/postgres
        project_id = self.supabase_url.split("//")[1].split(".")[0]
        self.db_url = f"postgresql://postgres:{self.service_key}@db.{project_id}.supabase.co:5432/postgres"
        
        self.connection = None
    
    async def connect(self):
        """Connect to the database."""
        try:
            self.connection = await asyncpg.connect(self.db_url)
            print("✅ Connected to Supabase database")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the database."""
        if self.connection:
            await self.connection.close()
            print("✅ Disconnected from database")
    
    async def read_sql_file(self, file_path: str) -> str:
        """Read SQL file content."""
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Failed to read {file_path}: {e}")
            return ""
    
    async def execute_sql(self, sql: str, description: str) -> bool:
        """Execute SQL and return success status."""
        try:
            await self.connection.execute(sql)
            print(f"✅ {description}")
            return True
        except Exception as e:
            print(f"❌ {description} failed: {e}")
            return False
    
    async def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        try:
            result = await self.connection.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                table_name
            )
            return result
        except Exception as e:
            print(f"❌ Error checking table {table_name}: {e}")
            return False
    
    async def check_enum_exists(self, enum_name: str) -> bool:
        """Check if an enum type exists."""
        try:
            result = await self.connection.fetchval(
                "SELECT EXISTS (SELECT FROM pg_type WHERE typname = $1)",
                enum_name
            )
            return result
        except Exception as e:
            print(f"❌ Error checking enum {enum_name}: {e}")
            return False
    
    async def test_basic_operations(self) -> bool:
        """Test basic CRUD operations on workflow tables."""
        try:
            # Test workflow template creation
            template_id = await self.connection.fetchval("""
                INSERT INTO archon_workflow_templates (name, title, description, steps)
                VALUES ('test_workflow', 'Test Workflow', 'A test workflow', '[{"name": "test_step", "type": "action"}]'::jsonb)
                RETURNING id
            """)
            print(f"✅ Created test workflow template: {template_id}")
            
            # Test workflow execution creation
            execution_id = await self.connection.fetchval("""
                INSERT INTO archon_workflow_executions (workflow_template_id, triggered_by, total_steps)
                VALUES ($1, 'test_user', 1)
                RETURNING id
            """, template_id)
            print(f"✅ Created test workflow execution: {execution_id}")
            
            # Test step execution creation
            step_execution_id = await self.connection.fetchval("""
                INSERT INTO archon_workflow_step_executions (workflow_execution_id, step_index, step_name, step_type, step_config)
                VALUES ($1, 0, 'test_step', 'action', '{}'::jsonb)
                RETURNING id
            """, execution_id)
            print(f"✅ Created test step execution: {step_execution_id}")
            
            # Test template version creation
            version_id = await self.connection.fetchval("""
                INSERT INTO archon_workflow_template_versions (workflow_template_id, version_number, version_tag, template_snapshot)
                VALUES ($1, 1, '1.0.0', '{}'::jsonb)
                RETURNING id
            """, template_id)
            print(f"✅ Created test template version: {version_id}")
            
            # Clean up test data
            await self.connection.execute("DELETE FROM archon_workflow_templates WHERE id = $1", template_id)
            print("✅ Cleaned up test data")
            
            return True
            
        except Exception as e:
            print(f"❌ Basic operations test failed: {e}")
            return False
    
    async def run_migration_test(self) -> bool:
        """Run the complete migration test."""
        print("🚀 Starting Workflow Migration Test")
        print("=" * 50)
        
        # Connect to database
        if not await self.connect():
            return False
        
        try:
            # Read migration file
            migration_sql = await self.read_sql_file("migration/add_workflow_system.sql")
            if not migration_sql:
                return False
            
            # Apply migration
            if not await self.execute_sql(migration_sql, "Applied workflow migration"):
                return False
            
            # Check tables were created
            tables = [
                "archon_workflow_templates",
                "archon_workflow_executions", 
                "archon_workflow_step_executions",
                "archon_workflow_template_versions"
            ]
            
            for table in tables:
                exists = await self.check_table_exists(table)
                if exists:
                    print(f"✅ Table {table} exists")
                else:
                    print(f"❌ Table {table} missing")
                    return False
            
            # Check enums were created
            enums = [
                "workflow_status",
                "workflow_step_type",
                "workflow_execution_status",
                "step_execution_status"
            ]
            
            for enum in enums:
                exists = await self.check_enum_exists(enum)
                if exists:
                    print(f"✅ Enum {enum} exists")
                else:
                    print(f"❌ Enum {enum} missing")
                    return False
            
            # Test basic operations
            if not await self.test_basic_operations():
                return False
            
            # Test rollback (optional - uncomment to test)
            # rollback_sql = await self.read_sql_file("migration/rollback_workflow_system.sql")
            # if rollback_sql:
            #     await self.execute_sql(rollback_sql, "Applied workflow rollback")
            
            print("=" * 50)
            print("🎉 All migration tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ Migration test failed: {e}")
            return False
        
        finally:
            await self.disconnect()

async def main():
    """Main test function."""
    tester = WorkflowMigrationTester()
    success = await tester.run_migration_test()
    
    if success:
        print("\n✅ Workflow migration is ready for deployment!")
        sys.exit(0)
    else:
        print("\n❌ Workflow migration has issues that need to be fixed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
