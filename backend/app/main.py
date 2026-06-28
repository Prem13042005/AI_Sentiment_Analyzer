import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

from backend.app.database import init_db
from backend.app.routers.auth_router import router as auth_router
from backend.app.routers.predict_router import router as predict_router
from backend.app.routers.history_router import router as history_router

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentix.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager executing database table initialization 
    and seeding actions during backend startup.
    """
    logger.info("FastAPI: Running startup events...")
    try:
        init_db()
        logger.info("FastAPI: Startup sequence complete. Server ready.")
    except Exception as e:
        logger.critical(f"FastAPI: Startup sequence failed: {e}")
    yield
    logger.info("FastAPI: Shutting down server...")

app = FastAPI(
    title="Sentix AI API",
    description="Enterprise sentiment analytics REST gateway featuring DistilBERT inference and PostgreSQL logging.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://frontend:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler for validation constraints
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation failed for request {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(exc.errors())}
    )

# Global catch-all handler for unhandled backend exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception intercepted at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Include API Routers
app.include_router(auth_router)
app.include_router(predict_router)
app.include_router(history_router)

@app.get("/health", tags=["System Health"])
def check_health():
    """
    System status checker endpoint.
    """
    return {
        "status": "ok",
        "version": "1.0.0"
    }

@app.get("/", tags=["Root Gateway"])
def read_root():
    """
    Root landing redirect index description.
    """
    return {
        "message": "Sentix AI API. Docs at /docs"
    }
