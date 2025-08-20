-- =====================================================
-- ARCHON TEMPLATE INJECTION SYSTEM - DEFAULT TEMPLATES
-- =====================================================
-- This script seeds the database with default workflow templates and
-- essential components for the Template Injection System MVP.
-- 
-- Creates the foundational "workflow::default" template with 10 essential
-- components that provide standardized operational procedures.
-- 
-- Created: 2025-08-20
-- Version: 1.0.0
-- =====================================================

-- =====================================================
-- SECTION 1: ESSENTIAL TEMPLATE COMPONENTS
-- =====================================================

-- Insert essential template components for the default workflow
INSERT INTO archon_template_components (name, description, component_type, instruction_text, required_tools, estimated_duration, category, priority, tags) VALUES

-- Pre-task preparation components
('group::understand_homelab_env', 
 'Review homelab environment and available services',
 'group',
 'Before starting implementation, review the homelab environment and available services:

1. **Review Homelab Documentation**: Use the `view` tool to examine any relevant homelab documentation in the project
2. **Check Available Services**: Use the `homelab-vault` MCP tool to understand available credentials and services
3. **Understand Network Topology**: Review network configuration and deployment targets
4. **Identify Dependencies**: Determine what services, databases, or infrastructure components this task depends on
5. **Verify Access**: Ensure you have the necessary credentials and access to required systems

This context will inform your implementation approach and help avoid conflicts with existing infrastructure.',
 '["view", "homelab-vault"]',
 8,
 'preparation',
 'high',
 '["homelab", "infrastructure", "preparation"]'),

('group::guidelines_coding',
 'Follow project coding standards and best practices',
 'group', 
 'Implement following the project''s coding standards and best practices:

1. **Code Style**: Use consistent code formatting and style throughout
2. **Error Handling**: Implement proper error handling with informative messages
3. **Documentation**: Include clear inline comments explaining complex logic
4. **Security**: Follow security best practices for the technology stack
5. **Performance**: Consider performance implications of implementation choices
6. **Maintainability**: Write code that is easy to read, understand, and modify

Review existing code in the project to understand established patterns and conventions.',
 '["view"]',
 5,
 'development',
 'high',
 '["coding", "standards", "best-practices"]'),

('group::naming_conventions',
 'Use consistent naming across all code and resources',
 'group',
 'Apply consistent naming conventions throughout your implementation:

1. **Variables and Functions**: Use clear, descriptive names that explain purpose
2. **Files and Directories**: Follow project naming patterns for organization
3. **Database Objects**: Use consistent naming for tables, columns, and indexes
4. **API Endpoints**: Follow RESTful naming conventions where applicable
5. **Configuration**: Use descriptive names for environment variables and settings
6. **Documentation**: Use consistent terminology in comments and documentation

Consistency in naming improves code readability and maintainability.',
 '[]',
 3,
 'development', 
 'medium',
 '["naming", "conventions", "consistency"]'),

('group::testing_strategy',
 'Implement comprehensive testing approach',
 'group',
 'Plan and implement a comprehensive testing strategy:

1. **Unit Tests**: Test individual functions and components in isolation
2. **Integration Tests**: Test interactions between components and services
3. **Edge Cases**: Test boundary conditions and error scenarios
4. **Performance Tests**: Verify performance meets requirements where applicable
5. **Security Tests**: Test for common security vulnerabilities
6. **Documentation Tests**: Ensure examples in documentation work correctly

Choose appropriate testing frameworks and tools for the technology stack.',
 '[]',
 7,
 'testing',
 'high',
 '["testing", "quality", "validation"]'),

('group::documentation_strategy',
 'Document all changes and decisions comprehensively',
 'group',
 'Document your implementation thoroughly:

1. **Code Documentation**: Add clear inline comments explaining complex logic
2. **API Documentation**: Document any new APIs, endpoints, or interfaces
3. **Configuration Documentation**: Document new settings, environment variables, or configuration options
4. **Decision Documentation**: Record important architectural or implementation decisions
5. **Usage Examples**: Provide clear examples of how to use new functionality
6. **Update Existing Docs**: Update relevant existing documentation files

Good documentation ensures long-term maintainability and helps other developers.',
 '["str-replace-editor", "view"]',
 6,
 'documentation',
 'high',
 '["documentation", "maintenance", "knowledge-sharing"]');

-- =====================================================
-- SECTION 2: POST-TASK VALIDATION COMPONENTS  
-- =====================================================

INSERT INTO archon_template_components (name, description, component_type, instruction_text, required_tools, estimated_duration, category, priority, tags) VALUES

-- Post-implementation validation components
('group::create_tests',
 'Create appropriate unit and integration tests',
 'group',
 'Create comprehensive tests for your implementation:

1. **Unit Tests**: Write tests for individual functions and components
   - Test normal operation with valid inputs
   - Test error conditions and edge cases
   - Aim for high code coverage of critical paths

2. **Integration Tests**: Test component interactions
   - Test API endpoints if applicable
   - Test database operations if applicable
   - Test external service integrations

3. **Test Organization**: 
   - Follow project testing conventions
   - Use descriptive test names that explain what is being tested
   - Group related tests logically

4. **Test Data**: Create appropriate test fixtures and mock data
5. **Assertions**: Use clear, specific assertions that validate expected behavior

Ensure tests are reliable, fast, and provide clear feedback when they fail.',
 '["str-replace-editor", "view", "launch-process"]',
 15,
 'testing',
 'critical',
 '["testing", "validation", "quality-assurance"]'),

('group::test_locally',
 'Test implementation locally before committing',
 'group',
 'Thoroughly test your implementation in the local development environment:

1. **Run All Tests**: Execute the full test suite to ensure nothing is broken
   - Run unit tests: `pytest` or equivalent for the project
   - Run integration tests if applicable
   - Check test coverage and aim for comprehensive coverage

2. **Manual Testing**: Test the functionality manually
   - Test normal use cases and workflows
   - Test error conditions and edge cases
   - Verify user experience is smooth and intuitive

3. **Performance Testing**: Check performance characteristics
   - Measure response times for critical operations
   - Test with realistic data volumes
   - Identify any performance bottlenecks

4. **Integration Testing**: Test with other system components
   - Verify compatibility with existing features
   - Test any external service integrations
   - Check for any unintended side effects

Document any issues found and ensure they are resolved before proceeding.',
 '["launch-process", "read-terminal"]',
 12,
 'testing',
 'critical',
 '["local-testing", "validation", "quality-control"]'),

('group::commit_push_to_git',
 'Commit changes with descriptive messages and push to repository',
 'group',
 'Commit your changes following project conventions:

1. **Stage Changes**: Review and stage all relevant files
   - Use `git add` to stage modified files
   - Review changes with `git diff --staged`
   - Ensure no unintended files are included

2. **Commit Message**: Write a clear, descriptive commit message
   - Use conventional commit format if the project follows it
   - Include a concise summary of what was changed
   - Explain why the change was made if not obvious
   - Reference any relevant issue numbers

3. **Push to Repository**: Push changes to the appropriate branch
   - Push to feature branch or main branch as appropriate
   - Ensure you''re pushing to the correct remote repository
   - Verify the push was successful

4. **Verify**: Check that changes appear correctly in the remote repository

Example commit message: "feat: add OAuth2 authentication with Google provider"',
 '["launch-process"]',
 5,
 'version-control',
 'high',
 '["git", "version-control", "collaboration"]'),

('group::check_jenkins_build',
 'Monitor Jenkins CI/CD pipeline status and handle any issues',
 'group',
 'Monitor the CI/CD pipeline after pushing changes:

1. **Check Build Status**: Monitor Jenkins or CI system for build results
   - Watch for build completion notifications
   - Check build logs for any errors or warnings
   - Verify all pipeline stages complete successfully

2. **Handle Build Failures**: If the build fails, investigate and fix issues
   - Review build logs to identify the root cause
   - Fix any test failures, linting issues, or compilation errors
   - Make necessary corrections and push fixes
   - Monitor subsequent builds until successful

3. **Deployment Verification**: If applicable, verify deployment success
   - Check that changes are deployed to appropriate environments
   - Verify functionality works in deployed environment
   - Monitor for any runtime errors or issues

4. **Notifications**: Respond to any team notifications about build status
   - Address any feedback from automated checks
   - Communicate with team if manual intervention is needed

Ensure the pipeline is green before considering the task complete.',
 '["web-search", "view"]',
 8,
 'deployment',
 'high',
 '["ci-cd", "jenkins", "deployment", "monitoring"]'),

('group::send_task_to_review',
 'Mark task as ready for review with comprehensive summary',
 'group',
 'Prepare the task for review and mark it as complete:

1. **Update Task Status**: Change task status to "review" 
   - Use the appropriate MCP tool to update task status
   - Ensure task is properly categorized and tagged

2. **Provide Implementation Summary**: Document what was accomplished
   - Summarize the key changes made
   - Highlight any important decisions or trade-offs
   - Note any deviations from the original requirements

3. **Testing Summary**: Document testing performed
   - List tests that were run and their results
   - Note any manual testing performed
   - Include performance or security testing results if applicable

4. **Documentation Updates**: Confirm documentation is current
   - List any documentation files that were updated
   - Ensure README or other key docs reflect changes
   - Verify examples and instructions are accurate

5. **Next Steps**: Note any follow-up work needed
   - Identify any remaining tasks or improvements
   - Note any dependencies for future work
   - Suggest any monitoring or maintenance considerations

The task is now ready for review by the team or stakeholders.',
 '["manage_task_archon-prod"]',
 5,
 'completion',
 'critical',
 '["review", "completion", "documentation", "handoff"]');

-- =====================================================
-- SECTION 3: DEFAULT WORKFLOW TEMPLATE
-- =====================================================

-- Insert the default workflow template
INSERT INTO archon_workflow_templates (
  name,
  description,
  template_type,
  injection_level,
  template_content,
  user_task_position,
  estimated_duration,
  required_tools,
  applicable_phases,
  version,
  author
) VALUES (
  'workflow::default',
  'Standard operational workflow for most development tasks with comprehensive preparation, implementation, and validation phases',
  'workflow',
  'task',
  '{{group::understand_homelab_env}}

{{group::guidelines_coding}}

{{group::naming_conventions}}

{{group::testing_strategy}}

{{group::documentation_strategy}}

{{USER_TASK}}

{{group::create_tests}}

{{group::test_locally}}

{{group::commit_push_to_git}}

{{group::check_jenkins_build}}

{{group::send_task_to_review}}',
  6, -- USER_TASK appears at position 6 in the sequence
  65, -- Total estimated duration: sum of all component durations
  '["view", "homelab-vault", "str-replace-editor", "launch-process", "read-terminal", "manage_task_archon-prod", "web-search"]',
  '["planning", "development", "testing", "deployment", "maintenance"]',
  '1.0.0',
  'archon-system'
);

-- =====================================================
-- SECTION 4: VALIDATION AND COMPLETION
-- =====================================================

-- Validate that all components referenced in the template exist
DO $$
DECLARE
  template_content TEXT;
  component_name TEXT;
  component_exists BOOLEAN;
BEGIN
  -- Get the template content
  SELECT archon_workflow_templates.template_content INTO template_content
  FROM archon_workflow_templates
  WHERE name = 'workflow::default';

  -- Check each component reference
  FOR component_name IN
    SELECT unnest(regexp_split_to_array(
      regexp_replace(template_content, '.*\{\{([^}]+)\}\}.*', '\1', 'g'),
      E'\n'
    ))
    WHERE unnest(regexp_split_to_array(
      regexp_replace(template_content, '.*\{\{([^}]+)\}\}.*', '\1', 'g'),
      E'\n'
    )) LIKE 'group::%'
  LOOP
    SELECT EXISTS(SELECT 1 FROM archon_template_components WHERE name = component_name) INTO component_exists;

    IF NOT component_exists THEN
      RAISE EXCEPTION 'Template component % referenced in workflow::default does not exist', component_name;
    END IF;
  END LOOP;

  RAISE NOTICE 'All template components validated successfully';
END $$;

-- Display summary of what was created
DO $$
DECLARE
  component_count INTEGER;
  template_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO component_count FROM archon_template_components;
  SELECT COUNT(*) INTO template_count FROM archon_workflow_templates;

  RAISE NOTICE '=================================================';
  RAISE NOTICE 'ARCHON TEMPLATE INJECTION SEED DATA COMPLETED';
  RAISE NOTICE '=================================================';
  RAISE NOTICE 'Successfully created:';
  RAISE NOTICE '  - % template components', component_count;
  RAISE NOTICE '  - % workflow templates', template_count;
  RAISE NOTICE '';
  RAISE NOTICE 'Default workflow template: workflow::default';
  RAISE NOTICE '  - 10 essential components for standardized operations';
  RAISE NOTICE '  - Comprehensive preparation and validation phases';
  RAISE NOTICE '  - Estimated total duration: 65 minutes';
  RAISE NOTICE '  - User task positioned at step 6 of 11';
  RAISE NOTICE '';
  RAISE NOTICE 'Template injection system ready for use!';
  RAISE NOTICE 'Enable with: TEMPLATE_INJECTION_ENABLED=true';
  RAISE NOTICE '=================================================';
END $$;
