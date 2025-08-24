#!/bin/bash

# PostgreSQL Issue Database Stack - Webhook Deployment Script
# 
# This script triggers the Portainer webhook to deploy/update the PostgreSQL database stack
# from the GitHub repository.
#
# Usage:
#   ./deploy-webhook.sh
#   bash deploy-webhook.sh
#
# Prerequisites:
# - Portainer stack must be configured with webhook enabled
# - Repository access configured in Portainer
# - Network access to Portainer instance

set -e  # Exit on any error

# Configuration
WEBHOOK_URL="http://10.202.70.20:9000/api/stacks/webhooks/74794986-c457-4937-9359-0c0b0adf3b04"
PORTAINER_HOST="10.202.70.20:9000"
STACK_NAME="archon-postgresql-issue-db"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Portainer is accessible
check_portainer() {
    print_status "Checking Portainer accessibility..."
    
    if curl -s --connect-timeout 5 "http://${PORTAINER_HOST}" > /dev/null; then
        print_success "Portainer is accessible at http://${PORTAINER_HOST}"
        return 0
    else
        print_error "Cannot reach Portainer at http://${PORTAINER_HOST}"
        print_error "Please check:"
        print_error "  - Network connectivity"
        print_error "  - Portainer service status"
        print_error "  - Firewall settings"
        return 1
    fi
}

# Function to trigger webhook
trigger_webhook() {
    print_status "Triggering webhook deployment..."
    print_status "Webhook URL: ${WEBHOOK_URL}"
    
    # Trigger the webhook
    response=$(curl -s -w "%{http_code}" -X POST "${WEBHOOK_URL}" -o /tmp/webhook_response.txt)
    
    if [ "$response" = "200" ] || [ "$response" = "204" ]; then
        print_success "Webhook triggered successfully!"
        print_success "HTTP Status: $response"
        
        # Show response if available
        if [ -s /tmp/webhook_response.txt ]; then
            print_status "Response:"
            cat /tmp/webhook_response.txt
            echo
        fi
        
        print_status "Stack deployment initiated. Check Portainer for progress:"
        print_status "  → http://${PORTAINER_HOST}/#/stacks"
        
        return 0
    else
        print_error "Webhook failed with HTTP status: $response"
        
        if [ -s /tmp/webhook_response.txt ]; then
            print_error "Response:"
            cat /tmp/webhook_response.txt
            echo
        fi
        
        return 1
    fi
}

# Function to show deployment status
show_status() {
    print_status "After deployment, you can access:"
    echo
    echo "  📊 Portainer Dashboard:"
    echo "     http://${PORTAINER_HOST}/#/stacks"
    echo
    echo "  🗄️  PostgreSQL Database:"
    echo "     Host: 10.202.70.20"
    echo "     Port: 5433"
    echo "     Database: archon_issues"
    echo "     Username: archon_user"
    echo "     Connection: postgresql://archon_user:password@10.202.70.20:5433/archon_issues"
    echo
    echo "  🔧 pgAdmin Web Interface:"
    echo "     URL: http://10.202.70.20:5050"
    echo "     Email: admin@archon.local"
    echo "     Password: admin_secure_password_2024"
    echo
    echo "  📋 Stack Management:"
    echo "     Stack Name: ${STACK_NAME}"
    echo "     Services: archon-issue-db, pgadmin, db-init"
    echo
}

# Function to cleanup temporary files
cleanup() {
    rm -f /tmp/webhook_response.txt
}

# Main execution
main() {
    echo "=================================================="
    echo "PostgreSQL Database Stack - Webhook Deployment"
    echo "=================================================="
    echo
    
    # Check prerequisites
    if ! command -v curl &> /dev/null; then
        print_error "curl is required but not installed"
        exit 1
    fi
    
    # Check Portainer accessibility
    if ! check_portainer; then
        exit 1
    fi
    
    echo
    print_status "Deploying PostgreSQL Issue Database Stack..."
    print_status "Repository: https://github.com/PadsterH2012/archon-plus"
    print_status "Compose Path: database-stacks/postgresql-issue-db/docker-compose.yml"
    echo
    
    # Trigger webhook
    if trigger_webhook; then
        echo
        print_success "Deployment webhook triggered successfully!"
        echo
        show_status
    else
        echo
        print_error "Deployment failed!"
        print_error "Please check:"
        print_error "  - Webhook URL is correct"
        print_error "  - Stack configuration in Portainer"
        print_error "  - Repository access permissions"
        print_error "  - Environment variables are set"
        exit 1
    fi
    
    # Cleanup
    cleanup
}

# Handle script interruption
trap cleanup EXIT

# Run main function
main "$@"
