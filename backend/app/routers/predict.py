from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.schemas.predict import PredictRequest, PredictResponse, BulkPredictRequest, BulkPredictResponse
from backend.app.services.model_service import ModelService
from backend.app.services.db_service import DatabaseService
import pandas as pd
import io
import csv

router = APIRouter(prefix="/predict", tags=["Predictions"])

@router.post("", response_model=PredictResponse)
def predict_single(request: PredictRequest, db: Session = Depends(get_db)):
    """
    Executes single review sentiment prediction using the specified NLP model.
    Logs execution time, probabilities, and output to the database.
    """
    model_service = ModelService()
    
    try:
        # Run prediction
        res = model_service.predict(text=request.text, model_name=request.model_name)
        
        # Save to database
        DatabaseService.log_prediction(
            db=db,
            text=res["text"],
            model_name=res["model_name"],
            sentiment=res["sentiment"],
            confidence=res["confidence"],
            probabilities=res["probabilities"],
            execution_time_ms=res["execution_time_ms"]
        )
        
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/bulk", response_model=BulkPredictResponse)
def predict_bulk(request: BulkPredictRequest, db: Session = Depends(get_db)):
    """
    Analyzes multiple text reviews in batch.
    Logs all predictions to the database.
    """
    model_service = ModelService()
    
    try:
        results = model_service.predict_batch(texts=request.texts, model_name=request.model_name)
        
        # Save logs in bulk to minimize DB operations
        db_logs = [
            {
                "text": res["text"],
                "model_name": res["model_name"],
                "sentiment": res["sentiment"],
                "confidence": res["confidence"],
                "probabilities": res["probabilities"],
                "execution_time_ms": res["execution_time_ms"]
            }
            for res in results
        ]
        DatabaseService.log_bulk_predictions(db, db_logs)
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk prediction failed: {str(e)}")

@router.post("/bulk-csv")
async def predict_bulk_csv(
    file: UploadFile = File(...),
    model_name: str = Form("ensemble"),
    db: Session = Depends(get_db)
):
    """
    Uploads a reviews.csv file, analyzes sentiment for each row, 
    records logs, and streams back the annotated CSV for download.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
        
    try:
        contents = await file.read()
        # Parse CSV
        df = pd.read_csv(io.BytesIO(contents))
        
        # Find the text column (heuristic)
        possible_cols = ['text', 'review', 'reviews', 'comment', 'comments', 'feedback', 'text_content']
        text_column = None
        for col in df.columns:
            if col.lower() in possible_cols:
                text_column = col
                break
                
        # If no match, take the first string column, otherwise raise error
        if text_column is None:
            string_cols = df.select_dtypes(include=['object']).columns
            if len(string_cols) > 0:
                text_column = string_cols[0]
            else:
                raise HTTPException(status_code=400, detail="Could not find a valid text or review column in the CSV.")
        
        # Extract reviews
        texts = df[text_column].fillna("").astype(str).tolist()
        
        # Batch Predict
        model_service = ModelService()
        predictions = model_service.predict_batch(texts=texts, model_name=model_name)
        
        # Append sentiment and confidence columns to the dataframe
        df["predicted_sentiment"] = [res["sentiment"] for res in predictions]
        df["confidence"] = [res["confidence"] for res in predictions]
        
        # Log to DB in bulk
        db_logs = [
            {
                "text": res["text"],
                "model_name": res["model_name"],
                "sentiment": res["sentiment"],
                "confidence": res["confidence"],
                "probabilities": res["probabilities"],
                "execution_time_ms": res["execution_time_ms"]
            }
            for res in predictions
        ]
        DatabaseService.log_bulk_predictions(db, db_logs)
        
        # Export processed CSV to buffer
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        response_bytes = stream.getvalue().encode("utf-8")
        
        return StreamingResponse(
            io.BytesIO(response_bytes),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=analyzed_{file.filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV processing failed: {str(e)}")
