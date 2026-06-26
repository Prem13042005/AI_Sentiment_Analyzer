from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class SentimentTrendPoint(BaseModel):
    date: str
    Positive: int
    Negative: int

class WordFrequency(BaseModel):
    word: str
    count: int

class AnalyticsResponse(BaseModel):
    total_count: int
    positive_percentage: float
    negative_percentage: float
    sentiment_distribution: Dict[str, int]
    confidence_distribution: Dict[str, int]
    sentiment_trends: List[SentimentTrendPoint]
    top_positive_words: List[WordFrequency]
    top_negative_words: List[WordFrequency]
    model_average_latencies: Dict[str, float]

class ErrorAnalysisResponse(BaseModel):
    total_labeled: int
    accuracy: float
    false_positives: List[Dict[str, Any]]
    false_negatives: List[Dict[str, Any]]
    metrics: Dict[str, int]

class BenchmarkMetric(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    inference_time_ms: float

class BenchmarkResponse(BaseModel):
    benchmarks: Dict[str, BenchmarkMetric]
