# Archon Portainer Templates

This directory contains Docker Swarm stack templates for deploying Archon in different environments using Portainer.

## 📋 Available Templates

### 1. Archon with SaaS Supabase - PRODUCTION (`archon-saas-supabase-prod.yml`)
**Recommended for production deployments**

- Uses external Supabase (supabase.com) for database and auth
- Production-grade resource allocation
- INFO level logging for performance
- Standard production ports

**Services:**
- `archon-server`: Core API and business logic (Port: 8181)
- `archon-mcp`: Model Context Protocol interface (Port: 8051)
- `archon-agents`: AI operations and streaming (Port: 8052)
- `archon-ui`: Web interface (Port: 3737)
- `archon-embeddings`: Text embeddings service (Port: 8080)

### 2. Archon with SaaS Supabase - DEVELOPMENT (`archon-saas-supabase-dev.yml`)
**Recommended for development and testing**

- Uses external Supabase (supabase.com) for database and auth
- Reduced resource requirements for development
- DEBUG level logging for troubleshooting
- Alternative ports to avoid conflicts with production

**Services:**
- `dev-archon-server`: Core API and business logic (Port: 9181)
- `dev-archon-mcp`: Model Context Protocol interface (Port: 9051)
- `dev-archon-agents`: AI operations and streaming (Port: 9052)
- `dev-archon-ui`: Web interface (Port: 4737)
- `dev-archon-embeddings`: Text embeddings service (Port: 9080)

### 3. Archon Self-Hosted (`archon-self-hosted.yml`)
**For complete data privacy and control**

- Complete self-hosted Supabase stack
- No external dependencies
- Full data privacy and control
- Higher resource requirements

**Services:**
- `postgres`: PostgreSQL with pgvector extension
- `supabase-auth`: Authentication service (GoTrue)
- `supabase-rest`: PostgREST API (Port: 8000)
- `supabase-realtime`: Real-time subscriptions (Port: 4000)
- All Archon services (same as SaaS version)

## 🔄 Running Dev and Prod Simultaneously

The dev and prod templates are designed to run simultaneously in the same Docker Swarm without conflicts:

### Key Differences:
- **Service Names**: Dev services prefixed with `dev-`, prod uses standard names
- **Networks**: Separate networks (`archon-dev-network` vs `archon-network`)
- **Ports**: Dev uses 9xxx ports, prod uses 8xxx ports
- **Resources**: Dev uses reduced CPU/memory allocation
- **Logging**: Dev defaults to DEBUG, prod to INFO

### Port Mapping:
| Service | Development | Production |
|---------|-------------|------------|
| Server API | 9181 | 8181 |
| MCP Server | 9051 | 8051 |
| Agents Service | 9052 | 8052 |
| Web UI | 4737 | 3737 |
| Embeddings | 9080 | 8080 |

## 🚀 Quick Start

### Option 1: Using Portainer UI

1. **Add Template Repository**:
   - Go to Portainer → App Templates → Settings
   - Add template URL: `https://raw.githubusercontent.com/PadsterH2012/Archon/main/portainer-templates/templates.json`

2. **Deploy Stack**:
   - Go to App Templates
   - Select your desired template:
     - "Archon with SaaS Supabase - PRODUCTION" for production deployment
     - "Archon with SaaS Supabase - DEVELOPMENT" for development/testing
     - "Archon Self-Hosted (Full Stack)" for complete self-hosted setup
   - Fill in required environment variables
   - Click "Deploy the stack"

### Option 2: Manual Stack Deployment

1. **Copy Template**:
   ```bash
   # For production
   wget https://raw.githubusercontent.com/PadsterH2012/Archon/main/portainer-templates/archon-saas-supabase-prod.yml

   # For development
   wget https://raw.githubusercontent.com/PadsterH2012/Archon/main/portainer-templates/archon-saas-supabase-dev.yml

   # For self-hosted
   wget https://raw.githubusercontent.com/PadsterH2012/Archon/main/portainer-templates/archon-self-hosted.yml
   ```

2. **Deploy in Portainer**:
   - Go to Stacks → Add stack
   - Upload the YAML file
   - Configure environment variables
   - Deploy

### Option 3: Deploy Both Dev and Prod

To run both development and production environments simultaneously:

1. **Deploy Production First**:
   - Use `archon-saas-supabase-prod.yml`
   - Name the stack: `archon-prod`
   - Use production environment variables

2. **Deploy Development Second**:
   - Use `archon-saas-supabase-dev.yml`
   - Name the stack: `archon-dev`
   - Use development environment variables (different Supabase project recommended)

## ⚙️ Configuration

### SaaS Supabase Setup

**Prerequisites:**
1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Get your project credentials from Settings → API

**Required Environment Variables:**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-secret
```

**Database Setup:**
1. Go to your Supabase project → SQL Editor
2. Run the migration scripts from `/migration/complete_setup.sql`
3. Enable pgvector extension if not already enabled

### Self-Hosted Setup

**Required Environment Variables:**
```env
POSTGRES_PASSWORD=your-secure-password
JWT_SECRET=your-super-secret-jwt-token-with-at-least-32-characters-long
SERVICE_ROLE_KEY=your-service-role-jwt-token
```

**Optional Configuration:**
```env
POSTGRES_DB=archon
POSTGRES_USER=postgres
HOST=your-domain.com
API_EXTERNAL_URL=http://your-domain.com:8000
SITE_URL=http://your-domain.com:3737
```

## 🔧 Resource Requirements

### Production Template (archon-saas-supabase-prod.yml)
| Service | Memory | CPU | Storage |
|---------|--------|-----|---------|
| archon-server | 1GB | 1 core | - |
| archon-mcp | 512MB | 0.5 core | - |
| archon-agents | 1GB | 1 core | - |
| archon-ui | 512MB | 0.5 core | - |
| archon-embeddings | 2GB | 2 cores | - |
| **Total** | **5GB** | **5 cores** | **-** |

### Development Template (archon-saas-supabase-dev.yml)
| Service | Memory | CPU | Storage |
|---------|--------|-----|---------|
| dev-archon-server | 512MB | 0.5 core | - |
| dev-archon-mcp | 256MB | 0.25 core | - |
| dev-archon-agents | 512MB | 0.5 core | - |
| dev-archon-ui | 256MB | 0.25 core | - |
| dev-archon-embeddings | 1GB | 1 core | - |
| **Total** | **2.5GB** | **2.5 cores** | **Minimal** |

### Self-Hosted Template
| Service | Memory | CPU | Storage |
|---------|--------|-----|---------|
| postgres | 2GB | 1 core | 20GB+ |
| supabase-auth | 512MB | 0.5 core | - |
| supabase-rest | 512MB | 0.5 core | - |
| supabase-realtime | 1GB | 0.5 core | - |
| archon-server | 1GB | 1 core | - |
| archon-mcp | 512MB | 0.5 core | - |
| archon-agents | 1GB | 1 core | - |
| archon-ui | 512MB | 0.5 core | - |
| **Total** | **7GB** | **5 cores** | **20GB+** |

## 🌐 Network Configuration

### Ports Exposed

**Production Ports (archon-saas-supabase-prod.yml):**
- `3737`: Web UI
- `8181`: Main API Server
- `8051`: MCP Server
- `8052`: Agents Service
- `8080`: Text Embeddings Service

**Development Ports (archon-saas-supabase-dev.yml):**
- `4737`: Web UI
- `9181`: Main API Server
- `9051`: MCP Server
- `9052`: Agents Service
- `9080`: Text Embeddings Service

**Self-Hosted Additional Ports:**
- `5432`: PostgreSQL (internal)
- `8000`: Supabase REST API
- `4000`: Supabase Realtime
- `9999`: Supabase Auth

### Reverse Proxy Setup

For production deployments, use a reverse proxy (Traefik, Nginx, etc.):

```yaml
# Example Traefik labels for archon-ui service
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.archon.rule=Host(`archon.yourdomain.com`)"
  - "traefik.http.routers.archon.tls.certresolver=letsencrypt"
  - "traefik.http.services.archon.loadbalancer.server.port=5173"
```

## 🔒 Security Considerations

### SaaS Supabase
- Use Row Level Security (RLS) in Supabase
- Rotate API keys regularly
- Enable 2FA on Supabase account
- Monitor access logs

### Self-Hosted
- Use strong passwords for PostgreSQL
- Generate secure JWT secrets (32+ characters)
- Enable SSL/TLS for external access
- Regular security updates
- Backup encryption

## 📊 Monitoring

### Health Checks
All services include health checks:
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3
- Start period: 30-90 seconds

### Logging
Configure log levels via `LOG_LEVEL` environment variable:
- `DEBUG`: Detailed debugging information
- `INFO`: General information (default)
- `WARNING`: Warning messages only
- `ERROR`: Error messages only

### Optional: Logfire Integration
Add `LOGFIRE_TOKEN` for enhanced monitoring and observability.

## 🔄 Updates and Maintenance

### Updating Services
1. Pull latest images:
   ```bash
   docker service update --image ghcr.io/padsterh2012/archon-server:latest archon_archon-server
   ```

2. Or redeploy the entire stack with updated images

### Backup Strategies

**SaaS Supabase:**
- Automatic backups via Supabase
- Export data via Supabase dashboard
- Version control your configuration

**Self-Hosted:**
- Regular PostgreSQL backups:
  ```bash
  docker exec postgres pg_dump -U postgres archon > backup.sql
  ```
- Volume backups for persistent data
- Configuration backups

## 🐛 Troubleshooting

### Common Issues

**1. Services not starting:**
- Check resource constraints
- Verify environment variables
- Check service dependencies

**2. Database connection errors:**
- Verify Supabase credentials
- Check network connectivity
- Ensure database is accessible

**3. Port conflicts:**
- Modify port mappings in environment variables
- Check for conflicting services

### Debug Commands

```bash
# Check service logs
docker service logs archon_archon-server

# Check service status
docker service ls

# Inspect service configuration
docker service inspect archon_archon-server

# Check network connectivity
docker exec -it archon_archon-server.1.xxx ping postgres
```

## 📚 Additional Resources

- [Archon Documentation](https://github.com/PadsterH2012/Archon/tree/main/docs)
- [Docker Swarm Documentation](https://docs.docker.com/engine/swarm/)
- [Portainer Documentation](https://docs.portainer.io/)
- [Supabase Documentation](https://supabase.com/docs)

## 🤝 Support

For issues and questions:
- [GitHub Issues](https://github.com/PadsterH2012/Archon/issues)
- [GitHub Discussions](https://github.com/PadsterH2012/Archon/discussions)
- [Contributing Guide](https://github.com/PadsterH2012/Archon/blob/main/CONTRIBUTING.md)
