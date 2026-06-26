import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    """
    Validates backend API health check.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "models" in data

def test_predict_endpoint_ensemble():
    """
    Validates single sentiment predictions utilizing the default Ensemble model.
    """
    payload = {
        "text": "This movie was absolutely fantastic and beautiful!",
        "model_name": "ensemble"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == payload["text"]
    assert data["sentiment"] in ["Positive", "Negative"]
    assert 0.5 <= data["confidence"] <= 1.0
    assert "probabilities" in data
    assert "execution_time_ms" in data

def test_explain_endpoint_gru_attention():
    """
    Validates explainability generation for GRU Attention model.
    """
    payload = {
        "text": "The food was wonderful but service was laggy.",
        "model_name": "gru-attention"
    }
    response = client.post("/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == payload["text"]
    assert "lime_explanation" in data
    assert "attention_weights" in data
    
    # Check LIME fields
    lime = data["lime_explanation"]
    assert "words" in lime
    assert "positive_contributions" in lime
    assert "negative_contributions" in lime
    assert "sequence_attributions" in lime

def test_analytics_endpoints():
    """
    Validates that analytics reports can be retrieved successfully.
    """
    # Test aggregate stats
    res_stats = client.get("/analytics")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert "total_count" in stats
    assert "positive_percentage" in stats
    
    # Test benchmarks
    res_bench = client.get("/analytics/benchmark")
    assert res_bench.status_code == 200
    bench = res_bench.json()
    assert "benchmarks" in bench
    
    # Test logs history
    res_hist = client.get("/analytics/history?limit=5")
    assert res_hist.status_code == 200
    assert isinstance(res_hist.json(), list)
