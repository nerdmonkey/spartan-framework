import pytest
from unittest.mock import patch, Mock

def test_health_check_endpoint(test_client):
    """Test the health check endpoint returns expected response"""
    # Create a mock logger before patching
    mock_logger = Mock()

    # Patch the logger instance directly
    with patch('routes.health.logger', mock_logger):
        response = test_client.get("/api/health")

        assert response.status_code == 200
        assert response.json() == {
            "message": "OK",
            "status_code": 200
        }
        mock_logger.info.assert_called_once_with("Health check endpoint called")

def test_health_check_logging(test_client):
    """Test that the health check endpoint logs the expected message"""
    # Create a mock logger before patching
    mock_logger = Mock()

    # Patch the logger instance directly
    with patch('routes.health.logger', mock_logger):
        response = test_client.get("/api/health")

        # Verify the logger was called with the expected message
        mock_logger.info.assert_called_once_with("Health check endpoint called")

        # Verify the response is still correct
        assert response.status_code == 200
        assert response.json() == {
            "message": "OK",
            "status_code": 200
        }

def test_health_check_wrong_method(test_client):
    """Test that using incorrect HTTP method returns 405"""
    mock_logger = Mock()
    with patch('routes.health.logger', mock_logger):
        response = test_client.post("/api/health")
        assert response.status_code == 405

def test_health_check_wrong_path(test_client):
    """Test that incorrect path returns 404"""
    mock_logger = Mock()
    with patch('routes.health.logger', mock_logger):
        response = test_client.get("/api/health/wrong")
        assert response.status_code == 404
