import uuid
import pytest

def test_register_success(client):
    """
    Validates that a new user registration succeeds.
    """
    username = f"user_{uuid.uuid4().hex[:6]}"
    email = f"{username}@gmail.com"
    payload = {
        "username": username,
        "email": email,
        "password": "validpassword123"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == username
    assert data["email"] == email
    assert "id" in data

def test_register_duplicate_username(client):
    """
    Validates that registering a duplicate username fails with 400.
    """
    username = f"dup_{uuid.uuid4().hex[:6]}"
    email1 = f"{username}_1@gmail.com"
    email2 = f"{username}_2@gmail.com"
    
    payload1 = {
        "username": username,
        "email": email1,
        "password": "password123"
    }
    response1 = client.post("/api/v1/auth/register", json=payload1)
    assert response1.status_code == 201
    
    payload2 = {
        "username": username,
        "email": email2,
        "password": "password123"
    }
    response2 = client.post("/api/v1/auth/register", json=payload2)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Username already taken"

def test_register_weak_password(client):
    """
    Validates that weak passwords (<8 characters) fail Pydantic validation with 422.
    """
    payload = {
        "username": f"user_{uuid.uuid4().hex[:6]}",
        "email": "test@gmail.com",
        "password": "abc"  # Less than 8 chars
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422

def test_login_success(client, test_user):
    """
    Validates login returns 200 and access_token.
    """
    payload = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    response = client.post("/api/v1/auth/login", data=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["username"] == test_user["username"]
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    """
    Validates login fails with 401 on wrong password.
    """
    payload = {
        "username": test_user["username"],
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", data=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"

def test_login_nonexistent_user(client):
    """
    Validates login fails with 401 on nonexistent user.
    """
    payload = {
        "username": "nonexistent_user_abc",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/login", data=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"

def test_me_with_valid_token(client, test_user, auth_headers):
    """
    Validates GET /me with active JWT returns current user info.
    """
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]

def test_me_without_token(client):
    """
    Validates GET /me without token fails with 401.
    """
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
