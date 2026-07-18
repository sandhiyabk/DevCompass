# api/main.py

import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from database.connection import init_db, SessionLocal
from api.routes import auth, tasks, stuck, reflections, reports

app = FastAPI(
    title="DevCompass API",
    description="AI Work Companion for IT Freshers",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Server error: {str(exc)}"}
    )


app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(stuck.router)
app.include_router(reflections.router)
app.include_router(reports.router)


@app.on_event("startup")
def startup():
    init_db()
    print("DevCompass API started")

    scheduler = BackgroundScheduler()

    def run_weekly_reports():
        from core.weekly_report import generate_all_weekly_reports
        db = SessionLocal()
        try:
            generate_all_weekly_reports(db)
        finally:
            db.close()

    scheduler.add_job(
        run_weekly_reports,
        CronTrigger(day_of_week='sun', hour=20, minute=0)
    )
    scheduler.start()


@app.get("/")
def root():
    return {
        "message": "DevCompass API running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/test-db")
def test_db():
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"db": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"db": "failed", "error": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
