# PostgreSQL Issue Database Stack

This stack provides a PostgreSQL database with pgvector extension for Archon's issue management system.

## Components

- **PostgreSQL 15** with pgvector extension (ankane/pgvector:v0.5.1)
- **pgAdmin 4** for database administration
- **Database Initialization** service for setting up extensions

## Files

- `docker-compose.yml` - Main stack configuration
- `.env` - Environment variables and configuration
- `README.md` - This documentation
- `deploy-webhook.sh` - Automated webhook deployment script
- `test-webhook.sh` - Webhook and deployment testing script
- `WEBHOOK_DEPLOYMENT.md` - Detailed webhook deployment guide
- `.gitignore` - Git ignore rules for security

## Quick Start

### 1. Deploy via Portainer Webhook (Recommended)

```bash
# Quick deployment using webhook
curl -X POST http://10.202.70.20:9000/api/stacks/webhooks/74794986-c457-4937-9359-0c0b0adf3b04

# Or use the deployment script
./deploy-webhook.sh

# Test the deployment
./test-webhook.sh
```

### 2. Deploy via Portainer UI

1. Go to **Stacks** → **Add Stack**
2. Name: `archon-postgresql-issue-db`
3. **Repository**: Select this repository
4. **Compose path**: `database-stacks/postgresql-issue-db/docker-compose.yml`
5. **Environment file**: `database-stacks/postgresql-issue-db/.env`
6. **Enable webhook** for automated deployments
7. Deploy

### 2. Webhook Deployment (Recommended)

Trigger deployment via Portainer webhook:

```bash
# Trigger webhook deployment
curl -X POST http://10.202.70.20:9000/api/stacks/webhooks/74794986-c457-4937-9359-0c0b0adf3b04

# Or using wget
wget --method=POST http://10.202.70.20:9000/api/stacks/webhooks/74794986-c457-4937-9359-0c0b0adf3b04
```

**Webhook URL**: `http://10.202.70.20:9000/api/stacks/webhooks/74794986-c457-4937-9359-0c0b0adf3b04`

### 3. Manual Deployment

```bash
# Clone the repository
git clone https://github.com/PadsterH2012/archon-plus.git
cd archon-plus/database-stacks/postgresql-issue-db

# Deploy the stack with environment variables
POSTGRES_PASSWORD=archon_secure_password_2024 \
PGADMIN_PASSWORD=admin_secure_password_2024 \
docker stack deploy -c docker-compose.yml issues_db
```

## Access Information

### PostgreSQL Database
- **Host**: `10.202.70.20` (or your swarm manager IP)
- **Port**: `5433`
- **Database**: `archon_issues`
- **Username**: `archon_user`
- **Password**: Set in `.env` file

### pgAdmin Web Interface
- **URL**: `http://10.202.70.20:5050`
- **Email**: `admin@example.com`
- **Password**: Set in `.env` file

## Configuration

All configuration is managed through the `.env` file. Key variables:

- `POSTGRES_PASSWORD`: Database password (REQUIRED)
- `PGADMIN_PASSWORD`: pgAdmin password (REQUIRED)
- `POSTGRES_PORT`: External port for PostgreSQL (default: 5433)
- `PGADMIN_PORT`: External port for pgAdmin (default: 5050)

## Database Features

- **pgvector**: Vector similarity search extension
- **pgcrypto**: Cryptographic functions
- **uuid-ossp**: UUID generation functions
- **pg_trgm**: Trigram matching for text search

## Health Monitoring

The PostgreSQL service includes health checks:
- Checks every 30 seconds
- 5 retry attempts
- 30-second startup grace period

## Resource Limits

- **Memory**: 1GB limit, 512MB reserved
- **CPU**: 1.0 limit, 0.5 reserved

## Troubleshooting

### Service Not Starting
```bash
# Check service status
docker service ls | grep issues_db

# Check service logs
docker service logs issues_db_archon-issue-db --tail 50

# Check service details
docker service ps issues_db_archon-issue-db
```

### Connection Issues
```bash
# Test database connection
docker run --rm -it postgres:15 psql -h 10.202.70.20 -p 5433 -U archon_user -d archon_issues

# Check if port is accessible
telnet 10.202.70.20 5433
```

### Reset Database
```bash
# Remove the stack
docker stack rm issues_db

# Remove volumes (WARNING: This deletes all data)
docker volume rm issues_db_postgres_data issues_db_pgadmin_data

# Redeploy
docker stack deploy -c docker-compose.yml issues_db
```

## Security Notes

- Change default passwords in `.env` file
- Use strong passwords for production
- Consider network restrictions for database access
- pgAdmin is configured in desktop mode (no authentication required)

## Integration with Archon

This database is designed to work with Archon's issue management system. Connection details:

```bash
# Environment variables for Archon services
DATABASE_URL=postgresql://archon_user:your_password@10.202.70.20:5433/archon_issues
POSTGRESQL_HOST=10.202.70.20
POSTGRESQL_PORT=5433
POSTGRESQL_DATABASE=archon_issues
POSTGRESQL_USER=archon_user
POSTGRESQL_PASSWORD=your_password
```

## Backup and Maintenance

### Manual Backup
```bash
# Create backup
docker exec -t $(docker ps -q -f name=issues_db_archon-issue-db) pg_dump -U archon_user archon_issues > backup.sql

# Restore backup
docker exec -i $(docker ps -q -f name=issues_db_archon-issue-db) psql -U archon_user archon_issues < backup.sql
```

### Automated Backups
Consider implementing automated backups using cron jobs or backup solutions.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review Docker Swarm logs
- Consult PostgreSQL and pgAdmin documentation
