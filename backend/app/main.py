from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from backend.app.database.connection import get_db, init_db
from backend.app.middleware.logger import RequestLoggingMiddleware
from backend.app.routers import predict, explain, analytics
from backend.app.services.model_service import ModelService
from backend.app.services.db_service import DatabaseService

# Load Env config
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="Sentiment Intelligence Platform API",
    description="Enterprise NLP sentiment analytics API with multi-model inference, explainability (LIME/Attention), and database logging.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, configure to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom logger middleware for process latency auditing
app.add_middleware(RequestLoggingMiddleware)

# Include API Routers
app.include_router(predict.router)
app.include_router(explain.router)
app.include_router(analytics.router)

@app.on_event("startup")
def startup_event():
    """
    FastAPI startup tasks.
    Initializes database tables, pre-loads NLP deep learning models,
    and runs database seeding if empty.
    """
    print("FastAPI: Running startup events...")
    # Initialize DB (creates SQLite/PostgreSQL schemas)
    init_db()
    
    # Pre-load/verify models in memory
    print("FastAPI: Initializing ModelService...")
    model_service = ModelService()
    
    # Auto-seed mock prediction logs if database is empty
    db_session = next(get_db())
    try:
        DatabaseService.seed_data(db_session)
    except Exception as e:
        print(f"FastAPI Startup Warning: Auto-seeding failed ({e})")
    finally:
        db_session.close()
        
    print("FastAPI: Startup sequence complete. Server ready.")

@app.get("/", include_in_schema=False)
def root_redirect():
    """
    Redirects API root request to interactive Swagger documentation.
    """
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["System Health"])
def check_health(db: Session = Depends(get_db)):
    """
    Performs system health check of model loader and database connection.
    """
    db_status = "Healthy"
    try:
        # Quick db query to verify link
        db.execute(type("Query", (object,), {"__str__": lambda s: "SELECT 1"})())
    except Exception:
        db_status = "Unhealthy"
        
    # Check loaded models
    model_service = ModelService()
    model_status = {
        name: ("Loaded" if name in model_service.models else "Not Loaded / Dynamic Fallback")
        for name in ["bilstm", "gru_attention", "cnn_lstm", "distilbert"]
    }
    
    overall_status = "Healthy" if db_status == "Healthy" else "Degraded"
    
    return {
        "status": overall_status,
        "database": db_status,
        "models": model_status,
        "environment": os.getenv("ENV", "production")
    }
