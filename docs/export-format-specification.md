# Archon Project Export Format Specification

## Overview

This document defines the comprehensive export format specification for Archon projects, enabling complete project portability, backup, and migration capabilities. The export format ensures data integrity, version compatibility, and seamless import/restore operations.

## Export Format Structure

### 1. Container Format

Archon projects are exported as **ZIP archives** containing structured JSON data and metadata files:

```
project-export-{project-id}-{timestamp}.zip
├── manifest.json                 # Export metadata and validation
├── project.json                  # Core project data
├── tasks.json                    # All project tasks
├── documents/                    # Document files and content
│   ├── index.json               # Document metadata index
│   └── {doc-id}.json            # Individual document files
├── versions/                     # Version history
│   ├── index.json               # Version metadata index
│   └── {version-id}.json        # Individual version snapshots
├── sources/                      # Linked knowledge sources
│   ├── index.json               # Source metadata index
│   └── {source-id}.json         # Source content and metadata
└── attachments/                  # Binary files and assets
    ├── index.json               # Attachment metadata
    └── files/                   # Actual binary files
```

### 2. Manifest Schema

The `manifest.json` file contains export metadata and validation information:

```json
{
  "format_version": "1.0.0",
  "archon_version": "2.0.0",
  "export_timestamp": "2025-08-18T22:45:00Z",
  "export_type": "full",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_title": "OAuth2 Authentication System",
  "exported_by": "AI IDE Agent",
  "export_options": {
    "include_versions": true,
    "include_sources": true,
    "include_attachments": true,
    "version_limit": null,
    "date_range": null
  },
  "data_integrity": {
    "total_files": 15,
    "total_size_bytes": 2048576,
    "checksums": {
      "project.json": "sha256:abc123...",
      "tasks.json": "sha256:def456...",
      "documents/index.json": "sha256:ghi789..."
    }
  },
  "compatibility": {
    "min_archon_version": "2.0.0",
    "supported_features": [
      "project_management",
      "task_hierarchy",
      "document_versioning",
      "source_linking",
      "mcp_integration"
    ]
  }
}
```

### 3. Project Data Schema

The `project.json` file contains the core project information:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "OAuth2 Authentication System",
  "description": "Secure OAuth2 implementation with multiple providers",
  "github_repo": "https://github.com/company/oauth-service",
  "pinned": false,
  "created_at": "2025-08-18T10:00:00Z",
  "updated_at": "2025-08-18T22:00:00Z",
  "metadata": {
    "progress": 75,
    "status": "active",
    "category": "authentication",
    "tags": ["oauth2", "security", "authentication"]
  },
  "prd": {
    "product_vision": "Secure OAuth2 authentication system",
    "target_users": ["Web users", "Mobile users", "API developers"],
    "key_features": ["Google OAuth2", "GitHub OAuth2", "Token refresh"],
    "success_metrics": ["< 3 clicks auth", "99.9% success rate"],
    "constraints": ["GDPR compliance", "2MB bundle limit"]
  },
  "features": [
    {
      "id": "feature-001",
      "name": "Google OAuth2 Provider",
      "description": "Integration with Google OAuth2 service",
      "status": "completed",
      "priority": "high",
      "created_at": "2025-08-18T10:00:00Z"
    }
  ],
  "data": [
    {
      "id": "data-001",
      "type": "configuration",
      "name": "OAuth2 Settings",
      "content": {
        "providers": ["google", "github"],
        "scopes": ["openid", "profile", "email"]
      }
    }
  ]
}
```

### 4. Tasks Data Schema

The `tasks.json` file contains all project tasks with hierarchy:

```json
{
  "tasks": [
    {
      "id": "task-001",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "parent_task_id": null,
      "title": "Implement Google OAuth2 Provider",
      "description": "Create GoogleOAuthProvider class with endpoints and configuration",
      "status": "completed",
      "assignee": "AI IDE Agent",
      "task_order": 10,
      "feature": "authentication",
      "sources": [
        {
          "url": "https://developers.google.com/identity/protocols/oauth2",
          "type": "documentation",
          "relevance": "Official OAuth2 specification"
        }
      ],
      "code_examples": [
        {
          "file": "src/auth/base.py",
          "class": "BaseAuthProvider",
          "purpose": "Provider interface pattern"
        }
      ],
      "archived": false,
      "archived_at": null,
      "archived_by": null,
      "created_at": "2025-08-18T10:00:00Z",
      "updated_at": "2025-08-18T15:00:00Z"
    }
  ],
  "task_hierarchy": {
    "root_tasks": ["task-001"],
    "parent_child_map": {
      "task-001": ["task-002", "task-003"]
    }
  },
  "statistics": {
    "total_tasks": 15,
    "completed_tasks": 8,
    "in_progress_tasks": 3,
    "todo_tasks": 4,
    "archived_tasks": 2
  }
}
```

### 5. Documents Schema

Documents are stored in the `documents/` directory with an index file:

**documents/index.json:**
```json
{
  "documents": [
    {
      "id": "doc-001",
      "document_type": "prp",
      "title": "OAuth2 Implementation PRP",
      "status": "approved",
      "version": "2.1",
      "author": "prp-creator",
      "created_at": "2025-08-18T10:00:00Z",
      "updated_at": "2025-08-18T20:00:00Z",
      "file_path": "doc-001.json",
      "size_bytes": 15420
    }
  ],
  "total_documents": 1,
  "total_size_bytes": 15420
}
```

**documents/{doc-id}.json:**
```json
{
  "id": "doc-001",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_type": "prp",
  "title": "OAuth2 Implementation PRP",
  "content": {
    "document_type": "prp",
    "title": "OAuth2 Authentication Implementation",
    "version": "2.1",
    "author": "prp-creator",
    "date": "2025-08-18",
    "status": "approved",
    "goal": "Implement secure OAuth2 authentication with Google and GitHub providers",
    "why": [
      "Enable secure user authentication without password management",
      "Reduce registration friction and improve user conversion rates"
    ],
    "what": {
      "description": "Complete OAuth2 flow with provider selection and token management",
      "success_criteria": [
        "Users can authenticate with Google/GitHub in <3 clicks",
        "Secure token storage with automatic refresh handling"
      ]
    },
    "context": {
      "documentation": [
        {
          "source": "https://developers.google.com/identity/protocols/oauth2",
          "why": "Official OAuth2 implementation guide"
        }
      ],
      "existing_code": [
        {
          "file": "src/auth/base.py",
          "purpose": "Base authentication classes and interfaces"
        }
      ]
    },
    "implementation_blueprint": {
      "phase_1_provider_setup": {
        "description": "Configure OAuth2 providers and basic flow",
        "tasks": [
          {
            "title": "Create OAuth2 provider configurations",
            "files": ["src/auth/oauth/providers.py"],
            "details": "Define GoogleOAuthProvider and GitHubOAuthProvider classes"
          }
        ]
      }
    },
    "validation": {
      "level_1_syntax": [
        "ruff check --fix src/auth/oauth/",
        "mypy src/auth/oauth/"
      ],
      "level_2_unit_tests": [
        "pytest tests/auth/test_oauth_providers.py -v"
      ]
    }
  },
  "metadata": {
    "tags": ["oauth2", "authentication", "prp"],
    "status": "approved",
    "version": "2.1",
    "author": "prp-creator"
  },
  "timestamps": {
    "created_at": "2025-08-18T10:00:00Z",
    "updated_at": "2025-08-18T20:00:00Z"
  }
}
```

## Export Types

### 1. Full Export
- Complete project data including all versions, sources, and attachments
- Suitable for complete project migration or comprehensive backup

### 2. Selective Export
- Specific components (documents only, tasks only, etc.)
- Date range filtering
- Version limit filtering

### 3. Incremental Export
- Changes since last export
- Delta-based for efficient synchronization

## Data Integrity and Validation

### 1. Checksums
- SHA-256 checksums for all files
- Manifest contains complete checksum index
- Import process validates all checksums

### 2. Schema Validation
- JSON Schema validation for all data files
- Version compatibility checking
- Required field validation

### 3. Referential Integrity
- Cross-reference validation between files
- Foreign key consistency checking
- Orphaned record detection

## Compression and Optimization

### 1. Compression
- ZIP compression with optimal settings
- Large text content compressed efficiently
- Binary files stored with appropriate compression

### 2. Size Optimization
- Optional exclusion of large attachments
- Version history pruning options
- Content deduplication where possible

## Version Compatibility

### 1. Format Versioning
- Semantic versioning for export format (1.0.0)
- Backward compatibility guarantees
- Migration paths for format upgrades

### 2. Archon Version Compatibility
- Minimum required Archon version specified
- Feature compatibility matrix
- Graceful degradation for unsupported features

## Security Considerations

### 1. Data Sanitization
- Removal of sensitive credentials
- Optional anonymization of user data
- Configurable data filtering

### 2. Access Control
- Export permission validation
- Audit logging of export operations
- Secure file handling

## Implementation Guidelines

### 1. Export Process
1. Validate export permissions
2. Collect and validate all project data
3. Generate checksums and metadata
4. Create ZIP archive with proper structure
5. Verify export integrity

### 2. Import Process
1. Validate ZIP structure and manifest
2. Verify checksums and data integrity
3. Check version compatibility
4. Validate all JSON schemas
5. Import data with conflict resolution
6. Verify import success

### 3. Error Handling
- Comprehensive error reporting
- Partial export/import capabilities
- Rollback mechanisms for failed imports
- Detailed logging and diagnostics

## Future Extensions

### 1. Enhanced Formats
- Support for additional container formats (TAR, 7Z)
- Streaming export for large projects
- Cloud storage integration

### 2. Advanced Features
- Encrypted exports for sensitive projects
- Collaborative export/import workflows
- Automated backup scheduling
- Cross-platform compatibility enhancements

This specification ensures complete project portability while maintaining data integrity and providing flexible export/import options for various use cases.
