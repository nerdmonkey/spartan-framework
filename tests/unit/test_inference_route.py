import pytest
from unittest.mock import patch, Mock

def test_inference_endpoint(test_client):
    """Test the inference endpoint returns expected response"""
    # Create a mock logger before patching
    mock_logger = Mock()

    # Patch the logger instance directly
    with patch('routes.inference.logger', mock_logger):
        response = test_client.get("/api/inference")

        assert response.status_code == 200
        assert response.json() == {
            "message": "OK",
            "status_code": 200
        }
        mock_logger.info.assert_called_once_with("Inference endpoint called")

def test_inference_logging(test_client):
    """Test that the inference endpoint logs the expected message"""
    # Create a mock logger before patching
    mock_logger = Mock()

    # Patch the logger instance directly
    with patch('routes.inference.logger', mock_logger):
        response = test_client.get("/api/inference")

        # Verify the logger was called with the expected message
        mock_logger.info.assert_called_once_with("Inference endpoint called")

        # Verify the response is still correct
        assert response.status_code == 200
        assert response.json() == {
            "message": "OK",
            "status_code": 200
        }

def test_inference_wrong_method(test_client):
    """Test that using incorrect HTTP method returns 405"""
    mock_logger = Mock()
    with patch('routes.inference.logger', mock_logger):
        response = test_client.post("/api/inference")
        assert response.status_code == 405

def test_inference_wrong_path(test_client):
    """Test that incorrect path returns 404"""
    mock_logger = Mock()
    with patch('routes.inference.logger', mock_logger):
        response = test_client.get("/api/inference/wrong")
        assert response.status_code == 404
