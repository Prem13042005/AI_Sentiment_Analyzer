import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database.models import Base

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentiment_platform.database")

# Load DB URL from env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sentiment.db")

engine = None
SessionLocal = None

def init_db():
    global engine, SessionLocal
    try:
        # If Postgres is configured, try it first with a fast timeout
        if DATABASE_URL.startswith("postgresql"):
            logger.info("Attempting to connect to PostgreSQL...")
            engine = create_engine(
                DATABASE_URL, 
                connect_args={"connect_timeout": 3},
                pool_pre_ping=True
            )
            # Verify connection
            with engine.connect() as conn:
                logger.info("Successfully connected to PostgreSQL database.")
        else:
            raise ValueError("Using SQLite configuration.")
            
    except Exception as e:
        if DATABASE_URL.startswith("postgresql"):
            logger.warning(f"PostgreSQL connection failed ({e}). Falling back to SQLite...")
        else:
            logger.info("Initializing local SQLite database.")
            
        fallback_url = "sqlite:///./sentiment.db"
        engine = create_engine(
            fallback_url, 
            connect_args={"check_same_thread": False}
        )
        
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized.")

# Initialize immediately on import
init_db()

def get_db():
    """
    Dependency generator for FastAPI routes.
    Yields active database session and ensures closure.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
