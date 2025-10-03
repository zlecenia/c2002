"""
E2E tests for Fleet Config Manager module
"""

import pytest
import requests


def test_list_system_configs(api_url, configurator_token):
    """Test listing system configurations"""
    headers = {"Authorization": f"Bearer {configurator_token}"}
    response = requests.get(f"{api_url}/fleet-config/system-configs", headers=headers)
    assert response.status_code == 200
    configs = response.json()
    assert isinstance(configs, list)


def test_create_system_config(api_url, configurator_token):
    """Test creating a system configuration"""
    headers = {"Authorization": f"Bearer {configurator_token}"}
    config_data = {
        "config_key": f"test_config_{pytest.test_run_id}",
        "config_value": {"setting1": "value1", "setting2": 123},
        "description": "E2E test configuration",
    }
    response = requests.post(
        f"{api_url}/fleet-config/system-configs", headers=headers, json=config_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["config_key"] == config_data["config_key"]


def test_update_system_config(api_url, configurator_token):
    """Test updating a system configuration"""
    headers = {"Authorization": f"Bearer {configurator_token}"}

    # Create config
    config_data = {
        "config_key": f"test_update_config_{pytest.test_run_id}",
        "config_value": {"original": "value"},
        "description": "Original",
    }
    create_response = requests.post(
        f"{api_url}/fleet-config/system-configs", headers=headers, json=config_data
    )
    config_id = create_response.json()["id"]

    # Update config
    update_data = {"config_value": {"updated": "new_value"}, "description": "Updated"}
    response = requests.put(
        f"{api_url}/fleet-config/system-configs/{config_id}", headers=headers, json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated"


def test_delete_system_config(api_url, configurator_token):
    """Test deleting a system configuration"""
    headers = {"Authorization": f"Bearer {configurator_token}"}

    # Create config
    config_data = {
        "config_key": f"test_delete_config_{pytest.test_run_id}",
        "config_value": {"to": "delete"},
        "description": "To be deleted",
    }
    create_response = requests.post(
        f"{api_url}/fleet-config/system-configs", headers=headers, json=config_data
    )
    config_id = create_response.json()["id"]

    # Delete config
    response = requests.delete(
        f"{api_url}/fleet-config/system-configs/{config_id}", headers=headers
    )
    assert response.status_code == 200


def test_list_json_templates(api_url, configurator_token):
    """Test listing JSON templates"""
    headers = {"Authorization": f"Bearer {configurator_token}"}
    response = requests.get(f"{api_url}/fleet-config/json-templates", headers=headers)
    assert response.status_code == 200
    templates = response.json()
    assert isinstance(templates, list)


def test_filter_json_templates_by_type(api_url, configurator_token):
    """Test filtering JSON templates by type"""
    headers = {"Authorization": f"Bearer {configurator_token}"}
    response = requests.get(
        f"{api_url}/fleet-config/json-templates?type=test_flow", headers=headers
    )
    assert response.status_code == 200
    templates = response.json()
    for template in templates:
        assert template["template_type"] == "test_flow"


def test_create_json_template(api_url, configurator_token):
    """Test creating a JSON template"""
    headers = {"Authorization": f"Bearer {configurator_token}"}
    template_data = {
        "name": f"Test Template E2E {pytest.test_run_id}",
        "template_type": "device_config",
        "category": "test_category",
        "default_values": {"param1": "value1"},
        "schema": {"type": "object"},
        "description": "E2E test template",
    }
    response = requests.post(
        f"{api_url}/fleet-config/json-templates", headers=headers, json=template_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == template_data["name"]


def test_backup_endpoint(api_url, configurator_token):
    """Test backup creation endpoint"""
    headers = {"Authorization": f"Bearer {configurator_token}"}
    backup_data = {
        "backup_name": f"E2E_Backup_{pytest.test_run_id}",
        "backup_data": {"system_configs": [], "device_configs": []},
    }
    response = requests.post(f"{api_url}/fleet-config/backup", headers=headers, json=backup_data)
    assert response.status_code == 200
    data = response.json()
    assert "backup_id" in data or "message" in data
