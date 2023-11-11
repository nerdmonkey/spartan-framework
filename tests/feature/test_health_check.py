from fastapi import status


def test_health_check(client):
    # Given an operational web service

    # When the health check endpoint is requested
    response = client.get("/api/health-check")

    # Then the response should have a 200 OK status
    assert response.status_code == status.HTTP_200_OK
    # And the response body should confirm the service is OK
    assert response.json() == {"message": "OK"}
