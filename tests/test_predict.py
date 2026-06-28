import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def mock_huggingface_pipeline():
    """
    Mocks get_pipeline inside predict_router to return a callable mock pipeline
    so that tests run without invoking the real model or downloading weights.
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
            score = 0.50  # resolves to neutral since score < 0.65
        return [{"label": label, "score": score}]
        
    mock_nlp.side_effect = mock_pipeline_call
    
    with patch("backend.app.routers.predict_router.get_pipeline", return_value=mock_nlp):
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
