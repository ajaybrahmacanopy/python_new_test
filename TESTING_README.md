# Testing & CI/CD

This project includes comprehensive testing and continuous integration.

## 🧪 Running Tests Locally

### Install Development Dependencies

```bash
pip install -r requirements.txt
```

This includes:

- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `flake8` - Linting
- `black` - Code formatting
- `httpx` - HTTP testing for FastAPI

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run specific test
pytest tests/test_api.py::test_health_endpoint
```

### Run Linting

```bash
# Check with flake8
flake8 src/ api.py main.py example.py

# Check formatting with black
black --check src/ api.py main.py example.py

# Auto-format with black
black src/ api.py main.py example.py
```

## 📊 Test Structure

```
tests/
├── __init__.py
├── test_models.py      # Pydantic model tests
├── test_utils.py       # Utility function tests
└── test_api.py         # FastAPI endpoint tests
```

### Test Coverage

Current tests cover:

- ✅ Pydantic model validation
- ✅ Utility functions (tokens, diagrams, relevance)
- ✅ API endpoints (health, chat/answer)
- ✅ Error handling
- ✅ Edge cases

## 🔄 GitHub Actions CI/CD

### Workflows

The project includes automated CI/CD via GitHub Actions:

#### 1. **Lint Job**

- Runs `flake8` for code quality
- Runs `black` for code formatting
- Triggers on: Push & Pull Requests

#### 2. **Test Job**

- Installs system dependencies (poppler, tesseract)
- Runs pytest with coverage
- Uploads coverage to Codecov
- Triggers on: Push & Pull Requests

#### 3. **Docker Build Job**

- Builds Docker image
- Tests import successful
- Caches layers for speed
- Triggers on: Push & Pull Requests
- Requires: Lint & Test jobs to pass

### Workflow File

Location: `.github/workflows/ci.yml`

```yaml
# Automatically runs on:
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
```

## 📈 Coverage Reports

### Local Coverage

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open report
open htmlcov/index.html
```

### CI Coverage

Coverage reports are automatically uploaded to Codecov on every CI run.

## ✅ Pre-commit Checklist

Before committing, run:

```bash
# 1. Format code
black src/ api.py main.py example.py tests/

# 2. Run linter
flake8 src/ api.py main.py example.py

# 3. Run tests
pytest --cov=src

# 4. Check if Docker builds
docker build -t rag-api:test .
```

## 🐛 Debugging Failed Tests

### Test fails locally

```bash
# Run with verbose output
pytest -v

# Run with print statements visible
pytest -s

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l
```

### CI fails on GitHub

1. Check the "Actions" tab in your repository
2. Click on the failed workflow
3. Expand the failed step to see logs
4. Common issues:
   - Missing dependencies
   - Environment variable issues
   - System dependency problems

## 🔧 Configuration Files

- `pytest.ini` - Pytest configuration
- `.flake8` - Flake8 linting rules
- `.github/workflows/ci.yml` - CI/CD pipeline

## 📝 Writing New Tests

### Test Template

```python
"""Test module description"""
import pytest
from src.your_module import your_function


def test_your_function_success():
    """Test successful case"""
    result = your_function("input")
    assert result == "expected"


def test_your_function_error():
    """Test error handling"""
    with pytest.raises(ValueError):
        your_function("bad_input")
```

### Mocking External Services

```python
from unittest.mock import patch, MagicMock

@patch('src.module.external_api_call')
def test_with_mock(mock_api):
    """Test with mocked external call"""
    mock_api.return_value = "mocked response"
    result = function_that_calls_api()
    assert result == "expected"
```

## 🎯 Best Practices

1. ✅ **Write tests first** (TDD approach)
2. ✅ **Keep tests simple** - One concept per test
3. ✅ **Use descriptive names** - `test_function_does_x_when_y`
4. ✅ **Mock external services** - Don't call real APIs in tests
5. ✅ **Test edge cases** - Empty strings, None, errors
6. ✅ **Maintain test coverage** - Aim for >80%

## 🚀 Next Steps

- [ ] Add integration tests
- [ ] Add performance tests
- [ ] Set up branch protection rules
- [ ] Add test coverage badge to README
- [ ] Set up automated dependency updates
