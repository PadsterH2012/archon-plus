-- =====================================================
-- Additional Workflow Templates Migration
-- =====================================================
-- This migration adds new workflow templates for different scenarios:
-- - workflow::hotfix (urgent fixes)
-- - workflow::milestone_pass (milestone completion)
-- - workflow::research (research and investigation)
-- - workflow::maintenance (routine maintenance)
-- =====================================================

-- Insert new template components for incident management
INSERT INTO archon_template_components (
    id, name, description, component_type, instruction_text, 
    required_tools, estimated_duration, category, priority, tags, is_active
) VALUES 
-- Incident Management Components
(
    gen_random_uuid(),
    'group::incident_assessment',
    'Assess incident severity and impact',
    'group',
    'Before implementing the fix, assess the incident:

1. **Severity Assessment**:
   - Determine impact scope (users affected, systems down)
   - Classify severity level (P0-Critical, P1-High, P2-Medium, P3-Low)
   - Identify root cause if immediately apparent
   - Document initial findings in incident log

2. **Impact Analysis**:
   - Check system monitoring for affected services
   - Review error logs and metrics
   - Identify downstream dependencies
   - Estimate business impact and urgency

3. **Communication Setup**:
   - Notify stakeholders of incident status
   - Set up incident communication channel
   - Prepare status updates for affected users
   - Escalate to on-call team if needed',
    ARRAY['homelab-vault', 'view', 'web-search'],
    10,
    'incident_management',
    'critical',
    ARRAY['incident', 'assessment', 'severity', 'impact'],
    true
),
(
    gen_random_uuid(),
    'group::minimal_viable_fix',
    'Implement minimal viable fix for incident',
    'group',
    'Implement the smallest possible fix to restore service:

1. **Fix Strategy**:
   - Focus on restoring service, not perfect solution
   - Implement temporary workaround if needed
   - Avoid complex changes that could introduce new issues
   - Document what the fix does and why

2. **Safety Checks**:
   - Verify fix in staging/test environment if possible
   - Have rollback plan ready before applying
   - Monitor key metrics during implementation
   - Keep fix scope minimal and focused

3. **Implementation**:
   - Apply fix with minimal disruption
   - Monitor system behavior immediately after
   - Verify fix resolves the immediate issue
   - Document any side effects or limitations',
    ARRAY['str-replace-editor', 'launch-process', 'view'],
    15,
    'incident_management',
    'critical',
    ARRAY['hotfix', 'minimal', 'fix', 'incident'],
    true
),
(
    gen_random_uuid(),
    'group::immediate_testing',
    'Perform immediate testing of hotfix',
    'group',
    'Test the hotfix to ensure it resolves the issue:

1. **Functional Testing**:
   - Verify the specific issue is resolved
   - Test core functionality still works
   - Check that no new errors are introduced
   - Validate fix works in production environment

2. **Monitoring Validation**:
   - Check error rates return to normal
   - Verify performance metrics are stable
   - Monitor for any new alerts or warnings
   - Confirm user-facing functionality restored

3. **Smoke Testing**:
   - Test critical user journeys
   - Verify integrations still function
   - Check that dependent services are working
   - Validate data integrity maintained',
    ARRAY['launch-process', 'web-fetch', 'view'],
    8,
    'testing',
    'high',
    ARRAY['testing', 'validation', 'hotfix', 'smoke'],
    true
),
(
    gen_random_uuid(),
    'group::emergency_deployment',
    'Deploy hotfix with emergency procedures',
    'group',
    'Deploy the hotfix using emergency deployment procedures:

1. **Pre-Deployment**:
   - Notify all stakeholders of emergency deployment
   - Prepare rollback plan and test it
   - Ensure monitoring is active and alerting
   - Have incident response team on standby

2. **Deployment Execution**:
   - Use fastest safe deployment method
   - Monitor deployment progress closely
   - Verify each step completes successfully
   - Be ready to rollback immediately if issues occur

3. **Post-Deployment Validation**:
   - Verify fix is active in production
   - Check all monitoring systems show green
   - Confirm user reports indicate issue resolved
   - Update incident status and stakeholders',
    ARRAY['launch-process', 'homelab-vault'],
    12,
    'deployment',
    'critical',
    ARRAY['deployment', 'emergency', 'hotfix', 'production'],
    true
),
(
    gen_random_uuid(),
    'group::post_incident_review',
    'Conduct post-incident review and documentation',
    'group',
    'Complete post-incident activities:

1. **Incident Documentation**:
   - Document timeline of events
   - Record root cause analysis
   - Note what worked well and what didn''t
   - Capture lessons learned

2. **Follow-up Actions**:
   - Create tickets for permanent fix if needed
   - Identify process improvements
   - Update monitoring and alerting
   - Schedule team retrospective

3. **Communication**:
   - Send final incident report to stakeholders
   - Update status page with resolution
   - Thank team members for response
   - Share learnings with broader team',
    ARRAY['str-replace-editor', 'view'],
    15,
    'documentation',
    'medium',
    ARRAY['post-incident', 'review', 'documentation', 'lessons'],
    true
);

-- Insert milestone management components
INSERT INTO archon_template_components (
    id, name, description, component_type, instruction_text, 
    required_tools, estimated_duration, category, priority, tags, is_active
) VALUES 
(
    gen_random_uuid(),
    'group::milestone_review_checklist',
    'Complete milestone review checklist',
    'group',
    'Review milestone completion criteria:

1. **Deliverable Review**:
   - Verify all planned features are complete
   - Check that acceptance criteria are met
   - Review code quality and test coverage
   - Confirm documentation is up to date

2. **Quality Gates**:
   - All tests passing (unit, integration, e2e)
   - Security scan results reviewed and approved
   - Performance benchmarks met
   - Accessibility requirements satisfied

3. **Stakeholder Sign-off**:
   - Product owner approval on features
   - Technical lead approval on implementation
   - QA sign-off on testing
   - Security team approval if required',
    ARRAY['view', 'launch-process', 'web-fetch'],
    20,
    'milestone',
    'high',
    ARRAY['milestone', 'review', 'checklist', 'quality'],
    true
),
(
    gen_random_uuid(),
    'group::stakeholder_communication',
    'Communicate milestone status to stakeholders',
    'group',
    'Update stakeholders on milestone progress:

1. **Status Communication**:
   - Prepare milestone completion summary
   - Highlight key achievements and deliverables
   - Note any scope changes or issues encountered
   - Provide metrics on quality and performance

2. **Stakeholder Updates**:
   - Send update to project sponsors
   - Update project management tools
   - Communicate to dependent teams
   - Update public roadmap if applicable

3. **Next Steps Communication**:
   - Outline next milestone objectives
   - Communicate any timeline changes
   - Identify dependencies and blockers
   - Schedule milestone retrospective',
    ARRAY['str-replace-editor', 'web-fetch'],
    10,
    'communication',
    'medium',
    ARRAY['stakeholder', 'communication', 'milestone', 'status'],
    true
),
(
    gen_random_uuid(),
    'group::integration_testing',
    'Perform comprehensive integration testing',
    'group',
    'Execute integration testing for milestone:

1. **System Integration**:
   - Test all component interactions
   - Verify data flows between services
   - Check API contracts and compatibility
   - Validate third-party integrations

2. **End-to-End Testing**:
   - Execute complete user journeys
   - Test cross-system workflows
   - Verify business process automation
   - Check error handling and recovery

3. **Environment Testing**:
   - Test in staging environment
   - Verify production-like configuration
   - Check deployment and rollback procedures
   - Validate monitoring and alerting',
    ARRAY['launch-process', 'web-fetch', 'view'],
    25,
    'testing',
    'high',
    ARRAY['integration', 'testing', 'e2e', 'validation'],
    true
),
(
    gen_random_uuid(),
    'group::performance_validation',
    'Validate performance meets requirements',
    'group',
    'Validate system performance for milestone:

1. **Performance Testing**:
   - Execute load testing scenarios
   - Measure response times and throughput
   - Test under peak load conditions
   - Verify resource utilization is acceptable

2. **Benchmark Validation**:
   - Compare against performance targets
   - Check regression from previous milestone
   - Validate scalability requirements
   - Measure system stability under load

3. **Optimization Review**:
   - Identify performance bottlenecks
   - Review database query performance
   - Check caching effectiveness
   - Validate CDN and asset optimization',
    ARRAY['launch-process', 'web-fetch'],
    20,
    'performance',
    'high',
    ARRAY['performance', 'load', 'testing', 'benchmarks'],
    true
),
(
    gen_random_uuid(),
    'group::security_audit',
    'Conduct security audit and validation',
    'group',
    'Perform security validation for milestone:

1. **Security Scanning**:
   - Run automated security scans
   - Check for known vulnerabilities
   - Validate dependency security
   - Review security configuration

2. **Access Control Review**:
   - Verify authentication mechanisms
   - Check authorization rules
   - Review user permission models
   - Validate data access controls

3. **Security Best Practices**:
   - Review code for security issues
   - Check input validation and sanitization
   - Verify secure communication protocols
   - Validate data encryption at rest and transit',
    ARRAY['launch-process', 'web-search', 'view'],
    18,
    'security',
    'critical',
    ARRAY['security', 'audit', 'vulnerability', 'compliance'],
    true
),
(
    gen_random_uuid(),
    'group::deployment_preparation',
    'Prepare for milestone deployment',
    'group',
    'Prepare deployment for milestone release:

1. **Deployment Planning**:
   - Create deployment runbook
   - Plan deployment timeline and windows
   - Identify rollback procedures
   - Coordinate with operations team

2. **Environment Preparation**:
   - Prepare production environment
   - Update configuration management
   - Verify infrastructure capacity
   - Test deployment procedures in staging

3. **Communication Planning**:
   - Prepare deployment communications
   - Schedule maintenance windows
   - Notify affected users and teams
   - Prepare incident response procedures',
    ARRAY['str-replace-editor', 'homelab-vault', 'view'],
    15,
    'deployment',
    'high',
    ARRAY['deployment', 'preparation', 'planning', 'release'],
    true
),
(
    gen_random_uuid(),
    'group::milestone_signoff',
    'Obtain formal milestone sign-off',
    'group',
    'Complete formal milestone approval process:

1. **Final Review**:
   - Conduct final milestone review meeting
   - Present completion evidence to stakeholders
   - Address any remaining concerns
   - Confirm all criteria are satisfied

2. **Formal Approval**:
   - Obtain written sign-off from product owner
   - Get technical approval from architecture team
   - Secure business approval from sponsors
   - Document approval in project records

3. **Milestone Closure**:
   - Update project management systems
   - Archive milestone artifacts
   - Celebrate team achievements
   - Transition to next milestone planning',
    ARRAY['str-replace-editor', 'view'],
    10,
    'approval',
    'medium',
    ARRAY['signoff', 'approval', 'milestone', 'closure'],
    true
);

-- Insert research components
INSERT INTO archon_template_components (
    id, name, description, component_type, instruction_text,
    required_tools, estimated_duration, category, priority, tags, is_active
) VALUES
(
    gen_random_uuid(),
    'group::research_scope_definition',
    'Define research scope and objectives',
    'group',
    'Define clear research scope and objectives:

1. **Research Questions**:
   - Identify primary research questions to answer
   - Define success criteria for research
   - Set boundaries on what is in/out of scope
   - Establish timeline and resource constraints

2. **Background Context**:
   - Review existing knowledge and documentation
   - Identify what has been tried before
   - Understand current state and limitations
   - Note any assumptions or constraints

3. **Research Methodology**:
   - Choose appropriate research methods
   - Plan data collection and analysis approach
   - Identify required tools and resources
   - Set up research documentation structure',
    ARRAY['view', 'web-search', 'str-replace-editor'],
    15,
    'research',
    'high',
    ARRAY['research', 'scope', 'objectives', 'methodology'],
    true
),
(
    gen_random_uuid(),
    'group::literature_review',
    'Conduct literature and documentation review',
    'group',
    'Review existing literature and documentation:

1. **Documentation Review**:
   - Search internal documentation and wikis
   - Review existing project documentation
   - Check API documentation and specifications
   - Look for related work and previous solutions

2. **External Research**:
   - Search for industry best practices
   - Review relevant technical papers and articles
   - Check open source solutions and libraries
   - Look for case studies and examples

3. **Knowledge Synthesis**:
   - Summarize key findings and insights
   - Identify patterns and common approaches
   - Note gaps in existing knowledge
   - Document sources and references',
    ARRAY['web-search', 'web-fetch', 'view', 'str-replace-editor'],
    25,
    'research',
    'medium',
    ARRAY['literature', 'review', 'documentation', 'research'],
    true
),
(
    gen_random_uuid(),
    'group::existing_solution_analysis',
    'Analyze existing solutions and alternatives',
    'group',
    'Analyze existing solutions and alternatives:

1. **Solution Inventory**:
   - List all known existing solutions
   - Include internal tools and external options
   - Note open source and commercial alternatives
   - Consider build vs buy vs adapt options

2. **Comparative Analysis**:
   - Compare features and capabilities
   - Analyze pros and cons of each option
   - Consider cost, complexity, and maintenance
   - Evaluate fit with current architecture

3. **Gap Analysis**:
   - Identify what each solution provides
   - Note missing features or limitations
   - Consider integration requirements
   - Assess customization and extension needs',
    ARRAY['web-search', 'web-fetch', 'view', 'codebase-retrieval'],
    20,
    'analysis',
    'high',
    ARRAY['analysis', 'solutions', 'alternatives', 'comparison'],
    true
),
(
    gen_random_uuid(),
    'group::findings_documentation',
    'Document research findings and insights',
    'group',
    'Document comprehensive research findings:

1. **Research Summary**:
   - Summarize key findings and discoveries
   - Answer the original research questions
   - Highlight unexpected insights or learnings
   - Note any limitations or uncertainties

2. **Evidence and Data**:
   - Present supporting evidence for findings
   - Include relevant data, metrics, or examples
   - Reference sources and methodology used
   - Provide links to detailed analysis

3. **Implications and Impact**:
   - Discuss implications of findings
   - Consider impact on current project/system
   - Identify risks and opportunities
   - Note dependencies and prerequisites',
    ARRAY['str-replace-editor', 'view'],
    18,
    'documentation',
    'medium',
    ARRAY['documentation', 'findings', 'insights', 'evidence'],
    true
),
(
    gen_random_uuid(),
    'group::recommendation_summary',
    'Provide recommendations based on research',
    'group',
    'Provide clear recommendations based on research:

1. **Primary Recommendations**:
   - State clear, actionable recommendations
   - Prioritize recommendations by impact and effort
   - Provide rationale for each recommendation
   - Include implementation considerations

2. **Alternative Options**:
   - Present alternative approaches considered
   - Explain why primary recommendation is preferred
   - Note when alternatives might be better
   - Consider phased or hybrid approaches

3. **Next Steps**:
   - Outline immediate next steps
   - Identify who should be involved
   - Suggest timeline for implementation
   - Note any additional research needed',
    ARRAY['str-replace-editor', 'view'],
    15,
    'recommendations',
    'high',
    ARRAY['recommendations', 'summary', 'next-steps', 'action'],
    true
),
(
    gen_random_uuid(),
    'group::knowledge_sharing',
    'Share research knowledge with team',
    'group',
    'Share research knowledge and insights:

1. **Knowledge Transfer**:
   - Present findings to relevant teams
   - Create shareable documentation
   - Update team wikis and knowledge bases
   - Conduct knowledge sharing sessions

2. **Documentation Updates**:
   - Update project documentation with findings
   - Add to architectural decision records
   - Update best practices and guidelines
   - Create reusable templates or examples

3. **Community Sharing**:
   - Share insights with broader community
   - Contribute to open source if applicable
   - Write blog posts or articles
   - Present at team meetings or conferences',
    ARRAY['str-replace-editor', 'web-fetch', 'view'],
    12,
    'knowledge_sharing',
    'medium',
    ARRAY['knowledge', 'sharing', 'documentation', 'community'],
    true
);

-- Insert maintenance components
INSERT INTO archon_template_components (
    id, name, description, component_type, instruction_text,
    required_tools, estimated_duration, category, priority, tags, is_active
) VALUES
(
    gen_random_uuid(),
    'group::system_health_check',
    'Perform comprehensive system health check',
    'group',
    'Perform comprehensive system health assessment:

1. **Service Health**:
   - Check all services are running and responsive
   - Verify service dependencies are healthy
   - Review service logs for errors or warnings
   - Check resource utilization (CPU, memory, disk)

2. **Infrastructure Health**:
   - Verify database connectivity and performance
   - Check network connectivity and latency
   - Review storage capacity and performance
   - Validate backup systems are functioning

3. **Monitoring and Alerting**:
   - Verify monitoring systems are active
   - Check alert configurations are current
   - Review recent alerts and incidents
   - Validate dashboards show accurate data',
    ARRAY['homelab-vault', 'launch-process', 'web-fetch'],
    20,
    'maintenance',
    'high',
    ARRAY['health', 'monitoring', 'infrastructure', 'services'],
    true
),
(
    gen_random_uuid(),
    'group::backup_verification',
    'Verify backup systems and data integrity',
    'group',
    'Verify backup systems and data integrity:

1. **Backup Status**:
   - Check all scheduled backups completed successfully
   - Verify backup retention policies are followed
   - Review backup storage capacity and usage
   - Check backup encryption and security

2. **Data Integrity**:
   - Verify backup data integrity checks
   - Test backup restoration procedures
   - Check backup completeness and consistency
   - Validate backup metadata and catalogs

3. **Recovery Testing**:
   - Test backup restoration in test environment
   - Verify recovery time objectives (RTO)
   - Check recovery point objectives (RPO)
   - Document any issues or improvements needed',
    ARRAY['homelab-vault', 'launch-process', 'view'],
    25,
    'backup',
    'critical',
    ARRAY['backup', 'recovery', 'data', 'integrity'],
    true
),
(
    gen_random_uuid(),
    'group::monitoring_validation',
    'Validate monitoring and alerting systems',
    'group',
    'Validate monitoring and alerting effectiveness:

1. **Monitoring Coverage**:
   - Review monitoring coverage for all systems
   - Check for monitoring gaps or blind spots
   - Verify metrics collection is working
   - Validate dashboard accuracy and relevance

2. **Alert Validation**:
   - Test alert delivery mechanisms
   - Verify alert thresholds are appropriate
   - Check alert escalation procedures
   - Review alert fatigue and false positives

3. **Performance Metrics**:
   - Review system performance trends
   - Check capacity planning metrics
   - Validate SLA/SLO compliance
   - Identify performance optimization opportunities',
    ARRAY['web-fetch', 'homelab-vault', 'view'],
    15,
    'monitoring',
    'high',
    ARRAY['monitoring', 'alerting', 'metrics', 'performance'],
    true
),
(
    gen_random_uuid(),
    'group::maintenance_log',
    'Document maintenance activities and findings',
    'group',
    'Document maintenance activities and findings:

1. **Activity Documentation**:
   - Record all maintenance activities performed
   - Document any issues found and resolved
   - Note system changes or updates made
   - Record performance metrics and observations

2. **Findings Summary**:
   - Summarize overall system health status
   - Highlight any concerns or recommendations
   - Note trends or patterns observed
   - Document follow-up actions needed

3. **Maintenance Records**:
   - Update maintenance schedules and logs
   - Record next maintenance due dates
   - Update system documentation if needed
   - Share findings with relevant teams',
    ARRAY['str-replace-editor', 'view'],
    10,
    'documentation',
    'medium',
    ARRAY['documentation', 'maintenance', 'log', 'findings'],
    true
);

-- Insert new workflow template definitions
INSERT INTO archon_template_definitions (
    id, name, title, description, template_type, template_data,
    category, tags, is_public, is_active, created_by
) VALUES
(
    gen_random_uuid(),
    'workflow_hotfix',
    'Hotfix Workflow Template',
    'Expedited workflow for urgent fixes and critical incidents',
    'project',
    jsonb_build_object(
        'template_content', '{{group::incident_assessment}}

{{group::minimal_viable_fix}}

{{USER_TASK}}

{{group::immediate_testing}}

{{group::emergency_deployment}}

{{group::post_incident_review}}',
        'user_task_position', 3,
        'estimated_duration', 60,
        'required_tools', ARRAY['homelab-vault', 'str-replace-editor', 'launch-process', 'view'],
        'workflow_type', 'hotfix',
        'priority', 'critical',
        'description', 'Use this template for urgent fixes that need immediate attention. Includes incident assessment, minimal viable fix implementation, testing, emergency deployment, and post-incident review.'
    ),
    'template-injection',
    ARRAY['hotfix', 'incident', 'emergency', 'urgent'],
    true,
    true,
    'system'
),
(
    gen_random_uuid(),
    'workflow_milestone_pass',
    'Milestone Completion Workflow Template',
    'Comprehensive validation workflow for milestone completion',
    'project',
    jsonb_build_object(
        'template_content', '{{group::milestone_review_checklist}}

{{group::stakeholder_communication}}

{{group::documentation_update}}

{{USER_TASK}}

{{group::integration_testing}}

{{group::performance_validation}}

{{group::security_audit}}

{{group::deployment_preparation}}

{{group::milestone_signoff}}',
        'user_task_position', 4,
        'estimated_duration', 120,
        'required_tools', ARRAY['view', 'str-replace-editor', 'launch-process', 'web-fetch', 'homelab-vault'],
        'workflow_type', 'milestone',
        'priority', 'high',
        'description', 'Use this template for milestone completion tasks. Includes comprehensive review, testing, validation, and formal sign-off procedures.'
    ),
    'template-injection',
    ARRAY['milestone', 'completion', 'validation', 'signoff'],
    true,
    true,
    'system'
),
(
    gen_random_uuid(),
    'workflow_research',
    'Research and Investigation Workflow Template',
    'Structured workflow for research and investigation tasks',
    'project',
    jsonb_build_object(
        'template_content', '{{group::research_scope_definition}}

{{group::literature_review}}

{{group::existing_solution_analysis}}

{{USER_TASK}}

{{group::findings_documentation}}

{{group::recommendation_summary}}

{{group::knowledge_sharing}}',
        'user_task_position', 4,
        'estimated_duration', 90,
        'required_tools', ARRAY['web-search', 'web-fetch', 'view', 'str-replace-editor', 'codebase-retrieval'],
        'workflow_type', 'research',
        'priority', 'medium',
        'description', 'Use this template for research and investigation tasks. Includes scope definition, literature review, solution analysis, documentation, and knowledge sharing.'
    ),
    'template-injection',
    ARRAY['research', 'investigation', 'analysis', 'documentation'],
    true,
    true,
    'system'
),
(
    gen_random_uuid(),
    'workflow_maintenance',
    'Maintenance and Operations Workflow Template',
    'Routine maintenance and system operations workflow',
    'project',
    jsonb_build_object(
        'template_content', '{{group::system_health_check}}

{{group::backup_verification}}

{{USER_TASK}}

{{group::monitoring_validation}}

{{group::documentation_update}}

{{group::maintenance_log}}',
        'user_task_position', 3,
        'estimated_duration', 75,
        'required_tools', ARRAY['homelab-vault', 'launch-process', 'web-fetch', 'view', 'str-replace-editor'],
        'workflow_type', 'maintenance',
        'priority', 'medium',
        'description', 'Use this template for routine maintenance and operational tasks. Includes health checks, backup verification, monitoring validation, and documentation.'
    ),
    'template-injection',
    ARRAY['maintenance', 'operations', 'health', 'monitoring'],
    true,
    true,
    'system'
);

-- Update the existing workflow_default template to include documentation_update component
UPDATE archon_template_definitions
SET template_data = jsonb_set(
    template_data,
    '{template_content}',
    '"{{group::understand_homelab_env}}

{{group::documentation_update}}

{{USER_TASK}}

{{group::create_tests}}

{{group::deployment_validation}}"'::jsonb
)
WHERE name = 'workflow_default';

-- Verify the migration completed successfully
SELECT
    'Migration completed successfully' as status,
    COUNT(CASE WHEN name LIKE 'workflow_%' THEN 1 END) as workflow_templates,
    COUNT(CASE WHEN name LIKE 'group::%' THEN 1 END) as group_components
FROM archon_template_definitions
FULL OUTER JOIN archon_template_components ON true;
