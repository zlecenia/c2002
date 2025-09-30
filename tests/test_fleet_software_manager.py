"""
E2E tests for Fleet Software Manager module
"""
import pytest
import requests

def test_get_software_dashboard_stats(api_url, auth_headers):
    """Test getting software dashboard statistics"""
    response = requests.get(
        f"{api_url}/fleet-software/dashboard/stats",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_software" in data
    assert "total_versions" in data
    assert "total_installations" in data

def test_list_software(api_url, auth_headers):
    """Test listing all software packages"""
    response = requests.get(
        f"{api_url}/fleet-software/software",
        headers=auth_headers
    )
    assert response.status_code == 200
    software = response.json()
    assert isinstance(software, list)

def test_create_software(api_url, auth_headers):
    """Test creating a new software package"""
    software_data = {
        "name": f"Test Software E2E {pytest.test_run_id}",
        "description": "E2E test software package",
        "current_version": "1.0.0"
    }
    response = requests.post(
        f"{api_url}/fleet-software/software",
        headers=auth_headers,
        json=software_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == software_data["name"]
    return data["id"]

def test_update_software(api_url, auth_headers):
    """Test updating a software package"""
    # First create software
    software_data = {
        "name": f"Test Update Software {pytest.test_run_id}",
        "description": "Original description",
        "current_version": "1.0.0"
    }
    create_response = requests.post(
        f"{api_url}/fleet-software/software",
        headers=auth_headers,
        json=software_data
    )
    software_id = create_response.json()["id"]
    
    # Update the software
    update_data = {
        "description": "Updated description",
        "current_version": "1.1.0"
    }
    response = requests.put(
        f"{api_url}/fleet-software/software/{software_id}",
        headers=auth_headers,
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description"

def test_delete_software(api_url, auth_headers):
    """Test deleting a software package"""
    # First create software
    software_data = {
        "name": f"Test Delete Software {pytest.test_run_id}",
        "description": "To be deleted",
        "current_version": "1.0.0"
    }
    create_response = requests.post(
        f"{api_url}/fleet-software/software",
        headers=auth_headers,
        json=software_data
    )
    software_id = create_response.json()["id"]
    
    # Delete the software
    response = requests.delete(
        f"{api_url}/fleet-software/software/{software_id}",
        headers=auth_headers
    )
    assert response.status_code == 200

def test_get_software_versions(api_url, auth_headers):
    """Test getting versions for a software package"""
    # First create software
    software_data = {
        "name": f"Test Version Software {pytest.test_run_id}",
        "description": "For version testing",
        "current_version": "1.0.0"
    }
    create_response = requests.post(
        f"{api_url}/fleet-software/software",
        headers=auth_headers,
        json=software_data
    )
    software_id = create_response.json()["id"]
    
    # Get versions
    response = requests.get(
        f"{api_url}/fleet-software/software/{software_id}/versions",
        headers=auth_headers
    )
    assert response.status_code == 200
    versions = response.json()
    assert isinstance(versions, list)

def test_create_software_version(api_url, auth_headers):
    """Test creating a new version for software"""
    # First create software
    software_data = {
        "name": f"Test Version Create {pytest.test_run_id}",
        "description": "For version creation",
        "current_version": "1.0.0"
    }
    create_response = requests.post(
        f"{api_url}/fleet-software/software",
        headers=auth_headers,
        json=software_data
    )
    software_id = create_response.json()["id"]
    
    # Create a version
    version_data = {
        "version_number": "2.0.0",
        "release_notes": "Major update",
        "is_stable": True
    }
    response = requests.post(
        f"{api_url}/fleet-software/software/{software_id}/versions",
        headers=auth_headers,
        json=version_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["version_number"] == "2.0.0"

def test_list_installations(api_url, auth_headers):
    """Test listing all software installations"""
    response = requests.get(
        f"{api_url}/fleet-software/installations",
        headers=auth_headers
    )
    assert response.status_code == 200
    installations = response.json()
    assert isinstance(installations, list)

def test_modular_fsm_page_loads(base_url):
    """Test that modular FSM page loads successfully"""
    response = requests.get(f"{base_url}/fsm-modular")
    assert response.status_code == 200
    assert "Fleet Software Manager" in response.text
    assert "Modular Version" in response.text
