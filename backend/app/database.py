import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentix.database")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sentix.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    connect_args["uri"] = True

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

def init_db():
    """
    Initializes database tables and registers models.
    """
    # Local imports inside function to avoid circular dependencies with models importing Base
    from backend.app.models.user import User
    from backend.app.models.analysis import Analysis
    
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully via database.py")
