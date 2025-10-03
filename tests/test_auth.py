"""
E2E tests for Authentication endpoints
"""

import pytest
import requests


def test_login_success(api_url):
    """Test successful login with valid credentials"""
    response = requests.post(
        f"{api_url}/auth/login", data={"username": "maker1", "password": "pass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "maker1"
    assert data["user"]["role"] == "maker"


def test_login_invalid_credentials(api_url):
    """Test login with invalid credentials"""
    response = requests.post(
        f"{api_url}/auth/login", data={"username": "invalid", "password": "wrong"}
    )
    assert response.status_code == 401


def test_get_current_user(api_url, auth_headers):
    """Test getting current user information"""
    response = requests.get(f"{api_url}/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "maker1"
    assert "roles" in data


def test_role_switching(api_url, auth_token):
    """Test role switching for multi-role user"""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Switch to manager role
    response = requests.post(
        f"{api_url}/auth/switch-role", headers=headers, json={"new_role": "manager"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["active_role"] == "manager"

    # Verify new token works
    new_token = data["access_token"]
    new_headers = {"Authorization": f"Bearer {new_token}"}
    me_response = requests.get(f"{api_url}/auth/me", headers=new_headers)
    assert me_response.status_code == 200


def test_qr_code_login_invalid(api_url):
    """Test QR code login with invalid code"""
    response = requests.post(f"{api_url}/auth/login/qr", json={"qr_code": "invalid_qr_code"})
    assert response.status_code == 401


def test_unauthorized_access(api_url):
    """Test accessing protected endpoint without token"""
    response = requests.get(f"{api_url}/auth/me")
    assert response.status_code == 401
