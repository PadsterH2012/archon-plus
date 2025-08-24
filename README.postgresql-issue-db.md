# Archon PostgreSQL Issue Database

This directory contains the Docker configuration for a dedicated PostgreSQL database container designed for Archon's issue and bug management system. The container includes pgvector extension for embedding support and persistent storage.

## 🚀 Quick Start

### 1. Configure Environment

```bash
# Copy the environment template
cp .env.postgresql-issue-db .env

# Edit the configuration (IMPORTANT: Change default passwords!)
nano .env
```

### 2. Start the Database

```bash
# Start the PostgreSQL container
docker-compose -f docker-compose.postgresql-issue-db.yml up -d

# Check the logs
docker-compose -f docker-compose.postgresql-issue-db.yml logs -f archon-issue-db
```

### 3. Verify Installation

```bash
# Check container health
docker-compose -f docker-compose.postgresql-issue-db.yml ps

# Connect to the database
docker exec -it Archon-Issue-DB psql -U archon_user -d archon_issues

# Test pgvector extension
\dx
```

## 📁 File Structure

```
.
├── Dockerfile.postgresql              # PostgreSQL container with pgvector
├── docker-compose.postgresql-issue-db.yml  # Docker Compose configuration
├── .env.postgresql-issue-db          # Environment template
└── README.postgresql-issue-db.md     # This file
```

## 🔧 Configuration

### Database Settings

- **Database Name**: `archon_issues`
- **Default User**: `archon_user`
- **Default Port**: `5433` (to avoid conflicts)
- **Persistent Storage**: `/mnt/network_repo/stack_dbs/postgresql/issue_db`

### Installed Extensions

- **vector**: For embedding storage and similarity search
- **pgcrypto**: For encryption functions
- **uuid-ossp**: For UUID generation
- **pg_trgm**: For text search and indexing

## 🔌 Connecting to the Database

### From Archon Applications

```python
# Database URL format
DATABASE_URL = "postgresql://archon_user:password@localhost:5433/archon_issues"

# Or using individual parameters
POSTGRESQL_HOST = "localhost"
POSTGRESQL_PORT = 5433
POSTGRESQL_DATABASE = "archon_issues"
POSTGRESQL_USER = "archon_user"
POSTGRESQL_PASSWORD = "your_password"
```

### From Command Line

```bash
# Using psql
psql -h localhost -p 5433 -U archon_user -d archon_issues

# Using Docker exec
docker exec -it Archon-Issue-DB psql -U archon_user -d archon_issues
```

## 🛠 Management Commands

### Start/Stop Services

```bash
# Start all services
docker-compose -f docker-compose.postgresql-issue-db.yml up -d

# Start with pgAdmin (optional)
docker-compose -f docker-compose.postgresql-issue-db.yml --profile admin up -d

# Stop services
docker-compose -f docker-compose.postgresql-issue-db.yml down

# Stop and remove volumes (⚠️ DELETES DATA!)
docker-compose -f docker-compose.postgresql-issue-db.yml down -v
```

### Database Operations

```bash
# Create backup
docker exec Archon-Issue-DB pg_dump -U archon_user archon_issues > backup.sql

# Restore backup
docker exec -i Archon-Issue-DB psql -U archon_user -d archon_issues < backup.sql

# View logs
docker-compose -f docker-compose.postgresql-issue-db.yml logs -f archon-issue-db
```

## 🔒 Security Considerations

1. **Change Default Passwords**: Always modify the default passwords in `.env`
2. **Network Security**: The container uses a dedicated network
3. **File Permissions**: Ensure proper permissions on the data directory
4. **SSL**: Configure SSL for production environments

## 📊 Performance Tuning

The container includes optimized PostgreSQL settings for Archon workloads:

- **Shared Buffers**: 256MB
- **Effective Cache Size**: 1GB
- **Max Connections**: 200
- **Vector Extension**: Optimized for embedding operations

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose -f docker-compose.postgresql-issue-db.yml logs archon-issue-db

# Check permissions
ls -la /mnt/network_repo/stack_dbs/postgresql/issue_db

# Reset data directory (⚠️ DELETES DATA!)
sudo rm -rf /mnt/network_repo/stack_dbs/postgresql/issue_db/*
```

### Connection Issues

```bash
# Test network connectivity
docker exec Archon-Issue-DB pg_isready -U archon_user -d archon_issues

# Check port binding
netstat -tlnp | grep 5433

# Verify environment variables
docker exec Archon-Issue-DB env | grep POSTGRES
```

### Extension Issues

```bash
# Verify extensions are installed
docker exec -it Archon-Issue-DB psql -U archon_user -d archon_issues -c "\dx"

# Reinstall extensions if needed
docker exec -it Archon-Issue-DB psql -U archon_user -d archon_issues -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## 🔗 Integration with Archon

This PostgreSQL container is designed to integrate with:

- **Issue/Bug Management System**: Primary data storage
- **Vector Search**: Embedding storage for semantic search
- **Project Management**: Task and project data
- **User Management**: Authentication and authorization data

## 📝 Next Steps

1. Configure your Archon application to use this database
2. Run database migrations to create required tables
3. Set up automated backups
4. Configure monitoring and alerting
5. Implement SSL for production use

## 🆘 Support

For issues related to this PostgreSQL setup:

1. Check the troubleshooting section above
2. Review container logs
3. Verify environment configuration
4. Check Archon documentation for database requirements
