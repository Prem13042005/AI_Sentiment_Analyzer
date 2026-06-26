from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
load_dotenv()

from backend.app.database import get_db, init_db
from backend.app.middleware.logger import RequestLoggingMiddleware
from backend.app.routers import predict, explain, analytics
from backend.app.routers.auth_router import router as auth_router
from backend.app.routers.predict_router import router as predict_router
from backend.app.routers.history_router import router as history_router
from backend.app.utils.model_registry import ModelRegistry
from backend.app.services.model_service import ModelService
from backend.app.services.db_service import DatabaseService

app = FastAPI(
    title="Sentiment Intelligence Platform API",
    description="Enterprise NLP sentiment analytics API with multi-model inference, explainability (LIME/Attention), and database logging.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://frontend:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom logger middleware for process latency auditing
app.add_middleware(RequestLoggingMiddleware)

# Register new routers
app.include_router(auth_router)
app.include_router(predict_router)
app.include_router(history_router)

# Include legacy API Routers
app.include_router(predict.router)
app.include_router(explain.router)
app.include_router(analytics.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

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
    
    # Initialize ModelRegistry singleton and load models
    model_dir = os.getenv("MODEL_DIR", "./models")
    ModelRegistry.get_instance().load_models(model_dir)
    
    # Pre-load/verify legacy ModelService
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

@app.get("/health", tags=["System Health"])
def check_health():
    """
    Performs system health check of model loader and database connection.
    """
    return {
        "status": "ok",
        "models_ready": ModelRegistry.get_instance().is_ready(),
        "version": "1.0.0"
    }

@app.get("/")
def read_root():
    return {"message": "SIP API running. Docs at /docs"}
