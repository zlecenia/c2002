"""
E2E tests for module pages and static files
"""

import pytest
import requests


def test_homepage_loads(base_url):
    """Test that homepage loads successfully"""
    response = requests.get(base_url)
    assert response.status_code == 200
    assert "Fleet Management" in response.text


def test_api_docs_loads(base_url):
    """Test that API documentation loads"""
    response = requests.get(f"{base_url}/docs")
    assert response.status_code == 200


def test_connect_plus_plus_page(base_url):
    """Test Connect++ module page loads"""
    response = requests.get(f"{base_url}/connect-plus-plus")
    assert response.status_code == 200
    assert "Connect++" in response.text


def test_connect_display_page(base_url):
    """Test Connect Display module page loads"""
    response = requests.get(f"{base_url}/connect-display")
    assert response.status_code == 200
    assert "Connect Display" in response.text


def test_connect_manager_page(base_url):
    """Test Connect Manager module page loads"""
    response = requests.get(f"{base_url}/connect-manager")
    assert response.status_code == 200
    assert "Connect Manager" in response.text


def test_fleet_data_manager_page(base_url):
    """Test Fleet Data Manager module page loads"""
    response = requests.get(f"{base_url}/fleet-data-manager")
    assert response.status_code == 200
    assert "Fleet Data Manager" in response.text


def test_fleet_config_manager_page(base_url):
    """Test Fleet Config Manager module page loads"""
    response = requests.get(f"{base_url}/fleet-config-manager")
    assert response.status_code == 200
    assert "Fleet Config Manager" in response.text


def test_fleet_software_manager_page(base_url):
    """Test Fleet Software Manager module page loads"""
    response = requests.get(f"{base_url}/fleet-software-manager")
    assert response.status_code == 200
    assert "Fleet Software Manager" in response.text


def test_fleet_workshop_manager_page(base_url):
    """Test Fleet Workshop Manager module page loads"""
    response = requests.get(f"{base_url}/fleet-workshop-manager")
    assert response.status_code == 200
    assert "Fleet Workshop Manager" in response.text


def test_modular_fsm_page_loads(base_url):
    """Test modular FSM page loads"""
    response = requests.get(f"{base_url}/fsm-modular")
    assert response.status_code == 200
    assert "Fleet Software Manager" in response.text
    assert "Modular Version" in response.text


def test_common_css_loads(base_url):
    """Test common CSS file loads from modules"""
    response = requests.get(f"{base_url}/modules/common/static/css/base.css")
    assert response.status_code == 200
    assert "text/css" in response.headers.get("content-type", "")


def test_common_auth_js_loads(base_url):
    """Test common auth.js file loads"""
    response = requests.get(f"{base_url}/modules/common/static/js/auth.js")
    assert response.status_code == 200
    assert "javascript" in response.headers.get("content-type", "").lower()


def test_common_utils_js_loads(base_url):
    """Test common utils.js file loads"""
    response = requests.get(f"{base_url}/modules/common/static/js/utils.js")
    assert response.status_code == 200
    assert "javascript" in response.headers.get("content-type", "").lower()


def test_fsm_css_loads(base_url):
    """Test FSM module CSS loads"""
    response = requests.get(f"{base_url}/modules/fsm/frontend/fsm.css")
    assert response.status_code == 200
    assert "text/css" in response.headers.get("content-type", "")


def test_fsm_js_loads(base_url):
    """Test FSM module JavaScript loads"""
    response = requests.get(f"{base_url}/modules/fsm/frontend/fsm.js")
    assert response.status_code == 200
    assert "javascript" in response.headers.get("content-type", "").lower()


def test_404_for_nonexistent_module(base_url):
    """Test 404 for non-existent module"""
    response = requests.get(f"{base_url}/nonexistent-module")
    assert response.status_code == 404
