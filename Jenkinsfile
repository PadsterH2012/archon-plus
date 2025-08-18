pipeline {
    agent any
    
    environment {
        HARBOR_REGISTRY = 'hl-harbor.techpad.uk'
        HARBOR_PROJECT = 'archon'
        HARBOR_CREDENTIALS = 'jenkins-access'
        IMAGE_TAG = "${BUILD_NUMBER}-${GIT_COMMIT.take(7)}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    // Jenkins already checked out the code, just verify we're on the right branch
                    sh 'git branch'
                    sh 'pwd && ls -la'
                }
            }
        }
        
        stage('Environment Setup') {
            steps {
                script {
                    // Load environment variables
                    sh 'cp .env.example .env.build'

                    // Inject build-specific variables
                    sh """
                        echo "BUILD_NUMBER=${BUILD_NUMBER}" >> .env.build
                        echo "GIT_COMMIT=${GIT_COMMIT}" >> .env.build
                        echo "BUILD_TIMESTAMP=\$(date -u +%Y%m%d_%H%M%S)" >> .env.build
                    """
                }
            }
        }
        
        stage('Build Docker Images') {
            parallel {
                stage('Build Archon Server') {
                    steps {
                        dir("python") {
                            script {
                                sh """
                                    docker build \\
                                        -f Dockerfile.server \\
                                        -t archon-server:${BUILD_NUMBER} \\
                                        -t archon-server:latest \\
                                        --build-arg BUILD_NUMBER=${BUILD_NUMBER} \\
                                        --build-arg GIT_COMMIT=${GIT_COMMIT} \\
                                        .
                                """
                            }
                        }
                    }
                }
                
                stage('Build Archon MCP') {
                    steps {
                        dir("python") {
                            script {
                                sh """
                                    docker build \\
                                        -f Dockerfile.mcp \\
                                        -t archon-mcp:${BUILD_NUMBER} \\
                                        -t archon-mcp:latest \\
                                        --build-arg BUILD_NUMBER=${BUILD_NUMBER} \\
                                        --build-arg GIT_COMMIT=${GIT_COMMIT} \\
                                        .
                                """
                            }
                        }
                    }
                }
                
                stage('Build Archon Agents') {
                    steps {
                        dir("python") {
                            script {
                                sh """
                                    docker build \\
                                        -f Dockerfile.agents \\
                                        -t archon-agents:${BUILD_NUMBER} \\
                                        -t archon-agents:latest \\
                                        --build-arg BUILD_NUMBER=${BUILD_NUMBER} \\
                                        --build-arg GIT_COMMIT=${GIT_COMMIT} \\
                                        .
                                """
                            }
                        }
                    }
                }
                
                stage('Build Archon UI') {
                    steps {
                        dir("archon-ui-main") {
                            script {
                                sh """
                                    docker build \\
                                        -t archon-ui:${BUILD_NUMBER} \\
                                        -t archon-ui:latest \\
                                        --build-arg BUILD_NUMBER=${BUILD_NUMBER} \\
                                        --build-arg GIT_COMMIT=${GIT_COMMIT} \\
                                        .
                                """
                            }
                        }
                    }
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                script {
                    // Optional: Add container security scanning
                    sh """
                        echo "Running security scans on built images..."
                        # Add your preferred security scanning tool here
                        # Example: trivy, clair, or harbor's built-in scanning
                    """
                }
            }
        }
        
        stage('Push to Harbor Registry') {
            steps {
                echo "🚢 Pushing to Harbor registry..."

                script {
                    withCredentials([usernamePassword(credentialsId: "${HARBOR_CREDENTIALS}", usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS')]) {
                        sh '''
                            echo "🔐 Attempting Harbor registry login..."
                            echo "🔧 Installing homelab CA certificate for Harbor registry..."

                            # Create Docker certs directory for Harbor registry
                            echo "P0w3rPla72012@@" | sudo -S mkdir -p /etc/docker/certs.d/${HARBOR_REGISTRY}

                            # Extract CA certificate from Harbor
                            echo "📥 Extracting CA certificate from Harbor..."
                            echo | openssl s_client -servername ${HARBOR_REGISTRY} -connect ${HARBOR_REGISTRY}:443 2>/dev/null | openssl x509 > /tmp/homelab-ca.crt

                            # Install the CA certificate for Docker
                            echo "🔧 Installing CA certificate for Docker..."
                            echo "P0w3rPla72012@@" | sudo -S cp /tmp/homelab-ca.crt /etc/docker/certs.d/${HARBOR_REGISTRY}/ca.crt

                            # Also install system-wide
                            echo "🔧 Installing CA certificate system-wide..."
                            echo "P0w3rPla72012@@" | sudo -S cp /tmp/homelab-ca.crt /usr/local/share/ca-certificates/homelab-ca.crt
                            echo "P0w3rPla72012@@" | sudo -S update-ca-certificates

                            echo "✅ CA certificate installed"

                            echo "🔄 Attempting Harbor registry login..."
                            echo "$HARBOR_PASS" | docker login ${HARBOR_REGISTRY} -u "$HARBOR_USER" --password-stdin
                            echo "✅ Harbor login successful!"

                            echo "🏷️ Retagging images for Harbor..."
                            docker tag archon-server:${BUILD_NUMBER} ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-server:${IMAGE_TAG}
                            docker tag archon-mcp:${BUILD_NUMBER} ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-mcp:${IMAGE_TAG}
                            docker tag archon-agents:${BUILD_NUMBER} ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-agents:${IMAGE_TAG}
                            docker tag archon-ui:${BUILD_NUMBER} ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-ui:${IMAGE_TAG}

                            docker tag archon-server:latest ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-server:latest
                            docker tag archon-mcp:latest ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-mcp:latest
                            docker tag archon-agents:latest ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-agents:latest
                            docker tag archon-ui:latest ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-ui:latest

                            echo "📤 Pushing versioned images..."
                            docker push ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-server:${IMAGE_TAG}
                            docker push ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-mcp:${IMAGE_TAG}
                            docker push ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-agents:${IMAGE_TAG}
                            docker push ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-ui:${IMAGE_TAG}

                            echo "📤 Pushing latest images..."
                            docker push ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-server:latest
                            docker push ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-mcp:latest
                            docker push ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-agents:latest
                            docker push ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-ui:latest

                            echo "✅ Successfully pushed to Harbor!"
                            echo "🌐 Images available at: ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-*:${IMAGE_TAG}"
                        '''
                    }
                }
            }
        }

        stage('Update Deployment Manifests') {
            steps {
                script {
                    // Update docker-compose files with new image tags
                    sh """
                        # Create deployment-specific compose file
                        cp deployment/swarm/archon-stack.yml deployment/swarm/archon-stack-${BUILD_NUMBER}.yml

                        # Update image tags in deployment manifest
                        sed -i 's|image: hl-harbor.techpad.uk/archon/archon-server:.*|image: ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-server:${IMAGE_TAG}|g' deployment/swarm/archon-stack-${BUILD_NUMBER}.yml
                        sed -i 's|image: hl-harbor.techpad.uk/archon/archon-mcp:.*|image: ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-mcp:${IMAGE_TAG}|g' deployment/swarm/archon-stack-${BUILD_NUMBER}.yml
                        sed -i 's|image: hl-harbor.techpad.uk/archon/archon-agents:.*|image: ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-agents:${IMAGE_TAG}|g' deployment/swarm/archon-stack-${BUILD_NUMBER}.yml
                        sed -i 's|image: hl-harbor.techpad.uk/archon/archon-ui:.*|image: ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/archon-ui:${IMAGE_TAG}|g' deployment/swarm/archon-stack-${BUILD_NUMBER}.yml
                    """
                }
            }
        }

        stage('Deploy via Portainer Webhook') {
            when {
                anyOf {
                    branch 'homelab-deployment'
                    expression { params.FORCE_DEPLOY == true }
                }
            }
            steps {
                script {
                    sh """
                        echo "🚀 Triggering Portainer stack redeploy..."

                        # Trigger Portainer webhook to redeploy stack with new images
                        WEBHOOK_RESPONSE=\$(curl -s -w "%{http_code}" -X POST \\
                            http://10.202.70.20:9000/api/stacks/webhooks/33fc8bc2-1582-4ad5-97b7-d1bb9f4289f8)

                        echo "Webhook response: \$WEBHOOK_RESPONSE"

                        if [ "\$WEBHOOK_RESPONSE" = "200" ] || [ "\$WEBHOOK_RESPONSE" = "204" ]; then
                            echo "✅ Portainer webhook triggered successfully!"
                            echo "🔄 Stack redeployment initiated in Portainer"
                            echo "📊 Monitor deployment progress at: http://10.202.70.20:9000"
                            echo "🌐 Images deployed: hl-harbor.techpad.uk/archon/archon-*:${IMAGE_TAG}"
                        else
                            echo "❌ Webhook failed with response: \$WEBHOOK_RESPONSE"
                            exit 1
                        fi

                        echo "⏳ Waiting for deployment to start..."
                        sleep 10
                    """
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    sh """
                        echo "Performing health checks..."

                        # Wait for services to stabilize
                        sleep 60

                        # Check Archon API health (skip SSL verification for self-signed certs)
                        curl -f -k https://archon-api.techpad.uk/api/health || exit 1

                        # Check Archon Agents health (skip SSL verification for self-signed certs)
                        curl -f -k https://archon-agents.techpad.uk/health || exit 1

                        # Check Archon UI accessibility (skip SSL verification for self-signed certs)
                        curl -f -k https://archon.techpad.uk || exit 1

                        echo "All health checks passed!"
                    """
                }
            }
        }
    }

    post {
        always {
            script {
                // Cleanup
                sh """
                    docker logout ${HARBOR_REGISTRY}
                    docker system prune -f
                """
            }
        }

        success {
            script {
                echo "✅ Archon deployment completed successfully!"
                echo "🌐 Archon UI: https://archon.techpad.uk"
                echo "🔌 MCP Server: https://archon-mcp.techpad.uk"
                echo "📡 API Server: https://archon-api.techpad.uk"
            }
        }

        failure {
            script {
                echo "❌ Archon deployment failed!"
                // Optional: Send notifications, rollback, etc.
            }
        }
    }
}
