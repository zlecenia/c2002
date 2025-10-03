"""
E2E tests for Connect Manager module (Test Scenarios)
"""

import pytest
import requests


def test_list_scenarios(api_url, admin_token):
    """Test listing all test scenarios"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{api_url}/scenarios/", headers=headers)
    assert response.status_code == 200
    scenarios = response.json()
    assert isinstance(scenarios, list)


def test_create_scenario(api_url, admin_token):
    """Test creating a new test scenario"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    scenario_data = {
        "name": f"E2E Test Scenario {pytest.test_run_id}",
        "device_type": "mask_tester",
        "test_flow": {
            "steps": [{"step": 1, "action": "initialize"}, {"step": 2, "action": "test"}]
        },
    }
    response = requests.post(f"{api_url}/scenarios/", headers=headers, json=scenario_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == scenario_data["name"]
    assert "id" in data
    assert isinstance(data["id"], int)


def test_get_scenario(api_url, admin_token):
    """Test getting a specific scenario"""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create scenario first
    scenario_data = {
        "name": f"E2E Get Scenario {pytest.test_run_id}",
        "device_type": "pressure_sensor",
        "test_flow": {"steps": []},
    }
    create_response = requests.post(f"{api_url}/scenarios/", headers=headers, json=scenario_data)
    scenario_id = create_response.json()["id"]

    # Get the scenario
    response = requests.get(f"{api_url}/scenarios/{scenario_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == scenario_id


def test_update_scenario(api_url, admin_token):
    """Test updating a test scenario"""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create scenario
    scenario_data = {
        "name": f"E2E Update Scenario {pytest.test_run_id}",
        "device_type": "mask_tester",
        "test_flow": {"steps": [{"step": 1}]},
    }
    create_response = requests.post(f"{api_url}/scenarios/", headers=headers, json=scenario_data)
    scenario_id = create_response.json()["id"]

    # Update scenario
    update_data = {
        "name": "Updated Scenario Name",
        "test_flow": {"steps": [{"step": 1}, {"step": 2}]},
    }
    response = requests.put(f"{api_url}/scenarios/{scenario_id}", headers=headers, json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Scenario Name"


def test_delete_scenario(api_url, admin_token):
    """Test deleting a test scenario"""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create scenario
    scenario_data = {
        "name": f"E2E Delete Scenario {pytest.test_run_id}",
        "device_type": "flow_meter",
        "test_flow": {"steps": []},
    }
    create_response = requests.post(f"{api_url}/scenarios/", headers=headers, json=scenario_data)
    scenario_id = create_response.json()["id"]

    # Delete scenario
    response = requests.delete(f"{api_url}/scenarios/{scenario_id}", headers=headers)
    assert response.status_code == 200
