# api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Include routes
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(stuck.router)
app.include_router(reflections.router)
app.include_router(reports.router)


# Startup
@app.on_event("startup")
def startup():
    init_db()
    print("DevCompass API started")

    # Weekly report scheduler — every Sunday 8 PM
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)