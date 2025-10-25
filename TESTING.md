# Testing Guide

## Quick Start

### 1. Activate Virtual Environment
```bash
cd backend
source venv/bin/activate
```

### 2. Run All Tests
```bash
pytest
```

## Test Commands

### Run All Tests with Verbose Output
```bash
pytest -v
```

### Run Specific Test File
```bash
pytest tests/test_router.py
pytest tests/test_client_communication.py
pytest tests/test_legal_researcher.py
```

### Run Specific Test Class or Function
```bash
# Run a specific test class
pytest tests/test_router.py::TestBasicRouting -v

# Run a specific test function
pytest tests/test_router.py::TestBasicRouting::test_route_records_task -v
```

### Run Tests Matching a Pattern
```bash
# Run all tests with "communication" in the name
pytest -k "communication" -v

# Run all tests with "route" in the name
pytest -k "route" -v
```

### Run Tests with Coverage Report
```bash
# Simple coverage report
pytest --cov=. --cov-report=term

# HTML coverage report (opens in browser)
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### Run Tests and Show Print Statements
```bash
pytest -s
```

### Stop at First Failure
```bash
pytest -x
```

### Run Last Failed Tests Only
```bash
pytest --lf
```

### Run Tests in Parallel (faster)
```bash
pip install pytest-xdist
pytest -n auto
```

## Test Options Reference

| Option | Description |
|--------|-------------|
| `-v` or `--verbose` | More detailed output |
| `-s` | Show print statements |
| `-x` | Stop at first failure |
| `-k "pattern"` | Run tests matching pattern |
| `--lf` | Run last failed tests |
| `--ff` | Run failed tests first |
| `--tb=short` | Shorter traceback format |
| `--tb=no` | No traceback |
| `-m marker` | Run tests with specific marker |
| `--collect-only` | Show what tests would run |
| `-n auto` | Run tests in parallel (requires pytest-xdist) |

## Test Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── test_router.py              # Router routing tests
│   ├── test_client_communication.py # Client communication tests
│   └── test_legal_researcher.py    # Legal research tests
└── pytest.ini                       # Pytest configuration
```

## Current Test Results

All 8 tests passing:
- 4 routing tests (test_router.py)
- 2 client communication tests (test_client_communication.py)
- 2 legal research tests (test_legal_researcher.py)

## Writing New Tests

### Test File Template
```python
import pytest
from your_module import YourClass

@pytest.fixture
def your_fixture():
    """Create a test fixture"""
    return YourClass()

@pytest.mark.asyncio
async def test_async_function(your_fixture):
    """Test an async function"""
    result = await your_fixture.async_method()
    assert result == expected_value

def test_sync_function(your_fixture):
    """Test a sync function"""
    result = your_fixture.sync_method()
    assert result == expected_value
```

## Continuous Integration

To run tests automatically on commit, add this to your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    cd backend
    source venv/bin/activate
    pytest --cov=. --cov-report=xml
```

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError`, make sure:
1. You're in the `backend` directory
2. Virtual environment is activated
3. The `pytest.ini` file has `pythonpath = .`

### Async Test Errors
Make sure you have:
1. `pytest-asyncio` installed (latest version)
2. `@pytest.mark.asyncio` decorator on async test functions
3. `asyncio_mode = auto` in `pytest.ini`

### Version Conflicts
If you see pytest-asyncio errors, upgrade:
```bash
pip install --upgrade pytest pytest-asyncio
```

## Performance

Current test suite runs in ~0.31 seconds for all 8 tests.
