#!/usr/bin/env python3
"""
Apply Template Injection System Database Migration

This script applies the template injection schema to the Archon Supabase database.
It reads the migration SQL file and executes it safely with proper error handling.

Usage:
    python apply_template_injection_migration.py

Requirements:
    - SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables
    - asyncpg package: pip install asyncpg
    - python-dotenv package: pip install python-dotenv
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

async def apply_migration():
    """Apply the template injection migration to the database."""
    
    # Load environment variables
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")
        return False
    
    # Parse the URL to get database connection details
    # Supabase URL format: https://project.supabase.co
    # Database URL format: postgresql://postgres:[password]@db.project.supabase.co:5432/postgres
    
    parsed = urlparse(supabase_url)
    project_ref = parsed.hostname.split('.')[0]
    
    print(f"🔗 Connecting to Archon database: {project_ref}")
    
    try:
        # Read the migration file
        print("📄 Reading template injection migration...")
        with open('migration/add_template_injection_schema.sql', 'r') as f:
            migration_sql = f.read()
        
        print(f"✅ Migration file loaded ({len(migration_sql)} characters)")
        
        # Connect to database using service key as password
        conn = await asyncpg.connect(
            host=f"db.{project_ref}.supabase.co",
            port=5432,
            user="postgres",
            password=supabase_key,
            database="postgres",
            ssl="require"
        )
        
        print("✅ Connected to database")
        
        # Execute the migration
        print("🚀 Applying template injection migration...")
        await conn.execute(migration_sql)
        
        print("✅ Template injection migration applied successfully!")
        
        # Verify tables were created
        print("🔍 Verifying template injection tables...")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%template%'
            ORDER BY table_name;
        """)
        
        if tables:
            print("✅ Template injection tables created:")
            for table in tables:
                print(f"   - {table['table_name']}")
        else:
            print("⚠️  No template injection tables found")
        
        # Verify enum types were created
        print("🔍 Verifying template injection enum types...")
        enums = await conn.fetch("""
            SELECT typname 
            FROM pg_type 
            WHERE typname LIKE '%template%'
            ORDER BY typname;
        """)
        
        if enums:
            print("✅ Template injection enum types created:")
            for enum in enums:
                print(f"   - {enum['typname']}")
        else:
            print("⚠️  No template injection enum types found")
        
        # Apply seed data if available
        print("🌱 Applying template injection seed data...")
        try:
            with open('migration/seed_default_templates.sql', 'r') as f:
                seed_sql = f.read()
            
            await conn.execute(seed_sql)
            print("✅ Seed data applied successfully!")
            
            # Check seed data
            component_count = await conn.fetchval("SELECT COUNT(*) FROM archon_template_components")
            template_count = await conn.fetchval("SELECT COUNT(*) FROM archon_workflow_templates")
            
            print(f"✅ Created {component_count} template components")
            print(f"✅ Created {template_count} workflow templates")
            
        except FileNotFoundError:
            print("⚠️  Seed data file not found, skipping...")
        except Exception as e:
            print(f"⚠️  Failed to apply seed data: {e}")
        
        # Close connection
        await conn.close()
        print("✅ Database connection closed")
        
        print("\n🎉 Template Injection System migration completed successfully!")
        print("\nNext steps:")
        print("1. Implement TemplateInjectionService")
        print("2. Integrate with TaskService")
        print("3. Create MCP tools")
        print("4. Enable feature flags for testing")
        
        return True
        
    except FileNotFoundError:
        print("❌ Error: migration/add_template_injection_schema.sql not found")
        return False
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Template Injection System Migration")
    print("=" * 50)
    
    success = asyncio.run(apply_migration())
    
    if success:
        print("\n✅ Migration completed successfully!")
        exit(0)
    else:
        print("\n❌ Migration failed!")
        exit(1)
