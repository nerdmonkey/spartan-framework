from fastapi import status


# Test case for creating a user
def test_create_user(client):
    payload = {
        "username": "testuseranother",
        "email": "testuseranother@example.com",
        "password": "test1password",
    }
    response = client.post("/api/users", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['data']["username"] == "testuseranother"
    assert "email" in data['data']  # Verify that the email is also returned



# Test case for retrieving a list of users
def test_read_users(client):
    response = client.get("/api/users")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data['data'], list)  # Confirm that it's a list
    assert all("username" in user for user in data['data'])  # Check each user has a username



# Test case for retrieving a single user
def test_read_user(client):
    user_id = 1  # This should be replaced with a dynamic user creation and fetching of its ID
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['data']["id"] == user_id
    assert "username" in data['data']  # Verify that the username is in the response



# Test case for updating a user's information
def test_update_user(client):
    user_id = 1  # Replace with dynamic user creation
    payload = {
        "username": "updateduser",
        "email": "updateduser@example.com",
        "password": "updatedpassword",
    }
    response = client.put(f"/api/users/{user_id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["data"]["username"] == "updateduser"
    assert "email" in data["data"]  # Check for email in the response



# Test case for deleting a user
def test_delete_user(client):
    user_id = 1  # Replace with dynamic user creation
    response = client.delete(f"/api/users/{user_id}")
    assert response.status_code == status.HTTP_200_OK
