# Archon Deployment Configuration

This directory contains the standardized deployment configuration for Archon environments.

## 📁 File Structure

```
deployment/
├── .env.dev              # Development environment variables
├── .env.prod             # Production environment variables  
├── archon-dev-stack.yml  # Development Docker Swarm stack
├── archon-prod-stack.yml # Production Docker Swarm stack
└── README.md             # This file
```

## 🚀 Deployment Commands

### Development Environment
```bash
# Load development environment
source deployment/.env.dev

# Deploy development stack
docker stack deploy -c deployment/archon-dev-stack.yml archon-dev

# Access development services
# UI: http://10.202.70.20:4737
# API: http://10.202.70.20:9181
# MCP: http://10.202.70.20:9051
```

### Production Environment
```bash
# Load production environment
source deployment/.env.prod

# Deploy production stack
docker stack deploy -c deployment/archon-prod-stack.yml archon

# Access production services
# UI: http://10.202.70.20:3737
# API: http://10.202.70.20:8181
# MCP: http://10.202.70.20:8051
```

## 🔧 Environment Configuration

### Development (.env.dev)
- **Ports**: 9xxx series (9181, 9051, 9052, 4737, 9080)
- **Database**: Development Supabase project
- **Logging**: DEBUG level
- **Resources**: Reduced limits for development
- **CORS**: Enabled for development

### Production (.env.prod)
- **Ports**: 8xxx series (8181, 8051, 8052, 3737, 8080)
- **Database**: Production Supabase project
- **Logging**: INFO level
- **Resources**: Full production limits
- **CORS**: Disabled for security

## 📋 Service Overview

| Service | Development Port | Production Port | Purpose |
|---------|------------------|-----------------|---------|
| archon-server | 9181 | 8181 | Core API and business logic |
| archon-mcp | 9051 | 8051 | Model Context Protocol |
| archon-agents | 9052 | 8052 | AI operations and streaming |
| archon-ui | 4737 | 3737 | Web interface |
| archon-embeddings | 9080 | 8080 | Text embeddings service |

## 🔄 Migration from Old Structure

This replaces the previous scattered configuration:
- ❌ `portainer-templates/archon-saas-supabase.yml` (removed)
- ❌ `deployment/swarm/archon-stack.yml` (removed)
- ❌ `portainer-templates/.env.dev` (moved)
- ❌ `portainer-templates/.env.prod` (moved)

## 🛠 Troubleshooting

### Service Not Starting
1. Check environment variables are loaded: `env | grep ARCHON`
2. Verify Supabase connectivity: `curl $SUPABASE_URL/rest/v1/`
3. Check Docker Swarm status: `docker service ls`

### Port Conflicts
- Development uses 9xxx ports to avoid production conflicts
- Production uses 8xxx ports for standard deployment
- Ensure no other services are using these ports

### Network Issues
- All services use `archon-network` overlay network
- `archon-server` has network alias for nginx resolution
- Check network connectivity: `docker network ls`
