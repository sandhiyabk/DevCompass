# api/routes/reports.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database import crud
from core.weekly_report import generate_weekly_report
from core.roadmap import generate_roadmap
from api.routes.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/weekly")
def get_weekly_report(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report = generate_weekly_report(db, str(current_user.id))
    return report


@router.get("/roadmap")
def get_roadmap(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    skills = crud.get_user_skills(db, str(current_user.id))
    user_skills = [
        {"name": s.skill_name, "proficiency": s.proficiency}
        for s in skills
    ]

    recent_reflections = crud.get_recent_reflections(
        db, str(current_user.id), days=30
    )
    recent_concepts = [
        r.new_concept for r in recent_reflections
        if r.new_concept
    ]

    user_data = {
        "role": current_user.role,
        "company_type": current_user.company_type,
        "days_at_company": current_user.days_at_company,
        "personal_goal": current_user.personal_goal
    }

    roadmap = generate_roadmap(user_data, user_skills, recent_concepts)
    return roadmap


@router.get("/history")
def get_report_history(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reports = crud.get_recent_reports(db, str(current_user.id))
    return [
        {
            "week_start": str(r.week_start),
            "week_end": str(r.week_end),
            "tasks_completed": r.tasks_completed,
            "growth_score": r.growth_score,
            "skills_grown": r.skills_grown
        }
        for r in reports
    ]