#!/bin/bash

# PostgreSQL Issue Database Stack - Webhook Test Script
# 
# This script tests the Portainer webhook and verifies the deployment status
#
# Usage:
#   ./test-webhook.sh
#   bash test-webhook.sh

set -e

# Configuration
WEBHOOK_URL="http://10.202.70.20:9000/api/stacks/webhooks/74794986-c457-4937-9359-0c0b0adf3b04"
PORTAINER_HOST="10.202.70.20"
POSTGRES_HOST="10.202.70.20"
POSTGRES_PORT="5433"
PGADMIN_PORT="5050"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[TEST]${NC} $1"; }
print_success() { echo -e "${GREEN}[PASS]${NC} $1"; }
print_error() { echo -e "${RED}[FAIL]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Test functions
test_portainer_access() {
    print_status "Testing Portainer access..."
    if curl -s --connect-timeout 5 "http://${PORTAINER_HOST}:9000" > /dev/null; then
        print_success "Portainer is accessible"
        return 0
    else
        print_error "Cannot reach Portainer"
        return 1
    fi
}

test_webhook_trigger() {
    print_status "Testing webhook trigger..."
    response=$(curl -s -w "%{http_code}" -X POST "${WEBHOOK_URL}" -o /tmp/webhook_test.txt)
    
    if [ "$response" = "200" ] || [ "$response" = "204" ]; then
        print_success "Webhook triggered successfully (HTTP $response)"
        return 0
    else
        print_error "Webhook failed (HTTP $response)"
        if [ -s /tmp/webhook_test.txt ]; then
            cat /tmp/webhook_test.txt
        fi
        return 1
    fi
}

test_postgres_port() {
    print_status "Testing PostgreSQL port accessibility..."
    if timeout 5 bash -c "</dev/tcp/${POSTGRES_HOST}/${POSTGRES_PORT}"; then
        print_success "PostgreSQL port ${POSTGRES_PORT} is accessible"
        return 0
    else
        print_error "PostgreSQL port ${POSTGRES_PORT} is not accessible"
        return 1
    fi
}

test_pgadmin_port() {
    print_status "Testing pgAdmin port accessibility..."
    if timeout 5 bash -c "</dev/tcp/${POSTGRES_HOST}/${PGADMIN_PORT}"; then
        print_success "pgAdmin port ${PGADMIN_PORT} is accessible"
        return 0
    else
        print_error "pgAdmin port ${PGADMIN_PORT} is not accessible"
        return 1
    fi
}

test_postgres_connection() {
    print_status "Testing PostgreSQL connection..."
    if command -v psql &> /dev/null; then
        if PGPASSWORD=archon_secure_password_2024 psql -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -U archon_user -d archon_issues -c "SELECT version();" &> /dev/null; then
            print_success "PostgreSQL connection successful"
            return 0
        else
            print_warning "PostgreSQL connection failed (may need time to start)"
            return 1
        fi
    else
        print_warning "psql not available, skipping connection test"
        return 0
    fi
}

test_pgadmin_web() {
    print_status "Testing pgAdmin web interface..."
    if curl -s --connect-timeout 5 "http://${POSTGRES_HOST}:${PGADMIN_PORT}" | grep -q "pgAdmin"; then
        print_success "pgAdmin web interface is accessible"
        return 0
    else
        print_warning "pgAdmin web interface not ready (may need time to start)"
        return 1
    fi
}

# Main test execution
main() {
    echo "=================================================="
    echo "PostgreSQL Database Stack - Webhook Test"
    echo "=================================================="
    echo
    
    local tests_passed=0
    local tests_total=0
    
    # Test 1: Portainer Access
    ((tests_total++))
    if test_portainer_access; then
        ((tests_passed++))
    fi
    echo
    
    # Test 2: Webhook Trigger
    ((tests_total++))
    if test_webhook_trigger; then
        ((tests_passed++))
        
        print_status "Waiting 30 seconds for deployment to start..."
        sleep 30
    fi
    echo
    
    # Test 3: PostgreSQL Port
    ((tests_total++))
    if test_postgres_port; then
        ((tests_passed++))
    fi
    echo
    
    # Test 4: pgAdmin Port
    ((tests_total++))
    if test_pgadmin_port; then
        ((tests_passed++))
    fi
    echo
    
    # Test 5: PostgreSQL Connection
    ((tests_total++))
    if test_postgres_connection; then
        ((tests_passed++))
    fi
    echo
    
    # Test 6: pgAdmin Web Interface
    ((tests_total++))
    if test_pgadmin_web; then
        ((tests_passed++))
    fi
    echo
    
    # Summary
    echo "=================================================="
    echo "Test Results: ${tests_passed}/${tests_total} passed"
    echo "=================================================="
    
    if [ $tests_passed -eq $tests_total ]; then
        print_success "All tests passed! Deployment is successful."
        echo
        echo "🎉 Your PostgreSQL database stack is ready!"
        echo
        echo "📊 Access Information:"
        echo "   PostgreSQL: postgresql://archon_user:password@${POSTGRES_HOST}:${POSTGRES_PORT}/archon_issues"
        echo "   pgAdmin:    http://${POSTGRES_HOST}:${PGADMIN_PORT}"
        echo "   Portainer:  http://${PORTAINER_HOST}:9000"
        
        return 0
    else
        print_error "Some tests failed. Check the output above for details."
        echo
        echo "🔧 Troubleshooting:"
        echo "   1. Check Portainer stack status"
        echo "   2. Review service logs"
        echo "   3. Verify environment variables"
        echo "   4. Wait longer for services to start"
        
        return 1
    fi
}

# Cleanup
cleanup() {
    rm -f /tmp/webhook_test.txt
}

trap cleanup EXIT

# Run tests
main "$@"
