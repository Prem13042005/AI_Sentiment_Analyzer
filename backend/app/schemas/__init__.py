from pydantic import BaseModel, Field, EmailStr, model_validator, ConfigDict
from typing import Literal, List, Optional, Dict, Any
from datetime import datetime

class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="The input text to classify.")
    model_name: str = Field("ensemble", description="The ML model to employ.")

    @model_validator(mode="before")
    @classmethod
    def strip_and_validate_text(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "text" in values and isinstance(values["text"], str):
                values["text"] = values["text"].strip()
            if "model_name" in values and values["model_name"] not in ["bilstm", "gru", "cnn_lstm", "distilbert", "ensemble"]:
                raise ValueError("model_name must be one of ['bilstm', 'gru', 'cnn_lstm', 'distilbert', 'ensemble']")
        return values

class ModelScore(BaseModel):
    model_name: str
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float  # 0.0-1.0

class LimeWord(BaseModel):
    word: str
    weight: float  # positive = supports positive, negative = supports negative

class PredictResponse(BaseModel):
    id: Optional[str] = None
    text: str
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float
    model_scores: List[ModelScore]
    lime_words: Optional[List[LimeWord]] = None
    attention_weights: Optional[Dict[str, float]] = None  # word -> weight, GRU only
    processing_time_ms: float
    model_used: str

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern="^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    user_id: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class HistoryItem(BaseModel):
    id: str
    text_snippet: str  # first 100 chars of original text
    sentiment: str
    confidence: float
    model_used: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class BulkPredictRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, max_length=100)  # max 100 rows

class BulkPredictResponse(BaseModel):
    results: List[PredictResponse]
    total: int
    processing_time_ms: float
