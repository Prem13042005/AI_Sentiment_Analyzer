from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime

class UserCreate(BaseModel):
    """
    Validation schema for creating a new operator.
    """
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)

class UserLogin(BaseModel):
    """
    Validation schema for operator login credentials.
    """
    username: str
    password: str

class Token(BaseModel):
    """
    JWT token structure returned upon successful login.
    """
    access_token: str
    token_type: str = "bearer"
    username: str
    user_id: str

class UserResponse(BaseModel):
    """
    Serialized operator data.
    """
    id: str
    username: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PredictRequest(BaseModel):
    """
    Single prediction request validation.
    """
    text: str = Field(..., min_length=1, max_length=2000)
    model_name: str = Field("ensemble")

    @field_validator("text", mode="before")
    @classmethod
    def validate_text(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise ValueError("text must be a string")
        stripped = v.strip()
        if not stripped:
            raise ValueError("text cannot be blank")
        return stripped

class PredictResponse(BaseModel):
    """
    Single prediction result payload.
    """
    id: Optional[str] = None
    text: str
    sentiment: str
    confidence: float
    model_used: str
    processing_time_ms: float

class HistoryItem(BaseModel):
    """
    Serialized history log record from the database.
    """
    id: str
    text: str
    text_snippet: str
    sentiment: str
    confidence: float
    model_used: str
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class StatsResponse(BaseModel):
    """
    Aggregate metrics dashboard payload.
    """
    total: int
    positive: int
    negative: int
    neutral: int
    positive_pct: float
    negative_pct: float
    neutral_pct: float
    most_used_model: str
    analyses_last_30_days: List[Dict[str, Any]]
    
    # Frontend compatibility maps
    total_count: int
    positive_count: int
    negative_count: int
    neutral_count: int
    analyses_last_7_days: List[Dict[str, Any]]

class BulkPredictRequest(BaseModel):
    """
    Batch prediction request payload.
    """
    texts: List[str] = Field(..., min_length=1, max_length=100)

class BulkPredictResponse(BaseModel):
    """
    Batch prediction results payload.
    """
    results: List[PredictResponse]
    total: int
    failed: int

class GoogleLoginRequest(BaseModel):
    """
    Validation schema for logging in or registering via Google credentials.
    """
    email: EmailStr
    name: str
