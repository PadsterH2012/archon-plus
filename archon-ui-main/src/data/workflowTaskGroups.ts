import { WorkflowTaskGroup } from '../types/workflow';

export const DOCUMENTATION_CODE_QUALITY_GROUP: WorkflowTaskGroup = {
  id: 'doc-code-quality',
  name: 'Documentation & Code Quality',
  description: 'Standardized tasks for maintaining documentation and code quality standards',
  category: 'documentation',
  version: '1.0.0',
  author: 'archon-system',
  requiredTools: ['str-replace-editor', 'view', 'launch-process'],
  applicablePhases: ['development', 'testing', 'maintenance'],
  entryPoints: ['doc-update-readme'],
  exitPoints: ['code-quality-check'],
  tasks: [
    {
      id: 'doc-update-readme',
      title: 'Update README Documentation',
      description: 'Ensure README.md is current with project changes, installation instructions, and usage examples',
      assignee: 'AI IDE Agent',
      estimatedDuration: 15,
      dependencies: [],
      prerequisites: ['Project has README.md file'],
      validationSteps: [
        'README.md exists and is readable',
        'Installation instructions are current',
        'Usage examples work with current codebase',
        'All sections are properly formatted'
      ],
      tools: ['str-replace-editor', 'view'],
      metadata: {
        category: 'documentation',
        priority: 'medium',
        tags: ['readme', 'documentation', 'user-guide']
      }
    },
    {
      id: 'doc-update-api',
      title: 'Update API Documentation',
      description: 'Generate or update API documentation for new or modified endpoints',
      assignee: 'AI IDE Agent',
      estimatedDuration: 20,
      dependencies: ['doc-update-readme'],
      prerequisites: ['API endpoints exist', 'Documentation framework is set up'],
      validationSteps: [
        'All endpoints are documented',
        'Request/response schemas are accurate',
        'Authentication requirements are specified',
        'Error codes and messages are documented'
      ],
      tools: ['str-replace-editor', 'view', 'codebase-retrieval'],
      metadata: {
        category: 'documentation',
        priority: 'high',
        tags: ['api', 'documentation', 'endpoints']
      }
    },
    {
      id: 'doc-inline-comments',
      title: 'Add Inline Code Comments',
      description: 'Ensure complex functions and classes have appropriate inline documentation',
      assignee: 'AI IDE Agent',
      estimatedDuration: 25,
      dependencies: ['doc-update-api'],
      prerequisites: ['Code files exist', 'Coding standards are defined'],
      validationSteps: [
        'Complex functions have docstrings/comments',
        'Class purposes are documented',
        'Non-obvious logic is explained',
        'Comments follow project style guide'
      ],
      tools: ['str-replace-editor', 'view', 'codebase-retrieval'],
      metadata: {
        category: 'documentation',
        priority: 'medium',
        tags: ['comments', 'docstrings', 'code-documentation']
      }
    },
    {
      id: 'test-unit-create',
      title: 'Create/Update Unit Tests',
      description: 'Ensure comprehensive unit test coverage for new or modified code',
      assignee: 'AI IDE Agent',
      estimatedDuration: 30,
      dependencies: ['doc-inline-comments'],
      prerequisites: ['Testing framework is configured', 'Code to test exists'],
      validationSteps: [
        'Unit tests exist for new/modified functions',
        'Test coverage meets project standards (>80%)',
        'Tests pass successfully',
        'Edge cases are covered'
      ],
      tools: ['str-replace-editor', 'view', 'launch-process'],
      metadata: {
        category: 'testing',
        priority: 'high',
        tags: ['unit-tests', 'coverage', 'testing']
      }
    },
    {
      id: 'test-integration-create',
      title: 'Create/Update Integration Tests',
      description: 'Create integration tests for component interactions and API endpoints',
      assignee: 'AI IDE Agent',
      estimatedDuration: 45,
      dependencies: ['test-unit-create'],
      prerequisites: ['Integration test framework exists', 'Components to test are available'],
      validationSteps: [
        'Integration tests cover component interactions',
        'API endpoint tests are comprehensive',
        'Database integration tests work',
        'All integration tests pass'
      ],
      tools: ['str-replace-editor', 'view', 'launch-process'],
      conditional: {
        condition: 'project.hasAPI || project.hasDatabase',
        onTrue: ['test-integration-create'],
        onFalse: ['code-quality-check']
      },
      metadata: {
        category: 'testing',
        priority: 'high',
        tags: ['integration-tests', 'api-tests', 'testing']
      }
    },
    {
      id: 'code-quality-check',
      title: 'Run Code Quality Checks',
      description: 'Execute linting, formatting, and code quality analysis tools',
      assignee: 'AI IDE Agent',
      estimatedDuration: 10,
      dependencies: ['test-integration-create'],
      prerequisites: ['Linting tools are configured', 'Code quality standards are defined'],
      validationSteps: [
        'Linting passes without errors',
        'Code formatting is consistent',
        'Security vulnerabilities are checked',
        'Code complexity metrics are acceptable'
      ],
      tools: ['launch-process'],
      metadata: {
        category: 'quality',
        priority: 'high',
        tags: ['linting', 'formatting', 'code-quality']
      }
    }
  ],
  metadata: {
    created: '2024-01-01T00:00:00Z',
    updated: '2024-01-01T00:00:00Z',
    usageCount: 0,
    successRate: 0
  }
};

export const VERSION_CONTROL_DEPLOYMENT_GROUP: WorkflowTaskGroup = {
  id: 'version-control-deployment',
  name: 'Version Control & Deployment',
  description: 'Standardized tasks for version control operations and deployment processes',
  category: 'deployment',
  version: '1.0.0',
  author: 'archon-system',
  requiredTools: ['launch-process', 'github-api'],
  applicablePhases: ['development', 'testing', 'deployment'],
  entryPoints: ['git-commit-changes'],
  exitPoints: ['deployment-monitor'],
  tasks: [
    {
      id: 'git-commit-changes',
      title: 'Commit Changes with Descriptive Messages',
      description: 'Create meaningful commit messages following conventional commit standards',
      assignee: 'AI IDE Agent',
      estimatedDuration: 5,
      dependencies: [],
      prerequisites: ['Changes are ready for commit', 'Working directory is clean of unrelated changes'],
      validationSteps: [
        'Commit message follows conventional format',
        'All relevant files are included',
        'No sensitive data is committed',
        'Commit is atomic and focused'
      ],
      tools: ['launch-process'],
      metadata: {
        category: 'version-control',
        priority: 'high',
        tags: ['git', 'commit', 'version-control']
      }
    },
    {
      id: 'git-push-branch',
      title: 'Push to Appropriate Branch',
      description: 'Push changes to the correct branch based on project workflow (main, develop, feature)',
      assignee: 'AI IDE Agent',
      estimatedDuration: 5,
      dependencies: ['git-commit-changes'],
      prerequisites: ['Commits are ready', 'Target branch is determined'],
      validationSteps: [
        'Push completed successfully',
        'Correct branch was targeted',
        'No conflicts occurred',
        'Remote repository is updated'
      ],
      tools: ['launch-process', 'github-api'],
      metadata: {
        category: 'version-control',
        priority: 'high',
        tags: ['git', 'push', 'branching']
      }
    },
    {
      id: 'ci-pipeline-monitor',
      title: 'Monitor Jenkins CI/CD Pipeline',
      description: 'Monitor pipeline execution and handle any failures or issues',
      assignee: 'archon-task-manager',
      estimatedDuration: 15,
      dependencies: ['git-push-branch'],
      prerequisites: ['Jenkins pipeline is configured', 'Pipeline was triggered'],
      validationSteps: [
        'Pipeline status is monitored',
        'Build completed successfully',
        'Tests passed in pipeline',
        'Artifacts were generated if applicable'
      ],
      tools: ['web-fetch', 'launch-process'],
      metadata: {
        category: 'deployment',
        priority: 'critical',
        tags: ['jenkins', 'ci-cd', 'pipeline', 'monitoring']
      }
    },
    {
      id: 'deployment-handle-failures',
      title: 'Handle Deployment Failures and Rollbacks',
      description: 'Detect deployment failures and execute rollback procedures if needed',
      assignee: 'archon-task-manager',
      estimatedDuration: 20,
      dependencies: ['ci-pipeline-monitor'],
      prerequisites: ['Deployment monitoring is active', 'Rollback procedures are defined'],
      validationSteps: [
        'Deployment status is verified',
        'Health checks pass',
        'Rollback executed if needed',
        'System is in stable state'
      ],
      tools: ['web-fetch', 'launch-process'],
      conditional: {
        condition: 'deployment.status === "failed"',
        onTrue: ['deployment-rollback'],
        onFalse: ['deployment-monitor']
      },
      metadata: {
        category: 'deployment',
        priority: 'critical',
        tags: ['deployment', 'rollback', 'failure-handling']
      }
    },
    {
      id: 'deployment-monitor',
      title: 'Monitor Deployment Status',
      description: 'Continuously monitor deployment health and performance metrics',
      assignee: 'archon-task-manager',
      estimatedDuration: 10,
      dependencies: ['deployment-handle-failures'],
      prerequisites: ['Deployment is active', 'Monitoring tools are available'],
      validationSteps: [
        'Service is responding correctly',
        'Performance metrics are normal',
        'Error rates are acceptable',
        'All health checks pass'
      ],
      tools: ['web-fetch'],
      metadata: {
        category: 'deployment',
        priority: 'high',
        tags: ['monitoring', 'health-check', 'deployment']
      }
    }
  ],
  metadata: {
    created: '2024-01-01T00:00:00Z',
    updated: '2024-01-01T00:00:00Z',
    usageCount: 0,
    successRate: 0
  }
};

export const INFRASTRUCTURE_NETWORKING_GROUP: WorkflowTaskGroup = {
  id: 'infrastructure-networking',
  name: 'Infrastructure & Networking',
  description: 'Standardized tasks for infrastructure setup and network configuration',
  category: 'infrastructure',
  version: '1.0.0',
  author: 'archon-system',
  requiredTools: ['phpipam', 'web-fetch', 'launch-process'],
  applicablePhases: ['planning', 'deployment', 'maintenance'],
  entryPoints: ['dns-add-records'],
  exitPoints: ['firewall-update'],
  tasks: [
    {
      id: 'dns-add-records',
      title: 'Add DNS Records for New Services',
      description: 'Create appropriate DNS records (A, CNAME, SRV) for new services',
      assignee: 'archon-task-manager',
      estimatedDuration: 10,
      dependencies: [],
      prerequisites: ['Service hostname is determined', 'DNS management access available'],
      validationSteps: [
        'DNS records are created correctly',
        'Records propagate successfully',
        'Service is reachable via hostname',
        'TTL values are appropriate'
      ],
      tools: ['web-fetch', 'launch-process'],
      metadata: {
        category: 'networking',
        priority: 'high',
        tags: ['dns', 'networking', 'service-discovery']
      }
    },
    {
      id: 'ip-find-available',
      title: 'Find Available IP Addresses',
      description: 'Use phpipam MCP tool to locate available IP addresses in appropriate subnets',
      assignee: 'archon-task-manager',
      estimatedDuration: 5,
      dependencies: ['dns-add-records'],
      prerequisites: ['phpipam access configured', 'Target subnet identified'],
      validationSteps: [
        'Available IP addresses identified',
        'IP addresses are in correct subnet',
        'No conflicts with existing assignments',
        'IP addresses are reserved'
      ],
      tools: ['phpipam'],
      metadata: {
        category: 'networking',
        priority: 'high',
        tags: ['ip-management', 'phpipam', 'networking']
      }
    },
    {
      id: 'loadbalancer-configure',
      title: 'Configure Load Balancer Rules',
      description: 'Set up load balancer rules for new services if needed',
      assignee: 'archon-task-manager',
      estimatedDuration: 15,
      dependencies: ['ip-find-available'],
      prerequisites: ['Load balancer access available', 'Service endpoints defined'],
      validationSteps: [
        'Load balancer rules are configured',
        'Health checks are working',
        'Traffic is distributed correctly',
        'SSL termination works if applicable'
      ],
      tools: ['web-fetch', 'launch-process'],
      conditional: {
        condition: 'service.requiresLoadBalancer',
        onTrue: ['loadbalancer-configure'],
        onFalse: ['firewall-update']
      },
      metadata: {
        category: 'infrastructure',
        priority: 'medium',
        tags: ['load-balancer', 'traffic-management', 'infrastructure']
      }
    },
    {
      id: 'firewall-update',
      title: 'Update Firewall Configurations',
      description: 'Configure firewall rules to allow necessary traffic for new services',
      assignee: 'archon-task-manager',
      estimatedDuration: 10,
      dependencies: ['loadbalancer-configure'],
      prerequisites: ['Firewall management access', 'Required ports identified'],
      validationSteps: [
        'Firewall rules are created',
        'Required ports are open',
        'Unnecessary ports remain closed',
        'Security policies are maintained'
      ],
      tools: ['launch-process'],
      metadata: {
        category: 'security',
        priority: 'critical',
        tags: ['firewall', 'security', 'networking']
      }
    }
  ],
  metadata: {
    created: '2024-01-01T00:00:00Z',
    updated: '2024-01-01T00:00:00Z',
    usageCount: 0,
    successRate: 0
  }
};

export const HOMELAB_OPERATIONS_GROUP: WorkflowTaskGroup = {
  id: 'homelab-operations',
  name: 'Homelab Operations',
  description: 'Standardized tasks for homelab service management and operations',
  category: 'operations',
  version: '1.0.0',
  author: 'archon-system',
  requiredTools: ['homelab-vault', 'web-fetch', 'view'],
  applicablePhases: ['planning', 'deployment', 'maintenance'],
  entryPoints: ['homelab-read-docs'],
  exitPoints: ['homelab-verify-resources'],
  tasks: [
    {
      id: 'homelab-read-docs',
      title: 'Read Homelab Documentation',
      description: 'Review homelab documentation to understand available services and configurations',
      assignee: 'archon-task-manager',
      estimatedDuration: 10,
      dependencies: [],
      prerequisites: ['Homelab documentation is accessible'],
      validationSteps: [
        'Documentation is current and readable',
        'Available services are identified',
        'Service dependencies are understood',
        'Configuration requirements are clear'
      ],
      tools: ['view', 'web-fetch'],
      metadata: {
        category: 'operations',
        priority: 'medium',
        tags: ['documentation', 'homelab', 'service-discovery']
      }
    },
    {
      id: 'homelab-retrieve-credentials',
      title: 'Retrieve Credentials from Homelab Vault',
      description: 'Securely retrieve necessary credentials for homelab service access',
      assignee: 'archon-task-manager',
      estimatedDuration: 5,
      dependencies: ['homelab-read-docs'],
      prerequisites: ['Homelab vault access configured', 'Required credentials identified'],
      validationSteps: [
        'Credentials retrieved successfully',
        'Credentials are current and valid',
        'Access permissions are appropriate',
        'Credentials are securely handled'
      ],
      tools: ['homelab-vault'],
      metadata: {
        category: 'security',
        priority: 'critical',
        tags: ['credentials', 'vault', 'security', 'homelab']
      }
    },
    {
      id: 'homelab-check-dependencies',
      title: 'Check Service Dependencies and Prerequisites',
      description: 'Verify that all required services and dependencies are available and running',
      assignee: 'archon-task-manager',
      estimatedDuration: 15,
      dependencies: ['homelab-retrieve-credentials'],
      prerequisites: ['Service dependencies are documented', 'Health check endpoints available'],
      validationSteps: [
        'All dependencies are identified',
        'Dependent services are running',
        'Network connectivity is verified',
        'Service versions are compatible'
      ],
      tools: ['web-fetch', 'launch-process'],
      metadata: {
        category: 'operations',
        priority: 'high',
        tags: ['dependencies', 'health-check', 'homelab']
      }
    },
    {
      id: 'homelab-verify-resources',
      title: 'Verify Resource Availability',
      description: 'Check CPU, memory, storage, and network resources for service deployment',
      assignee: 'archon-task-manager',
      estimatedDuration: 10,
      dependencies: ['homelab-check-dependencies'],
      prerequisites: ['Resource monitoring tools available', 'Resource requirements defined'],
      validationSteps: [
        'CPU resources are sufficient',
        'Memory availability meets requirements',
        'Storage space is adequate',
        'Network bandwidth is available'
      ],
      tools: ['web-fetch', 'launch-process'],
      metadata: {
        category: 'operations',
        priority: 'high',
        tags: ['resources', 'monitoring', 'capacity-planning', 'homelab']
      }
    }
  ],
  metadata: {
    created: '2024-01-01T00:00:00Z',
    updated: '2024-01-01T00:00:00Z',
    usageCount: 0,
    successRate: 0
  }
};

// Export all task groups for easy access
export const ALL_TASK_GROUPS = [
  DOCUMENTATION_CODE_QUALITY_GROUP,
  VERSION_CONTROL_DEPLOYMENT_GROUP,
  INFRASTRUCTURE_NETWORKING_GROUP,
  HOMELAB_OPERATIONS_GROUP
];
