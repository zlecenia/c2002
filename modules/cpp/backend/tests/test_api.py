"""
API Tests for Connect++ (CPP)
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and info endpoints"""
    
    def test_health_check(self):
        """Test /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["module"] == "Connect++ (CPP)"
        assert data["port"] == 8080
        assert data["version"] == "1.0.0"
    
    def test_root_endpoint(self):
        """Test / endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Connect++ (CPP) API"
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"


class TestSystemEndpoints:
    """Test system endpoints"""
    
    def test_system_start(self):
        """Test POST /api/v1/tests/system/start"""
        response = client.post("/api/v1/tests/system/start?device_ip=192.168.1.100")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "starting"
        assert data["progress"] == 0
        assert data["estimated_time"] == 10
        assert data["device_ip"] == "192.168.1.100"
    
    def test_system_diagnostic(self):
        """Test POST /api/v1/tests/system/diagnostic"""
        response = client.post("/api/v1/tests/system/diagnostic")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "results" in data
        assert "pressure_sensors" in data["results"]
        assert "pneumatic" in data["results"]
        assert "communication" in data["results"]
        assert "hardware" in data["results"]


class TestTestEndpoints:
    """Test test session endpoints"""
    
    def test_initialize_test_unauthorized(self):
        """Test POST /api/v1/tests/initialize without auth"""
        test_data = {
            "device_kind_id": 1,
            "device_type_id": 1,
            "test_kind_id": 3,
            "scenario_id": 1,
            "device_serial": "G1-2024-001234"
        }
        response = client.post("/api/v1/tests/initialize", json=test_data)
        # Should return 401 or 403 without proper auth token
        assert response.status_code in [401, 403]
    
    def test_get_test_session_not_found(self):
        """Test GET /api/v1/tests/{id} with non-existent ID"""
        # Mock auth header (in real app this would be a valid JWT)
        headers = {"Authorization": "Bearer mock-token"}
        response = client.get("/api/v1/tests/TEST-9999-XXXXX", headers=headers)
        assert response.status_code in [401, 403, 404]


class TestDocumentation:
    """Test API documentation endpoints"""
    
    def test_openapi_docs(self):
        """Test /docs endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert b"FastAPI" in response.content or b"Swagger" in response.content
    
    def test_openapi_json(self):
        """Test /openapi.json endpoint"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data


# Test data validation
class TestDataValidation:
    """Test request data validation"""
    
    def test_system_start_missing_device_ip(self):
        """Test system start without device_ip"""
        response = client.post("/api/v1/tests/system/start")
        assert response.status_code == 422  # Validation error
    
    def test_initialize_test_invalid_data(self):
        """Test initialize with invalid data"""
        invalid_data = {
            "device_kind_id": "not-a-number",
            "device_serial": ""
        }
        response = client.post("/api/v1/tests/initialize", json=invalid_data)
        assert response.status_code in [401, 403, 422]


# Performance tests
class TestPerformance:
    """Test API performance"""
    
    def test_health_response_time(self):
        """Test health endpoint response time"""
        import time
        start = time.time()
        response = client.get("/health")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 1.0  # Should respond in less than 1 second


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
