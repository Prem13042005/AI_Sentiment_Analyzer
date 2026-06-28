import bcrypt
# Monkeypatch bcrypt.hashpw to truncate passwords > 72 bytes to bypass passlib check bug with modern bcrypt
_orig_hashpw = bcrypt.hashpw
def _patched_hashpw(password, salt):
    if isinstance(password, bytes) and len(password) > 72:
        password = password[:72]
    elif isinstance(password, str) and len(password) > 72:
        password = password[:72]
    return _orig_hashpw(password, salt)
bcrypt.hashpw = _patched_hashpw

import sys
from unittest.mock import patch, MagicMock

# Pre-mock heavy machine learning libraries to bypass local environment import issues
sys.modules['tensorflow'] = MagicMock()
sys.modules['tensorflow.keras'] = MagicMock()
sys.modules['tensorflow.keras.layers'] = MagicMock()
sys.modules['tensorflow.keras.models'] = MagicMock()
sys.modules['torch'] = MagicMock()
sys.modules['transformers'] = MagicMock()

import os
import uuid
import pytest

# Force override DATABASE_URL env var to shared SQLite in-memory before importing anything from backend
os.environ["DATABASE_URL"] = "sqlite:///file:testdb?mode=memory&cache=shared"

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import init_db

@pytest.fixture(scope="session", autouse=True)
def mock_huggingface_pipeline():
    """
    Globally mock the transformers pipeline inside predict_router for all tests.
    """
    mock_nlp = MagicMock()
    def mock_pipeline_call(text, *args, **kwargs):
        clean = text.lower()
        if "love" in clean or "like" in clean or "great" in clean:
            label = "POSITIVE"
            score = 0.98
        elif "terrible" in clean or "waste" in clean or "poor" in clean:
            label = "NEGATIVE"
            score = 0.95
        else:
            label = "POSITIVE"
            score = 0.50
        return [{"label": label, "score": score}]
    mock_nlp.side_effect = mock_pipeline_call
    
    with patch("backend.app.routers.predict_router.get_pipeline", return_value=mock_nlp):
        yield

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Initializes database tables on test session startup.
    Since it uses SQLite in-memory, the schema automatically persists across all session tests.
    """
    init_db()
    yield

@pytest.fixture(scope="module")
def client():
    """
    Returns a FastAPI TestClient session.
    """
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def test_user(client):
    """
    Registers a new test operator and returns details (including raw password).
    """
    username = f"testuser_{uuid.uuid4().hex[:6]}"
    email = f"{username}@example.com"
    password = "password_secure_123"
    
    payload = {
        "username": username,
        "email": email,
        "password": password
    }
    
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    data["password"] = password  # Append raw password for subsequent logins
    return data

@pytest.fixture(scope="module")
def auth_headers(client, test_user):
    """
    Performs OAuth2 password login and returns Bearer token authorization headers.
    """
    payload = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    response = client.post("/api/v1/auth/login", data=payload)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
