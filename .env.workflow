# Workflow System Environment Configuration
# Copy this to .env after setting up your new Supabase project

# =====================================================
# WORKFLOW SUPABASE CONFIGURATION
# =====================================================
# Replace these with your new Supabase project credentials

# Your new Supabase project URL
SUPABASE_URL=https://aaoewgjxxeiyfpnlkkao.supabase.co

# Your new Supabase service role key (from Settings > API)
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFhb2V3Z2p4eGVpeWZwbmxra2FvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTUxOTA4NywiZXhwIjoyMDcxMDk1MDg3fQ.VjTlpr6V6eT7tpMxadGc90-yoZtL3LOK-MBpiqKyEwI

# Your new Supabase anon key (from Settings > API)
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFhb2V3Z2p4eGVpeWZwbmxra2FvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU1MTkwODcsImV4cCI6MjA3MTA5NTA4N30.BHimR8VPpjLySO5M3W5wxsJoffG6DVanG53KSM-06_A

# Database password you set during project creation
SUPABASE_DB_PASSWORD=your-database-password

# =====================================================
# EXISTING ARCHON CONFIGURATION
# =====================================================
# Keep these from your current .env file

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
