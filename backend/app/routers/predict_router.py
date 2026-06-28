import time
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from transformers import pipeline

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.analysis import Analysis
from backend.app.schemas import (
    PredictRequest, 
    PredictResponse, 
    BulkPredictRequest, 
    BulkPredictResponse
)
from backend.app.auth import get_current_user

# Setup logger
logger = logging.getLogger("sentix.predict_router")

router = APIRouter(prefix="/api/v1/predict", tags=["Predictions"])

# Singleton pipeline container
SENTIMENT_PIPELINE = None

def get_pipeline():
    """
    Initializes and returns the DistilBERT sentiment analysis pipeline as a singleton.
    """
    global SENTIMENT_PIPELINE
    if SENTIMENT_PIPELINE is None:
        logger.info("Initializing DistilBERT sentiment analysis pipeline...")
        SENTIMENT_PIPELINE = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        logger.info("DistilBERT model loaded successfully.")
    return SENTIMENT_PIPELINE

def run_distilbert(text: str) -> dict:
    """
    Executes DistilBERT sentiment classification inside a safe try-except block.
    If the prediction confidence score is below 0.65, resolves the sentiment as 'neutral'.
    """
    try:
        nlp = get_pipeline()
        res = nlp(text)[0]
        
        # Standard labels from distilbert sst-2: 'POSITIVE' or 'NEGATIVE'
        label = res["label"].lower()
        confidence = res["score"]
        
        # Check neutral threshold filter
        if confidence < 0.65:
            label = "neutral"
            
        return {
            "sentiment": label,
            "confidence": confidence,
            "error": None
        }
    except Exception as e:
        logger.error(f"DistilBERT model prediction failed: {e}")
        return {
            "sentiment": "neutral",
            "confidence": 0.0,
            "error": str(e)
        }

@router.post("", response_model=PredictResponse)
def predict_single(
    request: PredictRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Classifies the sentiment of a single text input.
    Saves the prediction audit log to the database and returns the result.
    """
    start_time = time.perf_counter()
    
    # Run prediction model
    res = run_distilbert(request.text)
    if res["error"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference pipeline failed: {res['error']}"
        )
        
    processing_time = max((time.perf_counter() - start_time) * 1000, 0.001)
    
    # Save log to DB
    db_analysis = Analysis(
        user_id=current_user.id,
        text=request.text,
        text_snippet=request.text[:150],
        sentiment=res["sentiment"],
        confidence=res["confidence"],
        model_used="distilbert",
        source="manual"
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    return PredictResponse(
        id=db_analysis.id,
        text=request.text,
        sentiment=res["sentiment"],
        confidence=res["confidence"],
        model_used="distilbert",
        processing_time_ms=processing_time
    )

@router.post("/bulk", response_model=BulkPredictResponse)
def predict_bulk(
    request: BulkPredictRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Classifies a list of text strings in a loop and logs each execution.
    """
    results = []
    failed = 0
    
    for text in request.texts:
        clean_text = text.strip()
        if not clean_text:
            failed += 1
            continue
            
        item_start = time.perf_counter()
        res = run_distilbert(clean_text)
        item_time = max((time.perf_counter() - item_start) * 1000, 0.001)
        
        if res["error"]:
            failed += 1
            continue
            
        # Log to DB
        db_analysis = Analysis(
            user_id=current_user.id,
            text=clean_text,
            text_snippet=clean_text[:150],
            sentiment=res["sentiment"],
            confidence=res["confidence"],
            model_used="distilbert",
            source="bulk"
        )
        db.add(db_analysis)
        
        results.append(PredictResponse(
            text=clean_text,
            sentiment=res["sentiment"],
            confidence=res["confidence"],
            model_used="distilbert",
            processing_time_ms=item_time
        ))
        
    db.commit()
    
    return BulkPredictResponse(
        results=results,
        total=len(request.texts),
        failed=failed
    )
