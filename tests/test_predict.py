import pytest
from unittest.mock import patch
from backend.app.utils.model_registry import ModelRegistry

@pytest.fixture(autouse=True)
def mock_model_inference():
    """
    Mocks ModelRegistry inference methods to ensure deterministic tests
    without requiring physical deep learning model files on disk.
    """
    def mock_predict_ensemble(text: str):
        clean = text.lower()
        if "love" in clean or "like" in clean or "great" in clean:
            sentiment = "positive"
            confidence = 0.98
        elif "terrible" in clean or "waste" in clean or "poor" in clean:
            sentiment = "negative"
            confidence = 0.95
        else:
            sentiment = "neutral"
            confidence = 0.50
            
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "model_scores": [
                {"model_name": "bilstm", "sentiment": sentiment, "confidence": confidence},
                {"model_name": "gru", "sentiment": sentiment, "confidence": confidence},
                {"model_name": "cnn_lstm", "sentiment": sentiment, "confidence": confidence},
                {"model_name": "distilbert", "sentiment": sentiment, "confidence": confidence}
            ]
        }

    with patch.object(ModelRegistry, "predict_ensemble", side_effect=mock_predict_ensemble):
        yield

def test_predict_positive_text(client, auth_headers):
    """
    Validates positive sentiment classification path.
    """
    payload = {
        "text": "I absolutely love this product!",
        "model_name": "ensemble"
    }
    response = client.post("/api/v1/predict", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "positive"
    assert data["confidence"] > 0.5

def test_predict_negative_text(client, auth_headers):
    """
    Validates negative sentiment classification path.
    """
    payload = {
        "text": "This is terrible, waste of money",
        "model_name": "ensemble"
    }
    response = client.post("/api/v1/predict", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "negative"
    assert data["confidence"] > 0.5

def test_predict_empty_string(client, auth_headers):
    """
    Validates empty string gets rejected with 422.
    """
    payload = {
        "text": "",
        "model_name": "ensemble"
    }
    response = client.post("/api/v1/predict", json=payload, headers=auth_headers)
    assert response.status_code == 422

def test_predict_whitespace_only(client, auth_headers):
    """
    Validates whitespace-only string gets stripped and rejected with 422.
    """
    payload = {
        "text": "   ",
        "model_name": "ensemble"
    }
    response = client.post("/api/v1/predict", json=payload, headers=auth_headers)
    assert response.status_code == 422

def test_predict_too_long(client, auth_headers):
    """
    Validates text exceeding 2000 characters gets rejected with 422.
    """
    payload = {
        "text": "a" * 2001,
        "model_name": "ensemble"
    }
    response = client.post("/api/v1/predict", json=payload, headers=auth_headers)
    assert response.status_code == 422

def test_predict_unauthenticated(client):
    """
    Validates prediction without token fails with 401.
    """
    payload = {
        "text": "Valid review text",
        "model_name": "ensemble"
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 401

def test_predict_returns_confidence(client, auth_headers):
    """
    Validates confidence scores are bounded in [0.0, 1.0].
    """
    payload = {
        "text": "Neutral comment.",
        "model_name": "ensemble"
    }
    response = client.post("/api/v1/predict", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert 0.0 <= data["confidence"] <= 1.0

def test_predict_returns_processing_time(client, auth_headers):
    """
    Validates processing speed metric tracking returns values > 0.
    """
    payload = {
        "text": "Super fast response testing.",
        "model_name": "ensemble"
    }
    response = client.post("/api/v1/predict", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["processing_time_ms"] > 0
