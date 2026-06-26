import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentiment_platform.database")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sentiment.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    if "mode=memory" in DATABASE_URL or "file:" in DATABASE_URL:
        connect_args["uri"] = True

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    # Import models here to ensure they are registered before creating tables, avoiding circular import
    from backend.app.models.user import User
    from backend.app.models.analysis import Analysis
    
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully via database/__init__.py")

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
