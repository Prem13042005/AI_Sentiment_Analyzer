from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.analysis import Analysis
from backend.app.schemas import HistoryItem, StatsResponse
from backend.app.auth import get_current_user

router = APIRouter(prefix="/api/v1/history", tags=["History & Audit"])

@router.get("/stats", response_model=StatsResponse)
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Computes system aggregate metrics for the authenticated operator.
    Includes total logs count, positive/negative/neutral share ratios,
    most used model architecture, and a 30-day historical time-series breakdown.
    """
    # Count totals
    total = db.query(Analysis).filter(Analysis.user_id == current_user.id).count()
    positive = db.query(Analysis).filter(Analysis.user_id == current_user.id, Analysis.sentiment == "positive").count()
    negative = db.query(Analysis).filter(Analysis.user_id == current_user.id, Analysis.sentiment == "negative").count()
    neutral = db.query(Analysis).filter(Analysis.user_id == current_user.id, Analysis.sentiment == "neutral").count()

    # Percentages
    positive_pct = (positive / total * 100) if total > 0 else 0.0
    negative_pct = (negative / total * 100) if total > 0 else 0.0
    neutral_pct = (neutral / total * 100) if total > 0 else 0.0

    # Most used model
    most_used_query = db.query(
        Analysis.model_used,
        func.count(Analysis.model_used).label("cnt")
    ).filter(
        Analysis.user_id == current_user.id
    ).group_by(
        Analysis.model_used
    ).order_by(
        func.count(Analysis.model_used).desc()
    ).first()

    most_used_model = most_used_query[0] if most_used_query else "distilbert"

    # Last 30 days time series breakdown (inclusive of today)
    today = datetime.utcnow().date()
    analyses_last_30_days = []
    
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        
        start_dt = datetime.combine(d, datetime.min.time())
        end_dt = datetime.combine(d, datetime.max.time())
        
        day_count = db.query(Analysis).filter(
            Analysis.user_id == current_user.id,
            Analysis.created_at >= start_dt,
            Analysis.created_at <= end_dt
        ).count()
        
        analyses_last_30_days.append({
            "date": d_str,
            "count": day_count
        })

    return StatsResponse(
        total=total,
        positive=positive,
        negative=negative,
        neutral=neutral,
        positive_pct=positive_pct,
        negative_pct=negative_pct,
        neutral_pct=neutral_pct,
        most_used_model=most_used_model,
        analyses_last_30_days=analyses_last_30_days,
        
        # Compatibility fields
        total_count=total,
        positive_count=positive,
        negative_count=negative,
        neutral_count=neutral,
        analyses_last_7_days=analyses_last_30_days[-7:]
    )

@router.get("", response_model=List[HistoryItem])
def get_history(
    sentiment: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the paginated and filtered list of prediction logs.
    """
    query = db.query(Analysis).filter(Analysis.user_id == current_user.id)
    
    if sentiment:
        query = query.filter(Analysis.sentiment == sentiment.lower().strip())
        
    results = query.order_by(Analysis.created_at.desc()).offset(offset).limit(limit).all()
    return results

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a specific prediction log if owned by the operator.
    """
    item = db.query(Analysis).filter(Analysis.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis record not found"
        )
        
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this record"
        )
        
    db.delete(item)
    db.commit()
