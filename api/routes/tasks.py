# api/routes/tasks.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from database.connection import get_db
from database import crud
from core.task_explainer import explain_task
from api.routes.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskSubmit(BaseModel):
    task_text: str


@router.post("/explain")
def submit_task(
    data: TaskSubmit,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    skills = crud.get_user_skills(db, str(current_user.id))
    user_skills = [
        {"name": s.skill_name, "proficiency": s.proficiency}
        for s in skills
    ]

    user_data = {
        "name": current_user.name,
        "role": current_user.role,
        "company_type": current_user.company_type,
        "days_at_company": current_user.days_at_company,
        "personal_goal": current_user.personal_goal
    }

    ai_result = explain_task(
        data.task_text, user_data, user_skills
    )

    task = crud.create_task(
        db, str(current_user.id), data.task_text, ai_result
    )

    return {
        "task_id": str(task.id),
        **ai_result
    }


@router.get("/recent")
def get_recent_tasks(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tasks = crud.get_recent_tasks(db, str(current_user.id))
    return [
        {
            "id": str(t.id),
            "task_input": t.task_input,
            "what_is_this": t.what_is_this,
            "task_date": str(t.task_date),
            "estimated_hours": t.estimated_hours
        }
        for t in tasks
    ]