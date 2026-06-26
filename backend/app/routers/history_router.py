from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.analysis import Analysis
from backend.app.schemas import HistoryItem
from backend.app.auth import get_current_user

router = APIRouter(prefix="/api/v1/history", tags=["history"])

@router.get("/", response_model=List[HistoryItem])
def read_user_history(
    sentiment: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the prediction history logs of the authenticated user.
    Allows filtering by sentiment, pagination with limit (max 200), and offset.
    """
    if limit > 200:
        limit = 200
        
    query = db.query(Analysis).filter(Analysis.user_id == current_user.id)
    
    if sentiment:
        query = query.filter(Analysis.sentiment == sentiment.lower().strip())
        
    results = query.order_by(Analysis.created_at.desc()).offset(offset).limit(limit).all()
    return results

@router.get("/stats")
def read_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Computes system aggregate metrics for the authenticated operator.
    Includes sentiment breakdown, most used architecture, and 7-day time series.
    """
    # Count totals
    total_count = db.query(Analysis).filter(Analysis.user_id == current_user.id).count()
    positive_count = db.query(Analysis).filter(
        Analysis.user_id == current_user.id,
        Analysis.sentiment == "positive"
    ).count()
    negative_count = db.query(Analysis).filter(
        Analysis.user_id == current_user.id,
        Analysis.sentiment == "negative"
    ).count()
    neutral_count = db.query(Analysis).filter(
        Analysis.user_id == current_user.id,
        Analysis.sentiment == "neutral"
    ).count()

    # Most used model architecture
    most_used = db.query(
        Analysis.model_used,
        func.count(Analysis.model_used).label("cnt")
    ).filter(
        Analysis.user_id == current_user.id
    ).group_by(
        Analysis.model_used
    ).order_by(
        func.count(Analysis.model_used).desc()
    ).first()

    most_used_model = most_used[0] if most_used else "None"

    # Last 7 days time series breakdown (inclusive of today)
    today = datetime.utcnow().date()
    analyses_last_7_days = []
    
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        
        start_dt = datetime.combine(d, datetime.min.time())
        end_dt = datetime.combine(d, datetime.max.time())
        
        day_count = db.query(Analysis).filter(
            Analysis.user_id == current_user.id,
            Analysis.created_at >= start_dt,
            Analysis.created_at <= end_dt
        ).count()
        
        analyses_last_7_days.append({
            "date": d_str,
            "count": day_count
        })

    pos_pct = (positive_count / total_count * 100) if total_count > 0 else 0.0
    neg_pct = (negative_count / total_count * 100) if total_count > 0 else 0.0

    return {
        "total_count": total_count,
        "total": total_count,
        "positive_count": positive_count,
        "positive": positive_count,
        "negative_count": negative_count,
        "negative": negative_count,
        "neutral_count": neutral_count,
        "neutral": neutral_count,
        "positive_pct": pos_pct,
        "negative_pct": neg_pct,
        "most_used_model": most_used_model,
        "analyses_last_7_days": analyses_last_7_days
    }

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a specific prediction log record if owned by the requesting user.
    """
    analysis = db.query(Analysis).filter(Analysis.id == item_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis record not found"
        )
        
    if analysis.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this record"
        )
        
    db.delete(analysis)
    db.commit()
