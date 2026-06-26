from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class PredictionLog(Base):
    """
    ORM Model for logging all sentiment predictions made via the API or dashboard.
    Supports historical analytics, trend monitoring, and model calibration dashboards.
    """
    __tablename__ = 'prediction_logs'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    sentiment = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    probabilities = Column(JSON, nullable=True) # E.g. {"positive": 0.98, "negative": 0.02}
    true_label = Column(String, nullable=True)   # Optional: For error analysis, "Positive" or "Negative"
    execution_time_ms = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "model_name": self.model_name,
            "sentiment": self.sentiment,
            "confidence": self.confidence,
            "probabilities": self.probabilities,
            "true_label": self.true_label,
            "execution_time_ms": self.execution_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
