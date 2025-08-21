# Workflow Templates Guide

This guide provides comprehensive information about the available workflow templates in the Template Injection System and how to use them effectively.

## Overview

Workflow templates provide standardized operational procedures that are automatically injected into agent task instructions. Each template is designed for specific scenarios and includes relevant components to ensure consistent, high-quality task execution.

## Available Workflow Templates

### 1. Default Workflow (`workflow_default`)

**Purpose**: General-purpose template for standard development tasks

**When to Use**:
- Regular development tasks
- Feature implementation
- Bug fixes (non-urgent)
- General maintenance work

**Template Structure**:
```
{{group::understand_homelab_env}}
{{group::documentation_update}}
{{USER_TASK}}
{{group::create_tests}}
{{group::deployment_validation}}
```

**Estimated Duration**: 65 minutes
**Required Tools**: `view`, `homelab-vault`, `str-replace-editor`, `launch-process`, `read-terminal`, `manage_task_archon-prod`

### 2. Hotfix Workflow (`workflow_hotfix`)

**Purpose**: Expedited workflow for urgent fixes and critical incidents

**When to Use**:
- Production outages
- Critical security vulnerabilities
- P0/P1 incidents
- Emergency fixes
- Time-sensitive issues

**Template Structure**:
```
{{group::incident_assessment}}
{{group::minimal_viable_fix}}
{{USER_TASK}}
{{group::immediate_testing}}
{{group::emergency_deployment}}
{{group::post_incident_review}}
```

**Estimated Duration**: 60 minutes
**Required Tools**: `homelab-vault`, `str-replace-editor`, `launch-process`, `view`

**Key Features**:
- Rapid incident assessment
- Focus on minimal viable fixes
- Emergency deployment procedures
- Post-incident review and learning

### 3. Milestone Completion Workflow (`workflow_milestone_pass`)

**Purpose**: Comprehensive validation workflow for milestone completion

**When to Use**:
- Sprint/milestone completion
- Release preparation
- Major feature delivery
- Quality gate validation
- Stakeholder sign-off requirements

**Template Structure**:
```
{{group::milestone_review_checklist}}
{{group::stakeholder_communication}}
{{group::documentation_update}}
{{USER_TASK}}
{{group::integration_testing}}
{{group::performance_validation}}
{{group::security_audit}}
{{group::deployment_preparation}}
{{group::milestone_signoff}}
```

**Estimated Duration**: 120 minutes
**Required Tools**: `view`, `str-replace-editor`, `launch-process`, `web-fetch`, `homelab-vault`

**Key Features**:
- Comprehensive quality gates
- Stakeholder communication
- Security and performance validation
- Formal sign-off procedures

### 4. Research Workflow (`workflow_research`)

**Purpose**: Structured workflow for research and investigation tasks

**When to Use**:
- Technology research
- Solution analysis
- Proof of concepts
- Feasibility studies
- Requirements gathering
- Best practices investigation

**Template Structure**:
```
{{group::research_scope_definition}}
{{group::literature_review}}
{{group::existing_solution_analysis}}
{{USER_TASK}}
{{group::findings_documentation}}
{{group::recommendation_summary}}
{{group::knowledge_sharing}}
```

**Estimated Duration**: 90 minutes
**Required Tools**: `web-search`, `web-fetch`, `view`, `str-replace-editor`, `codebase-retrieval`

**Key Features**:
- Structured research methodology
- Comprehensive solution analysis
- Knowledge documentation and sharing
- Clear recommendations

### 5. Maintenance Workflow (`workflow_maintenance`)

**Purpose**: Routine maintenance and system operations workflow

**When to Use**:
- Scheduled maintenance
- System health checks
- Backup verification
- Monitoring validation
- Routine updates
- Operational tasks

**Template Structure**:
```
{{group::system_health_check}}
{{group::backup_verification}}
{{USER_TASK}}
{{group::monitoring_validation}}
{{group::documentation_update}}
{{group::maintenance_log}}
```

**Estimated Duration**: 75 minutes
**Required Tools**: `homelab-vault`, `launch-process`, `web-fetch`, `view`, `str-replace-editor`

**Key Features**:
- Comprehensive health checks
- Backup and recovery validation
- Monitoring system verification
- Detailed maintenance logging

## Template Selection

### Automatic Selection

The Template Injection System includes intelligent template selection based on task context:

**Hotfix Detection**:
- Keywords: urgent, critical, emergency, hotfix, immediate, down, outage, production issue
- Patterns: P0/P1 severity, time pressure indicators
- Context: High priority tasks, incident-related work

**Milestone Detection**:
- Keywords: milestone, release, deploy, launch, sign-off, completion
- Patterns: Quality gates, stakeholder approval, final validation
- Context: Sprint completion, release preparation

**Research Detection**:
- Keywords: research, investigate, analyze, study, explore, proof of concept
- Patterns: Solution comparison, feasibility analysis
- Context: Discovery work, requirements gathering

**Maintenance Detection**:
- Keywords: maintenance, update, upgrade, health check, backup
- Patterns: Routine operations, system administration
- Context: Scheduled maintenance, operational tasks

### Manual Selection

You can explicitly specify a template using MCP tools:

```bash
# Create task with specific template
manage_task(
    action="create",
    project_id="your-project-id",
    title="Emergency Database Fix",
    description="Fix critical database connection issue",
    template_name="workflow_hotfix"
)
```

### Template Switching

Templates can be changed during task execution:

```bash
# Switch to different template
manage_template(
    action="switch_template",
    task_id="task-id",
    new_template="workflow_milestone_pass"
)
```

## Template Components

### Core Components

**Environment Understanding**:
- `group::understand_homelab_env`: Understand the homelab environment and constraints

**Documentation**:
- `group::documentation_update`: Update relevant documentation
- `group::findings_documentation`: Document research findings
- `group::maintenance_log`: Log maintenance activities

**Testing and Validation**:
- `group::create_tests`: Create comprehensive tests
- `group::immediate_testing`: Perform immediate testing for hotfixes
- `group::integration_testing`: Execute integration testing
- `group::performance_validation`: Validate performance requirements

**Deployment**:
- `group::deployment_validation`: Validate deployment procedures
- `group::emergency_deployment`: Execute emergency deployment
- `group::deployment_preparation`: Prepare for milestone deployment

### Specialized Components

**Incident Management**:
- `group::incident_assessment`: Assess incident severity and impact
- `group::minimal_viable_fix`: Implement minimal viable fix
- `group::post_incident_review`: Conduct post-incident review

**Research and Analysis**:
- `group::research_scope_definition`: Define research scope
- `group::literature_review`: Review existing documentation
- `group::existing_solution_analysis`: Analyze available solutions
- `group::recommendation_summary`: Provide recommendations

**Milestone Management**:
- `group::milestone_review_checklist`: Complete milestone checklist
- `group::stakeholder_communication`: Communicate with stakeholders
- `group::security_audit`: Conduct security validation
- `group::milestone_signoff`: Obtain formal approval

**System Operations**:
- `group::system_health_check`: Perform health assessments
- `group::backup_verification`: Verify backup systems
- `group::monitoring_validation`: Validate monitoring systems

## Best Practices

### Template Selection Guidelines

1. **Match Urgency to Template**:
   - Use `workflow_hotfix` for urgent, time-sensitive issues
   - Use `workflow_default` for regular development work
   - Use `workflow_milestone_pass` for formal deliverables

2. **Consider Scope and Complexity**:
   - Research templates for investigation work
   - Maintenance templates for operational tasks
   - Default templates for standard development

3. **Stakeholder Requirements**:
   - Use milestone templates when formal approval is needed
   - Use research templates when documentation is critical
   - Use hotfix templates when speed is essential

### Customization Guidelines

1. **Component Selection**:
   - Include only relevant components for your task
   - Consider dependencies between components
   - Balance thoroughness with efficiency

2. **Tool Requirements**:
   - Ensure required tools are available
   - Consider tool complexity and learning curve
   - Validate tool permissions and access

3. **Time Estimation**:
   - Use template duration as baseline
   - Adjust for task complexity and experience
   - Consider external dependencies and approvals

### Quality Assurance

1. **Template Validation**:
   - Test templates with sample tasks
   - Validate component instructions are clear
   - Ensure tool references are correct

2. **Performance Monitoring**:
   - Track template expansion times
   - Monitor agent task completion rates
   - Collect feedback on instruction quality

3. **Continuous Improvement**:
   - Update templates based on usage patterns
   - Refine components based on feedback
   - Add new templates for emerging patterns

## Troubleshooting

### Common Issues

**Template Not Found**:
- Verify template name spelling
- Check template is active in database
- Confirm template exists in current environment

**Expansion Timeouts**:
- Check database performance
- Verify component complexity
- Review template cache status

**Missing Components**:
- Verify component names in template
- Check component is active
- Confirm component exists in database

**Tool Availability**:
- Verify required tools are installed
- Check tool permissions and access
- Confirm tool compatibility

### Performance Optimization

1. **Template Caching**:
   - Templates are cached for 30 minutes
   - Components cached for 15 minutes
   - Clear cache if updates not reflected

2. **Component Optimization**:
   - Keep component instructions concise
   - Minimize tool requirements
   - Optimize for common use cases

3. **Selection Optimization**:
   - Use explicit template selection when possible
   - Provide clear task descriptions for auto-selection
   - Include relevant context data

## Support and Feedback

### Getting Help

- **Documentation**: Refer to this guide and operations documentation
- **Troubleshooting**: Check logs and health endpoints
- **Support**: Contact development team for template issues

### Providing Feedback

- **Template Effectiveness**: Report on template success rates
- **Component Quality**: Feedback on instruction clarity
- **Performance Issues**: Report expansion timeouts or errors
- **Feature Requests**: Suggest new templates or components

### Contributing

- **New Templates**: Propose templates for new scenarios
- **Component Improvements**: Suggest component enhancements
- **Documentation**: Help improve guides and examples
- **Testing**: Participate in template validation and testing
