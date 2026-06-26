import uuid
import pytest

def test_history_empty_for_new_user(client):
    """
    Validates that a new user gets an empty history listing.
    """
    # Create new unique user
    username = f"user_{uuid.uuid4().hex[:6]}"
    email = f"{username}@example.com"
    password = "password123"
    
    reg_res = client.post("/api/v1/auth/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    assert reg_res.status_code == 201
    
    login_res = client.post("/api/v1/auth/login", data={
        "username": username,
        "password": password
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check history
    response = client.get("/api/v1/history/", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

def test_history_stats_structure(client, auth_headers):
    """
    Validates stats endpoint returns the correct aggregate keys.
    """
    response = client.get("/api/v1/history/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "positive" in data
    assert "negative" in data
    assert "neutral" in data
    assert "most_used_model" in data
    assert "analyses_last_7_days" in data

def test_delete_own_history_item(client, auth_headers):
    """
    Validates a user can delete their own prediction log item.
    """
    # 1. Run prediction to create log item
    payload = {"text": "Deletable review item", "model_name": "ensemble"}
    res_predict = client.post("/api/v1/predict", json=payload, headers=auth_headers)
    assert res_predict.status_code == 200
    item_id = res_predict.json()["id"]
    
    # 2. Delete the item
    res_delete = client.delete(f"/api/v1/history/{item_id}", headers=auth_headers)
    assert res_delete.status_code == 204
    
    # 3. Retrieve history and assert deletion
    res_history = client.get("/api/v1/history/", headers=auth_headers)
    assert res_history.status_code == 200
    ids = [item["id"] for item in res_history.json()]
    assert item_id not in ids

def test_delete_nonexistent_item(client, auth_headers):
    """
    Validates deleting a nonexistent item returns 404.
    """
    fake_uuid = str(uuid.uuid4())
    response = client.delete(f"/api/v1/history/{fake_uuid}", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Analysis record not found"

def test_cannot_delete_other_users_item(client, auth_headers):
    """
    Validates user A cannot delete prediction logs logged by user B (returns 403).
    """
    # 1. User A (auth_headers) logs prediction
    payload = {"text": "Private User A feedback log", "model_name": "ensemble"}
    res_predict = client.post("/api/v1/predict", json=payload, headers=auth_headers)
    assert res_predict.status_code == 200
    item_id = res_predict.json()["id"]
    
    # 2. Register User B
    username_b = f"user_b_{uuid.uuid4().hex[:6]}"
    email_b = f"{username_b}@example.com"
    pw_b = "password_secure_123"
    
    reg_res = client.post("/api/v1/auth/register", json={
        "username": username_b,
        "email": email_b,
        "password": pw_b
    })
    assert reg_res.status_code == 201
    
    # 3. Authenticate User B
    login_res = client.post("/api/v1/auth/login", data={
        "username": username_b,
        "password": pw_b
    })
    assert login_res.status_code == 200
    token_b = login_res.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # 4. User B attempts to delete User A's log -> 403 Forbidden
    res_delete = client.delete(f"/api/v1/history/{item_id}", headers=headers_b)
    assert res_delete.status_code == 403
    assert res_delete.json()["detail"] == "Not authorized to delete this record"
