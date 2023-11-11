from fastapi import status


# Test case for creating a user
def test_create_user(client):
    # Given: the payload for a new user
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
    }

    # When: the client makes a POST request to create a user
    response = client.post("/api/users", json=payload)

    # Then: the server should respond with a 201 status code
    # and the response body should contain the username of the new user
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["username"] == "testuser"


# Test case for retrieving a list of users
def test_read_users(client):
    # Given: an existing set of users

    # When: the client makes a GET request to fetch the list of users
    response = client.get("/api/users")

    # Then: the server should respond with a 200 status code
    # and the response body should be a list
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


# Test case for retrieving a single user
def test_read_user(client):
    # Given: a user with a known ID
    user_id = 1  # Replace with a setup to create a user and get the ID

    # When: the client makes a GET request to fetch the user details
    response = client.get(f"/api/users/{user_id}")

    # Then: the server should respond with a 200 status code
    # and the response body should contain the details of the user
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == user_id


# Test case for updating a user's information
def test_update_user(client):
    # Given: a user with a known ID and the payload for updating the user
    user_id = 1  # Replace with a setup to create a user and get the ID
    payload = {
        "username": "updateduser",
        "email": "updateduser@example.com",
        "password": "updatedpassword",
    }

    # When: the client makes a PUT request to update the user's information
    response = client.put(f"/api/users/{user_id}", json=payload)

    # Then: the server should respond with a 200 status code
    # and the response body should reflect the updated user information
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "updateduser"


# Test case for deleting a user
def test_delete_user(client):
    # Given: a user with a known ID
    user_id = 1  # Replace with a setup to create a user and ensure they exist

    # When: the client makes a DELETE request to remove the user
    response = client.delete(f"/api/users/{user_id}")

    # Then: the server should respond with a 204 status code indicating successful deletion
    assert response.status_code == status.HTTP_204_NO_CONTENT
