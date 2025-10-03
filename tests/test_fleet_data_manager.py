"""
E2E tests for Fleet Data Manager module
"""

import pytest
import requests
import time


def test_get_dashboard_stats(api_url, manager_token):
    """Test getting fleet dashboard statistics"""
    headers = {"Authorization": f"Bearer {manager_token}"}
    response = requests.get(f"{api_url}/fleet-data/dashboard", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_devices" in data
    assert "active_devices" in data
    assert "total_customers" in data


def test_list_devices(api_url, manager_token):
    """Test listing all devices"""
    headers = {"Authorization": f"Bearer {manager_token}"}
    response = requests.get(f"{api_url}/fleet-data/devices", headers=headers)
    assert response.status_code == 200
    devices = response.json()
    assert isinstance(devices, list)


def test_create_device(api_url, manager_token):
    """Test creating a new device"""
    headers = {"Authorization": f"Bearer {manager_token}"}
    device_data = {
        "device_number": f"DEV-E2E-{int(time.time())}",
        "serial_number": f"TEST-E2E-{int(time.time())}",
        "device_type": "mask_tester",
        "status": "active",
        "customer_id": 1,
    }
    response = requests.post(f"{api_url}/fleet-data/devices", headers=headers, json=device_data)
    assert response.status_code == 200
    data = response.json()
    assert data["serial_number"] == device_data["serial_number"]
    assert "id" in data
    assert isinstance(data["id"], int)


def test_update_device(api_url, manager_token):
    """Test updating a device"""
    headers = {"Authorization": f"Bearer {manager_token}"}

    # First create a device
    device_data = {
        "device_number": f"DEV-UPDATE-{int(time.time())}",
        "serial_number": f"TEST-UPDATE-{int(time.time())}",
        "device_type": "mask_tester",
        "status": "active",
    }
    create_response = requests.post(
        f"{api_url}/fleet-data/devices", headers=headers, json=device_data
    )
    device_id = create_response.json()["id"]

    # Update the device
    update_data = {"status": "maintenance"}
    response = requests.put(
        f"{api_url}/fleet-data/devices/{device_id}", headers=headers, json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "maintenance"


def test_list_customers(api_url, manager_token):
    """Test listing all customers"""
    headers = {"Authorization": f"Bearer {manager_token}"}
    response = requests.get(f"{api_url}/fleet-data/customers", headers=headers)
    assert response.status_code == 200
    customers = response.json()
    assert isinstance(customers, list)


def test_create_customer(api_url, manager_token):
    """Test creating a new customer"""
    headers = {"Authorization": f"Bearer {manager_token}"}
    customer_data = {
        "name": f"Test Customer E2E {int(time.time())}",
        "contact_info": {"email": "test@example.com", "phone": "+48 123 456 789"},
    }
    response = requests.post(f"{api_url}/fleet-data/customers", headers=headers, json=customer_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == customer_data["name"]


def test_device_filtering(api_url, manager_token):
    """Test device filtering by type"""
    headers = {"Authorization": f"Bearer {manager_token}"}
    response = requests.get(
        f"{api_url}/fleet-data/devices?device_type=mask_tester", headers=headers
    )
    assert response.status_code == 200
    devices = response.json()
    for device in devices:
        assert device["device_type"] == "mask_tester"


def test_unauthorized_fleet_data_access(api_url, operator_token):
    """Test that operator cannot access fleet data endpoints"""
    headers = {"Authorization": f"Bearer {operator_token}"}
    response = requests.get(f"{api_url}/fleet-data/devices", headers=headers)
    # Operator shouldn't have access to manager endpoints
    assert response.status_code in [401, 403]
