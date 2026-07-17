from sqlalchemy import text
from database.connection import engine, SessionLocal, init_db

print("Testing database connection...\n")

# Engine test
try:
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version();"))
        print("✅ Engine Connected")
        print(version.fetchone()[0][:60], "...")
except Exception as e:
    print("❌ Engine Failed")
    print(e)

# Session test
try:
    db = SessionLocal()
    print("✅ Session Created")
    db.close()
    print("✅ Session Closed")
except Exception as e:
    print("❌ Session Failed")
    print(e)

# Table creation test
try:
    init_db()
    print("✅ Tables Verified")
except Exception as e:
    print("❌ Table Creation Failed")
    print(e)