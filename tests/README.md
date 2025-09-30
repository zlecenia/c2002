# E2E Test Suite - Fleet Management System

## Overview

This directory contains end-to-end (E2E) tests for the Fleet Management System. The tests verify the functionality of all 7 modules and their API endpoints.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                         # Pytest fixtures and configuration
├── test_auth.py                        # Authentication tests
├── test_fleet_data_manager.py          # Fleet Data Manager module tests
├── test_fleet_software_manager.py      # Fleet Software Manager module tests
├── test_fleet_config_manager.py        # Fleet Config Manager module tests
├── test_connect_manager.py             # Connect Manager (scenarios) tests
├── test_modules.py                     # Module page loading tests
└── README.md                           # This file
```

## Test Coverage

### Authentication (`test_auth.py`)
- ✅ Successful login with valid credentials
- ✅ Login with invalid credentials
- ✅ Get current user information
- ✅ Role switching for multi-role users
- ✅ QR code login (invalid code test)
- ✅ Unauthorized access protection

### Fleet Data Manager (`test_fleet_data_manager.py`)
- ✅ Get dashboard statistics
- ✅ List devices
- ✅ Create device
- ✅ Update device
- ✅ List customers
- ✅ Create customer
- ✅ Device filtering by type
- ✅ Unauthorized access prevention

### Fleet Software Manager (`test_fleet_software_manager.py`)
- ✅ Get software dashboard statistics
- ✅ List software packages
- ✅ Create software
- ✅ Update software
- ✅ Delete software
- ✅ Get software versions
- ✅ Create software version
- ✅ List installations
- ✅ Modular FSM page loading

### Fleet Config Manager (`test_fleet_config_manager.py`)
- ✅ List system configurations
- ✅ Create system configuration
- ✅ Update system configuration
- ✅ Delete system configuration
- ✅ List JSON templates
- ✅ Filter JSON templates by type
- ✅ Create JSON template
- ✅ Backup creation

### Connect Manager (`test_connect_manager.py`)
- ✅ List test scenarios
- ✅ Create scenario
- ✅ Get specific scenario
- ✅ Update scenario
- ✅ Delete scenario

### Module Pages (`test_modules.py`)
- ✅ Homepage loading
- ✅ API documentation loading
- ✅ All 7 module pages loading
- ✅ Modular FSM page loading
- ✅ Common CSS loading (`/modules/common/static/css/common.css`)
- ✅ Common JS loading (`auth.js`, `utils.js`)
- ✅ FSM module assets loading (`fsm.css`, `fsm.js`)
- ✅ 404 error handling

## Prerequisites

1. **Python 3.11+**
2. **pytest** - Test framework
3. **requests** - HTTP library

Install dependencies:
```bash
pip install pytest requests
```

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_auth.py
```

### Run specific test
```bash
pytest tests/test_auth.py::test_login_success -v
```

### Run tests matching a pattern
```bash
pytest tests/ -k "auth" -v
```

### Generate HTML report
```bash
pytest tests/ --html=test_report.html --self-contained-html
```

## Test Fixtures

Located in `conftest.py`:

- `base_url` - Base URL for the application
- `api_url` - API v1 base URL
- `auth_token` - Authentication token for maker1 user
- `auth_headers` - Headers with authentication token
- `operator_token` - Token for operator1 user
- `manager_token` - Token for manager1 user
- `configurator_token` - Token for configurator user
- `admin_token` - Token for admin user

## Test Users

The tests use the following default users:

| Username | Password | Role | Purpose |
|----------|----------|------|---------|
| maker1 | pass | maker (all roles) | Software management, role switching |
| manager1 | pass | manager | Device and customer management |
| configurator | pass | configurator | System configuration |
| admin | pass | superuser | Test scenarios |
| operator1 | pass | operator | Basic operations |

## Notes

- Tests require the API server to be running on `http://localhost:5000`
- Tests use unique identifiers (`pytest.test_run_id`) to avoid conflicts
- Some tests create data that may remain in the database
- Tests verify both success and error cases
- Role-based access control is tested with unauthorized access attempts

## Continuous Integration

To integrate with CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Run E2E Tests
  run: |
    python main.py &
    sleep 5
    pytest tests/ -v
```

## Maintenance

- Add new tests when adding new features or endpoints
- Update fixtures if authentication mechanism changes
- Keep test data unique to avoid conflicts
- Clean up test data when possible

---

**Last Updated:** September 30, 2025  
**Test Count:** 50+ tests across 6 test files
