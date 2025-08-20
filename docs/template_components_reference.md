# Template Components Reference

This document provides a comprehensive reference for all template components in the Archon Template Injection System.

## Overview

Template components are reusable instruction blocks that can be injected into agent task descriptions to provide standardized operational procedures. Each component follows the naming convention `type::name` where type is typically `group`, `action`, or `sequence`.

## Default Workflow Template: `workflow_default`

The default workflow template provides a comprehensive 11-step operational process that wraps around user tasks:

```
{{group::understand_homelab_env}}
{{group::guidelines_coding}}
{{group::naming_conventions}}
{{group::testing_strategy}}
{{group::documentation_strategy}}

{{USER_TASK}}

{{group::create_tests}}
{{group::test_locally}}
{{group::commit_push_to_git}}
{{group::check_jenkins_build}}
{{group::send_task_to_review}}
```

**Template Metadata:**
- **Version**: 1.1.0
- **Estimated Duration**: 73 minutes total
- **User Task Position**: 6 of 11 steps
- **Required Tools**: view, homelab-vault, str-replace-editor, launch-process, read-terminal, manage_task_archon-prod

## Template Components

### 1. group::understand_homelab_env
**Category**: Preparation | **Duration**: 8 min | **Priority**: High

Reviews homelab environment and available services before starting implementation.

**Key Actions:**
- Review homelab documentation using `view` tool
- Check available services using `homelab-vault` MCP tool
- Understand network topology and deployment targets
- Identify dependencies and required systems
- Verify access to necessary credentials

**Required Tools**: `["view", "homelab-vault"]`

### 2. group::guidelines_coding
**Category**: Development | **Duration**: 5 min | **Priority**: High

Ensures implementation follows project coding standards and best practices.

**Key Actions:**
- Use consistent code formatting and style
- Implement proper error handling with informative messages
- Include clear inline comments explaining complex logic
- Follow security best practices for the technology stack
- Consider performance implications of implementation choices
- Write maintainable code that's easy to read and modify

**Required Tools**: `["view"]`

### 3. group::naming_conventions
**Category**: Development | **Duration**: 3 min | **Priority**: Medium

Applies consistent naming conventions throughout implementation.

**Key Actions:**
- Use clear, descriptive names for variables and functions
- Follow project naming patterns for files and directories
- Use consistent naming for database objects
- Follow RESTful naming conventions for API endpoints
- Use descriptive names for environment variables and settings
- Maintain consistent terminology in comments and documentation

**Required Tools**: `[]`

### 4. group::testing_strategy
**Category**: Testing | **Duration**: 7 min | **Priority**: High

Plans and implements a comprehensive testing approach.

**Key Actions:**
- Test individual functions and components in isolation
- Test interactions between components and services
- Test boundary conditions and error scenarios
- Verify performance meets requirements where applicable
- Test for common security vulnerabilities
- Ensure examples in documentation work correctly

**Required Tools**: `[]`

### 5. group::documentation_strategy
**Category**: Documentation | **Duration**: 6 min | **Priority**: High

Documents implementation thoroughly for long-term maintainability.

**Key Actions:**
- Add clear inline comments explaining complex logic
- Document any new APIs, endpoints, or interfaces
- Document new settings, environment variables, or configuration options
- Record important architectural or implementation decisions
- Provide clear examples of how to use new functionality
- Update relevant existing documentation files

**Required Tools**: `["str-replace-editor", "view"]`

### 6. group::create_tests
**Category**: Testing | **Duration**: 15 min | **Priority**: Critical

Creates comprehensive tests for the implementation.

**Key Actions:**
- Write tests for individual functions and components
- Test normal operation with valid inputs
- Test error conditions and edge cases
- Aim for high code coverage of critical paths
- Test API endpoints and database operations if applicable
- Test external service integrations
- Follow project testing conventions
- Use descriptive test names and organize tests logically

**Required Tools**: `["str-replace-editor", "view", "launch-process"]`

### 7. group::test_locally
**Category**: Testing | **Duration**: 12 min | **Priority**: Critical

Thoroughly tests implementation in local development environment.

**Key Actions:**
- Execute the full test suite to ensure nothing is broken
- Run unit tests and integration tests if applicable
- Check test coverage and aim for comprehensive coverage
- Test functionality manually with normal use cases and error conditions
- Verify user experience is smooth and intuitive
- Measure response times for critical operations
- Test with realistic data volumes
- Verify compatibility with existing features
- Check for any unintended side effects

**Required Tools**: `["launch-process", "read-terminal"]`

### 8. group::commit_push_to_git
**Category**: Version Control | **Duration**: 5 min | **Priority**: High

Commits changes with descriptive messages and pushes to repository.

**Key Actions:**
- Review and stage all relevant files using `git add`
- Review changes with `git diff --staged`
- Ensure no unintended files are included
- Write clear, descriptive commit message
- Use conventional commit format if the project follows it
- Include concise summary of what was changed
- Explain why the change was made if not obvious
- Reference any relevant issue numbers
- Push to appropriate branch (feature branch or main branch)
- Verify the push was successful

**Required Tools**: `["launch-process"]`

### 9. group::check_jenkins_build
**Category**: CI/CD | **Duration**: 8 min | **Priority**: High

Monitors Jenkins CI/CD pipeline status and handles build issues.

**Key Actions:**
- Monitor the Jenkins build pipeline for your changes
- Check the build status in Jenkins dashboard
- Verify all stages complete successfully (build, test, deploy)
- Monitor for any failures or warnings
- Review build logs for error details if issues arise
- Fix any compilation or test failures
- Address any code quality or security issues
- Re-run failed builds after fixes
- Check unit test results and coverage
- Verify integration tests complete successfully
- Check deployment status and health checks
- Verify application starts and runs correctly

**Required Tools**: `["launch-process", "read-terminal"]`

### 10. group::send_task_to_review
**Category**: Completion | **Duration**: 5 min | **Priority**: Critical

Prepares task for review and marks it as complete.

**Key Actions:**
- Change task status to "review" using appropriate MCP tool
- Ensure task is properly categorized and tagged
- Summarize the key changes made
- Highlight any important decisions or trade-offs
- Note any deviations from the original requirements
- List tests that were run and their results
- Note any manual testing performed
- Include performance or security testing results if applicable
- List any documentation files that were updated
- Ensure README or other key docs reflect changes
- Verify examples and instructions are accurate
- Identify any remaining tasks or improvements
- Note any dependencies for future work
- Suggest any monitoring or maintenance considerations

**Required Tools**: `["manage_task_archon-prod"]`

## Usage Guidelines

### Component Selection
- All components in the default workflow are designed to work together
- Components can be used individually in custom templates
- Each component is self-contained and provides clear instructions
- Components reference specific MCP tools that must be available

### Customization
- Component instruction text can be modified for specific project needs
- Required tools can be updated based on available MCP tools
- Duration estimates can be adjusted based on project complexity
- Priority levels can be modified based on project requirements

### Best Practices
- Always test template expansion before deploying to production
- Validate that all referenced MCP tools are available
- Ensure component instructions are clear and actionable
- Monitor template usage and performance in production
- Update components based on user feedback and usage patterns

## Template Expansion Example

When a user task "Implement OAuth2 authentication" is processed with the default workflow template, it becomes:

```
[Step 1: Homelab Environment Review - 8 min]
[Step 2: Coding Guidelines - 5 min]
[Step 3: Naming Conventions - 3 min]
[Step 4: Testing Strategy - 7 min]
[Step 5: Documentation Strategy - 6 min]

Implement OAuth2 authentication

[Step 7: Create Tests - 15 min]
[Step 8: Test Locally - 12 min]
[Step 9: Commit and Push - 5 min]
[Step 10: Check Jenkins Build - 8 min]
[Step 11: Send to Review - 5 min]
```

**Total Duration**: 73 minutes (8 minutes of preparation + user task + 58 minutes of validation and completion)

This ensures every task follows standardized operational procedures while preserving the original user intent.
