# Chatbot Backend Testing Framework

A comprehensive testing framework for the chatbot backend services, built with pytest and designed for production-ready testing of AI, Data, and Personalization services.

## Overview

This testing framework provides:
- **Unit Tests**: Individual component testing
- **Integration Tests**: Service interaction testing
- **API Tests**: REST endpoint validation
- **Performance Tests**: Load and performance validation
- **Mock Services**: Isolated testing with mocked dependencies

## Project Structure

```
testing/
├── src/
│   └── testing_framework.py      # Core testing framework
├── tests/
│   ├── unit/                     # Unit tests
│   │   ├── ai/                   # AI service unit tests
│   │   ├── data/                 # Data service unit tests
│   │   └── personalization/      # Personalization service unit tests
│   ├── integration/              # Integration tests
│   ├── api/                      # API endpoint tests
│   ├── performance/              # Performance tests
│   ├── fixtures/                 # Test data fixtures
│   ├── data/                     # Test data files
│   └── utils/                    # Test utilities
├── conftest.py                   # Pytest configuration and fixtures
├── pytest.ini                    # Pytest settings
├── requirements.txt              # Test dependencies
├── .coveragerc                   # Coverage configuration
└── README.md                     # This file
```

## Quick Start

### Installation

```bash
cd chatbot-app/backend/testing
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m api
pytest -m performance

# Run service-specific tests
pytest -m ai
pytest -m data
pytest -m personalization

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/ai/test_nlp_processor.py

# Run tests with verbose output
pytest -v
```

### Test Configuration

Tests can be configured via environment variables:

```bash
# Set test environment
export TEST_ENVIRONMENT=integration

# Configure service URLs
export AI_SERVICE_URL=http://localhost:3007
export DATA_SERVICE_URL=http://localhost:3006
export PERSONALIZATION_SERVICE_URL=http://localhost:3005

# Enable/disable features
export TEST_COVERAGE=true
export TEST_MOCK_EXTERNAL=true
export TEST_PERFORMANCE=false
```

## Test Categories

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Focus on business logic validation

### Integration Tests
- Test service interactions
- Use real databases and services (in containers)
- Validate data flow between components

### API Tests
- Test REST endpoints
- Validate request/response formats
- Test authentication and authorization

### Performance Tests
- Load testing with locust
- Memory and CPU usage monitoring
- Response time validation

## Writing Tests

### Basic Test Structure

```python
import pytest
from testing_framework import BaseTestCase

class TestMyService(BaseTestCase):
    def test_my_function(self):
        # Setup
        input_data = {"key": "value"}

        # Execute
        result = my_service.process(input_data)

        # Assert
        assert result["status"] == "success"
        assert "data" in result
```

### Using Fixtures

```python
def test_with_fixtures(sample_user, mock_redis):
    # sample_user and mock_redis are provided by conftest.py
    result = user_service.create_user(sample_user)
    assert result["user_id"] == sample_user["user_id"]
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_function(async_api_test_case):
    result = await async_api_test_case.make_async_request("GET", "/health")
    assert result.status_code == 200
```

### Mocking Services

```python
def test_with_mocks(mock_services):
    # Mock AI service response
    mock_services["ai"].mock_response("/process", {"response": "mocked"})

    result = chat_service.process_message("hello")
    assert result["response"] == "mocked"
```

## Test Data Management

### Using Test Data Factory

```python
from tests.utils.test_helpers import TestDataFactory

def test_with_generated_data():
    user = TestDataFactory.generate_user_profile()
    conversation = TestDataFactory.generate_conversation(user["user_id"])

    assert user["user_id"] == conversation["user_id"]
```

### Loading Fixtures

```python
from tests.utils.test_helpers import TestFixtureLoader

def test_with_fixture():
    data = TestFixtureLoader.load_json_fixture("sample_user.json")
    assert data["name"] == "John Doe"
```

## Performance Testing

### Basic Performance Test

```python
def test_performance(performance_monitor):
    result, duration, memory = performance_monitor.measure_performance(
        my_function, arg1, arg2
    )

    assert duration < 1.0  # Less than 1 second
    assert memory < 50.0   # Less than 50MB
```

### Load Testing with Locust

```python
# performance/test_load.py
from locust import HttpUser, task

class ChatbotUser(HttpUser):
    @task
    def send_message(self):
        self.client.post("/process", json={
            "message": "Hello",
            "user_id": "test_user"
        })
```

## Coverage Reporting

Coverage reports are automatically generated:

```bash
# HTML report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser

# Terminal report
pytest --cov=src --cov-report=term-missing

# XML report for CI/CD
pytest --cov=src --cov-report=xml
```

## Best Practices

### Test Organization
- Group related tests in classes
- Use descriptive test method names
- Follow `test_*` naming convention

### Mocking Strategy
- Mock external dependencies (databases, APIs, file systems)
- Use realistic mock data
- Verify mock interactions when necessary

### Assertion Patterns
- Use specific assertions over generic ones
- Test both positive and negative cases
- Validate data structure and types

### Performance Guidelines
- Set realistic performance thresholds
- Monitor memory usage in long-running tests
- Use appropriate timeouts

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Backend Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        cd chatbot-app/backend/testing
        pip install -r requirements.txt
    - name: Run tests
      run: |
        cd chatbot-app/backend/testing
        pytest --cov=src --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure Python path includes `src/` directory
2. **Mock Failures**: Check mock setup and verify calls
3. **Async Test Issues**: Use `@pytest.mark.asyncio` decorator
4. **Coverage Issues**: Check `.coveragerc` configuration

### Debug Mode

```bash
# Run with debug output
pytest -v -s --tb=long

# Run specific test with debugging
pytest tests/unit/ai/test_nlp_processor.py::TestNLPProcessor::test_basic_processing -v -s
```

## Contributing

1. Follow existing test patterns
2. Add tests for new features
3. Update fixtures for new data requirements
4. Maintain test coverage above 80%
5. Run full test suite before committing

## License

This testing framework is part of the chatbot backend project.