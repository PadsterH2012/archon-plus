"""
Workflow Validation Module

This module provides comprehensive validation for workflow templates including:
- Structural validation and dependency checking
- Circular reference detection
- Parameter and tool configuration validation
- MCP tool compatibility checking
- Performance and complexity analysis
"""

import re
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass

from .workflow_models import (
    WorkflowTemplate,
    WorkflowStep,
    ActionStep,
    ConditionStep,
    WorkflowLinkStep,
    ParallelStep,
    LoopStep,
    WorkflowStepType
)


@dataclass
class ValidationError:
    """Represents a validation error with context"""
    code: str
    message: str
    step_name: Optional[str] = None
    field: Optional[str] = None
    severity: str = "error"  # error, warning, info
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of workflow validation"""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    info: List[ValidationError]
    
    @property
    def has_errors(self) -> bool:
        """Check if validation has errors"""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings"""
        return len(self.warnings) > 0
    
    def add_error(self, code: str, message: str, step_name: Optional[str] = None, 
                  field: Optional[str] = None, suggestion: Optional[str] = None):
        """Add validation error"""
        self.errors.append(ValidationError(
            code=code, message=message, step_name=step_name, 
            field=field, severity="error", suggestion=suggestion
        ))
        self.is_valid = False
    
    def add_warning(self, code: str, message: str, step_name: Optional[str] = None,
                    field: Optional[str] = None, suggestion: Optional[str] = None):
        """Add validation warning"""
        self.warnings.append(ValidationError(
            code=code, message=message, step_name=step_name,
            field=field, severity="warning", suggestion=suggestion
        ))
    
    def add_info(self, code: str, message: str, step_name: Optional[str] = None,
                 field: Optional[str] = None, suggestion: Optional[str] = None):
        """Add validation info"""
        self.info.append(ValidationError(
            code=code, message=message, step_name=step_name,
            field=field, severity="info", suggestion=suggestion
        ))


class WorkflowValidator:
    """Comprehensive workflow validation engine"""
    
    # Known MCP tools in Archon system
    KNOWN_MCP_TOOLS = {
        "health_check_archon",
        "session_info_archon", 
        "get_available_sources_archon",
        "perform_rag_query_archon",
        "search_code_examples_archon",
        "manage_project_archon",
        "manage_task_archon",
        "manage_document_archon",
        "manage_versions_archon",
        "get_project_features_archon"
    }
    
    # Variable pattern for parameter substitution
    VARIABLE_PATTERN = re.compile(r'\{\{([^}]+)\}\}')
    
    def __init__(self):
        self.result = ValidationResult(is_valid=True, errors=[], warnings=[], info=[])
    
    def validate_workflow(self, workflow: WorkflowTemplate) -> ValidationResult:
        """
        Perform comprehensive workflow validation.
        
        Args:
            workflow: Workflow template to validate
            
        Returns:
            ValidationResult with all validation issues
        """
        self.result = ValidationResult(is_valid=True, errors=[], warnings=[], info=[])
        
        # Basic structure validation
        self._validate_basic_structure(workflow)
        
        # Step validation
        self._validate_steps(workflow.steps)
        
        # Dependency validation
        self._validate_dependencies(workflow.steps)
        
        # Circular reference detection
        self._detect_circular_references(workflow.steps)
        
        # Parameter validation
        self._validate_parameters(workflow)
        
        # Performance analysis
        self._analyze_performance(workflow)
        
        # Tool compatibility check
        self._validate_tool_compatibility(workflow.steps)
        
        return self.result
    
    def _validate_basic_structure(self, workflow: WorkflowTemplate):
        """Validate basic workflow structure"""
        
        # Check required fields
        if not workflow.name:
            self.result.add_error(
                "MISSING_NAME", 
                "Workflow name is required",
                suggestion="Provide a unique workflow name using alphanumeric characters, underscores, and hyphens"
            )
        
        if not workflow.title:
            self.result.add_error(
                "MISSING_TITLE",
                "Workflow title is required",
                suggestion="Provide a human-readable title for the workflow"
            )
        
        if not workflow.steps:
            self.result.add_error(
                "NO_STEPS",
                "Workflow must have at least one step",
                suggestion="Add workflow steps to define the execution flow"
            )
        
        # Check for reasonable limits
        if len(workflow.steps) > 100:
            self.result.add_warning(
                "TOO_MANY_STEPS",
                f"Workflow has {len(workflow.steps)} steps, which may impact performance",
                suggestion="Consider breaking large workflows into smaller sub-workflows"
            )
        
        if workflow.timeout_minutes > 1440:  # 24 hours
            self.result.add_warning(
                "LONG_TIMEOUT",
                f"Workflow timeout of {workflow.timeout_minutes} minutes is very long",
                suggestion="Consider shorter timeouts to prevent runaway executions"
            )
    
    def _validate_steps(self, steps: List[WorkflowStep]):
        """Validate individual workflow steps"""
        
        step_names = set()
        
        for i, step in enumerate(steps):
            # Check for duplicate step names
            if step.name in step_names:
                self.result.add_error(
                    "DUPLICATE_STEP_NAME",
                    f"Duplicate step name '{step.name}' found",
                    step_name=step.name,
                    suggestion="Each step must have a unique name within the workflow"
                )
            step_names.add(step.name)
            
            # Validate step-specific requirements
            self._validate_step_specific(step, i)
    
    def _validate_step_specific(self, step: WorkflowStep, index: int):
        """Validate step-specific requirements"""
        
        if isinstance(step, ActionStep):
            self._validate_action_step(step)
        elif isinstance(step, ConditionStep):
            self._validate_condition_step(step)
        elif isinstance(step, WorkflowLinkStep):
            self._validate_workflow_link_step(step)
        elif isinstance(step, ParallelStep):
            self._validate_parallel_step(step)
        elif isinstance(step, LoopStep):
            self._validate_loop_step(step)
        
        # Common validations
        if step.timeout_seconds > 3600:  # 1 hour
            self.result.add_warning(
                "LONG_STEP_TIMEOUT",
                f"Step '{step.name}' has a very long timeout of {step.timeout_seconds} seconds",
                step_name=step.name,
                suggestion="Consider shorter timeouts for individual steps"
            )
        
        if step.retry_count > 10:
            self.result.add_warning(
                "HIGH_RETRY_COUNT",
                f"Step '{step.name}' has high retry count of {step.retry_count}",
                step_name=step.name,
                suggestion="High retry counts may indicate underlying issues"
            )
    
    def _validate_action_step(self, step: ActionStep):
        """Validate action step specifics"""
        
        # Check if tool is known
        if step.tool_name not in self.KNOWN_MCP_TOOLS:
            self.result.add_warning(
                "UNKNOWN_TOOL",
                f"Tool '{step.tool_name}' is not in the known MCP tools list",
                step_name=step.name,
                field="tool_name",
                suggestion=f"Verify tool name. Known tools: {', '.join(sorted(self.KNOWN_MCP_TOOLS))}"
            )
        
        # Validate parameter structure
        self._validate_parameters_structure(step.parameters, step.name)
    
    def _validate_condition_step(self, step: ConditionStep):
        """Validate condition step specifics"""
        
        # Check condition syntax (basic validation)
        if not step.condition.strip():
            self.result.add_error(
                "EMPTY_CONDITION",
                f"Condition step '{step.name}' has empty condition",
                step_name=step.name,
                field="condition",
                suggestion="Provide a valid condition expression"
            )
        
        # Check for common condition patterns
        if "{{" not in step.condition:
            self.result.add_warning(
                "STATIC_CONDITION",
                f"Condition step '{step.name}' appears to have a static condition",
                step_name=step.name,
                field="condition",
                suggestion="Conditions should typically reference dynamic values using {{variable}} syntax"
            )
    
    def _validate_workflow_link_step(self, step: WorkflowLinkStep):
        """Validate workflow link step specifics"""
        
        # Check workflow name format
        if not step.workflow_name.replace("_", "").replace("-", "").isalnum():
            self.result.add_warning(
                "INVALID_WORKFLOW_NAME_FORMAT",
                f"Workflow name '{step.workflow_name}' should use alphanumeric characters, underscores, and hyphens",
                step_name=step.name,
                field="workflow_name"
            )
        
        # Validate parameters
        self._validate_parameters_structure(step.parameters, step.name)
    
    def _validate_parallel_step(self, step: ParallelStep):
        """Validate parallel step specifics"""
        
        if len(step.steps) > 10:
            self.result.add_warning(
                "TOO_MANY_PARALLEL_STEPS",
                f"Parallel step '{step.name}' has {len(step.steps)} concurrent steps",
                step_name=step.name,
                suggestion="Too many parallel steps may overwhelm system resources"
            )
        
        # Recursively validate sub-steps
        self._validate_steps(step.steps)
    
    def _validate_loop_step(self, step: LoopStep):
        """Validate loop step specifics"""
        
        if step.max_iterations > 1000:
            self.result.add_warning(
                "HIGH_LOOP_ITERATIONS",
                f"Loop step '{step.name}' allows up to {step.max_iterations} iterations",
                step_name=step.name,
                suggestion="High iteration counts may cause performance issues"
            )
        
        # Check collection reference
        if not self.VARIABLE_PATTERN.search(step.collection):
            self.result.add_warning(
                "STATIC_COLLECTION",
                f"Loop step '{step.name}' collection appears to be static",
                step_name=step.name,
                field="collection",
                suggestion="Loop collections should typically reference dynamic values"
            )
        
        # Recursively validate sub-steps
        self._validate_steps(step.steps)
    
    def _validate_dependencies(self, steps: List[WorkflowStep]):
        """Validate step dependencies and references"""
        
        step_names = {step.name for step in steps}
        valid_references = step_names | {"next", "end", "fail", "retry"}
        
        for step in steps:
            # Check on_success and on_failure references
            if step.on_success not in valid_references:
                self.result.add_error(
                    "INVALID_SUCCESS_REFERENCE",
                    f"Step '{step.name}' references unknown step '{step.on_success}' in on_success",
                    step_name=step.name,
                    field="on_success",
                    suggestion=f"Valid references: {', '.join(sorted(valid_references))}"
                )
            
            if step.on_failure not in valid_references:
                self.result.add_error(
                    "INVALID_FAILURE_REFERENCE", 
                    f"Step '{step.name}' references unknown step '{step.on_failure}' in on_failure",
                    step_name=step.name,
                    field="on_failure",
                    suggestion=f"Valid references: {', '.join(sorted(valid_references))}"
                )
            
            # Check condition step specific references
            if isinstance(step, ConditionStep):
                if step.on_true not in valid_references:
                    self.result.add_error(
                        "INVALID_TRUE_REFERENCE",
                        f"Condition step '{step.name}' references unknown step '{step.on_true}' in on_true",
                        step_name=step.name,
                        field="on_true"
                    )
                
                if step.on_false not in valid_references:
                    self.result.add_error(
                        "INVALID_FALSE_REFERENCE",
                        f"Condition step '{step.name}' references unknown step '{step.on_false}' in on_false",
                        step_name=step.name,
                        field="on_false"
                    )
    
    def _detect_circular_references(self, steps: List[WorkflowStep]):
        """Detect circular references in workflow steps"""
        
        step_map = {step.name: step for step in steps}
        
        def has_cycle(start_step: str, visited: Set[str], path: List[str]) -> bool:
            if start_step in visited:
                cycle_start = path.index(start_step)
                cycle = " -> ".join(path[cycle_start:] + [start_step])
                self.result.add_error(
                    "CIRCULAR_REFERENCE",
                    f"Circular reference detected: {cycle}",
                    suggestion="Remove circular references to prevent infinite loops"
                )
                return True
            
            if start_step not in step_map:
                return False
            
            visited.add(start_step)
            path.append(start_step)
            
            step = step_map[start_step]
            next_steps = []
            
            # Collect next steps based on step type
            if isinstance(step, ConditionStep):
                if step.on_true in step_map:
                    next_steps.append(step.on_true)
                if step.on_false in step_map:
                    next_steps.append(step.on_false)
            else:
                if step.on_success in step_map:
                    next_steps.append(step.on_success)
                if step.on_failure in step_map:
                    next_steps.append(step.on_failure)
            
            # Check each next step
            for next_step in next_steps:
                if has_cycle(next_step, visited.copy(), path.copy()):
                    return True
            
            return False
        
        # Check for cycles starting from each step
        for step in steps:
            has_cycle(step.name, set(), [])
    
    def _validate_parameters(self, workflow: WorkflowTemplate):
        """Validate workflow parameters and their usage"""
        
        # Check parameter schema structure
        if workflow.parameters:
            for param_name, param_def in workflow.parameters.items():
                if not isinstance(param_def, dict):
                    self.result.add_warning(
                        "INVALID_PARAMETER_SCHEMA",
                        f"Parameter '{param_name}' should have a schema definition",
                        field="parameters",
                        suggestion="Use {'type': 'string', 'required': true} format for parameter definitions"
                    )
        
        # Check if declared parameters are used
        declared_params = set(workflow.parameters.keys()) if workflow.parameters else set()
        used_params = set()
        
        def extract_variables(text: str) -> Set[str]:
            """Extract variable references from text"""
            variables = set()
            for match in self.VARIABLE_PATTERN.finditer(text):
                var_ref = match.group(1)
                # Extract parameter references (workflow.parameters.param_name)
                if var_ref.startswith("workflow.parameters."):
                    param_name = var_ref.split(".")[-1]
                    variables.add(param_name)
            return variables
        
        # Scan all steps for parameter usage
        for step in workflow.steps:
            # Check step parameters
            if hasattr(step, 'parameters') and step.parameters:
                for value in step.parameters.values():
                    if isinstance(value, str):
                        used_params.update(extract_variables(value))
            
            # Check condition expressions
            if isinstance(step, ConditionStep):
                used_params.update(extract_variables(step.condition))
            
            # Check collection references in loops
            if isinstance(step, LoopStep):
                used_params.update(extract_variables(step.collection))
        
        # Report unused parameters
        unused_params = declared_params - used_params
        for param in unused_params:
            self.result.add_warning(
                "UNUSED_PARAMETER",
                f"Parameter '{param}' is declared but never used",
                field="parameters",
                suggestion="Remove unused parameters or add them to workflow steps"
            )
        
        # Report undeclared parameters
        undeclared_params = used_params - declared_params
        for param in undeclared_params:
            self.result.add_error(
                "UNDECLARED_PARAMETER",
                f"Parameter '{param}' is used but not declared",
                field="parameters",
                suggestion="Add parameter declaration to workflow.parameters"
            )
    
    def _validate_parameters_structure(self, parameters: Dict[str, Any], step_name: str):
        """Validate parameter structure for a step"""
        
        for param_name, param_value in parameters.items():
            if isinstance(param_value, str):
                # Check for unmatched braces
                open_braces = param_value.count("{{")
                close_braces = param_value.count("}}")
                
                if open_braces != close_braces:
                    self.result.add_error(
                        "UNMATCHED_BRACES",
                        f"Parameter '{param_name}' in step '{step_name}' has unmatched braces",
                        step_name=step_name,
                        field=param_name,
                        suggestion="Ensure all {{ have matching }}"
                    )
    
    def _analyze_performance(self, workflow: WorkflowTemplate):
        """Analyze workflow for performance issues"""
        
        total_timeout = sum(step.timeout_seconds for step in workflow.steps)
        if total_timeout > workflow.timeout_minutes * 60:
            self.result.add_warning(
                "TIMEOUT_MISMATCH",
                f"Sum of step timeouts ({total_timeout}s) exceeds workflow timeout ({workflow.timeout_minutes * 60}s)",
                suggestion="Adjust step timeouts or increase workflow timeout"
            )
        
        # Count nested complexity
        def count_complexity(steps: List[WorkflowStep]) -> int:
            complexity = len(steps)
            for step in steps:
                if isinstance(step, (ParallelStep, LoopStep)):
                    complexity += count_complexity(step.steps) * 2  # Nested steps add more complexity
            return complexity
        
        complexity = count_complexity(workflow.steps)
        if complexity > 50:
            self.result.add_warning(
                "HIGH_COMPLEXITY",
                f"Workflow complexity score is {complexity}",
                suggestion="Consider simplifying the workflow or breaking it into sub-workflows"
            )
    
    def _validate_tool_compatibility(self, steps: List[WorkflowStep]):
        """Validate MCP tool compatibility and parameters"""
        
        # Tool-specific parameter validation
        tool_requirements = {
            "manage_project_archon": ["action"],
            "manage_task_archon": ["action"],
            "manage_document_archon": ["action", "project_id"],
            "perform_rag_query_archon": ["query"],
            "search_code_examples_archon": ["query"]
        }
        
        for step in steps:
            if isinstance(step, ActionStep) and step.tool_name in tool_requirements:
                required_params = tool_requirements[step.tool_name]
                missing_params = []
                
                for param in required_params:
                    if param not in step.parameters:
                        missing_params.append(param)
                
                if missing_params:
                    self.result.add_error(
                        "MISSING_REQUIRED_PARAMETERS",
                        f"Step '{step.name}' missing required parameters for {step.tool_name}: {', '.join(missing_params)}",
                        step_name=step.name,
                        field="parameters",
                        suggestion=f"Add required parameters: {', '.join(missing_params)}"
                    )
            
            # Recursively check nested steps
            if isinstance(step, (ParallelStep, LoopStep)):
                self._validate_tool_compatibility(step.steps)


def validate_workflow_template(workflow: WorkflowTemplate) -> ValidationResult:
    """
    Convenience function to validate a workflow template.
    
    Args:
        workflow: Workflow template to validate
        
    Returns:
        ValidationResult with all validation issues
    """
    validator = WorkflowValidator()
    return validator.validate_workflow(workflow)
