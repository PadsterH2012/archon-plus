# Webhook Deployment Guide

This guide explains how to deploy the PostgreSQL Issue Database Stack using Portainer webhooks.

## 🚀 Quick Deployment

### Method 1: Using the Deployment Script

```bash
# Make script executable (if not already)
chmod +x deploy-webhook.sh

# Run the deployment script
./deploy-webhook.sh
```

### Method 2: Direct Webhook Call

```bash
# Using curl
curl -X POST http://10.202.70.20:9000/api/stacks/webhooks/74794986-c457-4937-9359-0c0b0adf3b04

# Using wget
wget --method=POST http://10.202.70.20:9000/api/stacks/webhooks/74794986-c457-4937-9359-0c0b0adf3b04

# Using PowerShell (Windows)
Invoke-WebRequest -Uri "http://10.202.70.20:9000/api/stacks/webhooks/74794986-c457-4937-9359-0c0b0adf3b04" -Method POST
```

## 📋 Webhook Configuration

- **Webhook URL**: `http://10.202.70.20:9000/api/stacks/webhooks/74794986-c457-4937-9359-0c0b0adf3b04`
- **Method**: POST
- **Stack Name**: `archon-postgresql-issue-db`
- **Repository**: `https://github.com/PadsterH2012/archon-plus`
- **Compose Path**: `database-stacks/postgresql-issue-db/docker-compose.yml`

## 🔧 Portainer Stack Configuration

To set up the webhook in Portainer:

1. **Go to Portainer** → Stacks → Add Stack
2. **Name**: `archon-postgresql-issue-db`
3. **Build method**: Repository
4. **Repository URL**: `https://github.com/PadsterH2012/archon-plus`
5. **Repository reference**: `refs/heads/main`
6. **Compose path**: `database-stacks/postgresql-issue-db/docker-compose.yml`
7. **Environment variables**:
   ```
   POSTGRES_PASSWORD=archon_secure_password_2024
   PGADMIN_PASSWORD=admin_secure_password_2024
   POSTGRES_PORT=5433
   PGADMIN_PORT=5050
   ```
8. **Enable webhook** in Advanced settings
9. **Deploy** the stack
10. **Copy webhook URL** from stack details

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy PostgreSQL Database
on:
  push:
    paths:
      - 'database-stacks/postgresql-issue-db/**'
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Portainer Webhook
        run: |
          curl -X POST http://10.202.70.20:9000/api/stacks/webhooks/74794986-c457-4937-9359-0c0b0adf3b04
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    
    triggers {
        githubPush()
    }
    
    stages {
        stage('Deploy Database Stack') {
            when {
                changeset "database-stacks/postgresql-issue-db/**"
            }
            steps {
                sh '''
                    curl -X POST http://10.202.70.20:9000/api/stacks/webhooks/74794986-c457-4937-9359-0c0b0adf3b04
                '''
            }
        }
    }
}
```

## 📊 Monitoring Deployment

After triggering the webhook:

1. **Check Portainer Dashboard**: `http://10.202.70.20:9000/#/stacks`
2. **Monitor stack status**: Look for `archon-postgresql-issue-db` stack
3. **View service logs**: Click on services to see deployment progress
4. **Verify services**: Ensure all services show `1/1` replicas

## 🔍 Troubleshooting

### Common Issues

1. **Webhook returns 404**:
   - Check webhook URL is correct
   - Verify stack exists in Portainer
   - Ensure webhook is enabled

2. **Webhook returns 500**:
   - Check repository access
   - Verify compose file path
   - Check environment variables

3. **Services not starting**:
   - Check service logs in Portainer
   - Verify environment variables are set
   - Check resource availability

### Debug Commands

```bash
# Check webhook response
curl -v -X POST http://10.202.70.20:9000/api/stacks/webhooks/74794986-c457-4937-9359-0c0b0adf3b04

# Check stack status via SSH
sshpass -p 'P0w3rPla72012@@' ssh paddy@10.202.70.20 "docker service ls | grep issues_db"

# Check service logs
sshpass -p 'P0w3rPla72012@@' ssh paddy@10.202.70.20 "docker service logs issues_db_archon-issue-db --tail 20"
```

## 🔐 Security Considerations

- **Webhook URL**: Contains sensitive UUID, keep secure
- **Network Access**: Ensure webhook endpoint is accessible
- **Environment Variables**: Use secure passwords in production
- **Repository Access**: Ensure Portainer has read access to repository

## 📈 Automation Ideas

1. **Auto-deploy on git push** to main branch
2. **Scheduled deployments** for updates
3. **Integration with monitoring** for health checks
4. **Slack/Teams notifications** on deployment status
5. **Rollback mechanisms** for failed deployments

## 🎯 Next Steps

1. Test webhook deployment
2. Set up CI/CD integration
3. Configure monitoring and alerting
4. Document environment-specific configurations
5. Create rollback procedures
