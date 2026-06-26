import time
import json
import logging
import numpy as np
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.analysis import Analysis
from backend.app.schemas import (
    PredictRequest, PredictResponse, ModelScore, LimeWord,
    BulkPredictRequest, BulkPredictResponse
)
from backend.app.auth import get_current_user
from backend.app.utils.model_registry import ModelRegistry
from backend.app.utils.lime_explain import LimeTextExplainer

# Setup logger
logger = logging.getLogger("sentiment_platform.predict_router")

router = APIRouter(prefix="/api/v1", tags=["predict"])

@router.post("/predict", response_model=PredictResponse)
def predict_sentiment(
    request: PredictRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Classifies the sentiment of a single input review.
    Logs execution time, individual model scores, LIME details, and outputs to SQLite.
    """
    start_time = time.time()
    
    registry = ModelRegistry.get_instance()
    if not registry.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Models not yet trained. Run train_models.py first."
        )
        
    text = request.text
    model_name = request.model_name
    
    model_scores: List[ModelScore] = []
    sentiment: str = "neutral"
    confidence: float = 0.0
    attention_weights = None
    lime_words = None
    
    try:
        if model_name == "bilstm":
            res = registry.predict_bilstm(text)
            sentiment = res["sentiment"]
            confidence = res["confidence"]
            model_scores.append(ModelScore(model_name="bilstm", sentiment=sentiment, confidence=confidence))
            
        elif model_name == "gru":
            res = registry.predict_gru(text)
            sentiment = res["sentiment"]
            confidence = res["confidence"]
            attention_weights = res.get("attention_weights")
            model_scores.append(ModelScore(model_name="gru", sentiment=sentiment, confidence=confidence))
            
        elif model_name == "cnn_lstm":
            res = registry.predict_cnn_lstm(text)
            sentiment = res["sentiment"]
            confidence = res["confidence"]
            model_scores.append(ModelScore(model_name="cnn_lstm", sentiment=sentiment, confidence=confidence))
            
        elif model_name == "distilbert":
            res = registry.predict_distilbert(text)
            sentiment = res["sentiment"]
            confidence = res["confidence"]
            model_scores.append(ModelScore(model_name="distilbert", sentiment=sentiment, confidence=confidence))
            
        elif model_name == "ensemble":
            res = registry.predict_ensemble(text)
            sentiment = res["sentiment"]
            confidence = res["confidence"]
            for ms in res.get("model_scores", []):
                model_scores.append(ModelScore(
                    model_name=ms["model_name"],
                    sentiment=ms["sentiment"],
                    confidence=ms["confidence"]
                ))
    except Exception as e:
        logger.error(f"Prediction failed for model {model_name}: {e}")
        sentiment = "neutral"
        confidence = 0.0
        
    # Run LIME explanation if model supports it (distilbert or ensemble)
    if model_name in ["distilbert", "ensemble"] and confidence > 0.0:
        try:
            def predict_probs_fn(texts: List[str]) -> np.ndarray:
                probs = np.zeros((len(texts), 2))
                for idx, t in enumerate(texts):
                    if model_name == "ensemble":
                        r = registry.predict_ensemble(t)
                    else:
                        r = registry.predict_distilbert(t)
                    # Convert class confidence to probability
                    p_pos = r["confidence"] if r["sentiment"] == "positive" else (1.0 - r["confidence"] if r["sentiment"] == "negative" else 0.5)
                    probs[idx, 1] = p_pos
                    probs[idx, 0] = 1.0 - p_pos
                return probs
                
            explainer = LimeTextExplainer(num_samples=100, keep_prob=0.75)
            lime_res = explainer.explain(text, predict_probs_fn)
            
            lime_words = []
            for item in lime_res.get("positive_contributions", []):
                lime_words.append(LimeWord(word=item["word"], weight=item["weight"]))
            for item in lime_res.get("negative_contributions", []):
                lime_words.append(LimeWord(word=item["word"], weight=-item["weight"]))
        except Exception as e:
            logger.error(f"LIME run failed silently: {e}")
            lime_words = []

    processing_time_ms = (time.time() - start_time) * 1000
    
    # Save Analysis to DB
    model_scores_json = json.dumps([ms.dict() for ms in model_scores])
    lime_data_json = json.dumps([lw.dict() for lw in lime_words]) if lime_words is not None else None
    
    db_analysis = Analysis(
        user_id=current_user.id,
        text=text,
        text_snippet=text[:100],
        sentiment=sentiment,
        confidence=confidence,
        model_used=model_name,
        model_scores_json=model_scores_json,
        lime_data_json=lime_data_json
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    return PredictResponse(
        id=db_analysis.id,
        text=text,
        sentiment=sentiment,
        confidence=confidence,
        model_scores=model_scores,
        lime_words=lime_words,
        attention_weights=attention_weights,
        processing_time_ms=round(processing_time_ms, 2),
        model_used=model_name
    )

@router.post("/predict/bulk", response_model=BulkPredictResponse)
def predict_bulk(
    request: BulkPredictRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Classifies a batch of reviews.
    Optimized for speed by bypassing LIME. Logs all entries to SQLite.
    """
    start_time = time.time()
    
    registry = ModelRegistry.get_instance()
    if not registry.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Models not yet trained. Run train_models.py first."
        )
        
    results = []
    analyses_to_save = []
    
    for text in request.texts:
        text_start = time.time()
        model_name = "ensemble"
        
        model_scores = []
        sentiment = "neutral"
        confidence = 0.0
        
        try:
            res = registry.predict_ensemble(text)
            sentiment = res["sentiment"]
            confidence = res["confidence"]
            for ms in res.get("model_scores", []):
                model_scores.append(ModelScore(
                    model_name=ms["model_name"],
                    sentiment=ms["sentiment"],
                    confidence=ms["confidence"]
                ))
        except Exception as e:
            logger.error(f"Bulk predict item failed: {e}")
            sentiment = "neutral"
            confidence = 0.0
            
        item_time_ms = (time.time() - text_start) * 1000
        
        results.append(PredictResponse(
            text=text,
            sentiment=sentiment,
            confidence=confidence,
            model_scores=model_scores,
            lime_words=None,
            attention_weights=None,
            processing_time_ms=round(item_time_ms, 2),
            model_used=model_name
        ))
        
        model_scores_json = json.dumps([ms.dict() for ms in model_scores])
        analyses_to_save.append(Analysis(
            user_id=current_user.id,
            text=text,
            text_snippet=text[:100],
            sentiment=sentiment,
            confidence=confidence,
            model_used=model_name,
            model_scores_json=model_scores_json,
            lime_data_json=None
        ))
        
    # Bulk save
    if analyses_to_save:
        db.bulk_save_objects(analyses_to_save)
        db.commit()
        
    total_time_ms = (time.time() - start_time) * 1000
    
    return BulkPredictResponse(
        results=results,
        total=len(request.texts),
        processing_time_ms=round(total_time_ms, 2)
    )
