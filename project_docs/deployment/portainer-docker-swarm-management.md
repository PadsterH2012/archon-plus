# Portainer & Docker Swarm Management

**File Path:** `docs/docs/portainer-docker-swarm-management.mdx`
**Last Updated:** 2025-08-23

## Purpose
Comprehensive documentation for managing Archon deployments using Portainer and Docker Swarm, including service updates, stack management, and troubleshooting procedures.

## Key Features

### Environment Architecture
- **archon-prod**: Production environment managed via Portainer
- **archon-dev**: Development environment managed via Portainer  
- **Local testing**: Development machine (hl-dev-lnx-01)

### Service Endpoints
| Environment | Portainer | Services | SSH Access |
|-------------|-----------|----------|------------|
| **archon-prod** | Portainer UI | Various ports | 10.202.70.20 |
| **archon-dev** | Portainer UI | Port 9181 (server) | 10.202.70.20 |
| **Local** | N/A | Port 8080 (server) | hl-dev-lnx-01 |

## Core Operations

### Docker Swarm Node Configuration

| Node | IP Address | Role | Purpose |
|------|------------|------|---------|
| **hl-dswarm1** | `10.202.70.20` | Manager | Swarm orchestration, SSH access point, Portainer host |
| **hl-dswarm2** | `10.202.70.21` | Worker | Service execution, container hosting |
| **hl-dswarm3** | `10.202.70.22` | Worker | Service execution, container hosting |

### SSH Access Setup
```bash
# SSH credentials for Docker Swarm cluster
USER="paddy"
PASSWORD="P0w3rPla72012@@"

# Primary access point (Swarm Manager)
SWARM_MANAGER="10.202.70.20"  # hl-dswarm1

# Worker nodes (for direct container access if needed)
WORKER_NODE_2="10.202.70.21"  # hl-dswarm2
WORKER_NODE_3="10.202.70.22"  # hl-dswarm3

# Using sshpass for automated access to swarm manager
sshpass -p 'P0w3rPla72012@@' ssh -o StrictHostKeyChecking=no paddy@10.202.70.20

# Access specific worker node (if container debugging needed)
sshpass -p 'P0w3rPla72012@@' ssh -o StrictHostKeyChecking=no paddy@10.202.70.21
```

### Service Management Commands
```bash
# List all services
docker service ls

# Update service with latest image
docker service update --force --image <image-name> <service-id>

# View service logs
docker service logs <service-id> --tail 50

# Scale service
docker service scale <service-id>=<replica-count>
```

### Stack Management Commands
```bash
# List all stacks
docker stack ls

# View stack services
docker stack services <stack-name>

# Deploy stack from compose file
docker stack deploy -c docker-compose.yml <stack-name>

# Remove stack
docker stack rm <stack-name>
```

## Harbor Registry Integration

### Image Management
- **Registry**: `hl-harbor.techpad.uk`
- **Images**: 
  - `archon/archon-server:latest`
  - `archon/archon-mcp:latest`
  - `archon/archon-agents:latest`
  - `archon/archon-ui:latest`

### Force Image Updates
```bash
# Force pull and update (recommended)
docker service update --force --image hl-harbor.techpad.uk/archon/archon-server:latest <service-id>
```

## Troubleshooting Procedures

### Service Recovery
```bash
# Method 1: Scale down and up
docker service scale <service-id>=0
sleep 10
docker service scale <service-id>=1

# Method 2: Force update
docker service update --force <service-id>
```

### Health Check Verification
```bash
# Check service health
curl http://<host>:<port>/health

# View container health status
docker ps --filter health=unhealthy
```

## Best Practices

### Update Workflow
1. **Test Locally**: Always test changes on local environment first
2. **Update Dev**: Deploy to archon-dev for testing
3. **Verify Functionality**: Run comprehensive tests
4. **Update Production**: Deploy to archon-prod after verification
5. **Monitor**: Watch logs and health checks post-deployment

### Monitoring
```bash
# Watch service status
watch 'docker service ls'

# Monitor specific service
watch 'docker service ps <service-id>'

# Follow logs in real-time
docker service logs -f <service-id>
```

## Service IDs Reference

| Service | Environment | Service ID | Port |
|---------|-------------|------------|------|
| archon-server | archon-dev | hvdujoo2getr | 9181 |
| archon-mcp | archon-dev | nizrruo5eprp | 9051 |
| archon-agents | archon-dev | mz1ip7odqrtc | 9052 |
| archon-ui | archon-dev | ijxwyfssm1om | 4737 |

*Note: Service IDs may change after updates. Use `docker service ls` to get current IDs.*

## Related Files
- **Troubleshooting Guide**: `docs/docs/docker-swarm-troubleshooting.mdx`
- **Stack Management**: `docs/docs/portainer-stack-management.mdx`
- **Server Deployment**: `docs/docs/server-deployment.mdx`
- **Configuration**: `docs/docs/configuration.mdx`

## Usage Examples

### Force Update archon-dev Server
```bash
# Connect to swarm manager
sshpass -p 'P0w3rPla72012@@' ssh -o StrictHostKeyChecking=no paddy@10.202.70.20

# Find the service
docker service ls | grep archon-dev

# Update the server service
docker service update --force --image hl-harbor.techpad.uk/archon/archon-server:latest hvdujoo2getr
```

### Update All Services in Stack
```bash
# Update all services in archon-dev stack
for service in $(docker service ls --filter label=com.docker.stack.namespace=archon-dev --format "{{.ID}}"); do
    docker service update --force $service
done
```

## Notes
This documentation provides the foundation for managing Archon's Docker Swarm deployments through both Portainer UI and command line interfaces. It includes practical examples, troubleshooting procedures, and best practices for maintaining production and development environments.

---
*Auto-generated documentation - verify accuracy before use*
