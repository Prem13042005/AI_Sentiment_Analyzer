from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services.db_service import DatabaseService
from backend.app.services.model_service import ModelService
from backend.app.schemas.analytics import AnalyticsResponse, ErrorAnalysisResponse, BenchmarkResponse
from typing import List, Dict, Any

router = APIRouter(prefix="/analytics", tags=["Analytics & Logging"])

@router.get("", response_model=AnalyticsResponse)
def get_dashboard_analytics(db: Session = Depends(get_db)):
    """
    Returns aggregated KPIs, sentiment distributions, time-series trends, 
    word cloud data, and model latency averages from prediction logs.
    """
    try:
        return DatabaseService.get_analytics(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load analytics: {str(e)}")

@router.get("/benchmark", response_model=BenchmarkResponse)
def get_model_benchmarks():
    """
    Retrieves model comparison benchmarking records (Accuracy, Precision, Recall, F1, Inference time).
    """
    try:
        benchmarks = ModelService().get_benchmarks()
        return {"benchmarks": benchmarks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch benchmarks: {str(e)}")

@router.get("/error-analysis", response_model=ErrorAnalysisResponse)
def get_model_error_analysis(db: Session = Depends(get_db)):
    """
    Performs error analysis by comparing model sentiment classifications 
    against known labels, returning accuracy, false positives, and false negatives.
    """
    try:
        return DatabaseService.get_error_analysis(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analysis failed: {str(e)}")

@router.get("/history", response_model=List[Dict[str, Any]])
def get_prediction_history(limit: int = 50, db: Session = Depends(get_db)):
    """
    Queries the latest logging records of predictions stored in the database.
    """
    try:
        logs = DatabaseService.get_logs(db, limit=limit)
        return [log.to_dict() for log in logs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history logs: {str(e)}")

@router.post("/seed")
def seed_mock_data(db: Session = Depends(get_db)):
    """
    Seeds the database with high-quality mock prediction logs for evaluation purposes.
    """
    try:
        DatabaseService.seed_data(db)
        return {"status": "success", "message": "Database successfully seeded with historical logs."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database seeding failed: {str(e)}")
