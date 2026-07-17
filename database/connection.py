# database/connection.py

import os
import socket
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def _force_ipv4_connect(dsn, **kwargs):
    """Connect using IPv4 only — fixes Render free tier + Supabase."""
    conn = psycopg2.connect(dsn, **kwargs)
    return conn


def _create_ipv4_engine(url):
    """Create engine that forces IPv4 by resolving the hostname manually."""
    from urllib.parse import urlparse, parse_qs

    parsed = urlparse(url)
    hostname = parsed.hostname

    try:
        addrs = socket.getaddrinfo(hostname, parsed.port or 5432, socket.AF_INET)
        if addrs:
            ipv4_addr = addrs[0][4][0]
            new_url = url.replace(hostname, ipv4_addr)
            return create_engine(
                new_url,
                connect_args={"sslmode": "require"},
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
            )
    except socket.gaierror:
        pass

    return create_engine(
        url,
        connect_args={"sslmode": "require"},
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")

if DATABASE_URL and "?" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

engine = _create_ipv4_engine(DATABASE_URL)

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

        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection working")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
