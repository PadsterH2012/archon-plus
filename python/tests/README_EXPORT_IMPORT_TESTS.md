# Export/Import System Testing Suite

This directory contains a comprehensive testing suite for the Archon export/import system, providing thorough validation of all export, import, and backup functionality.

## 📋 Test Categories

### 🔧 Unit Tests
**Location**: `python/tests/`

- **`test_export_service.py`** - ProjectExportService functionality
- **`test_import_service.py`** - ProjectImportService functionality  
- **`test_export_import_api.py`** - REST API endpoints
- **`test_backup_system.py`** - Backup manager and scheduler
- **`test_mcp_export_import_tools.py`** - MCP tools for workflow integration

### 🔗 Integration Tests
**Location**: `python/tests/integration/`

- **`test_export_import_integration.py`** - End-to-end export/import workflows
  - Full export/import cycles
  - Selective export/import
  - Conflict resolution testing
  - Data integrity validation
  - Large project handling
  - Version history preservation

### ⚡ Performance Tests
**Location**: `python/tests/performance/`

- **`test_export_import_performance.py`** - Performance benchmarks
  - Small project export/import (< 100 tasks)
  - Medium project export/import (100-1000 tasks)
  - Large project export/import (1000+ tasks)
  - Concurrent operation testing
  - Memory usage analysis
  - Compression efficiency testing

### 🛡️ Data Integrity Tests
**Location**: `python/tests/validation/`

- **`test_data_integrity.py`** - Data validation and integrity
  - Checksum validation
  - Round-trip data preservation
  - Unicode and special character handling
  - Large dataset integrity
  - Nested data structure validation
  - Export file format validation
  - Corruption detection
  - Edge case handling (empty projects, null values)

### 🎭 Scenario Tests
**Location**: `python/tests/scenarios/`

- **`test_export_import_scenarios.py`** - Real-world scenarios
  - Project migration between environments
  - Disaster recovery workflows
  - Team collaboration scenarios
  - Incremental backup strategies
  - Multi-project export/import
  - Error recovery scenarios

## 🚀 Running Tests

### Quick Start

```bash
# Run all essential tests
python tests/run_export_import_tests.py

# Run quick development tests
python tests/run_export_import_tests.py --quick

# Run smoke tests
python tests/run_export_import_tests.py --smoke

# Validate test environment
python tests/run_export_import_tests.py --validate
```

### Comprehensive Testing

```bash
# Run all tests with coverage
python tests/run_export_import_tests.py --all --coverage

# Run specific categories
python tests/run_export_import_tests.py --categories unit integration

# Run performance benchmarks
python tests/run_export_import_tests.py --performance

# Run with specific patterns
python tests/run_export_import_tests.py --pattern export --verbose
```

### Advanced Options

```bash
# Parallel execution
python tests/run_export_import_tests.py --parallel

# Stop on first failure
python tests/run_export_import_tests.py --stop-on-failure

# Filter by markers
python tests/run_export_import_tests.py --markers "not slow"

# Run specific test files
pytest test_export_service.py -v
pytest integration/test_export_import_integration.py::TestExportImportIntegration::test_full_export_import_cycle -v
```

## 📊 Test Coverage

The testing suite provides comprehensive coverage of:

### ✅ Export Functionality
- Project data export (core data, documents, tasks, versions)
- Multiple export types (full, selective, incremental)
- Export format validation and integrity
- Large dataset handling
- Error conditions and edge cases

### ✅ Import Functionality
- Project data import with validation
- Conflict detection and resolution
- Multiple import strategies (full, selective, merge)
- Data integrity verification
- Import file validation
- Error handling and rollback

### ✅ Backup System
- Automated backup creation and scheduling
- Backup restoration and verification
- Retention policy management
- Storage backend operations
- Health monitoring and error recovery

### ✅ API Integration
- REST endpoint functionality
- Request/response validation
- File upload/download handling
- Error response formatting
- Authentication and authorization

### ✅ MCP Tools
- Workflow integration tools
- Parameter validation
- Tool execution and result handling
- Error propagation and logging

## 🔧 Test Configuration

### Environment Setup

Tests require the following environment variables:
```bash
export TEST_MODE=true
export TESTING=true
export SUPABASE_URL=https://test.supabase.co
export SUPABASE_SERVICE_KEY=test-key
export ARCHON_SERVER_PORT=8181
export ARCHON_MCP_PORT=8051
export ARCHON_AGENTS_PORT=8052
```

### Test Fixtures

The test suite includes comprehensive fixtures:
- **Mock Supabase clients** with realistic response patterns
- **Sample project data** with various complexity levels
- **Temporary directories** for file operations
- **Test export files** for import testing
- **Database response mocking** for isolated testing

### Test Markers

Tests are organized with pytest markers:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.scenario` - Scenario tests
- `@pytest.mark.slow` - Long-running tests

## 📈 Performance Benchmarks

### Expected Performance Targets

| Project Size | Export Time | Import Time | File Size |
|-------------|-------------|-------------|-----------|
| Small (< 100 tasks) | < 5 seconds | < 5 seconds | < 1 MB |
| Medium (100-1000 tasks) | < 15 seconds | < 15 seconds | < 10 MB |
| Large (1000+ tasks) | < 30 seconds | < 25 seconds | < 50 MB |

### Memory Usage Targets
- Memory increase during large exports: < 100 MB
- Compression ratio: > 20% (ratio < 0.8)
- Concurrent operations: 5 projects in < 15 seconds

## 🐛 Debugging Tests

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Ensure test environment is set
   export TEST_MODE=true
   ```

2. **File Permission Errors**
   ```bash
   # Check temporary directory permissions
   python tests/run_export_import_tests.py --validate
   ```

3. **Import Errors**
   ```bash
   # Verify Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

### Verbose Testing

```bash
# Run with maximum verbosity
python tests/run_export_import_tests.py --verbose --categories unit

# Run specific test with debugging
pytest test_export_service.py::TestProjectExportService::test_export_project_success -v -s
```

## 📝 Test Development

### Adding New Tests

1. **Unit Tests**: Add to appropriate `test_*.py` file
2. **Integration Tests**: Add to `integration/` directory
3. **Performance Tests**: Add to `performance/` directory
4. **Scenarios**: Add to `scenarios/` directory

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`
- Async tests: Use `@pytest.mark.asyncio`

### Mock Patterns

```python
# Mock Supabase responses
mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [test_data]

# Mock service methods
with patch.object(service, 'method_name') as mock_method:
    mock_method.return_value = expected_result
```

## 🎯 Test Quality Metrics

### Coverage Targets
- **Unit Tests**: > 95% line coverage
- **Integration Tests**: > 90% feature coverage
- **API Tests**: 100% endpoint coverage
- **Error Handling**: 100% error path coverage

### Test Reliability
- All tests must be deterministic
- No external dependencies (mocked)
- Proper cleanup in teardown methods
- Isolated test execution

## 🔄 Continuous Integration

### Pre-commit Hooks
```bash
# Run quick tests before commit
python tests/run_export_import_tests.py --quick
```

### CI Pipeline Integration
```yaml
# Example GitHub Actions step
- name: Run Export/Import Tests
  run: |
    python tests/run_export_import_tests.py --all --coverage
    python tests/run_export_import_tests.py --performance
```

## 📚 Additional Resources

- **Export Format Specification**: `docs/export-format-specification.md`
- **API Documentation**: `docs/api/export-import-endpoints.md`
- **Service Documentation**: `docs/services/export-import-services.md`
- **MCP Tools Guide**: `docs/mcp/export-import-tools.md`

---

**Note**: This testing suite ensures the reliability, performance, and data integrity of the Archon export/import system through comprehensive automated testing across all functionality areas.
