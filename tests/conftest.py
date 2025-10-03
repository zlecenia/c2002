import pytest
import requests
from typing import Dict, Optional
import time
import random

BASE_URL = "http://localhost:5000"
API_V1 = f"{BASE_URL}/api/v1"

# Create a unique test run ID for the entire test session
pytest.test_run_id = int(time.time() * 1000) + random.randint(1000, 9999)


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the application"""
    return BASE_URL


@pytest.fixture(scope="session")
def api_url():
    """API v1 base URL"""
    return API_V1


@pytest.fixture(scope="function")
def auth_token():
    """Get authentication token for maker1 user"""
    response = requests.post(
        f"{API_V1}/auth/login", data={"username": "maker1", "password": "pass"}
    )
    assert response.status_code == 200
    data = response.json()
    return data["access_token"]


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    """Get headers with authentication token"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def operator_token():
    """Get authentication token for operator1 user"""
    response = requests.post(
        f"{API_V1}/auth/login", data={"username": "operator1", "password": "pass"}
    )
    assert response.status_code == 200
    data = response.json()
    return data["access_token"]


@pytest.fixture(scope="function")
def manager_token():
    """Get authentication token for manager1 user"""
    response = requests.post(
        f"{API_V1}/auth/login", data={"username": "manager1", "password": "pass"}
    )
    assert response.status_code == 200
    data = response.json()
    return data["access_token"]


@pytest.fixture(scope="function")
def configurator_token():
    """Get authentication token for configurator user"""
    response = requests.post(
        f"{API_V1}/auth/login", data={"username": "configurator", "password": "pass"}
    )
    assert response.status_code == 200
    data = response.json()
    return data["access_token"]


@pytest.fixture(scope="function")
def admin_token():
    """Get authentication token for admin user"""
    response = requests.post(f"{API_V1}/auth/login", data={"username": "admin", "password": "pass"})
    assert response.status_code == 200
    data = response.json()
    return data["access_token"]
