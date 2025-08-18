# Comprehensive Workflow Engine Test Suite

This directory contains a comprehensive test suite for the Archon workflow orchestration system, covering all aspects of workflow validation, execution, error handling, and integration.

## 🧪 Test Categories

### 1. **Validation Tests** (`validation`)
**Files:** `test_workflow_validation_comprehensive.py`, `test_workflow_models.py`

Tests workflow validation logic and error cases:
- ✅ Structural validation and dependency checking
- ✅ Circular reference detection
- ✅ Parameter and tool configuration validation
- ✅ Performance and complexity analysis
- ✅ Step-specific validation (action, condition, parallel, loop, workflow_link)
- ✅ Error handling and edge cases

### 2. **Execution Tests** (`execution`)
**Files:** `test_workflow_executor.py`, `test_workflow_execution_service_comprehensive.py`

Tests workflow execution engine and step processing:
- ✅ Workflow execution lifecycle management
- ✅ Step execution for different step types
- ✅ Background execution and task management
- ✅ Progress tracking and state management
- ✅ WebSocket integration for real-time updates
- ✅ Service layer functionality

### 3. **Error Handling Tests** (`error_handling`)
**Files:** `test_workflow_error_handling.py`

Tests error handling and rollback mechanisms:
- ✅ Step execution failures and retry mechanisms
- ✅ Workflow rollback and recovery scenarios
- ✅ Error propagation and handling strategies
- ✅ Timeout and cancellation handling
- ✅ Resource cleanup and state management
- ✅ Context isolation and corruption prevention

### 4. **Chaining Tests** (`chaining`)
**Files:** `test_workflow_chaining_parameters.py`

Tests workflow chaining and parameter passing:
- ✅ Parameter template resolution and variable substitution
- ✅ Step result chaining and data flow
- ✅ Complex parameter mapping and transformation
- ✅ Variable scoping and context management
- ✅ Nested parameter structures
- ✅ Loop and parallel parameter distribution

### 5. **Performance Tests** (`performance`)
**Files:** `test_workflow_performance.py`

Tests performance for large workflows:
- ✅ Large sequential workflow execution (100+ steps)
- ✅ Large parallel workflow execution (50+ parallel steps)
- ✅ Large loop workflow execution (200+ iterations)
- ✅ Concurrent workflow execution (10+ simultaneous workflows)
- ✅ Memory usage and resource management
- ✅ Performance benchmarking and profiling

### 6. **Integration Tests** (`integration`)
**Files:** `test_workflow_integration.py`, `test_workflow_repository.py`, `test_mcp_tool_integration.py`

Tests integration with database and MCP tools:
- ✅ Database integration and transaction handling
- ✅ MCP tool integration and real tool execution
- ✅ End-to-end workflow execution scenarios
- ✅ Cross-service integration testing
- ✅ Repository data access layer testing
- ✅ Singleton service instance management

### 7. **WebSocket Tests** (`websocket`)
**Files:** `test_workflow_websocket.py`

Tests WebSocket real-time monitoring:
- ✅ WebSocket connection management
- ✅ Real-time execution monitoring
- ✅ Message broadcasting and format validation
- ✅ Subscription management
- ✅ Error handling and disconnection scenarios
- ✅ Multiple subscriber management

## 🚀 Running Tests

### Quick Start

```bash
# Run all tests
python tests/run_workflow_tests.py all

# Run specific category
python tests/run_workflow_tests.py validation
python tests/run_workflow_tests.py execution
python tests/run_workflow_tests.py performance

# List available categories
python tests/run_workflow_tests.py --list

# Check test file availability
python tests/run_workflow_tests.py --check

# Verbose output
python tests/run_workflow_tests.py all --verbose
```

### Using pytest directly

```bash
# Run all workflow tests
pytest tests/test_workflow_*.py -v

# Run specific test file
pytest tests/test_workflow_validation_comprehensive.py -v

# Run tests with specific markers
pytest -m "validation" -v
pytest -m "performance" -v
pytest -m "integration" -v

# Run with coverage
pytest tests/test_workflow_*.py --cov=src.server.services.workflow --cov-report=html
```

## 📊 Test Coverage

The test suite provides comprehensive coverage of:

### Core Components
- ✅ **WorkflowExecutor** - Core execution engine
- ✅ **WorkflowExecutionService** - High-level execution service
- ✅ **WorkflowRepository** - Database access layer
- ✅ **WorkflowValidator** - Validation logic
- ✅ **MCPWorkflowIntegration** - MCP tool integration
- ✅ **WorkflowWebSocketManager** - Real-time monitoring

### Workflow Step Types
- ✅ **ActionStep** - Tool execution steps
- ✅ **ConditionStep** - Conditional branching
- ✅ **ParallelStep** - Parallel execution
- ✅ **LoopStep** - Iterative execution
- ✅ **WorkflowLinkStep** - Sub-workflow calls

### Error Scenarios
- ✅ **Step failures** with retry mechanisms
- ✅ **Timeout handling** and cancellation
- ✅ **Resource cleanup** and state management
- ✅ **Database failures** and transaction rollback
- ✅ **Network failures** and recovery
- ✅ **Memory management** and leak prevention

### Performance Scenarios
- ✅ **Large workflows** (100+ steps)
- ✅ **High concurrency** (10+ simultaneous executions)
- ✅ **Memory efficiency** testing
- ✅ **Execution time** benchmarking
- ✅ **Resource utilization** monitoring

## 🛠️ Test Infrastructure

### Mocking Strategy
- **Database operations** - Mocked Supabase client with realistic responses
- **MCP tool execution** - Configurable mock responses for different scenarios
- **WebSocket connections** - Mock WebSocket instances with async capabilities
- **Background tasks** - Mock task manager for testing async execution

### Test Fixtures
- **workflow_executor** - Pre-configured executor with mocked dependencies
- **execution_context** - Sample execution context for testing
- **sample_workflows** - Various workflow templates for different test scenarios
- **mock_repositories** - Database layer mocks with realistic behavior

### Performance Testing
- **Memory monitoring** - Uses `psutil` to track memory usage
- **Execution timing** - Measures performance of large workflows
- **Concurrency testing** - Tests multiple simultaneous executions
- **Resource cleanup** - Verifies proper cleanup after execution

## 📈 Test Metrics

### Expected Performance Benchmarks
- **Sequential workflows** (100 steps): < 10 seconds
- **Parallel workflows** (50 steps): < 5 seconds  
- **Loop workflows** (200 iterations): < 15 seconds
- **Concurrent executions** (10 workflows): < 20 seconds
- **Memory usage**: < 100MB for large workflows

### Coverage Targets
- **Line coverage**: > 90%
- **Branch coverage**: > 85%
- **Function coverage**: > 95%
- **Integration coverage**: All major workflows tested end-to-end

## 🔧 Development Guidelines

### Adding New Tests
1. **Choose appropriate category** based on test focus
2. **Follow naming convention**: `test_workflow_[category]_[feature].py`
3. **Use proper fixtures** for consistent test setup
4. **Include performance assertions** for execution tests
5. **Mock external dependencies** appropriately
6. **Add comprehensive docstrings** explaining test purpose

### Test Organization
```
tests/
├── test_workflow_validation_comprehensive.py    # Validation logic
├── test_workflow_execution_service_comprehensive.py  # Service layer
├── test_workflow_error_handling.py             # Error scenarios
├── test_workflow_chaining_parameters.py        # Parameter flow
├── test_workflow_performance.py                # Performance tests
├── test_workflow_integration.py                # Integration tests
├── test_workflow_websocket.py                  # WebSocket tests
├── run_workflow_tests.py                       # Test runner
└── README_WORKFLOW_TESTS.md                    # This file
```

### Best Practices
- ✅ **Isolate tests** - Each test should be independent
- ✅ **Use descriptive names** - Test names should explain what is being tested
- ✅ **Test edge cases** - Include boundary conditions and error scenarios
- ✅ **Mock appropriately** - Mock external dependencies, not internal logic
- ✅ **Assert meaningfully** - Verify both success and failure conditions
- ✅ **Clean up resources** - Ensure tests don't leak resources

## 🎯 Continuous Integration

The test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Run Workflow Tests
  run: |
    python tests/run_workflow_tests.py all
    
- name: Run Performance Tests
  run: |
    python tests/run_workflow_tests.py performance
    
- name: Generate Coverage Report
  run: |
    pytest tests/test_workflow_*.py --cov=src.server.services.workflow --cov-report=xml
```

## 📚 Additional Resources

- **Workflow Documentation**: See main project documentation
- **API Reference**: Check workflow API endpoints documentation
- **Performance Tuning**: See performance optimization guides
- **Troubleshooting**: Check common issues and solutions

---

**Total Test Files**: 8  
**Total Test Categories**: 7  
**Estimated Test Count**: 150+  
**Coverage Target**: 90%+
