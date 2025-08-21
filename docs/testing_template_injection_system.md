# Testing Template Injection System

This document provides comprehensive guidance for testing the Archon Template Injection System, including unit tests, integration tests, performance benchmarks, and quality validation.

## Overview

The Template Injection System testing suite ensures:
- **Functionality**: All components work correctly
- **Performance**: Meets speed and efficiency targets
- **Quality**: Generated instructions are coherent and useful
- **Reliability**: System handles errors gracefully
- **Scalability**: Performs well under load

## Test Categories

### 1. Unit Tests

**Location**: `python/tests/services/test_template_injection_service.py`

**Coverage**:
- TemplateInjectionService methods
- Template expansion logic
- Component resolution
- Error handling
- Caching mechanisms

**Running Unit Tests**:
```bash
cd python
uv run pytest tests/services/test_template_injection_service.py -v
```

### 2. Integration Tests

**Location**: `python/tests/integration/test_template_injection_e2e.py`

**Coverage**:
- End-to-end template expansion workflow
- TaskService integration
- Database operations
- Feature flag functionality
- Real component resolution

**Running Integration Tests**:
```bash
cd python
uv run pytest tests/integration/test_template_injection_e2e.py -v
```

### 3. MCP Tool Integration Tests

**Location**: `python/tests/mcp/test_project_module_template_integration.py`

**Coverage**:
- manage_task MCP tool with template parameters
- API integration
- Backward compatibility
- Error handling

**Running MCP Tests**:
```bash
cd python
uv run pytest tests/mcp/test_project_module_template_integration.py -v
```

### 4. Performance Tests

**Location**: `python/tests/performance/test_template_injection_performance.py`

**Coverage**:
- Template expansion performance (<100ms target)
- Task creation overhead (<50ms target)
- Concurrent load testing
- Cache performance
- Memory usage

**Running Performance Tests**:
```bash
cd python
uv run pytest tests/performance/test_template_injection_performance.py -v
```

## Validation Scripts

### Template Quality Validation

**Script**: `python/scripts/validate_template_quality.py`

**Purpose**: Validates that templates produce coherent, useful instructions

**Features**:
- Tests with various user task examples
- Analyzes instruction quality and structure
- Checks for completeness and coherence
- Generates quality scores and recommendations

**Usage**:
```bash
cd python
python scripts/validate_template_quality.py
```

**Quality Metrics**:
- Original task preservation
- Instruction structure and clarity
- Preparation and setup steps
- Testing and validation instructions
- Tool references and completeness
- Word diversity and redundancy

### Performance Benchmarking

**Script**: `python/scripts/benchmark_template_performance.py`

**Purpose**: Comprehensive performance benchmarking under various conditions

**Features**:
- Template expansion performance
- Concurrent load testing
- Cache efficiency analysis
- Task creation overhead measurement
- System resource monitoring

**Usage**:
```bash
cd python
python scripts/benchmark_template_performance.py
```

**Performance Targets**:
- Template expansion: <100ms
- Task creation overhead: <50ms
- Cache improvement: >2x speedup
- Concurrent load: <200ms average under 20 users

## Test Data and Fixtures

### Mock Data Structure

Tests use consistent mock data:

```python
# Template Definition
mock_template = {
    "name": "workflow_default",
    "template_data": {
        "template_content": "{{group::prep}}\n\n{{USER_TASK}}\n\n{{group::test}}",
        "user_task_position": 2
    }
}

# Template Components
mock_components = [
    {
        "name": "group::prep",
        "instruction_text": "Prepare for implementation...",
        "component_type": "group"
    }
]
```

### Test Scenarios

**Common Test Cases**:
1. Basic template expansion
2. Component resolution
3. Error handling (missing templates/components)
4. Cache performance
5. Concurrent access
6. Feature flag controls
7. Backward compatibility

## Running All Tests

### Complete Test Suite

```bash
cd python

# Run all template injection tests
uv run pytest tests/services/test_template_injection_service.py \
              tests/integration/test_template_injection_e2e.py \
              tests/mcp/test_project_module_template_integration.py \
              tests/performance/test_template_injection_performance.py \
              -v

# Run validation scripts
python scripts/validate_template_quality.py
python scripts/benchmark_template_performance.py
```

### Continuous Integration

For CI/CD pipelines:

```bash
# Fast test suite (unit + integration)
uv run pytest tests/services/test_template_injection_service.py \
              tests/integration/test_template_injection_e2e.py \
              tests/mcp/test_project_module_template_integration.py \
              --maxfail=5 -x

# Performance validation (separate job)
python scripts/benchmark_template_performance.py
```

## Test Environment Setup

### Prerequisites

1. **Python Environment**:
   ```bash
   cd python
   uv sync
   ```

2. **Database Setup**:
   - Ensure test database is available
   - Run template injection migrations
   - Seed with test data

3. **Environment Variables**:
   ```bash
   export TEMPLATE_INJECTION_ENABLED=true
   export SUPABASE_URL=your_test_db_url
   export SUPABASE_KEY=your_test_db_key
   ```

### Mock vs Real Database

**Unit Tests**: Use mocked Supabase client
**Integration Tests**: Can use real test database
**Performance Tests**: Recommend real database for accurate metrics

## Performance Targets

### Template Expansion
- **Target**: <100ms per expansion
- **Acceptable**: <150ms under load
- **Critical**: >300ms (investigate immediately)

### Task Creation Overhead
- **Target**: <50ms additional overhead
- **Acceptable**: <100ms
- **Critical**: >200ms

### Cache Performance
- **Target**: >2x improvement on cache hits
- **Acceptable**: >1.5x improvement
- **Critical**: <1.2x improvement

### Concurrent Load
- **Target**: 20 concurrent users, <200ms average
- **Acceptable**: 10 concurrent users, <300ms average
- **Critical**: Performance degrades significantly

## Quality Standards

### Template Quality Score
- **Excellent**: >90/100
- **Good**: 70-90/100
- **Needs Improvement**: 50-70/100
- **Poor**: <50/100

### Quality Criteria
1. **Original Task Preservation** (20 points)
2. **Appropriate Length** (15 points)
3. **Structured Content** (15 points)
4. **Preparation Steps** (10 points)
5. **Testing Instructions** (15 points)
6. **Completion Steps** (10 points)
7. **Tool References** (15 points)

## Troubleshooting

### Common Test Failures

1. **Template Not Found**:
   - Check database seeding
   - Verify template names match

2. **Component Resolution Fails**:
   - Ensure all referenced components exist
   - Check component naming conventions

3. **Performance Tests Fail**:
   - Check system resources
   - Verify database performance
   - Review cache configuration

4. **Mock Setup Issues**:
   - Verify mock data structure
   - Check async/await patterns
   - Ensure proper cleanup

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
uv run pytest tests/ -v -s
```

## Reporting

### Test Reports

Tests generate detailed reports:
- **Unit Test Coverage**: pytest-cov reports
- **Performance Metrics**: JSON reports with timing data
- **Quality Analysis**: Detailed quality scores and recommendations

### Continuous Monitoring

Set up monitoring for:
- Test success rates
- Performance regression detection
- Quality score trends
- Error rate monitoring

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Mock External Dependencies**: Use mocks for external services
3. **Performance Baselines**: Establish and maintain performance baselines
4. **Regular Validation**: Run quality validation regularly
5. **Load Testing**: Test under realistic load conditions
6. **Error Scenarios**: Test failure modes and recovery
7. **Documentation**: Keep test documentation updated

## Future Enhancements

Planned testing improvements:
- Automated quality regression detection
- Machine learning-based performance prediction
- Advanced load testing scenarios
- Integration with monitoring systems
- Automated performance optimization suggestions
