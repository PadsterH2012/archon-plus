#!/usr/bin/env python3
"""
Apply workflow migration to Supabase database
"""

import os
import asyncio
import asyncpg
from urllib.parse import urlparse

async def apply_migration():
    """Apply the workflow migration to the database"""
    
    # Parse Supabase URL to get connection details
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables")
        return False
    
    # Parse the URL to get database connection details
    # Supabase URL format: https://project.supabase.co
    # Database URL format: postgresql://postgres:[password]@db.project.supabase.co:5432/postgres
    
    parsed = urlparse(supabase_url)
    project_ref = parsed.hostname.split('.')[0]
    
    # Construct database URL
    db_url = f"postgresql://postgres.{project_ref}:5432/postgres"
    
    print(f"🔗 Connecting to database: {project_ref}")
    
    try:
        # Read the migration file
        with open('migration/add_workflow_system.sql', 'r') as f:
            migration_sql = f.read()
        
        print("📄 Migration file loaded successfully")
        
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
        print("🚀 Applying workflow migration...")
        await conn.execute(migration_sql)
        
        print("✅ Migration applied successfully!")
        
        # Verify tables were created
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
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(apply_migration())
    exit(0 if success else 1)
