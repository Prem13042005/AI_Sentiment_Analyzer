from fastapi import APIRouter, HTTPException, Depends
from backend.app.schemas.predict import ExplainRequest, ExplainResponse
from backend.app.services.model_service import ModelService
from backend.app.utils.lime_explain import LimeTextExplainer
import numpy as np
from typing import List

router = APIRouter(prefix="/explain", tags=["Explainable AI"])

@router.post("", response_model=ExplainResponse)
def explain_sentiment(request: ExplainRequest):
    """
    Generates explainability metrics for a review, including LIME word contributions 
    and Attention heatmaps (when utilizing the GRU Attention model).
    """
    model_service = ModelService()
    
    try:
        # 1. Run single prediction to get base sentiment classification
        base_prediction = model_service.predict(text=request.text, model_name=request.model_name)
        
        # 2. Define prediction function wrapper for LIME
        def lime_predict_fn(texts: List[str]) -> np.ndarray:
            batch_res = model_service.predict_batch(texts, model_name=request.model_name)
            probs = np.zeros((len(texts), 2))
            for i, res in enumerate(batch_res):
                probs[i, 0] = res["probabilities"]["negative"]
                probs[i, 1] = res["probabilities"]["positive"]
            return probs
            
        # 3. Generate LIME explanations
        explainer = LimeTextExplainer(num_samples=150, keep_prob=0.75)
        lime_explanation = explainer.explain(request.text, lime_predict_fn)
        
        # 4. Extract attention weights if the model is GRU Attention or Ensemble (querying GRU layer)
        attention_weights = None
        norm_model = request.model_name.lower().replace("-", "_")
        if norm_model in ["gru_attention", "ensemble"]:
            attention_weights = model_service.extract_attention_weights(request.text)
            
        return {
            "text": request.text,
            "model_name": request.model_name,
            "sentiment": base_prediction["sentiment"],
            "confidence": base_prediction["confidence"],
            "lime_explanation": lime_explanation,
            "attention_weights": attention_weights
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explainability run failed: {str(e)}")
