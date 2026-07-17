# api/routes/stuck.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from database.connection import get_db
from database import crud
from core.decision_coach import get_decision
from api.routes.auth import get_current_user

router = APIRouter(prefix="/stuck", tags=["stuck"])


class StuckInput(BaseModel):
    time_stuck_minutes: int
    approaches_tried: str
    next_idea: str
    task_id: Optional[str] = None


@router.post("/decide")
def stuck_decision(
    data: StuckInput,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_data = {
        "role": current_user.role,
        "days_at_company": current_user.days_at_company,
        "company_type": current_user.company_type
    }

    ai_result = get_decision(
        time_stuck_minutes=data.time_stuck_minutes,
        approaches_tried=data.approaches_tried,
        next_idea=data.next_idea,
        user_data=user_data
    )

    session = crud.create_stuck_session(
        db=db,
        user_id=str(current_user.id),
        data=data.dict(),
        ai_result=ai_result
    )

    return {"session_id": str(session.id), **ai_result}