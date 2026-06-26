from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class PredictRequest(BaseModel):
    text: str = Field(..., description="The raw input text to analyze.", min_length=1)
    model_name: Optional[str] = Field("ensemble", description="The NLP model to use: 'bilstm', 'gru-attention', 'cnn-lstm', 'distilbert', or 'ensemble'.")

class PredictResponse(BaseModel):
    text: str
    model_name: str
    sentiment: str
    confidence: float
    probabilities: Dict[str, float]
    execution_time_ms: float

class BulkPredictRequest(BaseModel):
    texts: List[str] = Field(..., description="List of review texts to analyze.", min_items=1)
    model_name: Optional[str] = Field("ensemble", description="The model to use for batch prediction.")

class BulkPredictResponse(BaseModel):
    results: List[PredictResponse]

class ExplainRequest(BaseModel):
    text: str = Field(..., description="The input text to generate explanation highlights for.", min_length=1)
    model_name: Optional[str] = Field("gru-attention", description="Model to explain: 'bilstm', 'gru-attention', 'cnn-lstm', 'distilbert', or 'ensemble'.")

class ExplainResponse(BaseModel):
    text: str
    model_name: str
    sentiment: str
    confidence: float
    lime_explanation: Dict[str, Any]
    attention_weights: Optional[List[Dict[str, Any]]] = None
