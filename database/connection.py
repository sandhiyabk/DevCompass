# database/connection.py

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")

if DATABASE_URL and "?" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """Dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    from database.models import (
        User, UserSkill, DailyTask,
        StuckSession, Reflection,
        KnowledgeBase, WeeklyReport
    )
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully")
if __name__ == "__main__":
    print("Testing database connection...")
    try:
        init_db()
        print("✅ All tables created successfully")
        
        # Test connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection working")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")